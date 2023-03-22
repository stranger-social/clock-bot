"""add lists

Revision ID: 02999f6f9787
Revises: 2503c81f3daf
Create Date: 2023-01-22 16:47:42.624564

"""
from alembic import op
import sqlalchemy as sa

from app.config import settings
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '02999f6f9787'
down_revision = '2503c81f3daf'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        f'{settings.database_table_prefix}list_ids',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('date_created', postgresql.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.Column('date_updated', postgresql.TIMESTAMP(timezone=False), onupdate=sa.text('now()'), nullable=True)
    )
    op.create_table(
        f'{settings.database_table_prefix}list_content',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('list_id', sa.Integer, sa.ForeignKey(f'{settings.database_table_prefix}list_ids.id', ondelete='CASCADE'), nullable=False),
        sa.Column('item_id', sa.Integer, nullable=False),
        sa.Column('content', sa.String(255), nullable=False),
        sa.Column('date_added', postgresql.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.Column('date_last_used', postgresql.TIMESTAMP(timezone=False), nullable=True),
    )
    
    
def downgrade():
    op.drop_table(f'{settings.database_table_prefix}list_content')
    op.drop_table(f'{settings.database_table_prefix}list_ids')
