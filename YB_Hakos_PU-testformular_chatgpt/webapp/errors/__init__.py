from flask import Blueprint

errors = Blueprint('errors', __name__)

import webapp.errors.handlers
