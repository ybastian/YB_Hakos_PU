import json
import os

with open('config.json') as config_file:
    config = json.load(config_file)


def config_bool(name, default=False):
    value = os.environ.get(name, config.get(name))
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).lower() in ('true', '1', 't', 'yes', 'y', 'on')


class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = config.get('MAIL_SERVER')
    MAIL_PORT = config.get('MAIL_PORT')
    MAIL_USE_TLS = config.get('MAIL_USE_TLS')
    MAIL_USE_SSL = config.get('MAIL_USE_SSL')
    MAIL_USERNAME = config.get('MAIL_USER')
    MAIL_PASSWORD = config.get('MAIL_PASS')
    MAIL_REPLYTO = config.get('MAIL_REPLYTO')
    ADMIN_USER = config.get('ADMIN_USER')
    ADMIN_EMAIL = config.get('ADMIN_EMAIL')
    ADMIN_PASSWORD = config.get('ADMIN_PASSWORD')
    MAIL_DEBUG = config.get('MAIL_DEBUG')
    CELERY_BROKER_URL = config.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = config.get('CELERY_RESULT_BACKEND')
    RESERVATION_MAXTIME_MINUTES = config.get('RESERVATION_MAXTIME_MINUTES')
    RESERVATION_TIME_MINUTES = config.get('RESERVATION_TIME_MINUTES')
    APPVERSION=os.environ.get('APPVERSION', 'local')
    GITCOMMIT=os.environ.get('GITCOMMIT', '')
    CLEANBUILD=os.environ.get('CLEANBUILD', '')
    ENVIRONMENT = config.get('ENVIRONMENT', 'LOCAL')
    SESSION_COOKIE_SECURE = config_bool(
        'SESSION_COOKIE_SECURE',
        default=str(ENVIRONMENT).upper() == 'PRODUCTION',
    )
