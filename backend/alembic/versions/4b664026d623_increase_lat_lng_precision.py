"""increase_lat_lng_precision

Revision ID: 4b664026d623
Revises: 317f9c06af8a
Create Date: 2025-10-30 18:41:45.493741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b664026d623'
down_revision = '317f9c06af8a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Increase precision for latitude and longitude to support worldwide coordinates
    # NUMERIC(9, 6) supports longitude range -180 to 180 (3 digits before decimal)
    # and latitude range -90 to 90 (2 digits before decimal)
    op.execute('ALTER TABLE addresses ALTER COLUMN latitude TYPE NUMERIC(9, 6)')
    op.execute('ALTER TABLE addresses ALTER COLUMN longitude TYPE NUMERIC(9, 6)')


def downgrade() -> None:
    # Revert to original precision
    op.execute('ALTER TABLE addresses ALTER COLUMN latitude TYPE NUMERIC(8, 6)')
    op.execute('ALTER TABLE addresses ALTER COLUMN longitude TYPE NUMERIC(8, 6)')
