from flask_restful import Api
from backend.user.views import blueprint as user_blueprint
from backend.user.views import UserResource
from backend.auth.views import blueprint as auth_blueprint
from backend.task.views import TaskResource
from backend.task.views import blueprint as task_blueprint
from backend.comment.views import CommentResource
from backend.comment.views import blueprint as comment_blueprint
from backend.participate.views import ParticipateResource
from backend.participate.views import blueprint as participate_blueprint
from backend.collect.views import CollectResource
from backend.message.views import MessageResource


def setup(app):
    api = Api(app)
    app.register_blueprint(user_blueprint, url_prefix='/users')
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(task_blueprint, url_prefix='/tasks')
    app.register_blueprint(participate_blueprint, url_prefix='/participates')
    app.register_blueprint(comment_blueprint, url_prefix='/comments/')

    api.add_resource(UserResource, '/users/')
    api.add_resource(TaskResource, '/tasks/')
    api.add_resource(CommentResource, '/comments/')
    api.add_resource(ParticipateResource, '/participates/')
    api.add_resource(CollectResource, '/collects/')
    api.add_resource(MessageResource, '/messages/')
