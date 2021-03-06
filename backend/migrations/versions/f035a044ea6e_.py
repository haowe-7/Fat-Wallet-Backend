"""empty message

Revision ID: f035a044ea6e
Revises: d43cc2212562
Create Date: 2019-06-27 03:17:39.601554

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f035a044ea6e'
down_revision = 'd43cc2212562'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tasks', 'extra',
               existing_type=mysql.TEXT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('tasks', 'extra',
               existing_type=mysql.TEXT(),
               nullable=False)
    # ### end Alembic commands ###
