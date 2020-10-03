from flask import Blueprint

name = 'api'

bp = Blueprint(name, __name__, url_prefix='/api')

