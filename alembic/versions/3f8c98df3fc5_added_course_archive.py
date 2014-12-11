
"""Added course archive tables

Revision ID: 3f8c98df3fc5
Revises: 1cccdbc325f5
Create Date: 2014-12-11 14:46:59.205383

"""

# revision identifiers, used by Alembic.
revision = '3f8c98df3fc5'
down_revision = '1cccdbc325f5'

from alembic import op
import sqlalchemy as db


def upgrade():
    try:
        op.create_table(
            'archivedcoursemembership',
            db.Column('id', db.Integer, primary_key=True),
            db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
            db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
        )
    except db.exc.ProgrammingError:
        print "Already created."

def downgrade():
    op.drop_table('archivedcoursemembership')