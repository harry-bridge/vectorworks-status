#!/bin/bash

# Wait for database to be up
python manage.py wait_for_db
sleep 10

# Apply database migrations
python manage.py migrate
# Collect our static media.
#python manage.py collectstatic --noinput

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn VectorworksStatus.wsgi:application \
    --bind 0.0.0.0:300 \
    --workers 3
    "$@"
