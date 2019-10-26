import difflib
import unittest

import libcst as cst
import delinter.imports as imports
from delinter.main import Delinter

from fixtures import unused_imports
from fixtures import reimports

class BaseTest(unittest.TestCase):

    def assert_expected_diff(self, fixture_module):
        pylint_messages = getattr(fixture_module, 'pylint_messages')
        source_code = getattr(fixture_module, 'source_code')
        transformer_class = getattr(fixture_module, 'transformer_class')
        expected_diff = getattr(fixture_module, 'expected_diff')

        warnings = pylint_messages.split('\n')
        warnings = [w for w in warnings if w]
        parsed_warnings = Delinter.parse_linter_warnings(
                warnings, fixture_module.delinter_class.CODE)

        source_tree = cst.parse_module(source_code)
        wrapper = cst.MetadataWrapper(source_tree)
        fixed_module = wrapper.visit(transformer_class((parsed_warnings)))
        diff = "".join(difflib.unified_diff(source_code.splitlines(1), fixed_module.code.splitlines(1)))

        diff = diff.replace('+++ ', '+++').replace('--- ', '---').replace('\n ', '\n')
        new_expected_diff = expected_diff.replace('\n ', '\n')
        self.assertEqual(diff, new_expected_diff)


class TestUnusedImports(BaseTest):

    def test_unused_import(self):
        self.assert_expected_diff(unused_imports)


class TestReimports(BaseTest):
    def test_reimports(self):
        self.assert_expected_diff(reimports)


if __name__ == '__main__':
    unittest.main()
