from sqlalchemy import Column, Integer, String
from flask_sqlalchemy import SQLAlchemy
from flaskr import app

db = SQLAlchemy(app, session_options=dict(autoflush=False, expire_on_commit=False))
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@127.0.0.1:3307/money'

class MyMixin(object):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
    }

class User(db.Model, MyMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)

