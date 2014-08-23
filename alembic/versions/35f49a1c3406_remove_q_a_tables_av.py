"""Remove Q&A tables & Availability

Revision ID: 35f49a1c3406
Revises: 52461c816e7c
Create Date: 2014-08-23 16:34:46.005790

"""

# revision identifiers, used by Alembic.
revision = '35f49a1c3406'
down_revision = '52461c816e7c'

from alembic import op
import sqlalchemy as db


def upgrade():
    op.drop_table('answer_vote')
    op.drop_table('question_vote')
    op.drop_table('answer')
    op.drop_table('question')
    op.drop_table('availability')

def downgrade():
    pass
