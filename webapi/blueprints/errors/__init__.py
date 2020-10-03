from flask import Blueprint, render_template, request

name = 'errors'

bp = Blueprint(name, __name__, template_folder='templates', static_folder='static')

from . import errors
