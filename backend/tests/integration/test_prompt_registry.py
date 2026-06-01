import pytest
from sqlalchemy import select

from app.eval.prompt_registry import has_any_version, register_prompt
from app.models import PromptVersion


@pytest.mark.asyncio
async def test_register_prompt_writes_version_and_file(session, tmp_path, monkeypatch):
    from app.eval import prompt_registry as pr

    monkeypatch.setattr(pr, "_PROMPT_ROOT", tmp_path / "pv")

    v = await register_prompt(session, "review_tagger", "body-a")
    assert v == 1
    await session.commit()

    row = (await session.execute(select(PromptVersion))).scalar_one()
    assert row.name == "review_tagger"
    assert row.version == 1
    assert row.body == "body-a"

    f = (tmp_path / "pv" / "review_tagger" / "v1.json").read_text(encoding="utf-8")
    assert "body-a" in f

    v2 = await register_prompt(session, "review_tagger", "body-b")
    assert v2 == 2
    await session.commit()

    rows = (await session.execute(select(PromptVersion))).scalars().all()
    assert len(rows) == 2
    assert await has_any_version(session, "review_tagger") is True
