from flask_restful import Api
from .user.views import blueprint as user_blueprint
from .user.views import UserResource
from .auth.views import blueprint as auth_blueprint


def setup(app):
    api = Api(app)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(auth_blueprint)
    api.add_resource(UserResource, '/users')
