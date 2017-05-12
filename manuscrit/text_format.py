import re
from pprint import pformat


def add_indent(s, n):
    """indent every line of a string"""
    if not s:
        return s
    prefix = n * ' '
    return re.sub('^', prefix, s, flags=re.MULTILINE)


def autoformat(thing):
    """indent every line of a string

    auto formats:
        objects : string version
        dictionaries : pretty print
    """
    if isinstance(thing, basestring):
        return thing
    if isinstance(thing, (dict, list)):
        return pformat(thing)
    else:
        return str(thing)


def add_title(string, title):
    return spaced(make_title(title)) + string


def spaced(string):
    return '\n' + string + '\n\n'


def make_title(line, n=4, c='-'):
    """Make a title.
    ex:
    ----title----
    """

    return n * str(c) + str(line) + n * str(c)


def bar():
    """A simple bar separator"""
    return '-' * 50


def wrap_in_lines(content):
    """wrap between two bars"""
    return '\n\n'.join([bar(), content, bar()])


def log_section(line):
    """Log uppercase surrounded by newlines

    line : string to log as title
    ............log file............

    LINE PASSED AS PARAMETER

    ...................................
    """
    _log_line_spaced(line.upper())


def log_sep(title=''):
    """Log Separator. Log a big separator in the log file.

    Use it to mark something like entering a function
    ............log file............

    ====================TITLE====================

    ...................................

    """
    _log_line_spaced(_make_title(title.upper(), 20, c='='))
