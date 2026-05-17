"""merge 9a7c and c1d7 heads

Revision ID: f8e9d0c1b2a3
Revises: 9a7c1d2e3f4b, c1d7b4a8e2f1
Create Date: 2026-05-17 00:00:00.000000

"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "f8e9d0c1b2a3"
down_revision: Union[str, Sequence[str], None] = ("9a7c1d2e3f4b", "c1d7b4a8e2f1")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
