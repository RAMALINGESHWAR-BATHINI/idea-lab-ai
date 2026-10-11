"""Add is_published column to events table.

The events model declares ``is_published`` but the original migration
omitted the corresponding column. This fixes the schema.
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy  # noqa: F401

revision: str = "235c820584a5"
down_revision: Union[str, None] = "ee9a7cd3da52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "events",
        sa.Column(
            "is_published",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("events", "is_published")
