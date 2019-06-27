from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import TEXT
from sqlalchemy.dialects.mysql import BIGINT
from enum import Enum
from backend import app
import os

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@mysql/money'
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class MyMixin(object):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
    }


class User(db.Model, MyMixin):
    __tablename__ = 'users'
    id = db.Column(BIGINT(unsigned=True), primary_key=True)
    student_id = db.Column(db.String(10), unique=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    major = db.Column(db.String(20))
    email = db.Column(db.String(30), unique=True)
    phone = db.Column(db.String(20), unique=True)
    nickname = db.Column(db.String(20))
    profile = db.Column(db.String(100))
    balance = db.Column(db.Integer, default=1000)
    avatar = db.Column(db.LargeBinary(2**21 - 1))  # 2M

    @staticmethod
    def get(user_id=None, student_id=None, username=None, offset=None, limit=None):
        q = User.query
        if user_id:
            q = q.filter(User.id == user_id)
            return q.all()
        if student_id:
            q = q.filter(User.student_id == student_id)
        if username:
            q = q.filter(User.username == username)
        if offset and limit:
            q = q.filter(User.id >= offset, User.id < int(offset) + int(limit))
        return q.all()

    @staticmethod
    def patch(user_id, student_id=None, password=None, email=None, major=None,
              phone=None, nickname=None, profile=None, balance=None, avatar=None):
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            if not user:
                return
            if student_id:
                user.student_id = student_id
            if password:
                user.password = password
            if email:
                user.email = email
            if major:
                user.major = major
            if phone:
                user.phone = phone
            if nickname:
                user.nickname = nickname
            if profile:
                user.profile = profile
            if avatar:
                user.avatar = avatar
            if balance:
                user.balance = balance
            db.session.commit()


class TaskType(Enum):
    QUESTIONNAIRE = 1  # 问卷调查
    RECRUITMENT = 2  # 协会招新
    EXPRESS = 3  # 快递


class Task(db.Model, MyMixin):
    __tablename__ = 'tasks'
    __table_args__ = (db.ForeignKeyConstraint(['creator_id'], ['users.id'],
                      name='task_user_fc', ondelete="CASCADE"),)
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(20), nullable=False)   # 任务标题
    task_type = db.Column(db.Integer, default=TaskType.QUESTIONNAIRE.value, nullable=False)  # 任务类型
    reward = db.Column(db.Integer, default=0, nullable=False)  # 任务赏金
    description = db.Column(TEXT)    # 任务描述
    # status = db.Column(db.Boolean, default=False)  # 任务状态: 是否开放
    due_time = db.Column(db.DateTime)  # 任务截止时间
    max_participate = db.Column(db.Integer)  # 参与人数上限
    extra = db.Column(db.TEXT)  # 任务内容，json格式
    image = db.Column(db.LargeBinary(2**21 - 1))  # 2M

    @staticmethod
    def get(task_id=None, creator_id=None, title=None, task_type=None,
            min_reward=None, max_reward=None, offset=None, limit=None):
        q = Task.query
        if task_id:
            q = q.filter(Task.id == task_id)
            return q.all()
        if creator_id:
            q = q.filter(Task.creator_id == creator_id)
        if title:
            q = q.filter(Task.title == title)
        if task_type:
            q = q.filter(Task.task_type == task_type)
        if min_reward:
            q = q.filter(Task.reward >= min_reward)
        if max_reward:
            q = q.filter(Task.reward <= max_reward)
        if offset and limit:
            q = q.filter(Task.id >= offset, Task.id < int(offset) + int(limit))
        return q.all()

    @staticmethod
    def patch(task_id, title=None, task_type=None, reward=None, description=None,
              due_time=None, max_participate=None, extra=None, image=None):
        if task_id:
            task = Task.query.filter(Task.id == task_id).first()
            if not task:
                return
            if title:
                task.title = title
            if task_type:
                task.task_type = task_type
            if reward:
                task.reward = reward
            if description:
                task.description = description
            if due_time:
                task.due_time = due_time
            if max_participate:
                task.max_participate = max_participate
            if extra:
                task.extra = extra
            if image:
                task.image = image
            db.session.commit()


class Submission(db.Model, MyMixin):    # 问卷调查的填写结果
    __tablename__ = 'submissons'
    __table_args__ = (db.ForeignKeyConstraint(['user_id'], ['users.id'],
                      name='submission_user_fc', ondelete="CASCADE"),
                      db.ForeignKeyConstraint(['task_id'], ['tasks.id'],
                      name='submission_task_fc', ondelete="CASCADE"),
                      db.UniqueConstraint('user_id', 'task_id', name='_submission_uc'),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)
    answer = db.Column(db.TEXT, nullable=False)   # json格式的答案

    @staticmethod
    def get(submission_id=None, user_id=None, task_id=None):
        q = Submission.query
        if user_id:
            q = q.filter(Submission.user_id == user_id)
        if task_id:
            q = q.filter(Submission.task_id == task_id)
        if user_id and task_id:
            q = q.filter(Submission.user_id == user_id, Submission.task_id == task_id)
        if submission_id:
            q = q.filter(Submission.id == submission_id)
        return q.all()


class Comment(db.Model, MyMixin):
    __tablename__ = 'comments'
    __table_args__ = (db.ForeignKeyConstraint(['user_id'], ['users.id'],
                      name='comment_user_fc', ondelete="CASCADE"),
                      db.ForeignKeyConstraint(['task_id'], ['tasks.id'],
                      name='comment_task_fc', ondelete="CASCADE"),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)
    content = db.Column(db.String(100))
    likes = db.Column(db.Integer, default=0)

    @staticmethod
    def get(user_id=None, task_id=None, comment_id=None):
        q = Comment.query
        if user_id:
            q = q.filter(Comment.user_id == user_id)
        if task_id:
            q = q.filter(Comment.task_id == task_id)
        if user_id and task_id:
            q = q.filter(Comment.user_id == user_id, Comment.task_id == task_id)
        if comment_id:
            q = q.filter(Comment.id == comment_id)
        return q.all()


class Collect(db.Model, MyMixin):
    __tablename__ = 'collects'
    __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='_collect_uc'),
                      db.ForeignKeyConstraint(['user_id'], ['users.id'],
                      name='collect_user_fc', ondelete="CASCADE"),
                      db.ForeignKeyConstraint(['task_id'], ['tasks.id'],
                      name='collect_task_fc', ondelete="CASCADE"),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)

    @staticmethod
    def get(user_id=None, task_id=None, collect_id=None):
        q = Collect.query
        if user_id:
            q = q.filter(Collect.user_id == user_id)
        if task_id:
            q = q.filter(Collect.task_id == task_id)
        if user_id and task_id:
            q = q.filter(Collect.user_id == user_id, Collect.task_id == task_id)
        if collect_id:
            q = q.filter(Collect.id == collect_id)
        return q.all()


class ParticipateStatus(Enum):
    APPLYING = 1  # 申请中
    ONGOING = 2  # 进行中
    FINISH = 3  # 已完成
    FAILED = 4  # 未完成


ParticipateStatusCN = {
    1: "申请中",
    2: "进行中",
    3: "已完成",
    4: "未完成"     # 任务截止时间已过时
}


class Participate(db.Model, MyMixin):
    __tablename__ = 'participates'
    __table_args__ = (db.UniqueConstraint('user_id', 'task_id', name='_participate_uc'),
                      db.ForeignKeyConstraint(['user_id'], ['users.id'],
                      name='participate_user_fc', ondelete="CASCADE"),
                      db.ForeignKeyConstraint(['task_id'], ['tasks.id'],
                      name='participate_task_fc', ondelete="CASCADE"),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)
    status = db.Column(db.Integer, default=ParticipateStatus.APPLYING.value)

    @staticmethod
    def get(user_id=None, task_id=None, participate_id=None, status=None):
        q = Participate.query
        if user_id:
            q = q.filter(Participate.user_id == user_id)
        if task_id:
            q = q.filter(Participate.task_id == task_id)
        if user_id and task_id:
            q = q.filter(Participate.user_id == user_id, Participate.task_id == task_id)
        if participate_id:
            q = q.filter(Participate.id == participate_id)
        if status:
            q = q.filter(Participate.status == status)
        return q.all()


class Message(db.Model, MyMixin):
    __tablename__ = 'messages'
    __table_args__ = (db.ForeignKeyConstraint(['user_id'], ['users.id'],
                      name='message_user_fc', ondelete="CASCADE"),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    content = db.Column(db.String(100))

    @staticmethod
    def get(user_id=None, message_id=None):
        q = Message.query
        if user_id:
            q = q.filter(Message.user_id == user_id)
        if message_id:
            q = q.filter(Message.id == message_id)
        return q.all()
