from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, Collect
from backend.auth.helpers import auth_helper
from sqlalchemy import exc
import logging
import re
blueprint = Blueprint('collect', __name__)


class CollectResource(Resource):
    def get(self):
        form = request.get_json(True, True)
        user_id = form.get('user_id')
        task_id = form.get('task_id')
        collects = Collect.get(user_id=user_id, task_id=task_id)
        result = [{"id": collect.id,
                   "user_id": collect.user_id,
                   "task_id": collect.task_id} for collect in collects]
        return dict(data=result), 200

    def post(self):
        user_id = auth_helper()
        form = request.get_json(True, True)
        task_id = form.get('task_id')
        if not task_id:
            return dict(error='请指定任务'), 400
        try:
            collect = Collect(user_id=user_id, task_id=task_id)
            db.session.add(collect)
            db.session.commit()
        except exc.IntegrityError as e:
            logging.error(f'collect failed, msg: {e}')
            if re.search(r"Duplicate entry '\S*' for key '\S*'", e.orig.args[1]):
                return dict(error='不能重复收藏该任务'), 400
            elif re.search(r"Cannot add or update a child row", e.orig.args[1]):
                return dict(error='任务不存在'), 400
            else:
                return dict(error=f'{e}'), 400
        return dict(data="收藏成功"), 200

    def delete(self):
        form = request.get_json(True, True)
        user_id = auth_helper()
        task_id = form.get('task_id')
        if not task_id:
            return dict(error="请指定任务"), 400
        collect = Collect.get(user_id=user_id, task_id=task_id)
        if not collect:
            return dict(error="未收藏该任务"), 400
        collect = collect[0]
        db.session.delete(collect)
        db.session.commit()
        return dict(data="取消收藏成功"), 200
