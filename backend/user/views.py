from flask import Blueprint, request, session, jsonify
from flask_restful import Resource
from backend.models import db, User
from backend.auth.helpers import encrypt_helper, auth_helper
from backend.file.helpers import upload_file
from sqlalchemy import exc
import logging
import re
# from backend.celery.config import celery
# from backend.task.helpers import get_cur_time
blueprint = Blueprint('user', __name__)


user_column_cn = {
    "username": "用户名",
    "email": "邮箱",
    "student_id": "学号",
    "phone": "手机号码"
}


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
                   "nickname": user.nickname, "profile": user.profile,
                   "balance": user.balance,
                   "avatar": user.avatar.decode() if user.avatar else None} for user in users]
        return dict(data=result, count=len(result)), 200

    def post(self):
        form = request.get_json(True, True)
        username = form.get('username')
        if not username:
            return dict(error='用户名不能为空'), 400
        password = form.get('password')
        if not password:
            return dict(error='密码不能为空'), 400
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
                return dict(error=f"该{user_column_cn[column]}已被使用"), 400
        return dict(data='register success!'), 200

    def patch(self):  # 不涉及username,password的修改
        form = request.get_json(True, True)
        user_id = auth_helper()
        if not form:
            return dict(error="表单不能为空"), 400
        student_id = form.get("student_id")
        email = form.get("email")
        major = form.get("major")
        phone = form.get("phone")
        nickname = form.get('nickname')
        profile = form.get('profile')
        balance = form.get('balance')

        try:
            User.patch(user_id=user_id, student_id=student_id,
                       email=email, major=major, phone=phone,
                       nickname=nickname, profile=profile, balance=balance)
        except exc.IntegrityError as e:
            if re.search(r"Duplicate entry '\S*' for key '\S*'", e.orig.args[1]):
                logging.error(f"patch user failed, msg: {e}")
                column = re.findall(r"'\S*'", e.orig.args[1])[1].strip("'")
                return dict(error=f"该{user_column_cn[column]}已被使用"), 400
        return dict(data='ok'), 200


@blueprint.route('/password', methods=['PUT'])
def update_password():
    form = request.get_json(True, True)
    user_id = auth_helper()
    new_pass = form.get("password")
    if not new_pass:
        return jsonify(error="密码不能为空"), 400
    new_pass = encrypt_helper(new_pass)
    User.patch(user_id=user_id, password=new_pass)
    cookie = request.cookies
    session_id = cookie.get('fat-wallet')
    session.pop(session_id)
    return jsonify(data="ok"), 200


@blueprint.route('/avatar', methods=['POST'])
def update_avatar():
    user_id = auth_helper()
    flag, msg = upload_file(f"avatar-{user_id}")
    if not flag:
        return jsonify(error=msg), 400
    user = User.get_by_id(user_id)
    user.avatar = msg
    db.session.commit()
    return jsonify(data=msg), 200
