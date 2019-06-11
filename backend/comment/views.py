from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, Comment
from backend.auth.helpers import auth_helper
from sqlalchemy import exc
import logging
blueprint = Blueprint('comment', __name__)


class CommentResource(Resource):
    def get(self):
        form = request.get_json(True, True)
        user_id = form.get('user_id')
        task_id = form.get('task_id')
        comments = Comment.get(user_id=user_id, task_id=task_id)
        result = [{"id": comment.id,
                   "user_id": comment.user_id,
                   "task_id": comment.task_id,
                   "content": comment.content} for comment in comments]
        return dict(data=result), 200

    def post(self):
        user_id = auth_helper()
        form = request.get_json(True, True)
        task_id = form.get('task_id')
        if not task_id:
            return dict(error='task id required'), 400
        content = form.get('content')
        if not content:
            return dict(error='content can not be empty'), 400
        try:
            comment = Comment(user_id=user_id, task_id=task_id, content=content)
            db.session.add(comment)
            db.session.commit()
        except exc.IntegrityError as e:
            logging.error(f'create comment failed, msg: {e}')
            return dict(error=f'{e}'), 400
        return dict(data="comment success!"), 200

    def delete(self):
        form = request.get_json(True, True)
        user_id = auth_helper()
        comment_id = form.get('comment_id')
        if not comment_id:
            return dict(error="comment id required"), 400
        comment = Comment.get(comment_id=comment_id)
        if not comment:
            return dict(error="comment not exist"), 400
        comment = comment[0]
        if user_id != comment.user_id:
            return dict(error="can not delete other's comment"), 400
        db.session.delete(comment)
        db.session.commit()
        return dict(data="delete success!"), 200

    def patch(self):  # 只允许修改comment内容
        form = request.get_json(True, True)
        user_id = auth_helper()
        comment_id = form.get('comment_id')
        content = form.get('content')
        if not comment_id:
            return dict(error="comment id required"), 400
        comment = Comment.get(comment_id=comment_id)
        if not comment:
            return dict(error="comment not exist"), 400
        comment = comment[0]
        if user_id != comment.user_id:
            return dict(error="can not modify other's comment"), 400
        comment.content = content
        db.session.commit()
        return dict(data='patch success!'), 200
