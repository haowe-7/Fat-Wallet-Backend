# 盈小钱后端

## 前置安装 

docker

docker-compose

python3 (如果有package缺失请pip3 install)

(linux or mac is recommended)

教程请移步[docker环境配置](docs/docker.md)

## 启动
```bash
$ cd docker
$ docker-compose up -d
$ cd ..
$ python3 bootstrap.py
```

## 文档

1. flask: a microframework http://flask.pocoo.org/docs/1.0/quickstart/
2. blueprint: create modular application http://flask.pocoo.org/docs/1.0/blueprints/
3. flask-restful: extension for flask to support building REST APIs https://flask-restful.readthedocs.io/en/latest/
4. SQLAlchemy: database access https://docs.sqlalchemy.org/en/latest/orm/tutorial.html
5. celery: task queue http://flask.pocoo.org/docs/1.0/patterns/celery/

## commit规范

http://www.ruanyifeng.com/blog/2016/01/commit_message_change_log.html

## 协作开发方式

1. 拉分支开发（命名与任务相关）
2. 完成后发PR到主分支，大家review后进行merge

## 数据库连接
```bash
$ mysql -uroot --protocol=TCP --port=3307 -p
```