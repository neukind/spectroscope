import logging


def log():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger("spectroscope")
