"""add foreign constraint

Revision ID: b71103ff10b8
Revises: 3ccb22040f9d
Create Date: 2019-06-11 10:04:01.163853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b71103ff10b8'
down_revision = '3ccb22040f9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('collect_task_fc', 'collects', 'tasks', ['task_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('collect_user_fc', 'collects', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('comment_task_fc', 'comments', 'tasks', ['task_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('comment_user_fc', 'comments', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('participate_user_fc', 'participates', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('participate_task_fc', 'participates', 'tasks', ['task_id'], ['id'], ondelete='CASCADE')
    op.drop_index('task_user_constraint', table_name='tasks')
    op.create_foreign_key('task_user_fc', 'tasks', 'users', ['creator_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('task_user_fc', 'tasks', type_='foreignkey')
    op.create_index('task_user_constraint', 'tasks', ['creator_id'], unique=False)
    op.drop_constraint('participate_task_fc', 'participates', type_='foreignkey')
    op.drop_constraint('participate_user_fc', 'participates', type_='foreignkey')
    op.drop_constraint('comment_user_fc', 'comments', type_='foreignkey')
    op.drop_constraint('comment_task_fc', 'comments', type_='foreignkey')
    op.drop_constraint('collect_user_fc', 'collects', type_='foreignkey')
    op.drop_constraint('collect_task_fc', 'collects', type_='foreignkey')
    # ### end Alembic commands ###
