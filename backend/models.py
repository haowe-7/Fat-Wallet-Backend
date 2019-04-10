from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
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
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(10), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(40))
    major = db.Column(db.String(20))
    email = db.Column(db.String(30))
    phone = db.Column(db.String(20))