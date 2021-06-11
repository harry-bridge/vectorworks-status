#!/bin/sh

echo "Starting VwxStatus worker..."

sleep 5

# Wait for the database to be ready
python manage.py wait_for_db

sleep 10

# Now we can launch the background worker process
python manage.py qcluster