#!/bin/sh
echo "Running docker-startup.sh"
echo "Upgrade database if needed"
flask --app app.py db upgrade
echo "Run celery"
celery -A make_celery worker -l info &
echo "Run flask app"
flask --app prod.py run
#exec python prod.py
