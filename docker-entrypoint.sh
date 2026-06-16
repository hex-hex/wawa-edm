#!/bin/sh
set -e

# Clean up data that would violate constraints (runs before migrate so the
# unique constraints can be applied), apply migrations, then hand off to the
# CMD (uvicorn).
python manage.py fix_data
python manage.py migrate --noinput

exec "$@"
