#!/bin/sh
set -e

# Apply database migrations on startup, then hand off to the CMD (uvicorn).
python manage.py migrate --noinput

exec "$@"
