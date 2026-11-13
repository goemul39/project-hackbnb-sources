#!/bin/sh
set -e

apache2ctl -D FOREGROUND &

# D8: use gunicorn instead of the Flask dev server
exec gunicorn --preload --workers 4 --bind 127.0.0.1:9001 \
    --access-logfile - --error-logfile - app:app
