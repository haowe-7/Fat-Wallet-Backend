from flask import Blueprint, request, make_response,session
from flask_restful import Resource
from backend.models import db, User
import hashlib

blueprint = Blueprint(__name__, __name__)

class UserResource(Resource):
    def get(self):
        return {'hello': 'world'}


@blueprint.route('/bp')
def show_user_profile():
    # show the user profile for that user
    ed_user = User(student_id="16340017",username="cf")
    db.session.add(ed_user)
    db.session.commit()
    return "good"

@blueprint.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        cookie = request.cookies
        if cookie.get('username') and cookie.get('username') == session.get('username'):# already login
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
                resp.set_cookie('username', username, max_age=300)
                session['username'] = username
            return resp
    else:
        return 'get login page'

@blueprint.route('/logout', methods=('GET', 'POST'))
def logout():
    cookie = request.cookies
    resp = make_response()
    resp.headers['content-type'] = 'text/plain'
    if cookie.get('username') and cookie.get('username') == session.get('username'):
        #delete cookies and session
        resp.delete_cookie('username')
        session.pop('username')
        resp.status_code = 200
        resp.response = 'logout success'
    else:
        resp.status_code = 400
        resp.response = 'You haven\'t login'
    return resp

@blueprint.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
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
        if User.query.filter_by(username=username).first() or User.query.filter_by(student_id=student_id):
            resp.status_code = 400
            resp.response = 'you have already registered'
        else:
            # insert into database
            user = User(username=username, student_id=student_id, password=pass_md5, email=email,\
                        major=major, phone=phone)
            db.session.add(user)
            db.session.commit()
            
            resp.status_code = 200
            resp.response = 'register success!'
        return resp
    else:
        return 'get register page'