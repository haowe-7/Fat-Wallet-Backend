from flask import Blueprint, request, jsonify
from flask_restful import Resource
from backend.models import db, Comment, User
from backend.auth.helpers import auth_helper
from sqlalchemy import exc
import logging
import re
blueprint = Blueprint('comment', __name__)


class CommentResource(Resource):
    def get(self):
        user_id = request.args.get('user_id')
        task_id = request.args.get('task_id')
        comments = Comment.get(user_id=user_id, task_id=task_id)
        result = [{"id": comment.id,
                   "user_id": comment.user_id,
                   "task_id": comment.task_id,
                   "content": comment.content,
                   "likes": comment.likes} for comment in comments]
        for value in result:
            user_id = value['user_id']
            user = User.get(user_id=user_id)
            value['username'] = user.username
        return dict(data=result), 200

    def post(self):
        user_id = auth_helper()
        form = request.get_json(True, True)
        task_id = form.get('task_id')
        if not task_id:
            return dict(error='请指定任务'), 400
        content = form.get('content')
        if not content:
            return dict(error='评论内容不能为空'), 400
        try:
            comment = Comment(user_id=user_id, task_id=task_id, content=content)
            db.session.add(comment)
            db.session.commit()
        except exc.IntegrityError as e:
            logging.error(f'create comment failed, msg: {e}')
            if re.search(r"Cannot add or update a child row", e.orig.args[1]):
                return dict(error='任务不存在'), 400
            else:
                return dict(error=f'{e}'), 400
        return dict(data="评论成功"), 200

    def delete(self):
        form = request.get_json(True, True)
        user_id = auth_helper()
        comment_id = form.get('comment_id')
        if not comment_id:
            return dict(error="请指定评论"), 400
        comment = Comment.get(comment_id=comment_id)
        if not comment:
            return dict(error="评论不存在"), 400
        comment = comment[0]
        if user_id != comment.user_id:
            return dict(error="只能删除自己的评论"), 400
        db.session.delete(comment)
        db.session.commit()
        return dict(data="删除评论成功"), 200

    def patch(self):  # 修改comment内容
        form = request.get_json(True, True)
        user_id = auth_helper()
        comment_id = form.get('comment_id')
        content = form.get('content')
        if not comment_id:
            return dict(error="请指定评论"), 400
        comment = Comment.get(comment_id=comment_id)
        if not comment:
            return dict(error="评论不存在"), 400
        comment = comment[0]
        if user_id != comment.user_id:
            return dict(error="只能修改自己的评论"), 400
        comment.content = content
        db.session.commit()
        return dict(data='修改评论成功'), 200


@blueprint.route('/updatelikes', methods=['PATCH'])
def update_likes():  # 修改评论点亮数(点亮/点灭)
    form = request.get_json(True, True)
    comment_id = form.get('comment_id')
    like = form.get('like')
    if not comment_id:
        return jsonify(error='请指定评论'), 400
    if not like or (like != 'yes' and like != 'no'):
        return jsonify(error='请提供正确的看法(点亮 or 点灭?)'), 400
    comment = Comment.get(comment_id=comment_id)
    if not comment:
        return jsonify(error='评论不存在'), 400
    comment = comment[0]
    if like == 'yes':
        comment.likes += 1
    else:
        comment.likes -= 1
    db.session().commit()
    return jsonify(data='操作成功'), 200
