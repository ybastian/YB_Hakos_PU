from flask import render_template
from webapp.errors import errors

@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', error=error), 404

@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', error=error), 403

@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', error=error), 500
