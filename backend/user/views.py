from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, User
from backend.auth.helpers import encrypt_helper, auth_helper
import json
blueprint = Blueprint('user', __name__)


class UserResource(Resource):
    def get(self):
        id =  request.args.get("user_id")
        student_id = request.args.get("student_id")
        username = request.args.get("username")
        users = User.get(user_id=id, student_id=student_id, username=username)
        result = [{"user_id": user.id, "student_id": user.student_id,
                   "username": user.username, "major": user.major,
                   "email": user.email, "phone": user.phone,
                   "avatar": user.avatar.decode() if user.avatar else None} for user in users]
        return dict(data=result), 200

    def post(self):
        form = request.get_json(True, True)
        username = form.get('username')
        if not username:
            return dict(error='username required'), 400
        student_id = form.get('student_id')
        password = form.get('password')
        if not password:
            return dict(error='password required'), 400
        email = form.get('email')
        major = form.get('major')
        phone = form.get('phone')
        pass_md5 = encrypt_helper(password)
        try:
            user = User(username=username, student_id=student_id, password=pass_md5, email=email,
                        major=major, phone=phone)
            db.session.add(user)
            db.session.commit()
        except Exception:
            return dict(error="aaa"), 400  # FIXME catch unique异常
        return dict(data='register success!'), 200

    def patch(self):  #　不涉及username,password的修改
        form = request.get_json(True, True)
        user_id = auth_helper()
        if not form:
            return dict(error="form is empty"), 400
        student_id = form.get("student_id")
        if password:
            password = encrypt_helper(password)
        email = form.get("email")
        major = form.get("major")
        phone = form.get("phone")
        avatar = form.get("avatar")
        User.patch(user_id=user_id, student_id=student_id,
                   email=email, major=major, phone=phone,
                   avatar=avatar.encode('utf-8') if avatar else None)
        return dict(data='ok'), 200


