from flask import Blueprint, request, make_response
from flask_restful import Resource
from backend.models import db, User
import hashlib
from backend.auth.helpers import auth_middleware


blueprint = Blueprint('user', __name__)


class UserResource(Resource):
    @auth_middleware
    def get(self, username):
        return {'hello': username}

    def post(self):
        print(request.get_json())
        username = request.get_json()['username']
        student_id = request.get_json()['student_id']
        password = request.get_json()['password']
        email = request.get_json()['email']
        major = request.get_json()['email']
        phone = request.get_json()['phone']
        # password encryption
        pass_md5 = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
        print(pass_md5)
        resp = make_response()
        resp.headers['content-type'] = 'text/plain'
        if User.query.filter_by(student_id=student_id).first():
            resp.status_code = 400
            resp.response = 'you have already registered'
        else:
            # insert into database
            user = User(username=username, student_id=student_id, password=pass_md5, email=email,
                        major=major, phone=phone)
            db.session.add(user)
            db.session.commit()
            
            resp.status_code = 200
            resp.response = 'register success!'
        return resp


@blueprint.route('/bp')
def show_user_profile():
    # show the user profile for that user
    ed_user = User(student_id="16340017", username="cf")
    db.session.add(ed_user)
    db.session.commit()
    return "good"
