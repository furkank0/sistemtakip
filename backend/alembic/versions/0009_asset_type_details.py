"""Add fields specific to asset types."""

import sqlalchemy as sa

from alembic import op

revision: str = "0009_asset_type_details"
down_revision: str | None = "0008_contacts"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("nameservers", sa.JSON(), nullable=True))
    op.add_column("assets", sa.Column("hosting_plan", sa.String(length=255), nullable=True))
    op.add_column("assets", sa.Column("management_url", sa.String(length=500), nullable=True))
    op.add_column("assets", sa.Column("ip_address", sa.String(length=45), nullable=True))
    op.add_column("assets", sa.Column("operating_system", sa.String(length=120), nullable=True))
    op.add_column("assets", sa.Column("vcpu_count", sa.Integer(), nullable=True))
    op.add_column("assets", sa.Column("memory_gb", sa.Integer(), nullable=True))
    op.add_column("assets", sa.Column("storage_gb", sa.Integer(), nullable=True))
    op.add_column("assets", sa.Column("product_name", sa.String(length=255), nullable=True))
    op.add_column("assets", sa.Column("seat_count", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("assets", "seat_count")
    op.drop_column("assets", "product_name")
    op.drop_column("assets", "storage_gb")
    op.drop_column("assets", "memory_gb")
    op.drop_column("assets", "vcpu_count")
    op.drop_column("assets", "operating_system")
    op.drop_column("assets", "ip_address")
    op.drop_column("assets", "management_url")
    op.drop_column("assets", "hosting_plan")
    op.drop_column("assets", "nameservers")
