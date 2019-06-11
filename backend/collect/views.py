from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, Collect
from backend.auth.helpers import auth_helper
from sqlalchemy import exc
import logging
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
            return dict(error='task id required'), 400
        try:
            collect = Collect(user_id=user_id, task_id=task_id)
            db.session.add(collect)
            db.session.commit()
        except exc.IntegrityError as e:
            logging.error(f'collect failed, msg: {e}')
            return dict(error=f'{e}'), 400
        return dict(data="collect success!"), 200

    def delete(self):
        form = request.get_json(True, True)
        user_id = auth_helper()
        task_id = form.get('task_id')
        if not task_id:
            return dict(error="task id required"), 400
        collect = Collect.get(user_id=user_id, task_id=task_id)
        if not collect:
            return dict(error="collect not exist"), 400
        collect = collect[0]
        db.session.delete(collect)
        db.session.commit()
        return dict(data="delete success!"), 200
