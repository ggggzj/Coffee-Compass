"""Register prompt versions: DB row + JSON file under prompt_versions/<name>/v<n>.json."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PromptVersion

_PROMPT_ROOT = Path(__file__).resolve().parent / "prompt_versions"


async def register_prompt(session: AsyncSession, name: str, body: str) -> int:
    """Insert next version for `name` and mirror to disk. Fails if duplicate (name, version)."""
    r = await session.execute(
        select(func.coalesce(func.max(PromptVersion.version), 0)).where(PromptVersion.name == name)
    )
    max_v = int(r.scalar_one() or 0)
    new_v = max_v + 1
    row = PromptVersion(name=name, version=new_v, body=body)
    session.add(row)
    await session.flush()

    safe_name = name.replace("/", "_")
    out_dir = _PROMPT_ROOT / safe_name
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"v{new_v}.json"
    payload = {
        "name": name,
        "version": new_v,
        "body": body,
        "created_at": datetime.now(tz=UTC).isoformat(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return new_v


async def has_any_version(session: AsyncSession, name: str) -> bool:
    r = await session.execute(
        select(func.count()).select_from(PromptVersion).where(PromptVersion.name == name)
    )
    return int(r.scalar_one() or 0) > 0
