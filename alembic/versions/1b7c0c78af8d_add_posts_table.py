"""add posts table

Revision ID: 1b7c0c78af8d
Revises: 9228d5423d64
Create Date: 2023-01-19 05:36:30.758720

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '1b7c0c78af8d'
down_revision = '9228d5423d64'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable = False, primary_key=True),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column("sensitive", sa.Boolean(), server_default="False", nullable=False),
    sa.Column('spoiler_text', sa.String(), nullable=True),
    sa.Column('visibility', sa.String(), nullable=False, default="unlisted"),
    sa.Column('published', sa.Boolean(), server_default="True", nullable=False),
    sa.Column('crontab_schedule', sa.String(), nullable=False),
    sa.Column('next_run', postgresql.TIMESTAMP(timezone=False), nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False)
    )
    op.create_foreign_key('posts_owner_id_fkey', source_table='posts', referent_table="users", local_cols=[
                          'owner_id'], remote_cols=['id'], ondelete="CASCADE")
    op.create_index('ix_crontab_schedule', 'posts', ['crontab_schedule'], unique=False)
    pass

def downgrade():
    op.drop_table('posts')
    pass