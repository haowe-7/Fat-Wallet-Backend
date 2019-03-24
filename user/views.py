from flask import Blueprint
from flask_restful import Resource
from models import db, User

blueprint = Blueprint(__name__, __name__)

class UserResource(Resource):
    def get(self):
        return {'hello' : 'world'}

@blueprint.route('/bp')
def show_user_profile():
    # show the user profile for that user
    ed_user = User(username="ct")
    db.session.add(ed_user)
    db.session.commit()
    return "good"
    