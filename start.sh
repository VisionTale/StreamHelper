#!/bin/sh

if [ ! -f /srv/venv/bin/activate ]; then
  python3 -m pip install --upgrade venv
	python3 -m venv /srv/venv
fi

. /srv/venv/bin/activate

python3 webapi.py