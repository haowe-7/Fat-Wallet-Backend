from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, Message
from backend.auth.helpers import auth_helper
from sqlalchemy import exc
import logging
import re
blueprint = Blueprint('message', __name__)


class MessageResource(Resource):
    def get(self):
        form = request.get_json(True, True)
        user_id = form.get('user_id')
        message_id = form.get('message_id')
        messages = Message.get(user_id=user_id, message_id=message_id)
        result = [{"id": message.id,
                   "user_id": message.user_id,
                   "content": message.content} for message in messages]
        return dict(data=result), 200
    
    def post(self):
        form = request.get_json(True, True)
        user_id = form.get('user_id')
        content = form.get('content')
        if not user_id:
            return dict(error='请指定要通知的用户'), 400
        if not content:
            return dict(error='消息内容不能为空'), 400
        try:
            message = Message(user_id=user_id, content=content)
            db.session.add(message)
            db.session.commit()
        except exc.IntegrityError as e:
            logging.error(f'create message failed, msg: {e}')
            if re.search(r"Cannot add or update a child row", e.orig.args[1]):
                return dict(error='用户不存在'), 400
            else:
                return dict(error=f'{e}'), 400
        return dict(data="消息创建成功"), 200
    
    def delete(self):
        form = request.get_json(True, True)
        message_id = form.get('message_id')
        user_id = auth_helper()
        if not message_id:
            return dict(error='请指定要删除的消息'), 400
        message = Message.get(message_id=message_id)
        if not message:
            return dict(error='消息不存在'), 400
        message = message[0]
        if user_id != message.user_id:
            return dict(error='只能删除自己的消息'), 400
        db.session.delete(message)
        db.session.commit()
        return dict(data='消息删除成功'), 200
