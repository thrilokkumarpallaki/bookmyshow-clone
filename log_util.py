import logging
import sys

logging.basicConfig(filename=r'/var/log/bookmyshow.log', filemode='a')


def get_logger(name, level=logging.ERROR):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
