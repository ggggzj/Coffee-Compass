"""Load golden eval queries + expected cafe IDs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

_GOLDEN_PATH = Path(__file__).resolve().parent / "golden_set.json"


class GoldenItem(BaseModel):
    id: str
    query: str
    expected_cafe_ids: list[int] = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class GoldenSet(BaseModel):
    version: int = 1
    items: list[GoldenItem]


def load_golden_set(path: Path | None = None) -> GoldenSet:
    p = path or _GOLDEN_PATH
    raw: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    return GoldenSet.model_validate(raw)
