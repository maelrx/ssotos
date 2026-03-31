"""Initial schema — creates all 12 tables.

Revision ID: 001
Revises:
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # 1. workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('root_path', sa.String(length=1024), nullable=False),
        sa.Column('config', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. actors
    op.create_table(
        'actors',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('actor_type', sa.String(length=50), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_actors_workspace_id', 'actors', ['workspace_id'])

    # 3. notes_projection
    op.create_table(
        'notes_projection',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('note_path', sa.String(length=1024), nullable=False),
        sa.Column('note_hash', sa.String(length=64), nullable=False),
        sa.Column('kind', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('tags', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('links', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('frontmatter', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('indexed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('sync_state', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notes_projection_workspace_id', 'notes_projection', ['workspace_id'])
    op.create_index('ix_notes_projection_workspace_path', 'notes_projection', ['workspace_id', 'note_path'], unique=True)

    # 4. policy_rules
    op.create_table(
        'policy_rules',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('actor', sa.String(length=255), nullable=True),
        sa.Column('capability_group', sa.String(length=50), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=True),
        sa.Column('domain', sa.String(length=50), nullable=True),
        sa.Column('path_pattern', sa.String(length=512), nullable=True),
        sa.Column('note_type', sa.String(length=50), nullable=True),
        sa.Column('sensitivity', sa.Integer(), nullable=True),
        sa.Column('outcome', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_policy_rules_workspace_id', 'policy_rules', ['workspace_id'])

    # 5. proposals
    op.create_table(
        'proposals',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('proposal_type', sa.String(length=50), nullable=False),
        sa.Column('source_domain', sa.String(length=50), nullable=False),
        sa.Column('target_domain', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=True),
        sa.Column('branch_name', sa.String(length=255), nullable=False),
        sa.Column('worktree_path', sa.String(length=1024), nullable=True),
        sa.Column('actor', sa.String(length=255), nullable=False),
        sa.Column('target_path', sa.String(length=1024), nullable=True),
        sa.Column('source_ref', sa.String(length=255), nullable=True),
        sa.Column('patch_path', sa.String(length=1024), nullable=True),
        sa.Column('base_commit', sa.String(length=40), nullable=True),
        sa.Column('head_commit', sa.String(length=40), nullable=True),
        sa.Column('reviewed_by', sa.String(length=255), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_note', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_proposals_workspace_status', 'proposals', ['workspace_id', 'status'])
    op.create_index('ix_proposals_workspace_id', 'proposals', ['workspace_id'])

    # 6. approvals
    op.create_table(
        'approvals',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('proposal_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('requester', sa.String(length=255), nullable=False),
        sa.Column('capability', sa.String(length=100), nullable=False),
        sa.Column('domain', sa.String(length=50), nullable=False),
        sa.Column('target', sa.String(length=1024), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('reviewed_by', sa.String(length=255), nullable=True),
        sa.Column('review_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.ForeignKeyConstraint(['proposal_id'], ['proposals.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_approvals_workspace_id', 'approvals', ['workspace_id'])
    op.create_index('ix_approvals_proposal_id', 'approvals', ['proposal_id'])

    # 7. jobs
    op.create_table(
        'jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('input_data', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('result_data', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('error_message', sa.String(length=2048), nullable=True),
        sa.Column('attempt_count', sa.Integer(), nullable=True),
        sa.Column('max_attempts', sa.Integer(), nullable=True),
        sa.Column('claimed_by', sa.String(length=255), nullable=True),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('trace_id', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_jobs_workspace_id', 'jobs', ['workspace_id'])
    op.create_index('ix_jobs_workspace_status', 'jobs', ['workspace_id', 'status'])
    op.create_index('ix_jobs_priority_created', 'jobs', ['priority', 'created_at'])

    # 8. job_events
    op.create_table(
        'job_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('message', sa.String(length=1024), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('trace_id', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_events_job_id', 'job_events', ['job_id'])

    # 9. chunks
    op.create_table(
        'chunks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('note_projection_id', sa.UUID(), nullable=False),
        sa.Column('heading_path', sa.String(length=512), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('char_start', sa.Integer(), nullable=False),
        sa.Column('char_end', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['note_projection_id'], ['notes_projection.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_chunks_note_projection_id', 'chunks', ['note_projection_id'])
    op.create_index('ix_chunks_note_projection_index', 'chunks', ['note_projection_id', 'chunk_index'])

    # 10. embeddings
    op.create_table(
        'embeddings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('chunk_id', sa.UUID(), nullable=False),
        sa.Column('note_projection_id', sa.UUID(), nullable=False),
        sa.Column('embedding_vector', postgresql.JSONB(astext=sa.Text()), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['chunk_id'], ['chunks.id']),
        sa.ForeignKeyConstraint(['note_projection_id'], ['notes_projection.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_embeddings_chunk_id', 'embeddings', ['chunk_id'])
    op.create_index('ix_embeddings_note_projection_id', 'embeddings', ['note_projection_id'])

    # 11. artifacts
    op.create_table(
        'artifacts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=True),
        sa.Column('artifact_type', sa.String(length=50), nullable=False),
        sa.Column('source_url', sa.String(length=2048), nullable=True),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('provenance', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_artifacts_workspace_id', 'artifacts', ['workspace_id'])
    op.create_index('ix_artifacts_job_id', 'artifacts', ['job_id'])
    op.create_index('ix_artifacts_workspace_type', 'artifacts', ['workspace_id', 'artifact_type'])

    # 12. audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=True),
        sa.Column('event_id', sa.UUID(), nullable=False),
        sa.Column('trace_id', sa.String(length=64), nullable=True),
        sa.Column('actor', sa.String(length=255), nullable=False),
        sa.Column('capability', sa.String(length=100), nullable=True),
        sa.Column('domain', sa.String(length=50), nullable=True),
        sa.Column('target', sa.String(length=1024), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=True),
        sa.Column('result', sa.String(length=20), nullable=False),
        sa.Column('reason', sa.String(length=1024), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id')
    )
    op.create_index('ix_audit_logs_workspace_id', 'audit_logs', ['workspace_id'])
    op.create_index('ix_audit_logs_workspace_timestamp', 'audit_logs', ['workspace_id', 'timestamp'])
    op.create_index('ix_audit_logs_actor_timestamp', 'audit_logs', ['actor', 'timestamp'])
    op.create_index('ix_audit_logs_trace_id', 'audit_logs', ['trace_id'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('artifacts')
    op.drop_table('embeddings')
    op.drop_table('chunks')
    op.drop_table('job_events')
    op.drop_table('jobs')
    op.drop_table('approvals')
    op.drop_table('proposals')
    op.drop_table('policy_rules')
    op.drop_table('notes_projection')
    op.drop_table('actors')
    op.drop_table('workspaces')
