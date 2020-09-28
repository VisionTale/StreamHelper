from flask import Flask
from webapi.libs.config import Config
from webapi.libs.logging import setup

config = Config()

template_folder = config.get('flask', 'template_path')
static_folder = config.get('flask', 'static_path')

webapi = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

webapi.config.from_mapping(config.flask_config())

logger = setup(webapi, config)

from webapi.modules import routes
