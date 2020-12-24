import logging


def log():
    logging.basicConfig(level=logging.DEBUG)
    return logging.getLogger("spectroscope")
