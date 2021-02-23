#!/usr/bin/env bash

BASEDIR=$(dirname "$0")
source $BASEDIR/venv/bin/activate
export FLASK_APP=$BASEDIR/app.py
export FLASK_ENV=development
flask run --host=0.0.0.0