"""Add Tutor Application

Revision ID: 4d719fb7394e
Revises: 552eaf60b004
Create Date: 2014-09-11 23:06:41.680778

"""

# revision identifiers, used by Alembic.
revision = '4d719fb7394e'
down_revision = '552eaf60b004'

from alembic import op
import sqlalchemy as db


def upgrade():
    op.create_table('tutor',
        db.Column('id', db.Integer, primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('location_id', db.Integer, db.ForeignKey('location.id')),
        db.Column('status', db.String(255)),
        db.Column('price', db.String(255)),
        db.Column('per', db.String(255)),
    )

    op.create_table('tutorcourse',
        db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
        db.Column('tutor_id', db.Integer, db.ForeignKey('tutor.id')),
    )

    op.create_table('tutorlanguage',
        db.Column('language_id', db.Integer, db.ForeignKey('language.id')),
        db.Column('tutor_id', db.Integer, db.ForeignKey('tutor.id')),
    )


def downgrade():
    op.drop_table('tutorcourse')
    op.drop_table('tutorlanguage')
    op.drop_table('tutor')


def downgrade():
    pass
