"""Add social to user

Revision ID: e9cbaf74ed2
Revises: 35f49a1c3406
Create Date: 2014-09-09 16:24:52.712756

"""

# revision identifiers, used by Alembic.
revision = 'e9cbaf74ed2'
down_revision = '35f49a1c3406'

from alembic import op
import sqlalchemy as db


def upgrade():
    op.add_column('user', db.Column('created_at', db.TIMESTAMP, server_default=db.func.now()))
    op.add_column('user', db.Column('facebook_token', db.UnicodeText))
    op.add_column('user', db.Column('twitter_token', db.UnicodeText))
    op.add_column('user', db.Column('twitter_secret', db.UnicodeText))
    op.add_column('user', db.Column('linkedin_token', db.UnicodeText))
    op.add_column('user', db.Column('google_token', db.UnicodeText))


def downgrade():
    pass
