# from app import app
from . import app
from .blueprint import setup

setup(app)
# app.run(host="0.0.0.0", debug=True)
