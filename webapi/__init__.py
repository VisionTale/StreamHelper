from flask import Flask, redirect, url_for
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
    from webapi.plugin import load_plugins, get_plugins, get_plugin_pages, get_active_plugins, _activate_plugin
    load_plugins(webapi, config, logger)
    _activate_plugin('base', 'errors', 'user')

    # Make function callable from html
    webapi.jinja_env.globals.update(get_plugin_pages=get_plugin_pages)
    webapi.jinja_env.globals.update(get_plugins=get_plugins)
    webapi.jinja_env.globals.update(get_active_plugins=get_active_plugins)

    @webapi.route('/')
    def index():
        return redirect(url_for('base.dashboard'))

    return webapi


