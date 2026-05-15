"""add optional clinical fields to therapy reports

Revision ID: c1d7b4a8e2f1
Revises: f4b754419606
Create Date: 2026-05-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d7b4a8e2f1'
down_revision: Union[str, None] = 'f4b754419606'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    table_exists = inspector.has_table('therapy_reports')

    if not table_exists:
        op.create_table(
            'therapy_reports',
            sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
            sa.Column('student_id', sa.Integer(), sa.ForeignKey('students.id', ondelete='CASCADE'), nullable=False),
            sa.Column('teacher_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('report_date', sa.Date(), nullable=False),
            sa.Column('therapy_type', sa.String(length=255), nullable=True),
            sa.Column('present_complaints', sa.Text(), nullable=True),
            sa.Column('current_observation', sa.Text(), nullable=True),
            sa.Column('assessment_done', sa.Text(), nullable=True),
            sa.Column('provisional_diagnosis', sa.Text(), nullable=True),
            sa.Column('progress_notes', sa.Text(), nullable=True),
            sa.Column('goals_achieved', sa.JSON(), nullable=True),
            sa.Column('progress_level', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        )
    else:
        existing_columns = {column['name'] for column in inspector.get_columns('therapy_reports')}
        columns_to_add = [
            sa.Column('present_complaints', sa.Text(), nullable=True),
            sa.Column('current_observation', sa.Text(), nullable=True),
            sa.Column('assessment_done', sa.Text(), nullable=True),
            sa.Column('provisional_diagnosis', sa.Text(), nullable=True),
        ]
        for column in columns_to_add:
            if column.name not in existing_columns:
                op.add_column('therapy_reports', column)

    index_names = {index['name'] for index in inspector.get_indexes('therapy_reports')} if table_exists else set()
    if 'ix_therapy_reports_student_id' not in index_names:
        op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_therapy_reports_student_id ON therapy_reports (student_id)'))
    if 'ix_therapy_reports_teacher_id' not in index_names:
        op.execute(sa.text('CREATE INDEX IF NOT EXISTS ix_therapy_reports_teacher_id ON therapy_reports (teacher_id)'))


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table('therapy_reports'):
        return

    existing_columns = {column['name'] for column in inspector.get_columns('therapy_reports')}
    for column_name in [
        'provisional_diagnosis',
        'assessment_done',
        'current_observation',
        'present_complaints',
    ]:
        if column_name in existing_columns:
            op.drop_column('therapy_reports', column_name)