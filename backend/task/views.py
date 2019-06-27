from flask import Blueprint, request, jsonify
from flask_restful import Resource
from backend.models import db, Task, User, Participate, ParticipateStatusCN, ParticipateStatus
from backend.models import Message, Collect, Comment
from backend.auth.helpers import auth_helper
from backend.celery.config import celery
from backend.task.helpers import get_cur_time
from backend import ADMIN_ID, PLEDGE
from backend.utils import change_balance
import json
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
            user_id = auth_helper()
            collect = Collect.get(user_id=user_id, task_id=value['task_id'])
            value['is_collect'] = True if collect else False    # 是否收藏该任务
            comments = Comment.get(task_id=value['task_id'])
            value['num_comments'] = len(comments) if comments else 0    # 任务的评论数
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
        extra = form.get('extra')
        try:
            extra = json.dumps(extra)
        except Exception:
            return dict(error='请指定正确的任务内容'), 400
        image = form.get('image')
        # 支付押金
        try:
            change_balance(creator_id, -1 * reward * max_participate)
        except RuntimeError as e:
            return dict(error=f'{e}'), 400
        task = Task(creator_id=creator_id, task_type=task_type, reward=reward,
                    description=description, due_time=due_time,
                    max_participate=max_participate, extra=extra, image=image)
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
            return dict(error="权限不足"), 403
        participates = Participate.get(task_id=task_id)
        if participates:
            # 有用户已经开始做任务/完成任务时无法修改
            for participate in participates:
                if participate.status != ParticipateStatus.APPLYING.value:
                    return dict(error='任务已经有人参与，无法修改'), 400
            # 撤销所有的申请并通知申请者
            ids = []
            for participate in participates:
                ids.append(participate.id)
                message = Message(user_id=participate.user_id, content=f'您申请参与的任务"{task.title}"有改动的信息，申请取消')
                db.session.add(message)
                db.session.commit()
                # 把押金还给申请者
                change_balance(participate.user_id, PLEDGE)
            stmt = Participate.__table__.delete().where(Participate.id.in_(ids))
            db.session.execute(stmt)
            db.session.commit()
            
        title = form.get('title')
        task_type = form.get('task_type')
        reward = form.get('reward')
        max_participate = form.get('max_participate')
        if title or task_type or reward or max_participate:
            return dict(error='只允许修改任务截止时间、简介、内容、图片'), 400
        due_time = form.get('due_time')
        if due_time and due_time < get_cur_time():
            return dict(error='截止时间已过'), 400
        description = form.get('description')
        extra = form.get('extra')
        if extra:
            try:
                extra = json.dumps(extra)
            except Exception:
                return dict(error='请指定正确的任务内容'), 400
        image = form.get('image')
        Task.patch(task_id=task_id, title=title, task_type=task_type, reward=reward,
                   description=description, due_time=due_time,
                   max_participate=max_participate, extra=extra, image=image)
        return dict(data='修改任务成功'), 200
    
    def delete(self):
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
        participates = Participate.get(task_id=task_id)
        if participates:
            # 有用户已经开始做任务/完成任务时无法取消
            for participate in participates:
                if participate.status != ParticipateStatus.APPLYING.value:
                    return dict(error='任务已经有人参与，无法取消'), 400
            # 通知所有申请该任务的用户: 该任务已取消
            for participate in participates:
                message = Message(user_id=participate.user_id, content=f'您申请参与的任务"{task.title}"已取消')
                # 把押金还给申请者
                change_balance(participate.user_id, PLEDGE)
                db.session.add(message)
                db.session.commit()
            # 数据库外键约束，删除任务自动删除所有participate
            # db.session.delete(participates)
            # db.session.commit()
        # 把押金还给发起者
        change_balance(user_id, task.reward * task.max_participate)
        # 数据库中删除任务
        db.session.delete(task)
        db.session.commit()
        return dict(data='取消任务成功'), 200


# @blueprint.route('/open', methods=['POST'])
# def open_task():
#     form = request.get_json(True, True)
#     user_id = auth_helper()
#     task_id = form.get("task_id")
#     if not task_id:
#         return jsonify(error='任务ID不能为空'), 400
#     task = Task.get(task_id=task_id)
#     if not task:
#         return jsonify(error='该任务不存在'), 400
#     task = task[0]
#     if task.creator_id != user_id:
#         return jsonify(error='权限不足'), 403
#     if task.start_time.strftime("%Y-%m-%d %H:%M") < get_cur_time():
#         return jsonify(error='任务开始时间已过'), 400
#     if task.status:
#         return jsonify(error='该任务已发布'), 400
#     task.status = True
#     db.session.commit()
#     return jsonify(data='发布任务成功'), 200


# @blueprint.route('/close', methods=['POST'])
# def close_task():
#     form = request.get_json(True, True)
#     user_id = auth_helper()
#     task_id = form.get("task_id")
#     if not task_id:
#         return jsonify(error='任务ID不能为空'), 400
#     task = Task.get(task_id=task_id)
#     if not task:
#         return jsonify(error='该任务不存在'), 400
#     task = task[0]
#     if task.creator_id != user_id:
#         return jsonify(error='权限不足'), 403
#     if not task.status:
#         return jsonify(error='该任务尚未启用'), 400
#     if get_cur_time() < task.start_time.strftime("%Y-%m-%d %H:%M"):
#         task.status = False
#         # 关闭任务将清空申请中和申请通过的乙方
#         for p in Participate.get(task_id=task_id):
#             # TODO 发消息给乙方，该任务已关闭
#             db.session.delete(p)
#         db.session.commit()
#         return jsonify(data='关闭任务成功'), 200
#     if not Participate.get(task_id=task_id, status=ParticipateStatus.ONGOING.value):
#         task.status = False
#         db.session.commit()
#         return jsonify(data='关闭任务成功'), 200
#     return jsonify(error='该任务已开始且参与人数不为0，无法取消'), 400


@celery.task()
def update_task_status():   # 检查任务是否到期
    tasks = Task.get()
    for task in tasks:
        # 任务截止时间已过
        if task.due_time.strftime("%Y-%m-%d %H:%M") < get_cur_time():
            participates = Participate.get(task_id=task.id)
            ids = []
            count = 0
            for participate in participates:
                if participate.status == ParticipateStatus.APPLYING.value:
                    # 取消申请，发消息告知乙方并退还押金
                    ids.append(participate.id)
                    message = Message(user_id=participate.user_id, content=f'您申请的任务{task.title}截止时间已过，申请已取消')
                    db.session.add(message)
                    db.session.commit()
                    change_balance(participate.user_id, PLEDGE)
                elif participate.status == ParticipateStatus.ONGOING.value:
                    # 乙方任务失败，改变参与状态，不退还押金并发送消息
                    participate.status = ParticipateStatus.FAILED.value
                    db.session.commit()
                    message = Message(user_id=participate.user_id, content=f'您正在进行的任务{task.title}截止时间已过，您未完成任务，无法退还押金')
                    db.session.add(message)
                    db.session.commit()
                elif participate.status == ParticipateStatus.FINISH.value:
                    count += 1
            # 取消所有申请
            stmt = Participate.__table__.delete().where(Participate.id.in_(ids))
            db.session.execute(stmt)
            db.session.commit()
            # 退还甲方剩余押金并发送消息
            change_balance(task.creator_id, (task.max_participate - count) * task.reward)
            message = Message(user_id=task.creator_id, content=f'您发起的任务{task.title}截止时间已过，剩余押金已退还')
            db.session.add(message)
            db.session.commit()


@blueprint.route('/extra', methods=['GET'])
def get_extra():    # 获取任务的具体内容，仅甲方和通过申请的乙方可查看
    user_id = auth_helper()
    task_id = request.args.get("task_id")
    if not task_id:
        return jsonify(error='请指定任务'), 400
    task = Task.get(task_id=task_id)
    if not task:
        return jsonify(error='任务不存在'), 400
    task = task[0]
    participate = Participate.get(user_id=user_id, task_id=task_id)
    # 未参与、申请中、非创建者
    if (not participate or (participate and participate[0].status == ParticipateStatus.APPLYING.value))\
            and task.creator_id != user_id:
        return jsonify(error='没有权限查看'), 403
    return jsonify(data=json.loads(task.extra)), 200


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
        # 支付乙方reward
        change_balance(participator_id, task.reward)
        # 退还乙方押金
        change_balance(participator_id, PLEDGE)
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
        # 不退还乙方押金
        pass
    return jsonify(data='申诉完成'), 200
