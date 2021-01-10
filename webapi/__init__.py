"""
Main application.
"""
from typing import Callable

from flask import Flask, Request, redirect, url_for, send_from_directory
from flask.templating import Environment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

from webapi.libs.config import Config
from webapi.libs.log import setup_webapi as setup, Logger
from webapi.libs.text import camel_case

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
first_run = True


def create_app():
    """
    Factory method for creating the flask application and all other substantial parts of the application. This includes
    the flask extensions, the framework-specific plugins and macros and the core logger.

    :return: the flask application object
    """
    global logger, jinja_env, first_run

    # Ensure bootstrap is available
    from webapi.libs.deps.bootstrap import download_bootstrap, get_bootstrap_version
    download_bootstrap(get_bootstrap_version())

    # Ensure jquery is available
    from webapi.libs.deps.jquery import download_jquery, get_jquery_version
    download_jquery(get_jquery_version())

    # Ensure ace is available
    from webapi.libs.deps.ace import download_ace, get_ace_version
    download_ace(get_ace_version())

    # Ensure fontawesome is available
    from webapi.libs.deps.fontawesome import download_fontawesome, get_fontawesome_version
    download_fontawesome(get_fontawesome_version())

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
    from webapi.plugin import load_plugins, get_plugins, get_plugin_pages, get_active_plugins, _activate_plugin, \
        get_plugins_jinja, exec_post_actions
    load_plugins(webapi, config, logger)
    # Make sure the main components are always activated
    _activate_plugin('base', 'errors', 'user')

    # Load macros
    from webapi.macro import load_macros, get_macros, get_macros_jinja
    load_macros(config, logger)

    # Provide plugins with macros
    for plugin in get_plugins().values():
        add_macros = {'config': Config, 'logger': Logger}
        if hasattr(plugin, 'request_macros'):
            for macro in plugin.request_macros:
                if macro in get_macros():
                    add_macros[macro] = get_macros()[macro]
        plugin.macros = add_macros

    # Run post load actions
    exec_post_actions()

    # Make function callable from jinja templates
    expose_function_for_templates(len=len, enumerate=enumerate, str=str, int=int, list=list, dict=dict,
                                  get_plugin_pages=get_plugin_pages, get_plugins=get_plugins_jinja,
                                  get_active_plugins=get_active_plugins, get_macros=get_macros_jinja,
                                  get_bootstrap_version=get_bootstrap_version, get_jquery_version=get_jquery_version,
                                  get_ace_version=get_ace_version, get_fontawesome_version=get_fontawesome_version,
                                  camel_case=camel_case)

    # Create a basic redirect to the base plugin
    @webapi.route('/')
    @webapi.route('/dashboard')
    def index():
        """
        Redirect to base plugin.

        :return:
        """
        return redirect(url_for('base.dashboard'))

    # Allow access to files in media folder
    @webapi.route('/media/<filename>')
    def get_file(filename):
        """
        Open a media file from global media folder.

        :param filename: filename to load
        :return: file
        """
        return send_from_directory(config.get('webapi', 'media_path'), filename)

    @webapi.route('/thumbnail/<filename>')
    def get_thumbnail(filename):
        """
        Open a thumbnail file from global thumbnail folder.

        :param filename: filename to load
        :return: file
        """
        return send_from_directory(config.get('webapi', 'thumbnail_path'), filename)

    @webapi.route('/favicon.ico')
    def favicon():
        """
        Redirects the favicon url.

        :return: url for favicon
        """
        return redirect(url_for('static', filename='ico/visiontale16.ico'))

    return webapi


def expose_function_for_templates(**kwargs):
    """
    Make a passed function callable from jinja framework.

    :param kwargs: keyword=func pairs, will be callable by the given keyword
    :return:
    """
    jinja_env.globals.update(**kwargs)


















