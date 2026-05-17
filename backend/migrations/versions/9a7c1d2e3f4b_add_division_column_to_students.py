"""add division column to students

Revision ID: 9a7c1d2e3f4b
Revises: 9c8d7e6f5a4b
Create Date: 2026-05-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = '9a7c1d2e3f4b'
down_revision: Union[str, None] = '9c8d7e6f5a4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_columns = {column['name'] for column in inspector.get_columns('students')}
    if 'division' not in existing_columns:
        op.add_column('students', sa.Column('division', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('students', 'division')