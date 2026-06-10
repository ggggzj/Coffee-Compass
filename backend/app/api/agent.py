from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.react_agent import run_chat
from app.config import get_settings
from app.db import get_session
from app.schemas import AgentChatRequest, AgentChatResponse, RecommendedCafe

router = APIRouter()


def get_agent_model() -> BaseChatModel:
    """The chat model backing the agent. A FastAPI dependency so tests can override
    it with a scripted fake model (no network)."""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.agent_model, temperature=0, api_key=settings.openai_api_key
    )


@router.post("/agent/chat", response_model=AgentChatResponse)
async def agent_chat(
    req: AgentChatRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    model: Annotated[BaseChatModel, Depends(get_agent_model)],
) -> AgentChatResponse:
    # user_id is accepted but dormant in v1 (see ADR-0002): the seam is kept so the
    # Zep / Preference Summary swap-in later touches neither the API nor the client.
    reply, recommendations = await run_chat(
        session=session, model=model, message=req.message
    )
    return AgentChatResponse(
        reply=reply,
        recommendations=[RecommendedCafe(**r) for r in recommendations],
    )
