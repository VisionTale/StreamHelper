#!/usr/bin/python3

from requests import get
from requests.exceptions import ConnectionError
try:
    code = get('http://localhost:5000/ping').status_code
except ConnectionError:
    code = 0

exit(code != 200)
