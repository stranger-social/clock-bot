"""add media path

Revision ID: 2503c81f3daf
Revises: 572b17cafccb
Create Date: 2023-01-20 02:46:44.080303

"""
from alembic import op
import sqlalchemy as sa

from app.config import settings


# revision identifiers, used by Alembic.
revision = '2503c81f3daf'
down_revision = '572b17cafccb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(f'{settings.database_table_prefix}posts', sa.Column('media_path', sa.String()))


def downgrade():
    op.drop_column(f'{settings.database_table_prefix}posts', 'media_path')
