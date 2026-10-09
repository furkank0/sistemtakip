"""Create vendors and link assets to vendors."""

import sqlalchemy as sa

from alembic import op

revision: str = "0004_vendors"
down_revision: str | None = "0003_tags"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "vendors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("support_email", sa.String(length=255)),
        sa.Column("panel_url", sa.String(length=500)),
    )
    op.create_index("ix_vendors_name", "vendors", ["name"])
    op.add_column("assets", sa.Column("vendor_id", sa.Integer(), nullable=True))
    op.create_index("ix_assets_vendor_id", "assets", ["vendor_id"])
    op.create_foreign_key(
        "fk_assets_vendor_id_vendors",
        "assets",
        "vendors",
        ["vendor_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_assets_vendor_id_vendors", "assets", type_="foreignkey")
    op.drop_index("ix_assets_vendor_id", table_name="assets")
    op.drop_column("assets", "vendor_id")
    op.drop_index("ix_vendors_name", table_name="vendors")
    op.drop_table("vendors")
