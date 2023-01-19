"""add users table

Revision ID: 9228d5423d64
Revises: 
Create Date: 2023-01-19 05:34:48.509856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9228d5423d64'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=False),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
                    sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )
    pass


def downgrade():
    op.drop_table('users')
    pass
