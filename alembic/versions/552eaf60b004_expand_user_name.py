"""Expand user_name

Revision ID: 552eaf60b004
Revises: e9cbaf74ed2
Create Date: 2014-09-09 18:56:35.036156

"""

# revision identifiers, used by Alembic.
revision = '552eaf60b004'
down_revision = 'e9cbaf74ed2'

from alembic import op
import sqlalchemy as db


def upgrade():
    op.alter_column('user', 'user_name', type_=db.UnicodeText)


def downgrade():
    pass
