import datetime


# 获取当前时间
def get_cur_time(time_format="%Y-%m-%d %H:%M"):
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime(time_format)
