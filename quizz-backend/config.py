import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "supersecret"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'quiz.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Celery Configuration
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/1"
    CELERY_TIMEZONE = "Asia/Kolkata"
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

    # MailHog configuration
    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025  # Default MailHog SMTP port
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = "noreply@quizmaster.com"
