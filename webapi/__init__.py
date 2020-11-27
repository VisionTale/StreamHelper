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
bootstrap_version = config.get('webapi', 'bootstrap_version')
jquery_version = config.get('webapi', 'jquery_version')
ace_version = config.get('webapi', 'ace_version')

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

    # Ensure ace is available
    download_ace(static_folder, ace_version)

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
    expose_function_for_templates(len=len, enumerate=enumerate,
                                  get_plugin_pages=get_plugin_pages, get_plugins=get_plugins_jinja,
                                  get_active_plugins=get_active_plugins, get_macros=get_macros_jinja,
                                  get_bootstrap_version=get_bootstrap_version, get_jquery_version=get_jquery_version,
                                  get_ace_version=get_ace_version, camel_case=camel_case)

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


def download_bootstrap(static_dir: str, version: str, verbose: bool = True):
    """
    Downloads the bootstrap dist files.

    :param static_dir: global static dir
    :param version: bootstrap version
    :param verbose: whether to print information, defaults to true.
    """
    from os.path import isdir, join

    bootstrap_dir = join(static_dir, f'bootstrap-{version}-dist')
    if not isdir(bootstrap_dir):
        debug_print("Downloading bootstrap files..", verbose)
        url = f'https://github.com/twbs/bootstrap/releases/download/v{version}/bootstrap-{version}-dist.zip'
        debug_print(f'Download url: {url}', verbose)

        zip_file_fp = join(static_dir, 'bootstrap.zip')
        download_and_unzip_archive(url, zip_file_fp, verbose=verbose)

        debug_print("Done!", verbose)


def download_jquery(static_dir: str, version: str, verbose: bool = True):
    """
    Downloads the jquery javascript and map files.

    :param static_dir: global static dir
    :param version: jquery version
    :param verbose: whether to print information, defaults to true.
    """
    from os.path import isdir, isfile, join

    jquery_dir = join(static_dir, 'jquery')
    if not isdir(jquery_dir) or not isfile(join(jquery_dir, f'jquery-{version}.min.js')):
        debug_print("Downloading jquery files..", verbose)

        from os import mkdir
        mkdir(jquery_dir)

        js_url = f'https://code.jquery.com/jquery-{version}.min.js'
        map_url = f'https://code.jquery.com/jquery-{version}.min.map'

        debug_print(f'Download urls: {js_url} + {map_url}', verbose)

        from requests import get
        js_request = get(js_url)
        map_request = get(map_url)

        js_fp = join(jquery_dir, f'jquery-{version}.min.js')
        map_fp = join(jquery_dir, f'jquery-{version}.min.map')

        with open(js_fp, 'wb') as f:
            f.write(js_request.content)

        with open(map_fp, 'wb') as f:
            f.write(map_request.content)

        debug_print("Done!", verbose)


def download_ace(static_dir: str, version: str, verbose: bool = True):
    """
    Downloads the ace files.

    :param static_dir: global static dir
    :param version: ace version
    :param verbose: whether to print information, defaults to true.
    :exception OSError: os.remove, requests.get, open, TextIOWrapper.write, ZipFile, ZipFile.extractall
    """
    from os.path import isdir, join

    ace_dir = join(static_dir, f'ace-builds-{version}')
    if not isdir(ace_dir):
        debug_print("Downloading ace files..", verbose)
        url = f'https://github.com/ajaxorg/ace-builds/archive/v{version}.zip'
        debug_print(f'Download url: {url}', verbose)

        zip_file_fp = join(static_dir, f'v{version}.zip')
        download_and_unzip_archive(url, zip_file_fp, verbose=verbose)

        debug_print("Done!", verbose)


def download_and_unzip_archive(url: str, zip_file_fp: str, remove: bool = True, verbose: bool = True):
    """
    Downloads and unzips an archive.
    
    :param url: url to request
    :param zip_file_fp: filepath for zip
    :param remove: whether to remove the zip after unpacking, defaults to true. 
    :param verbose: whether to print information, defaults to true.
    :exception OSError: os.remove, requests.get, open, TextIOWrapper.write, ZipFile, ZipFile.extractall
    """
    from requests import get
    r = get(url)
    debug_print("Saving archive..", verbose)
    with open(zip_file_fp, 'wb') as f:
        f.write(r.content)
    debug_print("Extracting..", verbose)
    from zipfile import ZipFile
    with ZipFile(zip_file_fp, 'r') as zip_file:
        zip_file.extractall(static_dir)
    if remove:
        debug_print("Removing archive..", verbose)
        from os import remove
        remove(zip_file_fp)


def get_bootstrap_version():
    return bootstrap_version


def get_jquery_version():
    return jquery_version


def get_ace_version():
    return ace_version


def debug_print(message: str, verbose: bool):
    """
    Print if verbose is set to true.

    :param message: message to print
    :param verbose: whether to print
    :return:
    """
    if verbose:
        print(message)
