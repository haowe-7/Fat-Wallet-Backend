from backend import ALLOWED_EXTENSIONS, app, FILE_FOLDER
from flask import request, send_file, Blueprint, jsonify
from werkzeug.utils import secure_filename
from backend.auth.views import random_helper
import os

blueprint = Blueprint('file', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(file_id):
    if 'file' not in request.files:
        return False, "No file part"
    file = request.files['file']
    if file.filename == '':
        return False, "No selected file"
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_name = f"{file_id}-{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], save_name))
        return True, save_name


@blueprint.route('/<string:file_name>', methods=['GET'])
def download_file(file_name):
    if '/' in file_name:
        return 'error', 400
    if file_name:
        return send_file(f"{FILE_FOLDER}/{file_name}", attachment_filename='file.jpg')
    return 'error', 400


@blueprint.route('/upload', methods=['POST'])
def upload():
    flag, msg = upload_file(random_helper())
    if not flag:
        return jsonify(error=msg), 400
    else:
        return jsonify(data=msg), 200
