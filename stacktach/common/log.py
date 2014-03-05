import logging


DEBUG = True
USE_STDERR = True


def setup_log():
    root_log = logging.getLogger('stacktach')

    if DEBUG:
        root_log.setLevel(logging.DEBUG)

    if USE_STDERR:
        err_handler = logging.StreamHandler()
        root_log.addHandler(err_handler)

    root_format = logging.Formatter('%(asctime)s [%(levelname)6s] '
                                    '%(name)s %(message)s')

    # add handler for root
    handler = logging.handlers.TimedRotatingFileHandler(
        'worker.log', when='h', interval=6, backupCount=4
    )
    root_log.addHandler(handler)

    # add format for root handlers
    for handler in root_log.handlers:
        handler.setFormatter(root_format)
