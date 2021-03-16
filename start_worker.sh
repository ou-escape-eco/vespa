#!/bin/bash

if [ "$DJANGO_ENV" == "production" ]; then
  export DJANGO_SETTINGS_MODULE="vespa.settings_production"
fi

echo Removing logs
rm tmp/*.log

echo Starting Celery
exec celery -A vespa worker -B -l info