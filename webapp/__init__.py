from flask import Flask
from flask_admin import Admin
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
#import jinja_partials
from celery import Celery, Task
from webapp.config import Config
from webapp.admin.utils import init_admin
from webapp.orders import constants


bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.session_protection = "strong"
mail = Mail()
admin = Admin()

db = SQLAlchemy(add_models_to_shell=True,
                metadata=MetaData(naming_convention={
                    "ix": 'ix_%(column_0_label)s',
                    "uq": "uq_%(table_name)s_%(column_0_name)s",
                    "ck": "ck_%(table_name)s_%(constraint_name)s",
                    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
                    "pk": "pk_%(table_name)s"
                }))

from webapp.users.setup_users import setup_users


"""
Create the background task processor "Celery"
"""
def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default() # allow using @shared_task decorator
    app.extensions["celery"] = celery_app
    return celery_app

"""
Create the Flask application
"""
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config.update(
        SESSION_COOKIE_SECURE=False, # needs to be false, so we can run without https locally
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    app.config.from_mapping(
        CELERY=dict(
            broker_url=app.config['CELERY_BROKER_URL'],
            result_backend=app.config['CELERY_RESULT_BACKEND'],
            task_ignore_result=True, # default is to ignore result, i.e. when sending emails
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)

    @app.context_processor
    def inject_constants():
        return dict(CONSTANTS=constants)

    app.jinja_env.add_extension('jinja_partials.PartialsJinjaExtension') # make render_partial available inside templates
    db.init_app(app)
    Migrate(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    init_admin(app, admin) # setup admin views

    @app.before_request
    def set_global_variables():
        from .global_vars import set_global_vars
        set_global_vars()

    with app.app_context():
        from webapp.users.routes import users
        from webapp.posts.routes import posts
        from webapp.main.routes import main
        from webapp.orders.routes import orders
        from webapp.errors.handlers import errors
        from webapp.inout.routes import bp as inout_bp
        app.register_blueprint(users)
        app.register_blueprint(posts)
        app.register_blueprint(main)
        app.register_blueprint(errors)
        app.register_blueprint(orders)
        app.register_blueprint(inout_bp)
        db.create_all()
        setup_users()

    return app
