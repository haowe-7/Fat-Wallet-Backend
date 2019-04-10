from flask import request, session


def auth_middleware(func):
    def helper(*args):
        session_id = request.cookies.get('fat-wallet')
        if session_id:
            return func(*args, session.get(session_id))
        else:
            return "permission denied", 403
    return helper


def auth_helper():
    session_id = request.cookies.get('fat-wallet')
    if session_id:
        return session.get(session_id)
