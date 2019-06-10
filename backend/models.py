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
    student_id = db.Column(db.String(10), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    major = db.Column(db.String(20))
    email = db.Column(db.String(30))
    phone = db.Column(db.String(20))
    avatar = db.Column(db.Binary(2**21-1))

    @staticmethod
    def get_by_username(username):
        if not username:
            return None
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_student_id(student_id):
        if not student_id:
            return None
        return User.query.filter_by(student_id=student_id).first()


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
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)


class Participate(db.Model, MyMixin):
    __tablename__ = 'participates'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)

