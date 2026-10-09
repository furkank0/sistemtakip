"""Create assets table."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_assets"
down_revision: str | None = "0001_initial"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("vendor", sa.String(length=255)),
        sa.Column("owner", sa.String(length=255)),
        sa.Column("cost", sa.Numeric(precision=12, scale=2)),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="TRY"),
        sa.Column("starts_at", sa.Date()),
        sa.Column("expires_at", sa.Date()),
        sa.Column("auto_renew", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_assets_type", "assets", ["type"])
    op.create_index("ix_assets_name", "assets", ["name"])
    op.create_index("ix_assets_expires_at", "assets", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_assets_expires_at", table_name="assets")
    op.drop_index("ix_assets_name", table_name="assets")
    op.drop_index("ix_assets_type", table_name="assets")
    op.drop_table("assets")
