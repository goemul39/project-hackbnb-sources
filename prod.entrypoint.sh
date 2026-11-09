#!/bin/sh
set -e

apache2ctl -D FOREGROUND &

# D8: run the Flask app with a production WSGI server (no Werkzeug dev server,
# no debugger, no stack traces) and load the app once before forking workers.
exec gunicorn --preload --workers 4 --bind 127.0.0.1:9001 \
    --access-logfile - --error-logfile - app:app
