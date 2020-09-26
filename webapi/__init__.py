from flask import Flask
from webapi.libs.config import Config
from webapi.libs.logging import setup

config = Config()

template_folder = config.get('webapi', 'template_path')
static_folder = config.get('webapi', 'static_path')

webapi = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

webapi.config.from_object(config.config())

setup(webapi, config)

from webapi.modules import routes
