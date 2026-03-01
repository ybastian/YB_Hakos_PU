#!/bin/sh
echo "Running docker-startup.sh"

# Make sure, parameters are set either true or false
[ -z "$RUNFLASK" ] && RUNFLASK=true
[ -z "$RUNCELERY" ] && RUNCELERY=true

if [  "$RUNFLASK" != "true" -a "$RUNFLASK" != "false" ]; then
  echo "WRONG PARAMETER RUNFLASK=$RUNFLASK"
  exit 1
fi

if [  "$RUNCELERY" != "true" -a "$RUNCELERY" != "false" ]; then
  echo "WRONG PARAMETER RUNCELERY=$RUNCELERY"
  exit 1
fi

if $RUNCELERY; then
  echo "Run celery"
  if $RUNFLASK; then #run in background
    celery -A make_celery worker -l info &
  else
    exec celery -A make_celery worker -l info
  fi
fi

if $RUNFLASK; then
  echo "Upgrade database if needed"
  flask --app app.py db upgrade

  echo "Run flask app"
  exec flask --app prod.py run
fi
