#!/bin/bash

if [ -d /app ]; then
    cd /app
fi
. venv/bin/activate

cd flaskapp/
export FLASK_APP=run.py
export FLASK_ENV=development
flask run --host=0.0.0.0
