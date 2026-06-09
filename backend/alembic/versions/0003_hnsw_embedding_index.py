"""replace ivfflat embedding index with hnsw

HNSW gives better recall/latency for our small (~100 row) cosine-similarity
search than ivfflat, and — unlike ivfflat — does not need a representative
amount of data present at index-build time to choose good centroids. We rebuild
the index here so the Week 4 load test measures HNSW, not ivfflat.
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("cafes_embedding_idx", table_name="cafes")
    op.create_index(
        "cafes_embedding_idx",
        "cafes",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_index("cafes_embedding_idx", table_name="cafes")
    op.create_index(
        "cafes_embedding_idx",
        "cafes",
        ["embedding"],
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )
