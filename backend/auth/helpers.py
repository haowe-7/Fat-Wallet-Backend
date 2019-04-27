from flask import request, session

def auth_helper():
    session_id = request.cookies.get('fat-wallet')
    if session_id:
        return session.get(session_id)
