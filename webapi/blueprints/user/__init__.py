from flask import Blueprint

NAME = 'user'

bp = Blueprint(NAME, __name__, template_folder='templates', static_folder='static')

from . import forms, routes
