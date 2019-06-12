from flask import Blueprint, request, session, jsonify
from flask_restful import Resource
from backend.models import db, User
from backend.auth.helpers import encrypt_helper, auth_helper
from sqlalchemy import exc
import logging
import re
blueprint = Blueprint('user', __name__)


class UserResource(Resource):
    def get(self):
        student_id = request.args.get("student_id")
        username = request.args.get("username")
        offset = request.args.get("offset")
        limit = request.args.get("limit")
        users = User.get(student_id=student_id, username=username, offset=offset, limit=limit)
        result = [{"user_id": user.id, "student_id": user.student_id,
                   "username": user.username, "major": user.major,
                   "email": user.email, "phone": user.phone,
                   "avatar": user.avatar.decode() if user.avatar else None} for user in users]
        return dict(data=result, count=len(result)), 200

    def post(self):
        form = request.get_json(True, True)
        username = form.get('username')
        if not username:
            return dict(error='username required'), 400
        password = form.get('password')
        if not password:
            return dict(error='password required'), 400
        email = form.get('email')
        pass_md5 = encrypt_helper(password)
        try:
            user = User(username=username, password=pass_md5, email=email)
            db.session.add(user)
            db.session.commit()
        except exc.IntegrityError as e:
            if re.search(r"Duplicate entry '\S*' for key '\S*'", e.orig.args[1]):
                logging.error(f"create user failed, msg: {e}")
                column = re.findall(r"'\S*'", e.orig.args[1])[1].strip("'")
                return dict(error=f"{column} has been used"), 400
        return dict(data='register success!'), 200

    def patch(self):  # 不涉及username,password的修改
        form = request.get_json(True, True)
        user_id = auth_helper()
        if not form:
            return dict(error="form is empty"), 400
        student_id = form.get("student_id")
        email = form.get("email")
        major = form.get("major")
        phone = form.get("phone")
        avatar = form.get("avatar")
        try:
            User.patch(user_id=user_id, student_id=student_id,
                       email=email, major=major, phone=phone,
                       avatar=avatar.encode('utf-8') if avatar else None)
        except exc.IntegrityError as e:
            if re.search(r"Duplicate entry '\S*' for key '\S*'", e.orig.args[1]):
                logging.error(f"patch user failed, msg: {e}")
                column = re.findall(r"'\S*'", e.orig.args[1])[1].strip("'")
                return dict(error=f"{column} has been used"), 400
        return dict(data='ok'), 200


@blueprint.route('/password', methods=['PUT'])
def update_password():
    form = request.get_json(True, True)
    user_id = auth_helper()
    new_pass = form.get("password")
    if not new_pass:
        return jsonify(error="password is required"), 400
    new_pass = encrypt_helper(new_pass)
    User.patch(user_id=user_id, password=new_pass)
    cookie = request.cookies
    session_id = cookie.get('fat-wallet')
    session.pop(session_id)
    return jsonify(data="ok"), 200
