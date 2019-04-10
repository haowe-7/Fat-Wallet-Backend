from flask import Blueprint, request, make_response, session
from backend.models import User
from .helpers import auth_helper
import hashlib
import random
import string

blueprint = Blueprint('auth', __name__)


@blueprint.route('/login', methods=['POST'])
def login():
    if auth_helper():
        return 'already login', 200
    username = request.get_json()['username']
    password = request.get_json()['password']
    pass_md5 = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
    user = User.query.filter_by(username=username).first()
    if not user:
        return 'account doen\'t exist', 400
    elif user.password != pass_md5:
        return 'incorrect password', 400
    else:
        resp = make_response()
        resp.status_code = 200
        resp.response = 'login success'
        session_id = random_helper()
        resp.set_cookie('fat-wallet', session_id, max_age=300)
        session[session_id] = username
    return resp


@blueprint.route('/logout', methods=['POST'])
def logout():
    cookie = request.cookies
    resp = make_response()
    session_id = cookie.get('fat-wallet')
    if session_id:
        username = session.get(session_id, None)
        resp.delete_cookie('fat-wallet')
        if username:
            session.pop(session_id)
            resp.status_code = 200
            resp.response = 'logout success'
            return resp
    resp.status_code = 400
    resp.response = 'You haven\'t login'
    return resp


def random_helper():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=32))
