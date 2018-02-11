import ConfigParser
import logging
import sys

def get_logger():
    """Debug mode with param -debug"""
    # Using logger instead of print
    l = logging.getLogger()
    l.addHandler(logging.StreamHandler())
    l.setLevel(logging.INFO)
    if "-debug" in sys.argv :
        l.setLevel(logging.DEBUG)
    return l

def parse_config():
    """Read config file and loads parameters as variables"""
    configParser = ConfigParser.RawConfigParser()
    configFilePath = r'./config.cfg'
    configParser.read(configFilePath)
    cfg = {}
    for section in configParser.sections():
        for name, value in configParser.items(section):
            cfg[name] = value
    return cfg
