from delinter import imports

transformer_class = imports.ReimportTransformer
delinter_class = imports.ReimportDelinter

source_code = '''import unitest.mock.patch
import unitest.mock.patch
import unittest as t
import unittest as t
from collections.abc import defaultdict
from collections.abc import defaultdict, OrderedDict
from collections import deque, defaultdict
from collections.abc import x, y as yy
from collections.abc import x, y as yy1
from collections.abc import defaultdict as dd

x = yy
z = yy1

'''

pylint_messages = '''
tests/input/sample_reimport.py:2:[W0404(reimported),]Reimport 'unitest.mock.patch' (imported line 1)"
tests/input/sample_reimport.py:4:[W0404(reimported),]Reimport 'unittest' (imported line 3)"
tests/input/sample_reimport.py:6:[W0404(reimported),]Reimport 'defaultdict' (imported line 5)"
tests/input/sample_reimport.py:7:[W0404(reimported),]Reimport 'defaultdict' (imported line 5)"
tests/input/sample_reimport.py:9:[W0404(reimported),]Reimport 'x' (imported line 8)"
tests/input/sample_reimport.py:9:[W0404(reimported),]Reimport 'y' (imported line 8)"
tests/input/sample_reimport.py:10:[W0404(reimported),]Reimport 'defaultdict' (imported line 5)"
'''


expected_diff = ('---\n'
'+++\n'
'@@ -1,12 +1,10 @@\n'
'-import unitest.mock.patch\n'
'import unitest.mock.patch\n'
'import unittest as t\n'
'-import unittest as t\n'
'from collections.abc import defaultdict\n'
'-from collections.abc import defaultdict, OrderedDict\n'
'-from collections import deque, defaultdict\n'
'+from collections.abc import OrderedDict\n'
'+from collections import deque\n'
'from collections.abc import x, y as yy\n'
'-from collections.abc import x, y as yy1\n'
'+from collections.abc import y as yy1\n'
'from collections.abc import defaultdict as dd\n'
'\n'
'x = yy\n')
