"""
Initializes the errors plugin.
"""
from flask import Blueprint, render_template, request
from webapi.libs.config import Config
from webapi.libs.log import Logger

description: str = "Http error pages"

bp: Blueprint = None
name: str = None
logger: Logger = None
config: Config = None


def set_blueprint(blueprint: Blueprint):
    """
    Plugins factory method to set a blueprint.

    :param blueprint:
    """
    global bp
    bp = blueprint

    from . import errors
