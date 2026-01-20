from flask import Blueprint

bp = Blueprint('inout', __name__)

from webapp.inout import routes
