#!/bin/sh
set -e

# Apply database migrations on startup, then hand off to the CMD (daphne).
python manage.py migrate --noinput

exec "$@"
