#!/bin/bash

echo Applying migrations
python manage.py migrate --noinput

if [ "$DJANGO_ENV" == "production" ]; then
  export DJANGO_SETTINGS_MODULE="vespa.settings_production"
  if [ ! -d "vespa/static" ]; then
    echo Generating static files
    python manage.py collectstatic --clear --no-input
  fi
  echo Starting production server
  exec gunicorn vespa.wsgi -b 0:8080 --access-logfile - --capture-output
else
  echo Starting development server
  exec python manage.py runserver 0:8080
fi
