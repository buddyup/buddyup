"""Add Action table

Revision ID: 148f858fde8b
Revises: db1b3bfb826
Create Date: 2014-06-26 16:05:00.122548

"""

# revision identifiers, used by Alembic.
revision = '148f858fde8b'
down_revision = 'db1b3bfb826'

from alembic import op
import sqlalchemy as db


def upgrade():
    op.create_table(
        'action',
        db.Column('id', db.Integer, primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('path', db.String(255)),
        db.Column('verb', db.String(8)),
        db.Column('action', db.Column('when_happened', db.TIMESTAMP, default=db.func.now()))
    )

def downgrade():
    op.drop_table('action')


