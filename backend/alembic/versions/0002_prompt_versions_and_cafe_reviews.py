"""prompt_versions table; cafe editorial_summary and review_snippets for Week 2"""

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prompt_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "version", name="prompt_versions_name_version_uq"),
    )
    op.add_column(
        "cafes",
        sa.Column("editorial_summary", sa.Text(), nullable=True),
    )
    op.add_column(
        "cafes",
        sa.Column("review_snippets", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("cafes", "review_snippets")
    op.drop_column("cafes", "editorial_summary")
    op.drop_table("prompt_versions")
