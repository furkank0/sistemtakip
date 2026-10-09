"""Add renewal reminder overrides and notification queue."""

import sqlalchemy as sa

from alembic import op

revision: str = "0007_renewal_notifications"
down_revision: str | None = "0006_audit_log"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("reminder_days", sa.JSON(), nullable=True))
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "asset_id",
            sa.Integer(),
            sa.ForeignKey("assets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rule", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.Date(), nullable=False),
        sa.Column("channel", sa.String(length=30), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "asset_id", "rule", "expires_at", name="uq_notifications_asset_rule_expiry"
        ),
    )
    op.create_index("ix_notifications_asset_id", "notifications", ["asset_id"])


def downgrade() -> None:
    op.drop_index("ix_notifications_asset_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_column("assets", "reminder_days")
