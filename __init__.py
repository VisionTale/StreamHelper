from flask import Flask
from libs.config import Config

config = Config()

webapi = Flask(__name__)

webapi.config.from_object(config.config())
