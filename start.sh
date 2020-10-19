#!/bin/sh

python3 webapi/libs/config.py

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
for file in "$SH_PLUGIN_PATH"/**/requirements.txt; do
  [ -e "$file" ] || break
  python3 -m pip install -r "$file";
done
for file in "$SH_MACRO_PATH"/**/requirements.txt; do
  [ -e "$file" ] || break
  python3 -m pip install -r "$file";
done

flask db upgrade
flask run