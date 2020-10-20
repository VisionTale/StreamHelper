from flask import Blueprint
from webapi.libs.config import Config
from webapi.libs.log import Logger

bp: Blueprint = None
name: str = None
logger: Logger = None
config: Config = None
provides_pages: list = [
    ('Dashboard', 'dashboard', 0)
]


def set_blueprint(blueprint: Blueprint):
    global bp
    bp = blueprint

    from . import routes

