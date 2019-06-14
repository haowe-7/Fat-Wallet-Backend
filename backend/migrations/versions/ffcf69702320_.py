"""update participate

Revision ID: ffcf69702320
Revises: a1d3a866ef92
Create Date: 2019-06-13 07:50:20.442654

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffcf69702320'
down_revision = 'a1d3a866ef92'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('participates', sa.Column('status', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('participates', 'status')
    # ### end Alembic commands ###
