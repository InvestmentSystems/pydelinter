from delinter import imports

transformer_class = imports.RemoveUnusedImportTransformer
delinter_class = imports.UnusedImportsDelinter

source_code = '''import unitest.mock.patch, unittest.mock.patch as p1
import unitest.mock.patch, unittest.mock.patch as p2
import unittest as t, unittest as t2
import unitest.mock.patch as p
import os
import pandas as pd, numpy as np
from collections.abc import defaultdict, OrderedDict
from itertools import filterfalse as _filterfalse
from collections.abc import x, y

p2.mock() # use p2
t.mock() # use t
y.mock() # use y
'''

pylint_messages = '''
test_unused_imports.py:1:[W0611(unused-import),]Unused import unitest.mock.patch
test_unused_imports.py:1:[W0611(unused-import),]Unused unittest.mock.patch imported as p1
test_unused_imports.py:3:[W0611(unused-import),]Unused unittest imported as t2
test_unused_imports.py:5:[W0611(unused-import),]Unused import os
test_unused_imports.py:6:[W0611(unused-import),]Unused pandas imported as pd
test_unused_imports.py:6:[W0611(unused-import),]Unused numpy imported as np
test_unused_imports.py:7:[W0611(unused-import),]Unused defaultdict imported from collections.abc
test_unused_imports.py:7:[W0611(unused-import),]Unused OrderedDict imported from collections.abc
test_unused_imports.py:8:[W0611(unused-import),]Unused filterfalse imported from itertools as _filterfalse
test_unused_imports.py:9:[W0611(unused-import),]Unused x imported from collections.abc
'''

expected_diff = (
'''---
+++
@@ -1,12 +1,7 @@
-import unitest.mock.patch, unittest.mock.patch as p1
import unitest.mock.patch, unittest.mock.patch as p2
-import unittest as t, unittest as t2
+import unittest as t
import unitest.mock.patch as p
-import os
-import pandas as pd, numpy as np
-from collections.abc import defaultdict, OrderedDict
-from itertools import filterfalse as _filterfalse
-from collections.abc import x, y
+from collections.abc import y

p2.mock() # use p2
t.mock() # use t
'''
)
