from flask import Blueprint

name = 'base'

bp = Blueprint(name, __name__, template_folder='templates', static_folder='static')


from . import routes
