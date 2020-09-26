from os.path import isfile
from os import getenv, urandom
from configparser import ConfigParser


class Config:
    def __init__(self):
        self._config_fp = getenv('WEBAPI_CONFIG_FP') or 'config.ini'
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
        config = ConfigParser()
        config['webapi'] = {}
        config['webapi']['SECRET_KEY'] = getenv('SECRET_KEY') or urandom(24).hex()
        with open(fp, 'w') as f:
            config.write(f)
