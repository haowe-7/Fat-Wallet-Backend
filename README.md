# 盈小钱后端

## 前置安装 

docker

docker-compose

教程请移步[docker环境配置](backend/docs/docker.md)

## 部署开发环境
```bash
$ cd docker
$ docker-compose up -d
$ docker-compose exec money bash
$ flask db upgrade heads
$ python3 -m unittest tests/test_init.py (假数据)
$ flask run --host=0.0.0.0
```

## 修改model后修改migrations文件
```
$ cd docker
$ docker-compose exec money bash
$ flask db migrate
$ flask db upgrade (更新本地数据库)
```

## 删除所有容器
```
$ cd docker
$ docker-compose down
```

## 文档

1. flask: a microframework http://flask.pocoo.org/docs/1.0/quickstart/
2. blueprint: create modular application http://flask.pocoo.org/docs/1.0/blueprints/
3. flask-restful: extension for flask to support building REST APIs https://flask-restful.readthedocs.io/en/latest/
4. SQLAlchemy: database access https://flask-sqlalchemy.palletsprojects.com/en/2.x/
5. celery: task queue http://flask.pocoo.org/docs/1.0/patterns/celery/

## commit规范

http://www.ruanyifeng.com/blog/2016/01/commit_message_change_log.html

## 协作开发方式

1. 拉分支开发（命名与任务相关）
2. 完成后发PR到主分支，大家review后进行merge

## 数据库连接
```bash
$ cd docker
$ docker-compose exec mysql bash
```

## 代码风格
**vscode setting**
```
{
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.enabled": true,
    "python.linting.flake8Args": [
        "--ignore", "E501"
    ],
}
```