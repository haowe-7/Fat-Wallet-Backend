from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, Participate
from backend.auth.helpers import auth_helper
from sqlalchemy import exc
import logging
blueprint = Blueprint('participate', __name__)


class ParticipateResource(Resource):
    def get(self):
        form = request.get_json(True, True)
        user_id = form.get('user_id')
        task_id = form.get('task_id')
        participates = Participate.get(user_id=user_id, task_id=task_id)
        result = [{"id": participate.id,
                   "user_id": participate.user_id,
                   "task_id": participate.task_id} for participate in participates]
        return dict(data=result), 200

    def post(self):
        user_id = auth_helper()
        form = request.get_json(True, True)
        task_id = form.get('task_id')
        if not task_id:
            return dict(error='task id required'), 400
        try:
            participate = Participate(user_id=user_id, task_id=task_id)
            db.session.add(participate)
            db.session.commit()
        except exc.IntegrityError as e:
            logging.error(f'collect failed, msg: {e}')
            return dict(error=f'{e}'), 400
        return dict(data="participate success!"), 200

    def delete(self):
        form = request.get_json(True, True)
        user_id = auth_helper()
        task_id = form.get('task_id')
        if not task_id:
            return dict(error="task id required"), 400
        participate = Participate.get(user_id=user_id, task_id=task_id)
        if not participate:
            return dict(error="participate not exist"), 400
        participate = participate[0]
        db.session.delete(participate)
        db.session.commit()
        return dict(data="delete success!"), 200
