"""empty message

Revision ID: 2224c5484e16
Revises: 00af8fe38878
Create Date: 2019-06-26 14:41:43.977658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2224c5484e16'
down_revision = '00af8fe38878'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('likes', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('nickname', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('profile', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile')
    op.drop_column('users', 'nickname')
    op.drop_column('comments', 'likes')
    # ### end Alembic commands ###
