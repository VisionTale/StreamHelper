from flask import Blueprint
from webapi.libs.config import Config
from webapi.libs.log import Logger

name = 'api'
config: Config = None
logger: Logger = None

bp = Blueprint(name, __name__, url_prefix='/api')

