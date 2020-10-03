from flask import Blueprint

name = 'user'

bp = Blueprint(name, __name__, template_folder='templates', static_folder='static')

from . import forms, routes
