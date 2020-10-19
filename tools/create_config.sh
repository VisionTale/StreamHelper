#!/bin/sh

if [ ! -d 'webapi' ]; then
  echo "Cannot find files. Execute from the applications root directory, not from './tools' or anywhere else."
  exit 1
fi

python3 webapi/libs/config.py