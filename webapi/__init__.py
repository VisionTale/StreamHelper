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
plugins = dict()


def create_app():
    global logger, plugins

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
        logger.debug(f'Trying to initialize plugin {d}')
        try:
            plugin = import_module(f'webapi.blueprints.{d}')

            attrs = ['name', 'bp']
            for attr in attrs:
                if not hasattr(plugin, attr):
                    raise AttributeError(f'Plugin {d} misses of the attribute {attr}, which is expected by the '
                                         f'framework')

            plugins[plugin.name] = plugin
            plugin.config = config
            plugin.logger = logger
            webapi.register_blueprint(plugin.bp)

            logger.debug('Finished')
        except Exception as e:
            logger.warn(f'Loading plugin {d} has failed: {e}')

    return webapi



