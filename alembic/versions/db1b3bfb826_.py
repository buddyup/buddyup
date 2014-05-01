"""Add Operator table

Revision ID: db1b3bfb826
Revises: 23a622f768da
Create Date: 2014-05-01 11:57:36.243472

"""

# revision identifiers, used by Alembic.
revision = 'db1b3bfb826'
down_revision = '23a622f768da'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'operator',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('login', sa.String(32), index=True, unique=True, nullable=False),
        sa.Column('password', sa.String(64)), # sha256 hexdigest is 64 chars
    )

def downgrade():
    op.drop_table('operator')
