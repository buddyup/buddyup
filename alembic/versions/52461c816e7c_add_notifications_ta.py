"""Add notifications table

Revision ID: 52461c816e7c
Revises: 148f858fde8b
Create Date: 2014-08-21 11:09:55.276087

"""

# revision identifiers, used by Alembic.
revision = '52461c816e7c'
down_revision = '148f858fde8b'

from alembic import op
import sqlalchemy as db


def upgrade():
    op.create_table(
        'notification',
        db.Column('id', db.Integer, primary_key=True),
        db.Column('time', db.TIMESTAMP, server_default=db.func.now()),
        db.Column('sender_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('recipient_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('payload', db.UnicodeText, default=u""),
        db.Column('action_link', db.UnicodeText, default=u""),
        db.Column('action_text', db.UnicodeText, default=u""),
        db.Column('deleted', db.Boolean, default=False)
    )

def downgrade():
    op.drop_table('notification')


