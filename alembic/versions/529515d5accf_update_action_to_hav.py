"""Update action to have timestamp

Revision ID: 529515d5accf
Revises: 148f858fde8b
Create Date: 2014-06-26 17:32:03.564963

"""

# revision identifiers, used by Alembic.
revision = '529515d5accf'
down_revision = '148f858fde8b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('action', sa.Column('when', sa.DateTime, default=sa.func.now()))

def downgrade():
    op.drop_column('action', 'when')
