from celery import Celery
from celery.schedules import crontab
from backend import app


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app.config.update(
    CELERY_BROKER_URL='redis://redis:6379',
    CELERY_RESULT_BACKEND='redis://redis:6379'
)
celery = make_celery(app)

CELERY_IMPORTS = ("backend.user.views",
                  "backend.task.views")

CELERYBEAT_SCHEDULE = {
    "update_task_status": {
        "task": "backend.task.views.update_task_status",
        "schedule": crontab()
    }
}
