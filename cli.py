import configparser
import logging
import sys


def get_logger():
    """Debug mode with param -debug"""
    # Using logger instead of print
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.WARNING)
    if "-debug" in sys.argv:
        logger.setLevel(logging.DEBUG)
    return logger


def parse_config():
    """Read config file and loads parameters as variables"""
    configParser = configparser.RawConfigParser()
    configFilePath = r'./config.cfg'
    configParser.read(configFilePath)
    cfg = {}
    for section in configParser.sections():
        for name, value in configParser.items(section):
            cfg[name] = value
    return cfg
