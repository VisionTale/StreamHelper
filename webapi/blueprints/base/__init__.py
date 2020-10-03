from flask import Blueprint

NAME = 'base'

bp = Blueprint('base', __name__, template_folder='templates', static_folder='static')

from . import routes
