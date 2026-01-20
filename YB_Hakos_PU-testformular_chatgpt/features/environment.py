# features/environment.py
use_selenium = True
from webapp.config import Config

if use_selenium:

    from selenium import webdriver

    def before_all(context):
        context.driver = webdriver.Chrome()
        context.config = Config()

    def after_all(context):
        context.driver.close()

# else:
#     import os
#     from behave import fixture, use_fixture
#     from webapp import create_app,db
#     app=create_app()
#
#     @fixture
#     def webapp_client(context, *args, **kwargs):
#         app.testing = True
#         context.client = app.test_client()
#         os.unlink(app.config['DATABASE'])
#         with app.app_context():
#             db.create_all()
#         yield context.client
#         # -- CLEANUP:
#         os.unlink(app.config['DATABASE'])
#
#     def before_feature(context, feature):
#         # -- HINT: Recreate a new flaskr client before each feature is executed.
#         use_fixture(webapp_client, context)