"""initial cafes table"""

import pgvector.sqlalchemy
import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "cafes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("google_place_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("rating", sa.REAL(), nullable=True),
        sa.Column("review_count", sa.Integer(), nullable=True),
        sa.Column("price_level", sa.SmallInteger(), nullable=True),
        sa.Column("categories", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("opening_hours", sa.JSON(), nullable=True),
        sa.Column("has_wifi", sa.Boolean(), nullable=True),
        sa.Column("has_outlet", sa.Boolean(), nullable=True),
        sa.Column("noise_level", sa.String(), nullable=True),
        sa.Column("good_for_studying", sa.Boolean(), nullable=True),
        sa.Column("ambience_text", sa.Text(), nullable=False, server_default=""),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(1536), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("google_place_id"),
    )
    op.create_index(
        "cafes_embedding_idx",
        "cafes",
        ["embedding"],
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
    op.create_index("cafes_has_outlet_idx", "cafes", ["has_outlet"])
    op.create_index("cafes_price_level_idx", "cafes", ["price_level"])


def downgrade() -> None:
    op.drop_index("cafes_price_level_idx", "cafes")
    op.drop_index("cafes_has_outlet_idx", "cafes")
    op.drop_index("cafes_embedding_idx", "cafes")
    op.drop_table("cafes")
