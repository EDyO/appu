import ConfigParser
import logging
import sys

def parse_args():
    """Debug mode with param -debug"""
    if "-debug" in sys.argv :
        l.setLevel(logging.DEBUG)

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
