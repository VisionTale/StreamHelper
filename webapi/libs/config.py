from os.path import isfile, join
from os import getenv, urandom
from configparser import ConfigParser
from pathlib import Path


class Config:

    def __init__(self):
        self._config_fp = getenv('SH_CONFIG_FP') or 'config.ini'
        if not isfile('config.ini'):
            Config.create_default_config(self._config_fp)
        self._config = ConfigParser()
        self._config.read('config.ini')

    def get(self, app, key):
        return self._config[app][key]

    def config(self) -> ConfigParser:
        return self._config

    @staticmethod
    def create_default_config(fp):
        home_path = str(Path.home())
        cache_path = join(home_path, '.cache', 'visiontale')
        data_path = join(home_path, '.local', 'share', 'visiontale', 'streamhelper')
        config = ConfigParser()
        config['webapi'] = {}
        config['webapi']['SECRET_KEY'] = getenv('SECRET_KEY') or urandom(24).hex()
        config['webapi']['TEMPLATES_AUTO_RELOAD'] = getenv('TEMPLATES_AUTO_RELOAD') or "true"
        config['webapi']['log_fp'] = getenv('SH_LOG_FP') or join(cache_path, 'streamhelper.log')
        config['webapi']['log_types'] = getenv('SH_LOG_TYPES') or 'STREAM, FILE'
        config['webapi']['log_level'] = getenv('SH_LOG_LEVEL') or 'DEBUG'
        config['webapi']['template_path'] = getenv('SH_TEMPLATE_PATH') or join(data_path, 'templates')
        config['webapi']['static_path'] = getenv('SH_STATIC_PATH') or join(data_path, 'static')

        with open(fp, 'w') as f:
            config.write(f)
