from flask_restful import Api
from backend.user.views import blueprint as user_blueprint
from backend.user.views import UserResource
from backend.auth.views import blueprint as auth_blueprint
from backend.task.views import TaskResource
from backend.comment.views import CommentResource
from backend.participate.views import ParticipateResource
from backend.collect.views import CollectResource
from backend.message.views import MessageResource


def setup(app):
    api = Api(app)
    app.register_blueprint(user_blueprint, url_prefix='/users')
    app.register_blueprint(auth_blueprint)

    api.add_resource(UserResource, '/users/')
    api.add_resource(TaskResource, '/tasks/')
    api.add_resource(CommentResource, '/comments/')
    api.add_resource(ParticipateResource, '/part/')
    api.add_resource(CollectResource, '/collect/')
    api.add_resource(MessageResource, '/message/')
