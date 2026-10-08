"""Initial empty schema revision."""

from collections.abc import Sequence
from typing import Optional

revision: str = "0001_initial"
down_revision: Optional[str] = None
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
