from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from backend import app


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@127.0.0.1:3307/money'
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
    username = db.Column(db.String(20))
