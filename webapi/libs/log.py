"""
Functions to create and delete loggers as well as auxiliary functions.
"""

from logging import Logger
from .config import Config
from .system import create_folder


def setup(logger: Logger, config: Config):
    """
    Configure a passed logger using standardized parameters from configuration.
    :param logger: logger to manipulate
    :param config: configuration object
    :return:
    """

    # Set formatting
    from logging import Formatter
    formatter = Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')

    # Get log types and initialize the associated log handlers
    log_types = config.get('webapi', 'log_types').upper().replace(',', ' ').replace('  ', ' ').split(' ')

    if 'STREAM' in log_types:
        from logging import StreamHandler
        stream_handler = StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if 'FILE' in log_types:
        from logging.handlers import RotatingFileHandler
        from os.path import dirname
        log_fp = config.get('webapi', 'log_fp')
        create_folder(dirname(log_fp))
        file_handler = RotatingFileHandler(filename=log_fp, encoding='utf-8', mode='w', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Set log level
    log_level = config.get('webapi', 'log_level').upper()
    log_mapping = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10, 'NOTSET': 0, 'INVALID': 10}
    if log_level not in log_mapping:
        log_level = 'INVALID'
    logger.setLevel(log_mapping[log_level])

    if log_level == 'INVALID':
        logger.warning('Invalid log level set. Select from ' + ', '.join(list(log_mapping.keys())[:-1]))


def setup_webapi(webapi, config: Config):
    """
    Create a custom logger and replace the default flask logger from the main application. Do not use for plugin
    specific loggers.
    :param webapi: main application object to manipulate it's logger
    :param config: configuration object
    :return:
    """

    # Save old handlers
    handlers = webapi.logger.handlers.copy()

    setup(webapi.logger, config)

    # Remove old handlers
    for handler in handlers:
        webapi.logger.removeHandler(handler)

    # Return logger (not necessary, but helpful for further use)
    return webapi.logger


def disassemble(webapi):
    """
    Close all logging handlers on main application.
    :param webapi: main application object
    :return:
    """

    # Remove all handlers
    handlers = webapi.logger.handlers.copy()
    for handler in handlers:
        handler.close()
        webapi.logger.removeHandler(handler)


def create(name: str, config: Config) -> Logger:
    """
    Creates a new pre-configured logger with the given name.
    :param name: name of the new logger
    :param config: configuration object
    :return: logger
   """

    # Create logger
    from logging import getLogger
    logger = getLogger(name)

    # Configure logger
    setup(logger, config)

    return logger
