"""Register review_tagger v2 prompt in prompt_versions if table is empty for that name."""

from __future__ import annotations

import asyncio

import click

from app.db import SessionLocal
from app.eval.prompt_registry import has_any_version, register_prompt
from app.ingestion.review_tagger_v2 import REVIEW_TAGGER_V2_BODY


@click.command()
def main() -> None:
    async def _go() -> None:
        async with SessionLocal() as session:
            if await has_any_version(session, "review_tagger"):
                click.echo(
                    "prompt_versions already has review_tagger; "
                    "use register_prompt for new versions"
                )
                return
            v = await register_prompt(session, "review_tagger", REVIEW_TAGGER_V2_BODY)
            await session.commit()
            click.echo(f"Registered review_tagger version {v}")

    asyncio.run(_go())


if __name__ == "__main__":
    main()
