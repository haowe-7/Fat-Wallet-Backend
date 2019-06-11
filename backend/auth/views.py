from flask import Blueprint, request, make_response, session, jsonify
from backend.models import User
from .helpers import auth_helper
import json
import hashlib
import random
import string

blueprint = Blueprint('auth', __name__)


@blueprint.route('/login', methods=['POST'])
def login():
    if auth_helper():
        return 'already login', 200
    form = request.get_json(True, True)
    username = form.get("username")
    password = form.get("password")
    pass_md5 = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
    user = User.get(username=username)
    if not user:
        return jsonify(error='account doen\'t exist'), 400
    user = user[0]
    if user.password != pass_md5:
        return jsonify(error='incorrect password'), 400
    resp = make_response()
    resp.status_code = 200
    data = dict(user_id=user.id, student_id=user.student_id,
                username=user.username, major=user.major,
                email=user.email, phone= user.phone,
                avatar=user.avatar.decode() if user.avatar else None)
    resp.response = json.dumps(data)
    session_id = random_helper()
    resp.set_cookie('fat-wallet', session_id, max_age=300)
    session[session_id] = user.id
    return resp


@blueprint.route('/logout', methods=['POST'])
def logout():
    cookie = request.cookies
    resp = make_response()
    session_id = cookie.get('fat-wallet')
    if session_id:
        user_id = session.get(session_id, None)
        resp.delete_cookie('fat-wallet')
        if user_id:
            session.pop(session_id)
            return jsonify(data='logout success'), 200
    return jsonify(error='You haven\'t login'), 400


def random_helper():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
