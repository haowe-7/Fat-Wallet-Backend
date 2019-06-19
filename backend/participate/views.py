from flask import Blueprint, request, jsonify
from flask_restful import Resource
from backend.models import db, Participate, ParticipateStatusCN, ParticipateStatus, Task
from backend.auth.helpers import auth_helper
from sqlalchemy import exc
from backend.task.helpers import get_cur_time
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
            return dict(error='该任务不存在'), 400  # FIXME 自己的任务自己能否参与
        task = task[0]
        if not task.status:
            return dict(error='该任务尚未发布'), 400
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
        # TODO 发消息给甲方，　申请信息
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
        if user_id != participator_id and user_id != participator_id:  # 自己或者任务发布者才能退出任务或请人离开任务
            return dict(error="您没有操作权限"), 403
        if task.start_time.strftime("%Y-%m-%d %H:%M") < get_cur_time():
            return dict(error="任务已开始，任务人员无法调整"), 400
        participate = participate[0]
        db.session.delete(participate)
        db.session.commit()
        # if user_id == task.creator_id:
        #     # TODO 发消息给乙方，被踢出任务
        # else:
        #     # TODO 发消息给甲方，乙方退出了任务
        return dict(data="ok"), 200


@blueprint.route('/permit', methods=['POST'])
def permit_application():  # 甲方审批(通过)
    form = request.get_json(True, True)
    user_id = auth_helper()
    participator_id = form.get('participator_id')
    if not participator_id:
        return jsonify(error="参与者不能为空"), 400
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
        return jsonify(error='该用户未提出申请'), 400
    participate = participate[0]
    if participate.status == ParticipateStatus.ONGOING.value:
        return jsonify(error='该用户已在任务中'), 400
    participate.status = ParticipateStatus.ONGOING.value
    db.session.commit()
    # TODO 发消息给乙方　申请已通过
    return jsonify(data='ok'), 400
