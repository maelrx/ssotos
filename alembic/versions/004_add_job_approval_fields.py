"""Add approval fields to Job model.

Revision ID: 004
Revises: 003
Create Date: 2026-04-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('approval_required', sa.Boolean(), default=False))
    op.add_column('jobs', sa.Column('approval_id', sa.UUID(), nullable=True))


def downgrade() -> None:
    op.drop_column('jobs', 'approval_id')
    op.drop_column('jobs', 'approval_required')
