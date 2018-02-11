import logging
import sys

import pytest

from cli import get_logger

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
