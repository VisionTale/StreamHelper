"""
Initializes the base plugin.
"""
from flask import Blueprint
from libs.config import Config
from libs.log import Logger

description: str = "Dashboard and other basic framework sites"

bp: Blueprint = None
name: str = None
logger: Logger = None
config: Config = None
provides_pages: list = [
    ('Dashboard', 'dashboard', 0)
]


def set_blueprint(blueprint: Blueprint):
    """
    Plugins factory method to set a blueprint.

    :param blueprint:
    """
    global bp
    bp = blueprint

    from . import routes
