from flask import Blueprint
from flask_restful import Resource
from backend.models import db, User


blueprint = Blueprint('user', __name__)


class UserResource(Resource):
    def get(self):
        return {'hello': 'world'}


@blueprint.route('/bp')
def show_user_profile():
    # show the user profile for that user
    ed_user = User(student_id="16340017", username="cf")
    db.session.add(ed_user)
    db.session.commit()
    return "good"
