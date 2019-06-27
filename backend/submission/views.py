from flask import Blueprint, request
from flask_restful import Resource
from backend.models import db, Submission, Task, Participate, ParticipateStatus
from backend.auth.helpers import auth_helper
from sqlalchemy import exc
import logging
import re
import json
blueprint = Blueprint('submission', __name__)


class SubmissionResource(Resource):
    def get(self):
        user_id = auth_helper()
        task_id = request.args.get('task_id')
        submissions = Submission.get(user_id=user_id, task_id=task_id)
        result = [{"id": submission.id,
                   "user_id": submission.user_id,
                   "task_id": submission.task_id,
                   "answer": json.loads(submission.answer)} for submission in submissions]
        return dict(data=result), 200

    def post(self):
        user_id = auth_helper()
        form = request.get_json(True, True)
        task_id = form.get('task_id')
        answer = form.get('answer')
        if not task_id:
            return dict(error='请指定任务'), 400
        task = Task.get(task_id=task_id)
        if not task:
            return dict(error='任务不存在'), 400
        participates = Participate.get(user_id=user_id, task_id=task_id)
        if not participates or (participates and participates[0].status == ParticipateStatus.APPLYING.value):
            return dict(error='未参与该任务'), 403
        try:
            answer = json.dumps(answer)
        except Exception:
            return dict(error='请提交正确的答案'), 400
        try:
            submission = Submission(user_id=user_id, task_id=task_id, answer=answer)
            db.session.add(submission)
            db.session.commit()
        except exc.IntegrityError as e:
            logging.error(f'submit answer failed, msg: {e}')
            if re.search(r"Duplicate entry '\S*' for key '\S*'", e.orig.args[1]):
                return dict(error='不能重复提交问卷'), 400
            else:
                return dict(error=f'{e}'), 400
        return dict(data='问卷提交成功'), 200
