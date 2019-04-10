from flask import Blueprint, request, make_response, session
from backend.models import db, User
import hashlib

blueprint = Blueprint('auth', __name__)


@blueprint.route('/login', methods=['POST'])
def login():
    cookie = request.cookies
    if cookie.get('fat-wallet') and cookie.get('fat-wallet') == session.get('fat-wallet'):    # already login
        return 'already login'
    else:
        username = request.get_json()['username']
        password = request.get_json()['password']
        pass_md5 = hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()
        resp = make_response()
        resp.headers['content-type'] = 'text/plain'
        user = User.query.filter_by(username=username).first()
        if not user:
            resp.status_code = 400
            resp.response = 'account doen\'t exist'
        elif user.password != pass_md5:
            resp.status_code = 400
            resp.response = 'incorrect password'
        else:
            resp.status_code = 200
            resp.response = 'login success'
            # set cookies and session
            resp.set_cookie('fat-wallet', username, max_age=300)
            session['fat-wallet'] = username
        return resp


@blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    cookie = request.cookies
    resp = make_response()
    resp.headers['content-type'] = 'text/plain'
    if cookie.get('fat-wallet') and cookie.get('fat-wallet') == session.get('fat-wallet'):
        # delete cookies and session
        resp.delete_cookie('fat-wallet')
        session.pop('fat-wallet')
        resp.status_code = 200
        resp.response = 'logout success'
    else:
        resp.status_code = 400
        resp.response = 'You haven\'t login'
    return resp


@blueprint.route('/register', methods=['POST'])
def register():
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
    if User.query.filter_by(username=username).first() or User.query.filter_by(student_id=student_id).first():
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
