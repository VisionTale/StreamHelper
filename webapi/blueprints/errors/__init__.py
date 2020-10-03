from flask import Blueprint, render_template, request
from webapi import db

NAME = 'errors'

bp = Blueprint('errors', __name__, template_folder='templates', static_folder='static')

from . import errors
