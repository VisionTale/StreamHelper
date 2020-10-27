from typing import Callable

from flask import Flask, redirect, url_for, send_from_directory
from flask.templating import Environment
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

# Pre-init flask extensions
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
bootstrap = Bootstrap()
logger: Logger = None
jinja_env: Environment = None


def create_app():
    """
    Factory method for creating the flask application and all other substantial parts of the application. This includes
    the flask extensions, the framework-specific plugins and macros and the core logger.
    :return: the flask application object
    """
    global logger, jinja_env

    # Initialization of the flask application
    webapi = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    webapi.config.from_mapping(config.flask_config())

    # Setup the logger
    logger = setup(webapi, config)

    # Make the jinja_env accessible
    jinja_env = webapi.jinja_env

    # Setup the database
    db.init_app(webapi)
    migrate.init_app(webapi, db)

    # Setup the session handler
    login.init_app(webapi)
    login.login_view = 'user.login'
    login.login_message = "Please log in to continue."

    # Setup the boostrap extension
    bootstrap.init_app(webapi)

    # Load modules
    from webapi.modules import models
    from webapi.modules.models import User

    # Load blueprints
    from webapi.plugin import load_plugins, get_plugins, get_plugin_pages, get_active_plugins, _activate_plugin
    load_plugins(webapi, config, logger)
    # Make sure the main components are always activated
    _activate_plugin('base', 'errors', 'user')

    # Make function callable from jinja templates
    expose_function_for_templates(get_plugin_pages=get_plugin_pages)
    expose_function_for_templates(get_plugins=get_plugins)
    expose_function_for_templates(get_active_plugins=get_active_plugins)

    # Create a basic redirect to the base plugin
    @webapi.route('/')
    @webapi.route('/dashboard')
    def index():
        return redirect(url_for('base.dashboard'))

    # Allow access to files in media folder
    @webapi.route('/media/<filename>')
    def get_file(filename):
        return send_from_directory(config.get('webapi', 'media_path'), filename)

    @webapi.route('/thumbnail/<filename>')
    def get_thumbnail(filename):
        return send_from_directory(config.get('webapi', 'thumbnail_path'), filename)

    return webapi


def expose_function_for_templates(**kwargs):
    jinja_env.globals.update(**kwargs)


