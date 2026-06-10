from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.agent.memory import Memory, get_memory
from app.agent.react_agent import stream_chat
from app.config import get_settings
from app.db import get_session
from app.schemas import AgentChatRequest, RecommendedCafe

router = APIRouter()


def get_agent_model() -> BaseChatModel:
    """The chat model backing the agent. A FastAPI dependency so tests can override
    it with a scripted fake model (no network)."""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.agent_model, temperature=0, api_key=settings.openai_api_key
    )


@router.post("/agent/chat")
async def agent_chat(
    req: AgentChatRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    model: Annotated[BaseChatModel, Depends(get_agent_model)],
    memory: Annotated[Memory, Depends(get_memory)],
) -> EventSourceResponse:
    # user_id is accepted but dormant in v1 (see ADR-0002): the seam is kept so the
    # Zep / Preference Summary swap-in later touches neither the API nor the client.
    history = memory.load(req.session_id)

    async def event_stream():
        reply: str | None = None
        async for event_type, data in stream_chat(
            session=session, model=model, message=req.message, history=history
        ):
            if event_type == "final":
                reply = data["reply"]
                data = {
                    "reply": reply,
                    "recommendations": [
                        RecommendedCafe(**r).model_dump() for r in data["recommendations"]
                    ],
                }
            yield {"event": event_type, "data": json.dumps(data)}
        # Append only after the stream completes successfully, so a mid-turn failure
        # never leaves a half-Turn in the Conversation (Q6, append-after-respond).
        if reply is not None:
            memory.append(req.session_id, "user", req.message)
            memory.append(req.session_id, "assistant", reply)

    return EventSourceResponse(event_stream())
