"""add task

Revision ID: 2faa9a36cfa5
Revises: 84571ffcfbbd
Create Date: 2019-06-03 16:32:28.447568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2faa9a36cfa5'
down_revision = '84571ffcfbbd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('task_type', sa.Integer(), nullable=True),
    sa.Column('reward', sa.Integer(), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    # ### end Alembic commands ###
