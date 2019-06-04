from flask import request, session
import hashlib


def auth_helper():
    session_id = request.cookies.get('fat-wallet')
    if session_id:
        user_id = session.get(session_id)
        return user_id


def encrypt_helper(raw):
    return hashlib.md5(raw.encode(encoding='UTF-8')).hexdigest()
