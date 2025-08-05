from celery import Celery, Task


def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    # Directly set broker and backend URLs (Redis in this case)
    celery_app = Celery(
        app.name,
        task_cls=FlaskTask,
        include=["tasks"],
        broker="redis://localhost:6379/0",
        backend="redis://localhost:6379/0",
    )

    # Optionally, still load other CELERY_ settings from app.config
    celery_app.config_from_object(app.config, namespace="CELERY")

    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app
