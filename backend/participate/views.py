from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, Participate
from backend.auth.helpers import auth_helper
blueprint = Blueprint('participate', __name__)

class ParticipateResource(Resource):
    def get(self):
        form = request.get_json(True, True)
        user_id = form.get('user_id')
        task_id = form.get('task_id')
        participates = Participate.get(user_id=user_id, task_id=task_id)
        result = [{"id":participate.id,
                   "user_id": participate.user_id, 
                   "task_id": participate.task_id} for participate in participates]
        return dict(data=result), 200

    def post(self):
        user_id = auth_helper()
        form = request.get_json(True, True)
        task_id = form.get('task_id')
        if not task_id:
            return dict(error='task id required'), 400
        participate = Participate()
        participate.user_id = user_id
        participate.task_id = task_id
        db.session.add(participate)
        db.session.commit()
        return dict(data="ok"), 200

    def delete(self):
        form = request.get_json(True, True)
        user_id = auth_helper()
        task_id = form.get('task_id')
        if not task_id:
           return dict(error="participate id required"), 400 
        participate = Participate.get(user_id=user_id, task_id=task_id)
        if not participate:
            return dict(error="participate not exist"), 400
        participate = participate[0]
        db.session.delete(participate)
        db.session.commit()
        return dict(data="ok"), 200
