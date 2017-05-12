from manuscrit import Logger
from textwrap import dedent
from pathlib2 import Path
import pytest
import re

# ---------------------config---------------------

test_log_file = Path('/tmp/log/test_log_file')


# ---------------------tools---------------------


def content(file):
    return open(str(file)).read()


def text_in_file(text, file):
    return dedent(text) in content(file)


def file_empty(file):
    """ensure file doesn't contain any printable character"""
    return not re.search('.', content(file))

# ---------------------fixture---------------------


@pytest.fixture
def log():
    return Logger(test_log_file)


# ---------------------non crash tests---------------------

def test_make_logger(log):
    assert test_log_file.is_file()


def test_log_this_empty(log):
    log.this()
    assert file_empty(test_log_file)


def test_log_this(log):
    text = 'a test log'
    log.this(text)
    assert text_in_file(text, test_log_file)


def test_indent(log):
    text = 'a test log'
    log.this(text)
    log.raise_indent()
    log.this(text)
    log.lower_indent()
    log.this(text)
    log.lower_indent()  # should have no effect
    log.this(text)
    expected = """\
                    a test log

                            a test log

                    a test log
                    
                    a test log
                    """
    assert text_in_file(expected, test_log_file)


def test_log_this_title(log):
    log.this('a test log', 'the title')
    expected = """\
                    ----the title----

                    a test log
                    """
    assert text_in_file(expected, test_log_file)


# -----------------------------------------------

"""TODO

test dir creation
test no file specified
test env var missing
make fixture for test dir and file


"""
