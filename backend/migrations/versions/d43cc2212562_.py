"""empty message

Revision ID: d43cc2212562
Revises: 377ba6575c9b
Create Date: 2019-06-27 03:11:54.089255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd43cc2212562'
down_revision = '377ba6575c9b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('submissons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('answer', sa.TEXT(), nullable=False),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], name='submission_task_fc', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='submission_user_fc', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'task_id', name='_submission_uc')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('submissons')
    # ### end Alembic commands ###
