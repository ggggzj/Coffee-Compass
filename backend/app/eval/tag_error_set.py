"""Load the labeled tag-error set: queries -> ground-truth hard-constraint slots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

_TAG_ERROR_PATH = Path(__file__).resolve().parent / "tag_error_set.json"


class GoldSlots(BaseModel):
    """The correct SQL-constraint slots: set only when explicitly asked, else None."""

    has_outlet: bool | None = None
    open_now: bool | None = None
    price_max: int | None = None


class TagErrorItem(BaseModel):
    id: str
    lang: Literal["en", "zh"]
    category: Literal["vibe", "constraint", "trap"]
    query: str
    gold: GoldSlots
    note: str = ""


class TagErrorSet(BaseModel):
    version: int = 1
    description: str = ""
    items: list[TagErrorItem]


def load_tag_error_set(path: Path | None = None) -> TagErrorSet:
    p = path or _TAG_ERROR_PATH
    raw: dict[str, Any] = json.loads(p.read_text(encoding="utf-8"))
    return TagErrorSet.model_validate(raw)
