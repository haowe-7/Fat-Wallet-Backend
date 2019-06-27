import unittest
from backend.auth.helpers import encrypt_helper
from backend.models import db, User, Task, Comment, Collect, Participate, ParticipateStatus, Submission
import logging
import json


class TestInit(unittest.TestCase):
    def test_init(self):
        self.add_data()
        self.delete_task()
        self.add_submission()

    # init database
    def add_data(self):
        logging.basicConfig(level=logging.INFO)
        logging.info('testing add data...')
        try:
            for i in range(0, 10):
                user = User(id=i + 1, student_id=f"{i+1}", username=f"ct{i+1}",
                            password=encrypt_helper("123"), email=f"bz{i}@163.com",
                            phone=f"123{i}")
                db.session.add(user)
                db.session.flush()
        except Exception as e:
            logging.error(f'error when adding users: {e}')

        try:
            for i in range(0, 10):
                task = Task(id=i + 1, title='cbbmjm哈哈', creator_id=f"{i%2+1}", task_type=f"{i%3+1}", reward=100,
                            description="pptmjj", due_time="2019-07-02 18:00", max_participate=i % 3 + 1)
                db.session.add(task)
                db.session.flush()
        except Exception as e:
            logging.error(f'error when adding tasks: {e}')

        try:
            for i in range(0, 10):
                comment = Comment(user_id=i + 1, task_id=i + 1, content="Nice!")
                db.session.add(comment)
                db.session.flush()
        except Exception as e:
            logging.error(f'error when adding comments: {e}')

        try:
            for i in range(0, 10):
                collect = Collect(user_id=i + 1, task_id=i + 1)
                db.session.add(collect)
                db.session.flush()
        except Exception as e:
            logging.error(f'error when adding comments: {e}')

        try:
            for i in range(0, 10):
                participate = Participate(user_id=i + 1, task_id=i % 2 + 1, status=1)
                db.session.add(participate)
                db.session.flush()
        except Exception as e:
            logging.error(f'error when adding participates: {e}')
        db.session.commit()
        logging.info('testing add data succeed')

    def delete_task(self):
        logging.info('testing delete task')
        for id in range(0, 10, 2):
            task = Task.get(task_id=id + 1)
            task = task[0]
            db.session.delete(task)
            db.session.commit()
        participates = Participate.get()
        assert len(participates) == 5, 'testing delete task failed'
        logging.info('testing delete task succeed')
        
    def add_submission(self):
        logging.info('testing add submission')
        try:
            for participate in Participate.get():
                participate.status = ParticipateStatus.ONGOING.value
                answer = json.dumps({'question1': 1, 'question2': "母鸡"})
                submission = Submission(user_id=participate.user_id, task_id=participate.task_id, answer=answer)
                db.session.add(submission)
                db.session.commit()
        except Exception as e:
            logging.error(f'testing add submission failed: {e}')
        else:
            logging.info('testing add submission succeed')


if __name__ == '__main__':
    unittest.main()
