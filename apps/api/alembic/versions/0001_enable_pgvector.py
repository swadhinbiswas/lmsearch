"""enable pgvector + core tables"""

revision = "0001"
down_revision = None

import sqlalchemy as sa  # noqa: E402

from alembic import op  # noqa: E402


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("source", sa.String(64), default="seed"),
        sa.Column("source_id", sa.String(256), default=""),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("brand", sa.String(128), default=""),
        sa.Column("category", sa.String(64), default="laptop"),
        sa.Column("price", sa.Numeric(12, 2), default=0),
        sa.Column("currency", sa.String(8), default="USD"),
        sa.Column("url", sa.Text, default=""),
        sa.Column("image_urls", sa.JSON, default=list),
        sa.Column("description", sa.Text, default=""),
        sa.Column("rating", sa.Float, default=0.0),
        sa.Column("in_stock", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_products_price", "products", ["price"])
    op.create_index("ix_products_category", "products", ["category"])
    op.create_table(
        "product_specs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id", ondelete="CASCADE")),
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column("value_text", sa.Text, default=""),
        sa.Column("value_num", sa.Float, nullable=True),
        sa.Column("unit", sa.String(32), default=""),
    )
    op.create_index("ix_specs_key_num", "product_specs", ["key", "value_num"])
    op.create_table(
        "product_embeddings",
        sa.Column(
            "product_id",
            sa.Integer,
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("embedding", sa.Text, nullable=True),
        sa.Column("text_hash", sa.String(64), default=""),
    )
    op.execute(
        "ALTER TABLE product_embeddings ALTER COLUMN embedding "
        "TYPE vector(384) USING embedding::vector(384)"
    )
    op.create_table(
        "search_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("raw_query", sa.Text, default=""),
        sa.Column("parsed_json", sa.JSON, default=dict),
        sa.Column("latency_ms", sa.Integer, default=0),
        sa.Column("result_count", sa.Integer, default=0),
        sa.Column("clicked_product_id", sa.Integer, nullable=True),
        sa.Column("ts", sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table("search_logs")
    op.drop_table("product_embeddings")
    op.drop_index("ix_specs_key_num")
    op.drop_table("product_specs")
    op.drop_index("ix_products_category")
    op.drop_index("ix_products_price")
    op.drop_table("products")
