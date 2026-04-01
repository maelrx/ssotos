"""Add idempotency_key to jobs table.

Revision ID: 005
Revises: 004
Create Date: 2026-04-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('idempotency_key', sa.String(255), nullable=True, unique=True))


def downgrade() -> None:
    op.drop_column('jobs', 'idempotency_key')
