"""Added verified email field

Revision ID: 293472b24b45
Revises: 4d719fb7394e
Create Date: 2014-09-29 17:13:13.638309

"""

# revision identifiers, used by Alembic.
revision = '293472b24b45'
down_revision = '4d719fb7394e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('email_verified', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'email_verified')
    ### end Alembic commands ###
