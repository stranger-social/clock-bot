"""add bot tokens

Revision ID: 572b17cafccb
Revises: 70fd100e8f9c
Create Date: 2023-01-19 21:52:37.698068

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '572b17cafccb'
down_revision = '70fd100e8f9c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('bot_tokens',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False)
    )
    op.add_column('posts', sa.Column('bot_token_id', sa.Integer(), sa.ForeignKey('bot_tokens.id')))

    pass


def downgrade():
    # drop table bot_tokens
    op.drop_table('bot_tokens')
    # drop column bot_token_id from posts
    op.drop_column('posts', 'bot_token_id')
    pass
