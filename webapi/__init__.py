from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from webapi.libs.config import Config
from webapi.libs.log import setup_webapi as setup, Logger

# Config loading
config = Config()
template_folder = config.get('flask', 'template_path')
static_folder = config.get('flask', 'static_path')

# Pre-Init
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()
logger: Logger = None
plugins = dict()
active_plugins = list()
plugin_pages = list()


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
        logger.debug(f'Loading plugin {d}')
        try:
            plugin = import_module(f'webapi.blueprints.{d}')

            attrs = ['set_blueprint']
            for attr in attrs:
                if not hasattr(plugin, attr):
                    raise AttributeError(f'Plugin {d} misses the attribute {attr}, which is expected by the framework.')

            plugin.name = d
            plugin.config = config
            plugin.logger = logger
            blueprint = Blueprint(
                d,
                d,
                template_folder=f'webapi/blueprints/{d}/templates',
                static_folder=f'webapi/blueprints/{d}/static',
                url_prefix=f'/{d}'
            )
            plugin.set_blueprint(blueprint)
            plugins[d] = plugin

            webapi.register_blueprint(blueprint)
            if hasattr(plugin, 'provides_pages'):
                for page in plugin.provides_pages:
                    plugin_pages.append((page[0], f'{plugin.name}.{page[1]}', page[2] if len(page) > 2 else 1000, d))

            logger.debug('Finished')
        except Exception as e:
            logger.warn(f'Loading plugin {d} has failed: {e}')

    # Make function callable from html
    webapi.jinja_env.globals.update(get_plugin_pages=get_plugin_pages)
    webapi.jinja_env.globals.update(get_plugins=get_plugins)

    return webapi


def get_plugin_pages() -> list:
    plugin_pages.sort(key=sort_pages)
    return plugin_pages


def sort_pages(page: tuple) -> tuple:
    return page[2], page[0]


def get_plugins() -> list:
    return [(key.capitalize(), plugins[key].description if hasattr(plugins[key], 'description') else "") for key in list(plugins.keys())]

