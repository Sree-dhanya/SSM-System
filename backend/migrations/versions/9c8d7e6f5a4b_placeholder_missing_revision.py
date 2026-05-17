"""placeholder missing revision

Revision ID: 9c8d7e6f5a4b
Revises: a65fb55baae5
Create Date: 2026-05-17 00:00:00.000000

This migration exists to restore a missing Alembic revision file that the
database is already stamped to. It is intentionally a no-op.

"""

from typing import Sequence, Union

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = "9c8d7e6f5a4b"
down_revision: Union[str, None] = "a65fb55baae5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No-op: DB is already at this revision.
    pass


def downgrade() -> None:
    # No-op.
    pass