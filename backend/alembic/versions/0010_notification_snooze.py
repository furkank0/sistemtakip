"""Add snooze deadline to renewal notifications."""

import sqlalchemy as sa

from alembic import op

revision: str = "0010_notification_snooze"
down_revision: str | None = "0009_asset_type_details"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("notifications", sa.Column("snoozed_until", sa.DateTime(timezone=True)))


def downgrade() -> None:
    op.drop_column("notifications", "snoozed_until")
