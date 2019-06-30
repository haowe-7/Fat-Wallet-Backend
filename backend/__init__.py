from flask import Flask

FILE_FOLDER = '..'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = FILE_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ADMIN_ID = 1    # 管理员用户id
PLEDGE = 10     # 任务申请者需支付的押金
