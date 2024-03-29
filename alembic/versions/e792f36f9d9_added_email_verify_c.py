"""Added email verify code field

Revision ID: e792f36f9d9
Revises: 293472b24b45
Create Date: 2014-09-29 18:24:43.581116

"""

# revision identifiers, used by Alembic.
revision = 'e792f36f9d9'
down_revision = '293472b24b45'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('email_verify_code', sa.UnicodeText(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'email_verify_code')
    ### end Alembic commands ###
