from flask import Blueprint, request, jsonify
from flask_restful import Resource
from backend.models import db, Task
from backend.auth.helpers import auth_helper
import time
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
        result = [{"task_id": task.id, "task_type": task.task_type,
                   "reward": task.reward, "description": task.description,
                   "status": task.status, "due_time": str(task.due_time),
                   "max_participate": task.max_participate, "creator_id": task.creator_id} for task in tasks]
        return dict(data=result, count=len(result)), 200

    def post(self):
        creator_id = auth_helper()
        form = request.get_json(True, True)
        task_type = form.get('task_type')
        if not task_type:
            return dict(error='任务类型不能为空'), 400
        reward = form.get('reward')
        if not reward:
            return dict(error='赏金不能为空'), 400
        description = form.get('description')
        if not description:
            return dict(error='任务描述不能为空'), 400
        due_time = form.get('due_time')
        if not due_time:
            return dict(error='任务截止时间不能为空'), 400
        max_participate = form.get('max_participate')
        if not max_participate:
            return dict(error='任务人数上限不能为空'), 400
        task = Task(creator_id=creator_id, task_type=task_type, reward=reward, 
                    description=description, due_time=due_time, max_participate=max_participate)
        db.session.add(task)
        db.session.commit()
        return dict(data="ok"), 200

    def patch(self):  # 任务start time前可以关闭，启用之前可以修改，关闭
        form = request.get_json(True, True)
        user_id = auth_helper()
        if not form:
            return dict(error="表单不能为空"), 400
        task_id = form.get("task_id")
        if not task_id:
            return dict(error="任务ID不能为空"), 400
        task = Task.get(task_id=task_id)
        if not task:
            return dict(error="该任务不存在"), 400
        task = task[0]
        if task.creator_id != user_id:
            return dict(error="您没有权限修改该任务"), 403
        if task.status:
            return dict(error="不能修改已启用的任务"), 400
        task_type = form.get('task_type')
        reward = form.get('reward')
        description = form.get('description')
        start_time = form.get('start_time')
        due_time = form.get('due_time')
        max_participate = form.get('max_participate')
        Task.patch(task_id=task_id, task_type=task_type, reward=reward, description=description,
                   start_time=start_time, due_time=due_time, max_participate=max_participate)
        return dict(data='ok'), 200


@blueprint.route('/close_task', methods=['POST'])
def close_task():
    form = request.get_json(True, True)
    user_id = auth_helper()
    task_id = form.get("task_id")
    if not task_id:
        return jsonify(error='任务ID不能为空'), 400
    task = Task.get(task_id=task_id)
    if not task:
        return jsonify(error='该任务不存在'), 400
    if task.creator_id != user_id:
        return jsonify(error='权限不足'), 403
    if not task.status:
        return jsonify(error='该任务尚未启用'), 400
    if not task.status or time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) < task.due_time:
        task.status = False
        return jsonify(data='ok'), 200
    return jsonify(error='该任务已启用且过了开始时间，无法取消'), 400
