import unittest
from backend.auth.helpers import encrypt_helper
from backend.models import db, User, Task, Comment


class TestInit(unittest.TestCase):
    def test_init(self):
        user1 = User(student_id="1", username="ct",
                     password=encrypt_helper("123"), email="bz@163.com",
                     phone="123")
        db.session.add(user1)

        task1 = Task(creator_id=1, task_type=1, reward=100, description="jmfmjj")
        db.session.add(task1)
        task2 = Task(creator_id=1, task_type=2, reward=100, description="cbbmjj")
        db.session.add(task2)

        comment1 = Comment(user_id=1, task_id=1, content="Nice!")
        db.session.add(comment1)
        comment2 = Comment(user_id=1, task_id=2, content="Great!")
        db.session.add(comment2)

        db.session.commit()


if __name__ == '__main__':
    unittest.main()
