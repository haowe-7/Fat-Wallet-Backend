from flask import Blueprint, request, jsonify
from flask_restful import Resource
from backend.models import db, Task, User, Participate, ParticipateStatusCN, ParticipateStatus
from backend.auth.helpers import auth_helper
from backend.celery.config import celery
from backend.task.helpers import get_cur_time
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
                   "status": task.status, "due_time": task.due_time.strftime("%Y-%m-%d %H:%M"),
                   "start_time": task.start_time.strftime("%Y-%m-%d %H:%M"),
                   "max_participate": task.max_participate, "creator_id": task.creator_id,
                   "image": task.image.decode() if task.image else None} for task in tasks]

        for value in result:
            creator = User.get(value["creator_id"])[0]
            value["creator_name"] = creator.username
            status = None
            if value["start_time"] < get_cur_time():
                status = ParticipateStatus.ONGOING.value  # 如果任务已开始，只显示审批通过的乙方
            participators = [{"user_id": p.user_id, "status": ParticipateStatusCN[p.status]}
                             for p in Participate.get(task_id=value["task_id"], status=status)]
            for p in participators:
                user = User.get(user_id=p["user_id"])[0]
                p["username"] = user.username
            value["participators"] = participators
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
        start_time = form.get('start_time')
        if not start_time:
            return dict(error='任务开始时间不能为空'), 400
        if start_time < get_cur_time():
            return dict(error='任务开始时间已过'), 400
        due_time = form.get('due_time')
        if not due_time:
            return dict(error='任务截止时间不能为空'), 400
        if due_time < get_cur_time():
            return dict(error='任务结束时间已过'), 400
        if start_time > due_time:
            return dict(error='任务开始时间晚于结束时间'), 400
        max_participate = form.get('max_participate')
        if not max_participate:
            return dict(error='任务人数上限不能为空'), 400
        image = form.get('image')
        task = Task(creator_id=creator_id, task_type=task_type, reward=reward,
                    description=description, start_time=start_time, due_time=due_time,
                    max_participate=max_participate, image=image)
        db.session.add(task)
        db.session.commit()
        return dict(data="ok"), 200

    def patch(self):
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
        if task.status:  # 任务start time前可以关闭，启用之前可以修改，关闭
            return dict(error="不能修改已启用的任务"), 400
        task_type = form.get('task_type')
        reward = form.get('reward')
        description = form.get('description')
        start_time = form.get('start_time')
        due_time = form.get('due_time')
        max_participate = form.get('max_participate')
        image = form.get('image')
        Task.patch(task_id=task_id, task_type=task_type, reward=reward, description=description,
                   start_time=start_time, due_time=due_time, max_participate=max_participate,
                   image=image)
        return dict(data='ok'), 200


@blueprint.route('/open_task', methods=['POST'])
def open_task():
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
    if task.start_time.strftime("%Y-%m-%d %H:%M") < get_cur_time():
        return jsonify(error='任务开始时间已过'), 400
    if task.status:
        return jsonify(error='该任务已发布'), 400
    task.status = True
    db.session.commit()
    return jsonify(data='发布任务成功'), 200


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
    if task.status and get_cur_time() < task.start_time.strftime("%Y-%m-%d %H:%M"):
        task.status = False
        participates = Participate.get(task_id=task_id)
        for p in participates:
            # if p.status == ParticipateStatus.APPLYING.value:
            #     # TODO 发消息给申请中的乙方，该任务已关闭
            # else:
            #     # TODO 发消息给审批通过的乙方，该任务已关闭
            db.session.delete(p)
        return jsonify(data='关闭任务成功'), 200
    return jsonify(error='该任务已启用且过了开始时间，无法取消'), 400


@celery.task()
def update_task_status():
    tasks = Task.get(status=True)
    for task in tasks:
        if task.due_time.strftime("%Y-%m-%d %H:%M") < get_cur_time():
            task.status = False
            db.session.commit()
            # TODO 发消息给甲方和乙方
