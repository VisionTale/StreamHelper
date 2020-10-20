from flask import Blueprint, render_template, request
from webapi.libs.config import Config
from webapi.libs.log import Logger

bp: Blueprint = None
name: str = None
logger: Logger = None
config: Config = None


def set_blueprint(blueprint: Blueprint):
    global bp
    bp = blueprint

    from . import errors
