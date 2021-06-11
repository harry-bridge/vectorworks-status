#!/bin/bash

# Wait for database to be up
python manage.py wait_for_db
sleep 10

python manage.py migrate                  # Apply database migrations

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn VectorworksStatus.wsgi:application \
    --bind 0.0.0.0:300 \
    --workers 3
    "$@"
