"""Make email nullable in teachers table

Revision ID: eeee5555ffff6666
Revises: dddd4444eeee5555
Create Date: 2026-05-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eeee5555ffff6666'
down_revision: Union[str, None] = 'dddd4444eeee5555'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('teachers', 'email',
               existing_type=sa.String(),
               nullable=True)


def downgrade() -> None:
    op.alter_column('teachers', 'email',
               existing_type=sa.String(),
               nullable=False)
