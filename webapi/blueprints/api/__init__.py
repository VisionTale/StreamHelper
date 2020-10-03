from flask import Blueprint

NAME = 'api'

bp = Blueprint(NAME, __name__, url_prefix='/api')

