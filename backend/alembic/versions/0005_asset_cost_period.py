"""Add recurring cost period to assets."""

import sqlalchemy as sa

from alembic import op

revision: str = "0005_asset_cost_period"
down_revision: str | None = "0004_vendors"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "assets",
        sa.Column(
            "cost_period",
            sa.String(length=20),
            nullable=False,
            server_default="unspecified",
        ),
    )


def downgrade() -> None:
    op.drop_column("assets", "cost_period")
