"""
Library to load and handle config values.
"""
from os.path import isfile, join, dirname
from os import getenv, urandom
from configparser import ConfigParser
from pathlib import Path

HOME_DIR = str(Path.home())
CACHE_DIR = getenv('SH_CACHE_DIR') or join(HOME_DIR, '.cache', 'streamhelper')
CONFIG_DIR = getenv('SH_CONFIG_DIR') or join(HOME_DIR, '.config', 'streamhelper')
DATA_DIR = getenv('SH_DATA_DIR') or join(HOME_DIR, '.local', 'share', 'streamhelper')


class Config:
    """Configuration handler for the base framework and all plugins."""

    def __init__(self):
        """
        Initialize the configuration object. If no configuration exists, the config is generated from scratch.

        Environment variables:
            - SH_CONFIG_DIR : Fallback directory for configuration files. Defaults to
                $HOME/.config/streamhelper
            - SH_CONFIG_FP : Filepath to store the configuration. Defaults to $SH_CONFIG_DIR/config.ini

        To change individual config options, see Config::update_config.
        """
        self._config_fp = getenv('SH_CONFIG_FP') or join(CONFIG_DIR, 'config.ini')
        self._config = ConfigParser()
        from .basics.file import create_underlying_folder
        create_underlying_folder(self._config_fp)
        if isfile(self._config_fp):
            self._config.read(self._config_fp)
        self.update_config()

    def get(self, app: str, key: str) -> str:
        """
        Get a configuration value for a plugin.

        :param app: the plugins internal name
        :param key: the key within the application
        :return: the value associated with the key (or an empty string if non existent)
        """
        try:
            return self._config[app][key]
        except KeyError:
            return ""

    def set(self, app: str, key: str, value: str):
        """
        Set a configuration value for a plugin.

        :param app: the plugins internal name
        :param key: the key within the application
        :param value: the value to set
        """
        if app not in self._config.sections():
            self.create_section(app)
        self._config[app][key] = value
        with open(self._config_fp, 'w') as f:
            self._config.write(f)

    def set_if_none(self, app: str, key: str, value: str):
        """
        Set a configuration value for a plugin but only if the value does not exist.

        :param app: the plugins internal name
        :param key: the key within the application
        :param value: the value to set
        """
        if app not in self._config.sections():
            self.create_section(app)
        if key in self._config[app].keys():
            return
        self._config[app][key] = value
        with open(self._config_fp, 'w') as f:
            self._config.write(f)

    def get_or_set(self, app: str, key: str, default_value: str) -> str:
        """
        Reads the configuration value for a plugin, if it does not exist, it set's it to the default value.

        :param app: the plugins internal name
        :param key: the key within the application
        :param default_value: the value to set to if the key does not exist
        :return: the value of the key
        """
        if not self.has(app, key):
            self.set(app, key, default_value)
        return self.get(app, key)

    def has(self, app: str, key: str) -> bool:
        """
        Check if a configuration value for a plugin exists.

        :param app: the plugins internal name
        :param key: the key within the application
        :return: Whether the key exists
        """
        if app not in self._config.sections():
            return False
        if key not in self._config[app].keys():
            return False
        return True

    def create_section(self, app: str):
        """
        Create a section for the plugin with the given name if not already existent.

        :param app: the plugins internal name
        """
        if app not in self._config.sections():
            self._config.add_section(app)

    def flask_config(self) -> dict:
        """
        Get the flask config with recognizable letter capitalization as dictionary.

        :return: dictionary containing all settings related to flask
        """
        d = dict(self._config['flask'])
        for key in list(d.keys()):
            d[key.upper()] = d[key]
        return d

    def update_config(self):
        """
        Updates the current config, adding all missing default values.

        Environment variables:
        - SH_CONFIG_DIR : Fallback directory for configuration files. Defaults to
                $HOME/.config/streamhelper
        - SH_CACHE_DIR : Fallback directory for non permanent files (e.g. logs). Defaults to
                $HOME/.cache/streamhelper
        - SH_DATA_DIR : Fallback directory for additional files (templates, plugins, etc.). Defaults to
                $HOME/.local/share/streamhelper
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
        - SH_PLUGIN_PATH : Directory containing all plugins as folders. Defaults to $SH_DATA_DIR/blueprints.
        - SH_MACRO_PATH : Directory containing all macros as folders. Defaults to $SH_DATA_DIR/macros.
        - SH_MEDIA_PATH : Directory containing all media files. Defaults to $SH_DATA_DIR/media.
        - SH_THUMBNAIL_PATH : Directory containing all thumbnails. Defaults to $SH_CACHE_DIR/thumbnails.
        - SH_BOOTSTRAP_VERSION : Version of bootstrap to use. Defaults to 4.5.3
        - SH_JQUERY_VERSION : Version of jquery to use. Defaults to 3.5.
        - SH_ACE_VERSION : Version of ace to use. Defaults to 1.4.12.
        - SH_FONTAWESOME_VERSION : Version of fontawesome to use. Defaults to 5.15.1.
        """

        from os.path import isdir, dirname
        if not isdir(dirname(self._config_fp)):
            from .basics.file import create_folder
            create_folder(dirname(self._config_fp))

        self.set_if_none('flask', 'SECRET_KEY', getenv('SECRET_KEY') or urandom(24).hex())
        self.set_if_none('flask', 'TEMPLATES_AUTO_RELOAD', getenv('TEMPLATES_AUTO_RELOAD') or "true")
        self.set_if_none('flask', 'SQLALCHEMY_DATABASE_URI', getenv('DATABASE_URI') or 'sqlite:///' +
                         join(CONFIG_DIR, 'streamhelper.db'))
        self.set_if_none('flask', 'SQLALCHEMY_TRACK_MODIFICATIONS', getenv('DATABASE_TRACK_MODIFICATIONS') or 'false')
        self.set_if_none('flask', 'template_path', getenv('SH_TEMPLATE_PATH') or join(DATA_DIR, 'templates'))
        self.set_if_none('flask', 'static_path', getenv('SH_STATIC_PATH') or join(DATA_DIR, 'static'))

        self.set_if_none('webapi', 'log_fp', getenv('SH_LOG_FP') or join(CACHE_DIR, 'streamhelper.log'))
        self.set_if_none('webapi', 'log_types', getenv('SH_LOG_TYPES') or 'STREAM, FILE')
        self.set_if_none('webapi', 'log_level', getenv('SH_LOG_LEVEL') or 'DEBUG')
        self.set_if_none('webapi', 'plugin_path', getenv('SH_PLUGIN_PATH') or join(DATA_DIR, 'blueprints'))
        self.set_if_none('webapi', 'macro_path', getenv('SH_MACRO_PATH') or join(DATA_DIR, 'macros'))
        self.set_if_none('webapi', 'media_path', getenv('SH_MEDIA_PATH') or join(DATA_DIR, 'media'))
        self.set_if_none('webapi', 'thumbnail_path', getenv('SH_THUMBNAIL_PATH') or join(CACHE_DIR, 'thumbnails'))
        self.set_if_none('webapi', 'bootstrap_version', getenv('SH_BOOTSTRAP_VERSION') or '4.5.3')
        self.set_if_none('webapi', 'jquery_version', getenv('SH_JQUERY_VERSION') or '3.5.1')
        self.set_if_none('webapi', 'ace_version', getenv('SH_ACE_VERSION') or '1.4.12')
        self.set_if_none('webapi', 'fontawesome_version', getenv('SH_FONTAWESOME_VERSION') or '5.15.1')
        self.set('webapi', 'data_dir', DATA_DIR)
        self.set('webapi', 'config_dir', CONFIG_DIR)
        self.set('webapi', 'cache_dir', CACHE_DIR)

        from .basics.file import create_folder
        create_folder(CACHE_DIR)
        create_folder(CONFIG_DIR)
        create_folder(DATA_DIR)
        create_folder(self.get('flask', 'template_path'))
        create_folder(self.get('flask', 'static_path'))
        create_folder(dirname(self.get('flask', 'sqlalchemy_database_uri').split('///')[1]))
        create_folder(dirname(self.get('webapi', 'log_fp')))
        create_folder(self.get('webapi', 'plugin_path'))
        create_folder(self.get('webapi', 'macro_path'))
        create_folder(self.get('webapi', 'media_path'))
        create_folder(self.get('webapi', 'thumbnail_path'))


if __name__ == '__main__':
    Config()
