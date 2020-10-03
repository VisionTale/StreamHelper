from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from webapi.libs.config import Config
from webapi.libs.log import setup_webapi as setup

# Config loading
config = Config()
template_folder = config.get('flask', 'template_path')
static_folder = config.get('flask', 'static_path')

# Initialization
webapi = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
webapi.config.from_mapping(config.flask_config())

# Logging
logger = setup(webapi, config)

# Database
db = SQLAlchemy(webapi)
migrate = Migrate(webapi, db)

# Session handler
login = LoginManager(webapi)
login.login_view = 'login'
login.login_message = "Please log in to continue."

bootstrap = Bootstrap(webapi)

# Load modules
from webapi.modules import routes, models, errors
from webapi.modules.models import User


@webapi.shell_context_processor
def make_shell_context():
    # Selected packages that will be pre-imported if using 'flask shell'
    return {'db': db, 'User': User, 'models': models, 'routes': routes}
