# -*- coding: utf-8 -*-
"""Collection of debug log utils

0) The location of this module should be available to import by adding it to the $PYTHONPATH

1) The location of the log file can be set with the PYTHON_SIMPLE_FILE_LOGGER environement variable.

    export PYTHON_SIMPLE_FILE_LOGGER=/path/to/log/file

2) Use log function in python code

from manuscrit import Logger

log = Logger()
log = Logger(<specified file>)

log('something')

3) Follow the log file in a terminal:

tail -f "$PYTHON_MANUSCRIT_DEFAULT_FILE"
"""


import attr
import inspect
import json
import logging
import os
import re

from . import text_format
from . import type_format
from os.path import abspath
from os.path import expanduser
from pathlib2 import Path
from sys import exit

# ---------------------SETTINGS---------------------

INDENT_STEP = 8

# ----| logging file
default_logging_file = os.environ.get(
    'PYTHON_MANUSCRIT_DEFAULT_FILE')

# ---------------------UTILS---------------------


# -----------------------------------------------

class StandardLibraryFileWriter():
    """Write to a file using standard logging library
    """

    def __init__(self, file_path):
        self.logger = logging.getLogger(file_path)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.FileHandler(str(file_path)))
        self.logger.propagate = False  # this logger is independant of the application

    def write(self, thing):
        self.logger.info(thing)


@attr.s
class SimpleFileWriter(object):
    """Write to a file
    """
    file_path = attr.ib()

    def write(self, thing):
        if not thing:
            return
        with open(self.file_path, 'a') as file:
            file.write(thing)
            file.write('\n')


class Logger:

    def __init__(self, file=default_logging_file):
        assert file, "file is not specified"
        path_object = Path(file).expanduser().resolve()
        self.logging_file = str(path_object)
        path_object.parent.mkdir(parents=True, exist_ok=True)
        self.reset_file()
        self.pad_file()
        # internal writer
        # self.logger = StandardLibraryFileWriter(logging_file)
        self.logger = SimpleFileWriter(self.logging_file)

        self.indent_level = 0
        self.indent_step = INDENT_STEP

        self(title='[ {} ]'.format(self.logging_file))

    def reset_file(self):
        """truncate
        """
        with open(self.logging_file, 'w') as f:
            pass

    def pad_file(self, n=100):
        """Write newlines

        Simulate a screen clear when following the log file with tail
        """
        with open(self.logging_file, 'a') as f:
            f.write('\n' * n)

    # ---------------------prints---------------------

    def __call__(self, thing=None, title=None, **kwargs):
        """Simplest write to the logging file

        auto formats:
            objects : string version
            dictionaries : pretty print

        Follow the current indent level of the module.
        This function is a base for all the other log functions"""

        if thing:
            string = text_format.autoformat(thing)
        else:
            string = ''
        if title:
            string = text_format.add_title(string, title)
        string = text_format.add_indent(string, self.indent_level)
        string += '\n'
        self.logger.write(string)

    def json(self, json_string, *args, **kwargs):
        """Log JSON string"""
        try:
            string = json.loads(json_string)
        except (ValueError, TypeError):
            string = '!! imput is not a valid json string !!'
        self(string, *args, **kwargs)

    def http(self, r, *args, **kwargs):
        """Log a request response from `request` package."""

        string = type_format.format_response(r, *args, **kwargs)
        self(string)

    def object(self, o, *args, **kwargs):
        """Log Object. Logs an object class, attributes names and classes, and methods.

        Like a supercharched dir() nicely printed.
        Show the object type, it's attributes and their respective types and list all it's callable separately"""
        string = type_format.format_object(o, **kwargs)
        self(string, *args, **kwargs)

    def function(self):
        """Log Function.

        Log the name  of the current function, it's file and line number, caller function and the local variables.
        Useful to visualize code paths, and function inputs. Plant this log at the beginning of a function you
        want to monitor

        ex output:

        --------------------------------------------------
        ------some_function() in test.py------
        (test.py:12)
        called by <module>() in other_file.py  (other_file.py:15)

            :arguments:

        {'kwargs': {'dolphin': 'flipper', 'fin_size': 30}}
        --------------------------------------------------
        """

        content = type_format.log_state(1)
        self(text_format.wrap_in_lines(content))

    def log_me(meo, title=None):
        """Log Mongoengine. Log a mongoengine object"""

        if title:
            _log_line_spaced(_make_title(title, 4))
        log_s(json.loads(meo.to_json()))

    # ---------------------settings---------------------

    def raise_indent(self):
        """raise all logs of one indent level"""
        self.indent_level += self.indent_step

    def lower_indent(self):
        """lower all logs of one indent level"""
        self.indent_level = max(0, self.indent_level - self.indent_step)

# ---------------------format---------------------


# ---------------------FORMAT INTERNALS---------------------
