from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import TEXT
from sqlalchemy.dialects.mysql import BIGINT
from enum import Enum
from . import app
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
    avatar = db.Column(db.Binary(2**21-1))  # 2M

    @staticmethod
    def get(user_id=None, student_id=None, username=None):
        q = User.query
        if user_id:
            q = q.filter(User.id == user_id)
        if student_id:
            q = q.filter(User.student_id == student_id)
        if username:
            q = q.filter(User.username == username)
        return q.all()

    @staticmethod
    def patch(user_id, student_id=None, password=None, email=None, major=None, phone=None, avatar=None):
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
            if avatar:
                user.avatar = avatar
            db.session.commit()


class TaskType(Enum):
    QUESTIONNAIRE = 1  # 问卷调查
    RECRUITMENT = 2  # 协会招新
    EXPRESS = 3  # 快递


class Task(db.Model, MyMixin):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer)
    task_type = db.Column(db.Integer, default=TaskType.QUESTIONNAIRE.value)
    reward = db.Column(db.Integer, default=0)
    description = db.Column(TEXT)


class Comment(db.Model, MyMixin):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)
    content = db.Column(db.String(100))

    @staticmethod
    def get(user_id=None, task_id=None, comment_id=None):
        q = Comment.query
        if user_id:
            q = q.filter(Comment.user_id == user_id)
        if task_id:
            q = q.filter(Comment.task_id == task_id)
        if comment_id:
            q = q.filter(Comment.id == comment_id)
        return q.all()


class Collect(db.Model, MyMixin):
    __tablename__ = 'collects'
    __table_args__ =  (db.UniqueConstraint('user_id', 'task_id', name='_collect_uc'),)
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
        if collect_id:
            q = q.filter(Collect.id == collect_id)
        return q.all()

class Participate(db.Model, MyMixin):
    __tablename__ = 'participates'
    __table_args__ =  (db.UniqueConstraint('user_id', 'task_id', name='_participate_uc'),)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)

    @staticmethod
    def get(user_id=None, task_id=None, participate_id=None):
        q = Participate.query
        if user_id:
            q = q.filter(Participate.user_id == user_id)
        if task_id:
            q = q.filter(Participate.task_id == task_id)
        if participate_id:
            q = q.filter(Participate.id == participate_id)
        return q.all()
