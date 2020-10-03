from os.path import isfile, join
from os import getenv, urandom
from configparser import ConfigParser
from pathlib import Path

HOME_DIR = str(Path.home())
CACHE_DIR = getenv('SH_CACHE_DIR') or join(HOME_DIR, '.cache', 'visiontale', 'streamhelper')
CONFIG_DIR = getenv('SH_CONFIG_DIR') or join(HOME_DIR, '.config', 'visiontale', 'streamhelper')
DATA_DIR = getenv('SH_DATA_DIR') or join(HOME_DIR, '.local', 'share', 'visiontale', 'streamhelper')


class Config:
    """Configuration handler for the base framework and all plugins."""

    def __init__(self):
        """
        Initialize the configuration object. If no configuration exists, the config is generated from scratch.

        Environment variables:
            - SH_CONFIG_DIR : Fallback directory for configuration files. Defaults to
                $HOME/.config/visiontale/streamhelper
            - SH_CONFIG_FP : Filepath to store the configuration. Defaults to $SH_CONFIG_DIR/config.ini

        To change individual config options, see Config::create_default_config.
        """
        self._config_fp = getenv('SH_CONFIG_FP') or join(CACHE_DIR, 'config.ini')
        if not isfile(self._config_fp):
            Config.create_default_config(self._config_fp)
        self._config = ConfigParser()
        self._config.read(self._config_fp)

    def get(self, app, key) -> str:
        """
        Get a configuration value for a plugin.
        :param app: the plugins internal name
        :param key: the key within the application
        :return: the value associated with the key
        """
        return self._config[app][key]

    def set(self, app, key, value):
        """
        Set a configuration value for a plugin.
        :param app: the plugins internal name
        :param key: the key within the application
        :param value: the value to set
        :return:
        """
        self._config[app][key] = value
        with open(self._config_fp, 'w') as f:
            self._config.write(f)

    def flask_config(self) -> dict:
        """
        Get the flask config with recognizable letter capitalization as dictionary.
        :return: dictionary containing all settings related to flask
        """
        d = dict(self._config['flask'])
        for key in list(d.keys()):
            d[key.upper()] = d[key]
        return d

    @staticmethod
    def create_default_config(fp):
        """
        Create the configuration file.

        Environment variables:
        - SH_CONFIG_DIR : Fallback directory for configuration files. Defaults to
                $HOME/.config/visiontale/streamhelper
        - SH_CACHE_DIR : Fallback directory for non permament files (e.g. logs). Defaults to
                $HOME/.cache/visiontale/streamhelper
        - SH_DATA_DIR : Fallback directory for configuration files. Defaults to
                $HOME/.local/share/visiontale/streamhelper
        - SECRET_KEY : Secret key for security of flask. Never publish your production key! Will be randomly generated
            otherwise
        - TEMPLATES_AUTO_RELOAD : Whether to reload templates on change. Defaults to true.
        - DATABASE_URL : Database uri to use by SQLAlchemy. Defaults to
            sqlite:///$SH_CONFIG_DIR/streamhelper.db
        - DATABASE_TRACK_MODIFICATIONS : Whether to track database modifications by Flask-SQLAlchemy. Defaults to false.
            Change only with caution, since this creates a huge overhead.
        - SH_TEMPLATE_PATH : Path to store templates. Defaults to $SH_DATA_DIR/templates.
        - SH_STATIC_PATH : Path to store static non-rendered files (e.g. css, js). Defaults to $SH_DATA_DIR/static.
        - SH_LOG_FP : Path to store the main log file. Defaults to $SH_DATA_DIR/streamhelper.log
        - SH_LOG_TYPES : Log types. Currently STREAM (output to console) and FILE (output to logfile) are supported.
            Set multiple types by comma or space separation. Defaults to 'STREAM, FILE'
        - SH_LOG_LEVEL : Log level. Supported are CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET. Defaults to DEBUG.

        :param fp: filepath to write the config to
        :return:
        """
        config = ConfigParser()
        config['flask'] = {}
        config['flask']['SECRET_KEY'] = getenv('SECRET_KEY') or urandom(24).hex()
        config['flask']['TEMPLATES_AUTO_RELOAD'] = getenv('TEMPLATES_AUTO_RELOAD') or "true"
        config['flask']['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URI') or 'sqlite:///' + join(CONFIG_DIR,
                                                                                                   'streamhelper.db')
        config['flask']['SQLALCHEMY_TRACK_MODIFICATIONS'] = getenv('DATABASE_TRACK_MODIFICATIONS') or 'false'
        config['flask']['template_path'] = getenv('SH_TEMPLATE_PATH') or join(DATA_DIR, 'templates')
        config['flask']['static_path'] = getenv('SH_STATIC_PATH') or join(DATA_DIR, 'static')
        config['webapi'] = {}
        config['webapi']['log_fp'] = getenv('SH_LOG_FP') or join(CACHE_DIR, 'streamhelper.log')
        config['webapi']['log_types'] = getenv('SH_LOG_TYPES') or 'STREAM, FILE'
        config['webapi']['log_level'] = getenv('SH_LOG_LEVEL') or 'DEBUG'

        with open(fp, 'w') as f:
            config.write(f)
