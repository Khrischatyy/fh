"""merge device migrations

Revision ID: 6d9b10f1af55
Revises: c1a2b3d4e5f6, joo25m3rkhhl
Create Date: 2025-12-05 00:37:54.387896

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d9b10f1af55'
down_revision = ('c1a2b3d4e5f6', 'joo25m3rkhhl')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
