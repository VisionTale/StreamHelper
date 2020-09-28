from .config import Config


def setup(webapi, config: Config):

    from flask.logging import default_handler

    webapi.logger.removeHandler(default_handler)

    from logging import getLogger, Formatter

    logger = getLogger('streamhelper')

    formatter = Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')

    log_types = config.get('webapi', 'log_types').upper().replace(',', ' ').replace('  ', ' ').split(' ')

    if 'STREAM' in log_types:

        from logging import StreamHandler

        stream_handler = StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if 'FILE' in log_types:

        from logging.handlers import RotatingFileHandler

        log_fp = config.get('webapi', 'log_fp')
        create_log_folder(log_fp)
        file_handler = RotatingFileHandler(filename=log_fp, encoding='utf-8', mode='w', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    log_level = config.get('webapi', 'log_level').upper()
    log_mapping = {'CRITICAL': 50, 'ERROR': 40, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10, 'NOTSET': 0, 'INVALID': 10}
    if log_level not in log_mapping:
        log_level = 'INVALID'
    logger.setLevel(log_mapping[log_level])

    if log_level == 'INVALID':
        logger.warning('Invalid log level set. Select from ' + ', '.join(list(log_mapping.keys())[:-1]))

    webapi.logger.addHandler(logger)

    return webapi.logger


def disassemble(webapi):

    handlers = webapi.logger.handlers.copy()
    for handler in handlers:
        handler.close()
        webapi.logger.removeHandler(handler)


def create_log_folder(log_fp):

    from os.path import dirname, isfile
    from os import mkdir
    from subprocess import run
    from getpass import getuser

    if not isfile(log_fp):
        try:
            mkdir(dirname(log_fp))
        except PermissionError:
            run('pkexec sh -c "mkdir -p %s && touch %s && chown -R %s %s"' % (dirname(log_fp), log_fp, getuser(),
                                                                              log_fp),
                shell=True, executable='/bin/bash', capture_output=True)


