"""Merge migration branches

Revision ID: dddd4444eeee5555
Revises: cccc3333dddd4444, f8e9d0c1b2a3
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dddd4444eeee5555'
down_revision: Union[str, Sequence[str]] = ('cccc3333dddd4444', 'f8e9d0c1b2a3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
