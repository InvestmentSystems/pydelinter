# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
[options.entry_points] section in setup.cfg:

    console_scripts =
         fibonacci = delinter.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""

import os
import re
import sys
import typing as tp
import difflib
import logging
import argparse
import collections
import dataclasses
from typing import Set
from typing import Dict
from typing import Union
from pathlib import Path
from collections import defaultdict

import libcst as cst
from pylint import epylint as lint

from delinter import __version__
from delinter.imports import UnusedImportsDelinter
from delinter.imports import RemoveUnusedImportTransformer
from delinter.imports import ReimportDelinter
from delinter.imports import ReimportTransformer


__author__ = "grdvnl"
__copyright__ = "grdvnl"
__license__ = "mit"

_logger = logging.getLogger(__name__)


SUPPORTED_LINTER_MAP = {
        UnusedImportsDelinter.CODE: (UnusedImportsDelinter, RemoveUnusedImportTransformer),
        ReimportDelinter.CODE: (ReimportDelinter, ReimportTransformer)
        }

pylint_str = str # output formatted string of Pylint output

class Delinter:

    pattern = re.compile(
            r'(?P<file_path>.*.py):(?P<line_no>.*):\[(?P<code>.*)\(.*\),(?P<obj>.*)\](?P<warning>.*)'
            )

    @classmethod
    def parse_linter_warnings(cls, warnings: tp.Iterable[pylint_str], msg_id):

        if msg_id not in SUPPORTED_LINTER_MAP:
            raise ValueError(f'{msg_id} not currently supported for delinting.')
        parsed_warnings = []
        for warning in warnings:
            m = re.match(cls.pattern, warning)
            if not m:
                raise ValueError(f'Unknown format {warning}')
            file_path = m.group('file_path')
            line_no = m.group('line_no')
            line_no = int(m.group('line_no'))
            code = m.group('code')
            warning_text = m.group('warning')

            if code != msg_id:
                continue
            if code not in SUPPORTED_LINTER_MAP:
                continue
            class_ = SUPPORTED_LINTER_MAP[code][0]
            parsed_warning = class_.parse_linter_warning(
                    (file_path, line_no, warning_text))
            parsed_warnings.append(parsed_warning)
        return parsed_warnings

def get_arg_parser():
    '''
    Return the arg parse for the delinter.
    '''
    parser = argparse.ArgumentParser(
            description='Command line tool for delinting certain pylint messages',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog='''Examples:

            Running the below examples will generate an unified-diff file that can be used as a patch to apply the changes to git or Mercurial.
            delinter/main.py --msg W0611 foo/core.py

            To process multiple python files, provide a folder
            delinter/main.py --msg W0611 foo/

            Running, this command on the test file available with this repository:
            delinter/main.py --msg W0611 delinter/test/input


            --- a/delinter/test/input/test_unused_imports.py
            +++ b/delinter/test/input/test_unused_imports.py
            @@ -1,12 +1,7 @@
            -import unitest.mock.patch, unittest.mock.patch as p1
             import unitest.mock.patch, unittest.mock.patch as p2
            -import unittest as t, unittest as t2
            +import unittest as t2
             import unitest.mock.patch as p
            -import os
            -import pandas as pd, numpy as np
            -from collections.abc import defaultdict, OrderedDict
            -from itertools import filterfalse as _filterfalse
            -from collections.abc import x, y
            +from collections.abc import y
             from collections import *

             p2.mock() # use p2

            ''')
    parser.add_argument(
            '--msg_id',
            type=str,
            help=("The pylint message that will be delinterd. Eg W0611"))

    parser.add_argument('file_path_or_folder',
            type=str,
            help=(
            "Path to a .py file or folder contain *.py files. "
            "This relative path will be used to generate the unified diff files.")
            )

    parser.add_argument(
        "--version",
        action="version",
        version="pydelinter {ver}".format(ver=__version__))

    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO)
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG)
    return parser

def _run_delinter(options):
    '''
    Run the delinter and produce the diff.
    '''
    root_file_path = options.file_path_or_folder
    # TODO: Handle Windows paths
    if Path(root_file_path).is_absolute():
        msg_template = r'{abspath}:{line}:[{msg_id}({symbol}),{obj}]{msg}'
        sep = ''
    else:
        msg_template = r'{path}:{line}:[{msg_id}({symbol}),{obj}]{msg}'
        sep = '/'

    pylint_command = f"{root_file_path} --enable=W --disable=C,R,E,F --msg-template={msg_template} --score=n"

    out, _ = lint.py_run(pylint_command, return_std=True)
    orig_result = "".join(out.readlines()).split('\n')
    result = [r.strip() for r in orig_result if r.strip() and not r.strip().
            startswith('************* Module ')]
    parsed_warnings = Delinter.parse_linter_warnings(result, options.msg_id)
    if os.path.isdir(root_file_path):
        files = list(Path(root_file_path).glob('**/*.py'))
    else:
        files = [root_file_path]

    for file_path in files:
        with open(file_path) as f:
            source_code = "".join(f.readlines())
            if not source_code:
                continue
            source_tree = cst.parse_module(source_code)
            wrapper = cst.MetadataWrapper(source_tree)
            local_warnings = [p for p in parsed_warnings if p.file_path == str(file_path)]
            fixed_module = wrapper.visit(
                    SUPPORTED_LINTER_MAP[options.msg_id][1](local_warnings))
            a_file_path = f'a{sep}{file_path}'
            b_file_path = f'b{sep}{file_path}'
            result = "".join(difflib.unified_diff(
                    source_code.splitlines(1),
                    fixed_module.code.splitlines(1),
                    fromfile=a_file_path,
                    tofile=b_file_path
                    ))
            if result:
                print(result)



def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args=None):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = get_arg_parser().parse_args(args)
    #setup_logging(args.loglevel)
    _logger.debug('Starting the pydelint process...')
    _run_delinter(args)
    _logger.debug('pydeling complete')


def run():
    """Entry point for console_scripts
    """
    main()


if __name__ == "__main__":
    run()
