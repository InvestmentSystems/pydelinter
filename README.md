[![Build Status](https://travis-ci.org/InvestmentSystems/pydelinter.svg?branch=master)](https://travis-ci.org/InvestmentSystems/pydelinter)
![PyPI version](https://badge.fury.io/py/pydelinter.svg)

# pydelinter

Pydelinter automatically generates unified-diffs of python source code that violate certain class of Pylint warnings.  You can run this tool on your source code, inspect the diffs and apply the diffs as patches.

## Installation

pip install pydelinter


## Usage

``` shell

$ delint -h
usage: delint [-h] [--msg_id MSG_ID] [--version] [-v] [-vv]
              file_path_or_folder

Command line tool for delinting certain pylint messages

positional arguments:
  file_path_or_folder  Path to a .py file or folder contain *.py files. This
                       relative path will be used to generate the unified diff
                       files.

optional arguments:
  -h, --help           show this help message and exit
  --msg_id MSG_ID      The pylint message that will be delinterd. Eg W0611
  --version            show program's version number and exit
  -v, --verbose        set loglevel to INFO
  -vv, --very-verbose  set loglevel to DEBUG

Examples:

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


```


## Status of pylint messages supported


| Message Id |  Message | Status  |
|------------|:--------:|:-------:|
| W0611 | unused-imports | :heavy_check_mark: |
| W0404 | reimported |:heavy_check_mark:  |
|W0108|unnecessary-lambda||
|W0107|unnecessary-pass||
|E1111|assignment-from-no-return||
|E0701|bad-except-order||
|E0711|not-implemented-raised||
|C0411|wrong-import-order||
|C0412|ungrouped-imports||
|C0410|multiple-imports||
|W0611|unused-variable||
|W0613|unused-argument||
|W0612|unused-wildcard-import||
|W0602|global-variable-not-assigned||
|R0102|simplifiable-if-statement||
|C0326|bad-whitespace||
|C0304|missing-final-newline||
|C0327|multiple-statements||
|C0305|trailing-newline||
|C0303|trailing-whitespace||
|C0325|superfluous-parens||

(more items will be added to this list after carefully reviewing all message groups supported by Pylint)

## Objectives of this tool

1. The tool will only support addressing one pytlint warning/error at a time. This is provided through the `msg_id` argument.
2. Any warnings that might need complex formatting will not be supported. We leave that to more sophisticated tools like ```Black```.

## Caveats

1. When dropping statements, preceeding newlines/comments attached to the statement will be removed.
2. Given how pylint reports warnings, the tool might have to be run on the same code base more than once, after applying the previous patch. For example, an (reimported) error on a particular statement, precededs an (unused-import) error. Therefore, re-running the program will force this statement to be tagged by pylint as an unused-import.
3. The diffs produces by this tool is only as good as how pylint reports warning/errors and howthe LibCST yields the CST. Therefore, manual review of the patches is always a good idea (along with a good test suite).

## Acknowledgements

This project has been set up using PyScaffold 3.2.3. For details and usage
information on PyScaffold see https://pyscaffold.org/.


This library primarily depends upon the LibCST [https://github.com/Instagram/LibCST] library.
