from flask import Blueprint, render_template, request
from webapi.libs.config import Config
from webapi.libs.log import Logger

name = 'errors'
config: Config = None
logger: Logger = None

bp = Blueprint(name, __name__, template_folder='templates', static_folder='static')

from . import errors
