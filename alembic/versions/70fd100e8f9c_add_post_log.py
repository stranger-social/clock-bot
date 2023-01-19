"""add post_log

Revision ID: 70fd100e8f9c
Revises: 1b7c0c78af8d
Create Date: 2023-01-19 16:23:37.441791

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '70fd100e8f9c'
down_revision = '1b7c0c78af8d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('post_log',
    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('last_posted', postgresql.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
    )
    pass

def downgrade():
    op.drop_table('post_log')
    pass
