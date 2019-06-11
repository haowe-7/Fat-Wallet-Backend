from flask_restful import Api
from backend.user.views import blueprint as user_blueprint
from backend.user.views import UserResource
from backend.auth.views import blueprint as auth_blueprint
from backend.task.views import TaskResource
from backend.comment.views import CommentResource


def setup(app):
    api = Api(app)
    app.register_blueprint(user_blueprint, url_prefix='/users')
    app.register_blueprint(auth_blueprint)

    api.add_resource(UserResource, '/users/')
    api.add_resource(TaskResource, '/tasks/')
    api.add_resource(CommentResource, '/comments/')
