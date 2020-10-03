from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from webapi.libs.config import Config
from webapi.libs.log import setup_webapi as setup

# Config loading
config = Config()
template_folder = config.get('flask', 'template_path')
static_folder = config.get('flask', 'static_path')

# Pre-Init
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()
logger = None


def create_app():
    global logger

    # Initialization
    webapi = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    webapi.config.from_mapping(config.flask_config())

    # Logging
    logger = setup(webapi, config)

    # Database
    db.init_app(webapi)
    migrate.init_app(webapi, db)

    # Session handler
    login.init_app(webapi)
    login.login_view = 'user.login'
    login.login_message = "Please log in to continue."

    # Boostrap
    bootstrap.init_app(webapi)

    # Load modules
    from webapi.modules import models
    from webapi.modules.models import User

    # Load blueprints
    from os import listdir
    from os.path import isdir, join
    from importlib import import_module
    for d in listdir('webapi/blueprints'):  # TODO config option
        if not isdir(join('webapi/blueprints', d)) or d == '__pycache__':
            continue
        logger.debug(f'Initializing directory {d}')
        plugin = import_module(f'webapi.blueprints.{d}')
        webapi.register_blueprint(plugin.bp)
        logger.debug('Finished')

    return webapi



