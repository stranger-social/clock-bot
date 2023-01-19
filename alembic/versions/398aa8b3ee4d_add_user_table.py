"""Add user table

Revision ID: 398aa8b3ee4d
Revises: 96c584a04bea
Create Date: 2022-05-20 16:27:01.402620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '398aa8b3ee4d'
down_revision = '96c584a04bea'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True),
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
