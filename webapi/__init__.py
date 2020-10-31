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
bootstrap_version = config.get('webapi', 'bootstrap_version')
jquery_version = config.get('webapi', 'jquery_version')

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

    # Ensure bootstrap is available
    download_bootstrap(static_folder, bootstrap_version)

    # Ensure jquery is available
    download_jquery(static_folder, jquery_version)

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
        get_plugins_jinja
    load_plugins(webapi, config, logger)
    # Make sure the main components are always activated
    _activate_plugin('base', 'errors', 'user')

    # Load macros
    from webapi.macro import load_macros, get_macros, get_macros_jinja
    load_macros(webapi, config, logger)

    # Provide plugins with macros
    for plugin in get_plugins().values():
        add_macros = {'config': Config, 'logger': Logger}
        if hasattr(plugin, 'request_macros'):
            for macro in plugin.request_macros:
                if macro in get_macros():
                    add_macros[macro] = get_macros()[macro]
        plugin.macros = add_macros

    # Make function callable from jinja templates
    expose_function_for_templates(get_plugin_pages=get_plugin_pages, get_plugins=get_plugins_jinja,
                                  get_active_plugins=get_active_plugins, get_macros=get_macros_jinja,
                                  get_bootstrap_version=get_bootstrap_version, get_jquery_version=get_jquery_version)

    # Run post load actions
    for plugin in get_plugins().values():
        if hasattr(plugin, 'post_loading_actions'):
            logger.debug(f'Running post loading actions for {plugin.name}')
            plugin.post_loading_actions()

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
    """
    Make a passed function callable from jinja framework.
    :param kwargs: keyword=func pairs, will be callable by the given keyword
    :return:
    """
    jinja_env.globals.update(**kwargs)


def download_bootstrap(static_dir, version):
    """
    Downloads the bootstrap dist files.
    :param static_dir: global static dir
    :param version: bootstrap version
    :return:
    """
    from os.path import isdir, join

    bootstrap_dir = join(static_dir, f'bootstrap-{version}-dist')
    if not isdir(bootstrap_dir):
        print("Downloading bootstrap files..")
        import requests

        url = f'https://github.com/twbs/bootstrap/releases/download/v{version}/bootstrap-{version}-dist.zip'
        zip_file_fp = join(static_dir, 'bootstrap.zip')
        r = requests.get(url)
        with open(zip_file_fp, 'wb') as f:
            f.write(r.content)
        from zipfile import ZipFile
        print("Unzipping..")
        with ZipFile(zip_file_fp, 'r') as zip_file:
            zip_file.extractall(static_dir)
        from os import remove
        remove(zip_file_fp)
        print("Done!")


def download_jquery(static_dir, version):
    """
    Downloads the jquery javascript and map file.
    :param static_dir: global static dir
    :param version: jquery version
    :return:
    """
    from os.path import isdir, isfile, join

    jquery_dir = join(static_dir, 'jquery')
    if not isdir(jquery_dir) or not isfile(join(jquery_dir, f'jquery-{version}.min.js')):
        print("Downloading jquery files..")
        import requests

        from os import mkdir
        mkdir(jquery_dir)

        js_url = f'https://code.jquery.com/jquery-{version}.min.js'
        map_url = f'https://code.jquery.com/jquery-{version}.min.map'

        js_request = requests.get(js_url)
        map_request = requests.get(map_url)

        js_fp = join(jquery_dir, f'jquery-{version}.min.js')
        map_fp = join(jquery_dir, f'jquery-{version}.min.map')

        with open(js_fp, 'wb') as f:
            f.write(js_request.content)

        with open(map_fp, 'wb') as f:
            f.write(map_request.content)


def get_bootstrap_version():
    return bootstrap_version


def get_jquery_version():
    return jquery_version
