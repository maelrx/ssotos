"""Add retry and checkpoint fields to Job model.

Revision ID: 003
Revises: 002
Create Date: 2026-04-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('next_retry_at', sa.DateTime(), nullable=True))
    op.add_column('jobs', sa.Column('last_checkpoint', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('jobs', 'next_retry_at')
    op.drop_column('jobs', 'last_checkpoint')
