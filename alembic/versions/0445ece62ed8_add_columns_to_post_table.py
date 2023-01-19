"""add columns to post table

Revision ID: 0445ece62ed8
Revises: 6bb7e10cc7cf
Create Date: 2022-05-20 16:36:31.344964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0445ece62ed8'
down_revision = '6bb7e10cc7cf'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column(
        'published', sa.Boolean(), nullable=False, server_default='TRUE'),)
    op.add_column('posts', sa.Column(
        'created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),)
    pass


def downgrade():
    op.drop_column('posts', 'published')
    op.drop_column('posts', 'created_at')
    pass
