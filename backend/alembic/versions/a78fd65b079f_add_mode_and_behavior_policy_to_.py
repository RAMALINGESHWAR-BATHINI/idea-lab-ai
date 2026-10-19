"""Add mode and behavior_policy columns to conversations."""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a78fd65b079f"
down_revision: Union[str, None] = "235c820584a5"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("conversations", sa.Column("mode", sa.String(20), nullable=True))
    op.add_column("conversations", sa.Column("behavior_policy", sa.String(20), nullable=True))


def downgrade() -> None:
    op.drop_column("conversations", "behavior_policy")
    op.drop_column("conversations", "mode")
