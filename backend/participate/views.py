from flask import Blueprint, request, jsonify
from flask_restful import Resource
from backend.models import db, Participate, ParticipateStatusCN, ParticipateStatus, Task, Message
from backend.auth.helpers import auth_helper
from backend.utils import change_balance
from backend import PLEDGE
from sqlalchemy import exc
import logging
import re
blueprint = Blueprint('participate', __name__)


class ParticipateResource(Resource):
    def get(self):
        user_id = request.args.get('user_id')
        task_id = request.args.get('task_id')
        status = request.args.get('status')
        participates = Participate.get(user_id=user_id, task_id=task_id, status=status)
        result = [{"id": participate.id,
                   "user_id": participate.user_id,
                   "task_id": participate.task_id,
                   "status": ParticipateStatusCN[participate.status]} for participate in participates]
        return dict(data=result), 200

    def post(self):
        user_id = auth_helper()
        form = request.get_json(True, True)
        task_id = form.get('task_id')
        if not task_id:
            return dict(error='请指定任务'), 400
        task = Task.get(task_id=task_id)
        if not task:
            return dict(error='该任务不存在'), 400
        task = task[0]
        if task.creator_id == user_id:
            return dict(error='发起者无需申请参与该任务'), 400
        # 支付押金
        try:
            change_balance(user_id, -1 * PLEDGE)
        except RuntimeError as e:
            return dict(error=f'{e}'), 400
        try:
            participate = Participate(user_id=user_id, task_id=task_id, status=ParticipateStatus.APPLYING.value)
            db.session.add(participate)
            db.session.commit()
        except exc.IntegrityError as e:
            logging.error(f'participate failed, msg: {e}')
            if re.search(r"Duplicate entry '\S*' for key '\S*'", e.orig.args[1]):
                return dict(error='您已经提交过该任务的申请'), 400
            elif re.search(r"Cannot add or update a child row", e.orig.args[1]):
                return dict(error='该任务不存在'), 400
            else:
                return dict(error=f'{e}'), 400
        # 发申请消息给甲方
        message = Message(user_id=task.creator_id, content=f'有人申请参加任务{task.title}')
        db.session.add(message)
        db.session.commit()
        return dict(data="已成功发出申请"), 200

    def delete(self):
        form = request.get_json(True, True)
        user_id = auth_helper()
        task_id = form.get('task_id')
        if not task_id:
            return dict(error="请指定任务"), 400
        task = Task.get(task_id=task_id)
        if not task:
            return dict(error="该任务不存在"), 400
        task = task[0]
        participator_id = form.get('participator_id')
        if not participator_id:
            return dict(error="参与者不能为空"), 400
        participate = Participate.get(user_id=participator_id, task_id=task_id)
        if not participate:
            return dict(error="该参与信息不存在"), 400
        if user_id != participator_id:  # 参与者才能取消参与任务
            return dict(error="您没有操作权限"), 403
        participate = participate[0]
        db.session.delete(participate)
        db.session.commit()
        # 发消息给甲方，乙方退出了任务
        message = Message(user_id=task.creator_id, content=f'有人退出了任务{task.title}')
        db.session.add(message)
        db.session.commit()
        # 不退还乙方押金
        return dict(data="ok"), 200


@blueprint.route('/review', methods=['POST'])
def review_participate():  # 甲方审批乙方的申请
    form = request.get_json(True, True)
    user_id = auth_helper()
    participator_id = form.get('participator_id')
    view = form.get('view')
    if not participator_id:
        return jsonify(error="请指定申请者"), 400
    task_id = form.get('task_id')
    if not task_id:
        return jsonify(error="请指定任务"), 400
    task = Task.get(task_id=task_id)
    if not task:
        return jsonify(error="该任务不存在"), 400
    task = task[0]
    if user_id != task.creator_id:
        return jsonify(error="您没有操作权限"), 403
    participate = Participate.get(user_id=participator_id, task_id=task_id)
    if not participate:
        return jsonify(error='申请不存在'), 400
    participate = participate[0]
    if participate.status != ParticipateStatus.APPLYING.value:
        return jsonify(error='该用户已在任务中'), 400
    
    if not view or (view != 'yes' and view != 'no'):
        return jsonify(error='请指定正确的审批结果')
    if view == 'yes':   # 同意乙方参与任务
        participate.status = ParticipateStatus.ONGOING.value
        db.session.commit()
        # 发消息给乙方　申请已通过
        message = Message(user_id=participator_id, content=f'您关于任务{task.title}的申请已通过')
        db.session.add(message)
        db.session.commit()
    else:   # 不同意乙方参与任务
        db.session.delete(participate)
        db.session.commit()
        # 发消息给乙方 申请未通过
        message = Message(user_id=participator_id, content=f'您关于任务{task.title}的申请未通过')
        db.session.add(message)
        db.session.commit()
        # 退还乙方押金
        change_balance(participator_id, PLEDGE)

    return jsonify(data='审批完成'), 200


@blueprint.route('/finish', methods=['POST'])
def finish_participate():   # 乙方确认完成任务
    user_id = auth_helper()
    form = request.get_json(True, True)
    task_id = form.get('task_id')
    if not task_id:
        return jsonify(error='请指定任务'), 400
    task = Task.get(task_id=task_id)
    if not task:
        return jsonify(error='任务不存在'), 400
    participate = Participate.get(user_id=user_id, task_id=task_id)
    if not participate or participate.status == ParticipateStatus.APPLYING.value:
        return jsonify(error='未参与该任务'), 400
    participate = participate[0]
    if participate.status == ParticipateStatus.FINISH.value:
        return jsonify(error='已完成该任务')
    participate.status = ParticipateStatus.FINISH.value
    db.session.commit()
    # 发消息告知甲方 乙方完成任务
    message = Message(user_id=task.creator_id, content=f'有人已完成任务{task.title}')
    db.session.add(message)
    db.session.commit()
    return jsonify(data='确认成功'), 200
