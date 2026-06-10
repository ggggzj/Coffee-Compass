from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.schemas import CafeDetail
from app.search.service import get_cafe

router = APIRouter()


@router.get("/cafes/{cafe_id}", response_model=CafeDetail)
async def read_cafe(
    cafe_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CafeDetail:
    # Same cafe-by-id load path the get_shop_detail agent tool uses.
    cafe = await get_cafe(cafe_id=cafe_id, session=session)
    if cafe is None:
        raise HTTPException(status_code=404, detail="cafe not found")
    return CafeDetail.model_validate(cafe)
