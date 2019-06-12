import unittest
from backend.auth.helpers import encrypt_helper
from backend.models import db, User, Task, Comment, Collect, Participate


class TestInit(unittest.TestCase):
    def test_init(self):
        for i in range(0, 10):
            user = User(id=i + 1, student_id=f"{i+1}", username=f"ct{i+1}",
                        password=encrypt_helper("123"), email=f"bz{i}@163.com",
                        phone=f"123{i}")
            db.session.add(user)
            db.session.flush()

        for i in range(0, 10):
            task = Task(id=i + 1, creator_id=f"{i%2+1}", task_type=f"{i%3+1}", reward=100, description="jmfmjj",
                        due_time="2019-06-13 18:00:00", max_participate=i%3+1)
            db.session.add(task)
            db.session.flush()

        for i in range(0, 10):
            comment = Comment(user_id=f"{i%2+1}", task_id=f"{i+1}", content="Nice!")
            db.session.add(comment)
            db.session.flush()

        for i in range(0, 10):
            collect = Collect(user_id=f"{i%2+1}", task_id=f"{i+1}")
            db.session.add(collect)
            db.session.flush()

        for i in range(0, 10):
            participate = Participate(user_id=f"{i%2+1}", task_id=f"{i+1}")
            db.session.add(participate)
            db.session.flush()

        db.session.commit()


if __name__ == '__main__':
    unittest.main()
