"""Activate Tutors

Revision ID: 1c7a3ed9b023
Revises: e792f36f9d9
Create Date: 2014-11-05 15:37:09.573811

"""

# revision identifiers, used by Alembic.
revision = '1c7a3ed9b023'
down_revision = 'e792f36f9d9'

from alembic import op
import sqlalchemy as db


def upgrade():
    # op.add_column('tutor', db.Column('approved', db.Boolean, default=False))
    pass

def downgrade():
    pass
