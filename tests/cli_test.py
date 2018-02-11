import ConfigParser
import logging
import sys

import pytest

from cli import get_logger, parse_config

def test_get_logger():
    l = get_logger()
    assert isinstance(l, logging.Logger)
    handlerClasses = []
    for handler in l.handlers:
        handlerClasses.append(handler.__class__)
    assert logging.StreamHandler in handlerClasses
    assert l.level == logging.INFO

def test_get_logger_debug(monkeypatch):
    testargs = ["appu", "-debug"]
    monkeypatch.setattr(sys, 'argv', testargs)
    l = get_logger()
    assert l.level == logging.DEBUG

class MockRawConfigParser(object):
    _params = {
        'file-config': [
            ('podcast_file', 'files/original_record.mp3'),
            ('song_file', 'files/song.mp3'),
            ('cover_file', 'files/logo.png'),
            ('final_file', 'podcast/episode.mp3'),
        ],
        'tag-config': [
            ('title', 'Episode title'),
            ('artist', 'Author'),
            ('album', 'Author\'s podcast'),
            ('track', 1),
            ('year', 2018),
            ('comment', 'Notes about this episode'),
        ],
    }

    def sections(self):
        return self._params.keys()

    def items(self, section):
        return self._params[section]

    def read(self, config_file):
        pass

def test_parse_config(monkeypatch):
    monkeypatch.setattr(ConfigParser, "RawConfigParser", MockRawConfigParser)
    cfg = parse_config()
    assert isinstance(cfg, dict)
