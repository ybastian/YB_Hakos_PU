import json

with open('config.json') as config_file:
    config = json.load(config_file)

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
