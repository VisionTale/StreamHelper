from flask import Blueprint
from webapi.libs.config import Config
from webapi.libs.log import Logger

name = 'base'
config: Config = None
logger: Logger = None

bp = Blueprint(name, __name__, template_folder='templates', static_folder='static')

from . import routes
