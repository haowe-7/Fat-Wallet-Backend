from backend.models import db, User


def change_balance(user_id, offset):
    """
    修改用户余额
    @params:
        user_id: 用户id
        offset: 余额变化数额，可正可负
    """
    user = User.get(user_id=user_id)
    if not user:
        raise RuntimeError('用户不存在')
    user = user[0]
    if user.balance + offset < 0:
        raise RuntimeError('用户余额不足')
    user.balance += offset
    db.session.commit()
