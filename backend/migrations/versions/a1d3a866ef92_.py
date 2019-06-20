"""update task

Revision ID: a1d3a866ef92
Revises: 3f43eee65150
Create Date: 2019-06-13 03:39:29.499713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1d3a866ef92'
down_revision = '3f43eee65150'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('due_time', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('image', sa.LargeBinary(length=2097151), nullable=True))
    op.add_column('tasks', sa.Column('max_participate', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('start_time', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('status', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tasks', 'status')
    op.drop_column('tasks', 'start_time')
    op.drop_column('tasks', 'max_participate')
    op.drop_column('tasks', 'image')
    op.drop_column('tasks', 'due_time')
    # ### end Alembic commands ###