from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, Message, User
from backend.auth.helpers import auth_helper
blueprint = Blueprint('message', __name__)


class MessageResource(Resource):
    def get(self):
        user_id = auth_helper()
        message_id = request.args.get('message_id')
        messages = Message.get(user_id=user_id, message_id=message_id)
        if len(messages) > 1:
            for i in range(0, len(messages) - 1):
                for j in range(i + 1, len(messages)):
                    if messages[i].id < messages[j].id:
                        t = messages[i]
                        messages[i] = messages[j]
                        messages[j] = t
        result = [{"id": message.id,
                   "user_id": message.user_id,
                   "content": message.content} for message in messages]
        for value in result:
            user_id = value['user_id']
            user = User.get_by_id(user_id)
            value['username'] = user.username
        return dict(data=result), 200

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
