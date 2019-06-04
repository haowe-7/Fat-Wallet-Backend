from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, User
from backend.auth.helpers import encrypt_helper
blueprint = Blueprint('user', __name__)


class UserResource(Resource):
    def get(self):
        return 'hello'

    def post(self):
        form = request.get_json()
        username = form.get('username')
        if not username:
            return dict(error='username required'), 400
        student_id = form.get('student_id')
        if not student_id:
            return dict(error='student id required'), 400
        password = form.get('password')
        if not password:
            return dict(error='password required'), 400
        email = form.get('email')
        major = form.get('major')
        phone = form.get('phone')
        pass_md5 = encrypt_helper(password)
        if User.get_by_student_id(student_id):
            return dict(error='you have already registered'), 400
        user = User(username=username, student_id=student_id, password=pass_md5, email=email,
                    major=major, phone=phone)
        db.session.add(user)
        db.session.commit()
        return dict(data='register success!'), 200
