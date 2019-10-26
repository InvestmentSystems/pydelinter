import unittest

import libcst as cst
import delinter.imports as imports
from delinter.main import Delinter

unused_import_warnings = '''
test_unused_imports.py:1:[W0611(unused-import),]Unused import unitest.mock.patch
test_unused_imports.py:1:[W0611(unused-import),]Unused unittest.mock.patch imported as p1
test_unused_imports.py:5:[W0611(unused-import),]Unused import os
test_unused_imports.py:6:[W0611(unused-import),]Unused pandas imported as pd
test_unused_imports.py:6:[W0611(unused-import),]Unused numpy imported as np
test_unused_imports.py:7:[W0611(unused-import),]Unused defaultdict imported from collections.abc
test_unused_imports.py:7:[W0611(unused-import),]Unused OrderedDict imported from collections.abc
test_unused_imports.py:8:[W0611(unused-import),]Unused filterfalse imported from itertools as _filterfalse
'''

class TestUnusedImports(unittest.TestCase):

    def test_pylint_warning(self):
        warnings = unused_import_warnings.split('\n')
        warnings = [w for w in warnings if w]
        parsed_warnings = Delinter.parse_linter_warnings(warnings, 'W0611')

        expected_warnings = [
                imports.UnusedImportsWarning(file_path='test_unused_imports.py', line_no=1, alias=None, dotted_as_name='unitest.mock.patch'),
                imports.UnusedImportsWarning(file_path='test_unused_imports.py', line_no=1, alias='p1', dotted_as_name='unittest.mock.patch'),
                imports.UnusedImportsWarning(file_path='test_unused_imports.py', line_no=5, alias=None, dotted_as_name='os'),
                imports.UnusedImportsWarning(file_path='test_unused_imports.py', line_no=6, alias='pd', dotted_as_name='pandas'),
                imports.UnusedImportsWarning(file_path='test_unused_imports.py', line_no=6, alias='np', dotted_as_name='numpy'),
                imports.UnusedFromImportsWarning(file_path='test_unused_imports.py', line_no=7, import_as_name='defaultdict', dotted_as_name='collections.abc', alias=None),
                imports.UnusedFromImportsWarning(file_path='test_unused_imports.py', line_no=7, import_as_name='OrderedDict', dotted_as_name='collections.abc', alias=None),
                imports.UnusedFromImportsWarning(file_path='test_unused_imports.py', line_no=8, import_as_name='filterfalse', dotted_as_name='itertools', alias='_filterfalse')]
        self.assertEqual(parsed_warnings, expected_warnings)

if __name__ == '__main__':
    unittest.main()
