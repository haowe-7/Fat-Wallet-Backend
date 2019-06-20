from flask import Blueprint, request, jsonify
from flask_restful import Resource
from backend.models import db, Task, User, Participate, ParticipateStatusCN, ParticipateStatus, Message
from backend.auth.helpers import auth_helper
from backend.celery.config import celery
from backend.task.helpers import get_cur_time
from backend import ADMIN_ID
blueprint = Blueprint('task', __name__)


class TaskResource(Resource):
    def get(self):
        creator_id = request.args.get("creator_id")
        title = request.args.get('title')
        task_type = request.args.get("task_type")
        min_reward = request.args.get("min_reward")
        max_reward = request.args.get("max_reward")
        offset = request.args.get("offset")
        limit = request.args.get("limit")
        tasks = Task.get(creator_id=creator_id, title=title, task_type=task_type,
                         min_reward=min_reward, max_reward=max_reward,
                         offset=offset, limit=limit)
        result = [{"task_id": task.id, "title": task.title, "task_type": task.task_type,
                   "reward": task.reward, "description": task.description,
                   "due_time": task.due_time.strftime("%Y-%m-%d %H:%M"),
                   "max_participate": task.max_participate, "creator_id": task.creator_id,
                   "image": task.image.decode() if task.image else None} for task in tasks]

        for value in result:
            creator = User.get(value["creator_id"])[0]
            value["creator_name"] = creator.username
            participators = [{"user_id": p.user_id, "status": ParticipateStatusCN[p.status]}
                             for p in Participate.get(task_id=value["task_id"])]
            for p in participators:
                user = User.get(user_id=p["user_id"])[0]
                p["username"] = user.username
            value["participators"] = participators
        return dict(data=result, count=len(result)), 200

    def post(self):
        creator_id = auth_helper()
        form = request.get_json(True, True)
        title = form.get('title')
        if not title:
            return dict(error='任务标题不能为空'), 400
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
        if due_time < get_cur_time():
            return dict(error='任务结束时间已过'), 400
        max_participate = form.get('max_participate')
        if not max_participate:
            return dict(error='任务人数上限不能为空'), 400
        image = form.get('image')
        task = Task(creator_id=creator_id, task_type=task_type, reward=reward,
                    description=description, due_time=due_time,
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
        title = form.get('title')
        task_type = form.get('task_type')
        reward = form.get('reward')
        description = form.get('description')
        start_time = form.get('start_time')
        due_time = form.get('due_time')
        max_participate = form.get('max_participate')
        image = form.get('image')
        Task.patch(task_id=task_id, title=title, task_type=task_type, reward=reward,
                   description=description, start_time=start_time, due_time=due_time,
                   max_participate=max_participate, image=image)
        return dict(data='ok'), 200


@blueprint.route('/open', methods=['POST'])
def open_task():
    form = request.get_json(True, True)
    user_id = auth_helper()
    task_id = form.get("task_id")
    if not task_id:
        return jsonify(error='任务ID不能为空'), 400
    task = Task.get(task_id=task_id)
    if not task:
        return jsonify(error='该任务不存在'), 400
    task = task[0]
    if task.creator_id != user_id:
        return jsonify(error='权限不足'), 403
    if task.start_time.strftime("%Y-%m-%d %H:%M") < get_cur_time():
        return jsonify(error='任务开始时间已过'), 400
    if task.status:
        return jsonify(error='该任务已发布'), 400
    task.status = True
    db.session.commit()
    return jsonify(data='发布任务成功'), 200


@blueprint.route('/close', methods=['POST'])
def close_task():
    form = request.get_json(True, True)
    user_id = auth_helper()
    task_id = form.get("task_id")
    if not task_id:
        return jsonify(error='任务ID不能为空'), 400
    task = Task.get(task_id=task_id)
    if not task:
        return jsonify(error='该任务不存在'), 400
    task = task[0]
    if task.creator_id != user_id:
        return jsonify(error='权限不足'), 403
    if not task.status:
        return jsonify(error='该任务尚未启用'), 400
    if get_cur_time() < task.start_time.strftime("%Y-%m-%d %H:%M"):
        task.status = False
        # 关闭任务将清空申请中和申请通过的乙方
        for p in Participate.get(task_id=task_id):
            # TODO 发消息给乙方，该任务已关闭
            db.session.delete(p)
        db.session.commit()
        return jsonify(data='关闭任务成功'), 200
    if not Participate.get(task_id=task_id, status=ParticipateStatus.ONGOING.value):
        task.status = False
        db.session.commit()
        return jsonify(data='关闭任务成功'), 200
    return jsonify(error='该任务已开始且参与人数不为0，无法取消'), 400


@celery.task()
def update_task_status():
    tasks = Task.get(status=True)
    for task in tasks:
        if task.due_time.strftime("%Y-%m-%d %H:%M") < get_cur_time():
            task.status = False
            db.session.commit()
            # TODO 发消息给甲方和乙方


@blueprint.route('/review', methods=['POST'])
def review_task():  # 甲方审核乙方的任务完成结果
    creator_id = auth_helper()
    form = request.get_json(True, True)
    participator_id = form.get('participator_id')
    view = form.get('view')
    task_id = form.get('task_id')
    if not participator_id:
        return jsonify(error='请指定任务参与者'), 400
    if not task_id:
        return jsonify(error='请指定任务'), 400
    task = Task.get(task_id=task_id)
    if not task:
        return jsonify(error='任务不存在'), 400
    task = task[0]
    if task.creator_id != creator_id:
        return jsonify(error='没有操作权限'), 403
    participate = Participate.get(user_id=participator_id, task_id=task_id)
    if not participate:
        return jsonify(error='用户未参与此任务'), 400
    participate = participate[0]
    if participate.status != ParticipateStatus.FINISH.value:
        return jsonify(error='用户未完成此任务'), 400
    if not view or (view != 'yes' and view != 'no'):
        return jsonify(error='请指定正确的审核结果'), 400
    if view == 'yes':   # 甲方满意，审核通过
        # 发消息告知乙方
        message = Message(user_id=participator_id,
                          content=f'您参与的任务{task.title}完成情况通过审核，赏金和押金将送至您的账户')
        db.session.add(message)
        db.session.commit()
        # TODO 支付乙方reward
        # TODO 退还乙方押金
    else:   # 甲方不满意，审核不通过
        # 发消息告知乙方
        message = Message(user_id=participator_id,
                          content=f'您参与的任务{task.title}完成情况未通过审核，暂时无法获得赏金和押金')
        db.session.add(message)
        db.session.commit()
    return jsonify(data='审核完成'), 200


@blueprint.route('/appeal', methods=['POST'])
def appeal_task():  # 乙方(是否)申诉甲方的审核结果
    user_id = auth_helper()
    form = request.get_json(True, True)
    task_id = form.get('task_id')
    view = form.get('view')
    if not task_id:
        return jsonify(error='请指定任务'), 400
    task = Task.get(task_id=task_id)
    if not task:
        return jsonify(error='任务不存在'), 400
    task = task[0]
    if not view or (view != 'yes' and view != 'no'):
        return jsonify(error='请指定正确的申诉请求'), 400
    participate = Participate.get(user_id=user_id, task_id=task_id)
    if not participate:
        return jsonify(error='未参与该任务'), 400
    participate = participate[0]
    if participate.status != ParticipateStatus.FINISH.value:
        return jsonify(error='未完成该任务'), 400
    if view == 'yes':   # 确认申诉
        # 发消息给admin
        message = Message(user_id=ADMIN_ID, content=f'关于任务{task.title}有新的申诉信息')
        db.session.add(message)
        db.session.commit()
    else:   # 不申诉
        # TODO 不退还乙方押金
        pass
    return jsonify(data='申诉完成'), 200
