"""HNSW index + GIN specs"""

revision = "0002"
down_revision = "0001"

from alembic import op  # noqa: E402


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_embeddings_hnsw ON product_embeddings "
        "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_products_title_gin ON products "
        "USING gin (to_tsvector('english', title))"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_embeddings_hnsw")
    op.execute("DROP INDEX IF EXISTS ix_products_title_gin")
