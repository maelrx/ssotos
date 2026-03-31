"""Add FTS tsvector and pgvector native vector type.

Revision ID: 002
Revises: 001
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add content_tsv tsvector column to chunks table
    op.add_column('chunks', sa.Column('content_tsv', sa.Text(), nullable=True))

    # 2. Populate content_tsv via to_tsvector('english', content) for all existing rows
    # We do this in two steps: first set the column, then backfill
    op.execute("""
        UPDATE chunks
        SET content_tsv = to_tsvector('english', content)
        WHERE content_tsv IS NULL
    """)

    # 3. Create GIN index on chunks.content_tsv
    op.create_index('ix_chunks_content_tsv', 'chunks', ['content_tsv'], postgresql_using='gin')

    # 4. Drop old indexes on embeddings (will be replaced by HNSW)
    op.drop_index('ix_embeddings_chunk_id', table_name='embeddings')
    op.drop_index('ix_embeddings_note_projection_id', table_name='embeddings')

    # 5. Add embedding_vector vector(1536) column to embeddings table
    # First add as nullable to avoid conflicts with existing data
    op.add_column('embeddings', sa.Column('embedding_vector_new', postgresql.VECTOR(1536), nullable=True))

    # 6. Migrate existing JSONB vectors to native vector format
    # Copy data from JSONB column to new vector column
    op.execute("""
        UPDATE embeddings
        SET embedding_vector_new = embedding_vector::vector(1536)
        WHERE embedding_vector IS NOT NULL
    """)

    # 7. Drop the old JSONB column and rename the new one
    op.drop_column('embeddings', 'embedding_vector')
    op.alter_column('embeddings', 'embedding_vector_new', new_column_name='embedding_vector')

    # 8. Create HNSW index on embeddings.embedding_vector using vector_cosine_ops
    op.execute("""
        CREATE INDEX ix_embeddings_embedding_vector_hnsw
        ON embeddings
        USING hnsw (embedding_vector vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)


def downgrade() -> None:
    # 1. Drop HNSW index
    op.drop_index('ix_embeddings_embedding_vector_hnsw', table_name='embeddings')

    # 2. Drop GIN index on chunks
    op.drop_index('ix_chunks_content_tsv', table_name='chunks')

    # 3. Convert vector back to JSONB (cannot preserve actual vector data losslessly)
    op.add_column('embeddings', sa.Column('embedding_vector_old', postgresql.JSONB(astext=sa.Text()), nullable=True))
    op.execute("""
        UPDATE embeddings
        SET embedding_vector_old = embedding_vector::jsonb
        WHERE embedding_vector IS NOT NULL
    """)
    op.drop_column('embeddings', 'embedding_vector')
    op.alter_column('embeddings', 'embedding_vector_old', new_column_name='embedding_vector')

    # 4. Recreate old indexes on embeddings
    op.create_index('ix_embeddings_chunk_id', 'embeddings', ['chunk_id'])
    op.create_index('ix_embeddings_note_projection_id', 'embeddings', ['note_projection_id'])

    # 5. Drop content_tsv column from chunks
    op.drop_column('chunks', 'content_tsv')
