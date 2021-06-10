#!/bin/bash

function postgres_ready(){
python3 << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(dbname="$POSTGRES_USER", user="$POSTGRES_USER", password="$POSTGRES_PASSWORD", host="$POSTGRES_HOST")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."

python3 manage.py migrate                  # Apply database migrations

# start cron
#echo Starting cron
#cron && tail -f /var/log/cron.log
#service cron start

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn VectorworksStatus.wsgi:application \
    --bind 0.0.0.0:300 \
    --workers 3
    "$@"
