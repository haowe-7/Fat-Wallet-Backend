from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, Task
from backend.auth.helpers import auth_helper
blueprint = Blueprint('task', __name__)


class TaskResource(Resource):
    def get(self):
        creator_id = request.args.get("creator_id")
        task_type = request.args.get("task_type")
        min_reward = request.args.get("min_reward")
        max_reward = request.args.get("max_reward")
        offset = request.args.get("offset")
        limit = request.args.get("limit")
        tasks = Task.get(creator_id=creator_id, task_type=task_type,
                         min_reward=min_reward, max_reward=max_reward,
                         offset=offset, limit=limit)
        result = [{"id": task.id, "task_type": task.task_type,
                   "reward": task.reward, "description": task.description} for task in tasks]
        return dict(data=result, count=len(result)), 200

    def post(self):
        creator_id = auth_helper()
        form = request.get_json(True, True)
        task_type = form.get('task_type')
        if not task_type:
            return dict(error='task type required'), 400
        reward = form.get('reward')
        if not reward:
            return dict(error='reward required'), 400
        description = form.get('description')
        if not description:
            return dict(error='task description required'), 400
        task = Task(creator_id=creator_id, task_type=task_type, reward=reward, description=description)
        db.session.add(task)
        db.session.commit()
        return dict(data="ok"), 200
