"""Create tags and asset tag associations."""

import sqlalchemy as sa

from alembic import op

revision: str = "0003_tags"
down_revision: str | None = "0002_assets"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=80), nullable=False, unique=True),
    )
    op.create_index("ix_tags_name", "tags", ["name"])
    op.create_table(
        "asset_tags",
        sa.Column(
            "asset_id", sa.Integer(), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "tag_id", sa.Integer(), sa.ForeignKey("tags.id", ondelete="CASCADE"), nullable=False
        ),
        sa.PrimaryKeyConstraint("asset_id", "tag_id"),
    )


def downgrade() -> None:
    op.drop_table("asset_tags")
    op.drop_index("ix_tags_name", table_name="tags")
    op.drop_table("tags")
