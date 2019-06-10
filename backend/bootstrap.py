# from app import app
from . import app
from .blueprint import setup
from flask import request, session, jsonify
import logging

setup(app)
# app.run(host="0.0.0.0", debug=True)

valid_path = {'/login', '/logout', '/users/'}


@app.before_request
def before_request():
    session_id = request.cookies.get('fat-wallet')
    valid = session.get(session_id, None)
    if request.path not in valid_path and not valid:
        logging.info("invalid request is caught")  # FIXME add logging to project
        return jsonify(error='permission denied'), 403  # 不能用dict
    if not valid and request.path == '/users/' and request.method != 'POST':
        return jsonify(error='permission denied'), 403
