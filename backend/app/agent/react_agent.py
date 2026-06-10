from __future__ import annotations

from dataclasses import dataclass, field

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langgraph.errors import GraphRecursionError
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools import DEFAULT_MAX_SEARCHES, build_agent_tools

SYSTEM_PROMPT = (
    "You are CoffeeCompass, a concise local coffee guide for the USC/LA area. "
    "Use the tools to ground every recommendation in real shops — never invent "
    "cafes.\n"
    "Search ONCE: write a single natural-language query that captures everything "
    "the user wants (vibe, price, outlets, open-now), then use whatever it "
    "returns. Do NOT re-search by rewording or swapping synonyms (e.g. cheap -> "
    "affordable -> budget) to try to find more — one search is enough.\n"
    "Recommend up to 5 cafes with a one-line rationale each. Fewer than 3 is "
    "perfectly fine when few match — do not keep hunting. When you have chosen "
    "which cafes to recommend, call present_recommendations with their ids before "
    "giving your final answer."
)

MAX_RECOMMENDATIONS = 5

# Hard backstop on agent super-steps (model+tool turns). The search budget in
# build_agent_tools is the practical cap; this guarantees the graph can never loop
# even if the model ignores tool messages. Normal turns use ~4-6 steps.
RECURSION_LIMIT = 12


@dataclass
class TurnContext:
    """Per-request state the tools record into, so the final payload is built in
    deterministic backend code rather than parsed from the LLM's prose."""

    seen: dict[int, dict] = field(default_factory=dict)
    last_batch: list[int] = field(default_factory=list)
    declared_ids: list[int] | None = None
    rationale: str | None = None

    def record_shops(self, summaries: list[dict]) -> None:
        self.last_batch = [s["id"] for s in summaries]
        for s in summaries:
            self.seen[s["id"]] = s

    def recommendations(self) -> list[dict]:
        """Hydrate the final recommendations. Declared ids (grounded against what
        the tools surfaced) win; otherwise fall back to the last search batch."""
        if self.declared_ids is not None:
            ids = [i for i in self.declared_ids if i in self.seen]
        else:
            ids = self.last_batch[:MAX_RECOMMENDATIONS]
        return [self.seen[i] for i in ids if i in self.seen]


class PresentRecommendationsArgs(BaseModel):
    cafe_ids: list[int] = Field(..., description="Ids of the cafes you are recommending.")
    rationale: str = Field("", description="A short overall rationale for the picks.")


def build_agent(
    session: AsyncSession, model: BaseChatModel, *, system_preamble: str | None = None
):
    """Build a per-request agent over the search tools, closing over a fresh
    TurnContext. Returns (agent, turn_context).

    ``system_preamble`` (e.g. a User's cross-Conversation Preference Summary) is
    appended to the base system prompt so it shapes this turn's recommendations."""
    turn = TurnContext()
    tools = build_agent_tools(
        session, on_results=turn.record_shops, max_searches=DEFAULT_MAX_SEARCHES
    )
    system_prompt = SYSTEM_PROMPT
    if system_preamble:
        system_prompt = f"{SYSTEM_PROMPT}\n\n{system_preamble}"

    async def present_recommendations(cafe_ids: list[int], rationale: str = "") -> str:
        turn.declared_ids = list(cafe_ids)
        turn.rationale = rationale
        return f"Recorded {len(cafe_ids)} recommendation(s)."

    present_tool = StructuredTool.from_function(
        coroutine=present_recommendations,
        name="present_recommendations",
        description=(
            "Declare the final cafe ids you are recommending to the user. Call this "
            "once, after searching, with the ids of the shops you chose."
        ),
        args_schema=PresentRecommendationsArgs,
    )

    agent = create_agent(model, [*tools, present_tool], system_prompt=system_prompt)
    return agent, turn


def _last_ai_text(messages: list[BaseMessage]) -> str:
    for m in reversed(messages):
        if isinstance(m, AIMessage) and m.content:
            return m.content if isinstance(m.content, str) else str(m.content)
    return ""


async def run_chat(
    *,
    session: AsyncSession,
    model: BaseChatModel,
    message: str,
    history: list[BaseMessage] | None = None,
    system_preamble: str | None = None,
) -> tuple[str, list[dict]]:
    """Run one agent turn and assemble its grounded final payload.

    Returns (reply_prose, recommendations). The recommendations are always built
    from TurnContext, so the payload is guaranteed even if the model never calls
    present_recommendations."""
    agent, turn = build_agent(session, model, system_preamble=system_preamble)
    messages = [*(history or []), HumanMessage(content=message)]
    try:
        out = await agent.ainvoke(
            {"messages": messages}, config={"recursion_limit": RECURSION_LIMIT}
        )
        reply = _last_ai_text(out["messages"])
    except GraphRecursionError:
        # Backstop tripped — still return the grounded payload we accumulated.
        reply = ""
    return reply, turn.recommendations()


def _tool_output_str(output) -> str:
    content = getattr(output, "content", output)
    text = content if isinstance(content, str) else str(content)
    return text[:500]


async def stream_chat(
    *,
    session: AsyncSession,
    model: BaseChatModel,
    message: str,
    history: list[BaseMessage] | None = None,
    system_preamble: str | None = None,
):
    """Run one agent turn, yielding (event_type, data) as the ReAct loop unfolds.

    Event types: 'thought' (reasoning before an action), 'action' (a tool call),
    'observation' (a tool result), and exactly one terminal 'final' carrying the
    grounded payload from TurnContext. The 'final' event is always emitted, so the
    map is never left empty even on a prose-only or tool-less turn (Q8)."""
    agent, turn = build_agent(session, model, system_preamble=system_preamble)
    messages = [*(history or []), HumanMessage(content=message)]
    reply = ""
    try:
        async for ev in agent.astream_events(
            {"messages": messages}, version="v2", config={"recursion_limit": RECURSION_LIMIT}
        ):
            etype = ev["event"]
            data = ev.get("data", {})
            if etype == "on_chat_model_end":
                out = data.get("output")
                content = getattr(out, "content", "") or ""
                text = content if isinstance(content, str) else str(content)
                if getattr(out, "tool_calls", None):
                    if text:
                        yield "thought", {"text": text}
                else:
                    reply = text  # an AI message with no tool calls is the final answer
            elif etype == "on_tool_start":
                yield "action", {"tool": ev.get("name"), "input": data.get("input")}
            elif etype == "on_tool_end":
                output = _tool_output_str(data.get("output"))
                yield "observation", {"tool": ev.get("name"), "output": output}
    except GraphRecursionError:
        # Backstop tripped — stop streaming steps and fall through to the final
        # event, which is still guaranteed below.
        pass
    yield "final", {"reply": reply, "recommendations": turn.recommendations()}
