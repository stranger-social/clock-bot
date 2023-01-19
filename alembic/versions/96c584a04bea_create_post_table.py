"""create post table

Revision ID: 96c584a04bea
Revises: 
Create Date: 2022-05-20 16:00:40.094551

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96c584a04bea'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('posts', sa.Column('id', sa.Integer(), nullable = False, primary_key=True),sa.Column('title', sa.String(), nullable=False),sa.Column('content', sa.String(), nullable=False))   
    pass


def downgrade():
    op.drop_table('posts')
    pass
