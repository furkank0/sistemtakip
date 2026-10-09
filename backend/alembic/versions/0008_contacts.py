"""Add asset contacts."""

import sqlalchemy as sa

from alembic import op

revision: str = "0008_contacts"
down_revision: str | None = "0007_renewal_notifications"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=80), nullable=True),
        sa.Column("role", sa.String(length=120), nullable=True),
    )
    op.create_index("ix_contacts_name", "contacts", ["name"])
    op.create_table(
        "asset_contacts",
        sa.Column(
            "asset_id",
            sa.Integer(),
            sa.ForeignKey("assets.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "contact_id",
            sa.Integer(),
            sa.ForeignKey("contacts.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("asset_contacts")
    op.drop_index("ix_contacts_name", table_name="contacts")
    op.drop_table("contacts")
