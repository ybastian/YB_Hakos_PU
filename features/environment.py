# features/environment.py
webserver_port = 5123 # use this port for the test web server

from behave import fixture, use_fixture

import threading
from wsgiref import simple_server
from wsgiref.simple_server import WSGIRequestHandler

# ---------------------------------------------------------------------------
# Selenium browser setup
# ---------------------------------------------------------------------------
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-proxy-server')
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument("--proxy-bypass-list=*")

# ---------------------------------------------------------------------------
# Flask test-client config
# ---------------------------------------------------------------------------
class TestConfig:
    SECRET_KEY = 'test-secret-key-for-behave'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    TESTING = True
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_REPLYTO = None
    MAIL_DEBUG = False
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'
    RESERVATION_MAXTIME_MINUTES = 60
    RESERVATION_TIME_MINUTES = 30
    # Admin user created by setup_users(). Password must satisfy:
    # length >3, >8 chars, upper + lower + digit.
    ADMIN_USER = 'testadmin'
    ADMIN_EMAIL = 'admin@test.com'
    ADMIN_PASSWORD = 'TestAdmin1!'


# ---------------------------------------------------------------------------
# Startup web server on port 5123 with in-memory db and browser
# ---------------------------------------------------------------------------
def before_all(context):
    context.driver = webdriver.Chrome(options=chrome_options)
    context.driver.implicitly_wait(1) # Always wait up to this amount of seconds when searching an element
    context.app_config = TestConfig()

    # Flask test app — created ONCE to avoid duplicate blueprint registration
    # (Flask-Admin's module-level Admin() singleton accumulates views on each
    # create_app() call, causing "already registered" errors on the second call).
    from webapp import create_app, db as _db
    context._flask_app = create_app(TestConfig)
    context._flask_db = _db
    # start server
    context.server = simple_server.WSGIServer(("localhost", webserver_port), WSGIRequestHandler)
    context.server.set_app(context._flask_app)
    context.pa_app = threading.Thread(target=context.server.serve_forever)
    context.pa_app.start()


def after_all(context):
    try:
        context.driver.quit()
    except Exception:
        pass
    context.server.shutdown()
    context.pa_app.join()

def before_scenario(context, scenario):
    # Push an app context that stays alive for the whole scenario so that
    # step code can use db.session directly without extra context managers.
    context._app_ctx = context._flask_app.app_context()
    context._app_ctx.push()
    context._flask_db.create_all()
    # Populate roles and groups (user_group, admin_group, etc.) so
    # fixture steps can assign users to groups.
    from webapp.users.setup_users import setup_users
    setup_users()
    context.client = context._flask_app.test_client()


def after_scenario(context, scenario):
    context._flask_db.session.remove()
    context._flask_db.drop_all()
    context._app_ctx.pop()
