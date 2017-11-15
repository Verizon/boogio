# ----------------------------------------------------------------------------
# Copyright (C) 2017 Verizon.  All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ----------------------------------------------------------------------------

'''Test cases for the tabulizer.py module.'''

import unittest

import json
import os
import tempfile

from boogio.utensils import tabulizer

import xlsxwriter


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTabulizerInit(unittest.TestCase):
    '''
    Basic test cases for Tabulizer creation and population.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''
        Get a temp directory for output.
        '''
        cls.tmpdir = tempfile.mkdtemp()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def tearDownClass(cls):
        '''
        Remove test files and temp directory.
        '''
        for root, dirs, files in os.walk(cls.tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(cls.tmpdir)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_init(self):

        # - - - - - - - - - - - - - - - - - - - -
        # Sample data.
        # - - - - - - - - - - - - - - - - - - - -
        data_2x2 = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        headers_2 = {'a': 'An eh', 'b': 'A bee'}
        columns_2 = ['a', 'b']

        # - - - - - - - - - - - - - - - - - - - -
        # Empty initialization.
        # - - - - - - - - - - - - - - - - - - - -
        tab = tabulizer.Tabulizer()
        self.assertIsNotNone(tab)

        self.assertIsNone(tab.data)
        self.assertIsNone(tab.headers)
        self.assertIsNone(tab.columns)

        # - - - - - - - - - - - - - - - - - - - -
        # All parameter initialization.
        # - - - - - - - - - - - - - - - - - - - -
        tab = tabulizer.Tabulizer(
            data=data_2x2,
            headers=headers_2,
            columns=columns_2
            )
        self.assertIsNotNone(tab)

        self.assertEqual(tab.data, data_2x2)
        self.assertEqual(tab.headers, headers_2)
        self.assertEqual(tab.columns, columns_2)

        # - - - - - - - - - - - - - - - - - - - -
        # Mixed parameter initialization.
        # - - - - - - - - - - - - - - - - - - - -
        tab = tabulizer.Tabulizer(
            data_2x2
            )
        self.assertIsNotNone(tab)

        self.assertEqual(tab.data, data_2x2)
        self.assertEqual(tab.headers, {'a': 'a', 'b': 'b'})
        self.assertEqual(tab.columns, ['a', 'b'])

        # - - - - - - - - - - - - - - - - - - - -
        tab = tabulizer.Tabulizer(
            data_2x2,
            headers_2
            )
        self.assertIsNotNone(tab)

        self.assertEqual(tab.data, data_2x2)
        self.assertEqual(tab.headers, headers_2)
        self.assertEqual(tab.columns, ['a', 'b'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_tsv_load(self):
        '''
        Basic tests for tabulizer.tsv_load(), and implicitly of
        tabulizer.sv_load.
        '''

        tsvfile1 = os.path.join(self.tmpdir, "sample1.tsv")
        with open(tsvfile1, 'w') as fp:
            fp.write("A\tB\tC\n")
            fp.write("Apple\tBanana\tCherry\n")
            fp.write("Ant\tBat\tCat\n")

        tab = tabulizer.Tabulizer()
        tab.tsv_load(tsvfile1)

        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(len(tab.data), 2)
        self.assertEqual(tab.headers, {'A': 'A', 'B': 'B', 'C': 'C'})
        self.assertEqual(tab.columns, ['A', 'B', 'C'])

        self.assertEqual(len(tab.data[0]), 3)
        self.assertEqual(len(tab.data[1]), 3)

        self.assertEqual(tab.data[0]['A'], 'Apple')
        self.assertEqual(tab.data[1]['A'], 'Ant')
        self.assertEqual(tab.data[0]['B'], 'Banana')
        self.assertEqual(tab.data[1]['B'], 'Bat')
        self.assertEqual(tab.data[0]['C'], 'Cherry')
        self.assertEqual(tab.data[1]['C'], 'Cat')

        # - - - - - - - - - - - - - - - - - - - -
        tsvfile2 = os.path.join(self.tmpdir, "sample1.tsv")
        with open(tsvfile1, 'w') as fp:
            fp.write("A\tB\tC\n")
            fp.write("Apple\t\tCherry\n")
            fp.write("\n")
            fp.write("\tBat\tCat\n")

        tab = tabulizer.Tabulizer()
        tab.tsv_load(tsvfile1)

        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(len(tab.data), 2)
        self.assertEqual(tab.headers, {'A': 'A', 'B': 'B', 'C': 'C'})
        self.assertEqual(tab.columns, ['A', 'B', 'C'])

        self.assertEqual(len(tab.data[0]), 2)
        self.assertEqual(len(tab.data[1]), 2)

        self.assertEqual(tab.data[0]['A'], 'Apple')
        self.assertEqual(tab.data[1]['B'], 'Bat')
        self.assertEqual(tab.data[0]['C'], 'Cherry')
        self.assertEqual(tab.data[1]['C'], 'Cat')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_csv_load(self):
        '''
        Basic tests for tabulizer.csv_load(), and implicitly of
        tabulizer.sv_load.
        '''

        csvfile1 = os.path.join(self.tmpdir, "sample1.csv")
        with open(csvfile1, 'w') as fp:
            fp.write("A,B,C\n")
            fp.write("Apple,Banana,Cherry\n")
            fp.write("Ant,Bat,Cat\n")

        tab = tabulizer.Tabulizer()
        tab.csv_load(csvfile1)

        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(len(tab.data), 2)
        self.assertEqual(tab.headers, {'A': 'A', 'B': 'B', 'C': 'C'})
        self.assertEqual(tab.columns, ['A', 'B', 'C'])

        self.assertEqual(len(tab.data[0]), 3)
        self.assertEqual(len(tab.data[1]), 3)

        self.assertEqual(tab.data[0]['A'], 'Apple')
        self.assertEqual(tab.data[1]['A'], 'Ant')
        self.assertEqual(tab.data[0]['B'], 'Banana')
        self.assertEqual(tab.data[1]['B'], 'Bat')
        self.assertEqual(tab.data[0]['C'], 'Cherry')
        self.assertEqual(tab.data[1]['C'], 'Cat')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_json_loads(self):
        '''
        Basic tests for tabulizer.json_loads().
        '''

        data = [
            {'A': 'Apple', 'B': 'Banana', 'C': 'Cherry'},
            {'A': 'Ant', 'B': 'Bat', 'C': 'Cat'}
            ]

        json_string = json.dumps(data)

        tab = tabulizer.Tabulizer()
        tab.columns = ['A', 'B', 'C']
        tab.json_loads(json_string)

        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(len(tab.data), 2)
        self.assertEqual(tab.headers, {'A': 'A', 'B': 'B', 'C': 'C'})
        self.assertEqual(tab.columns, ['A', 'B', 'C'])

        self.assertEqual(len(tab.data[0]), 3)
        self.assertEqual(len(tab.data[1]), 3)

        self.assertEqual(tab.data[0]['A'], 'Apple')
        self.assertEqual(tab.data[1]['A'], 'Ant')
        self.assertEqual(tab.data[0]['B'], 'Banana')
        self.assertEqual(tab.data[1]['B'], 'Bat')
        self.assertEqual(tab.data[0]['C'], 'Cherry')
        self.assertEqual(tab.data[1]['C'], 'Cat')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_json_load(self):
        '''
        Basic tests for tabulizer.json_load().
        '''

        data = [
            {'A': 'Apple', 'B': 'Banana', 'C': 'Cherry'},
            {'A': 'Ant', 'B': 'Bat', 'C': 'Cat'}
            ]

        jsonfile1 = os.path.join(self.tmpdir, "sample1.csv")
        with open(jsonfile1, 'w') as fp:
            json.dump(data, fp)

        tab = tabulizer.Tabulizer()
        tab.columns = ['A', 'B', 'C']
        tab.json_load(jsonfile1)

        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(len(tab.data), 2)
        self.assertEqual(tab.headers, {'A': 'A', 'B': 'B', 'C': 'C'})
        self.assertEqual(tab.columns, ['A', 'B', 'C'])

        self.assertEqual(len(tab.data[0]), 3)
        self.assertEqual(len(tab.data[1]), 3)

        self.assertEqual(tab.data[0]['A'], 'Apple')
        self.assertEqual(tab.data[1]['A'], 'Ant')
        self.assertEqual(tab.data[0]['B'], 'Banana')
        self.assertEqual(tab.data[1]['B'], 'Bat')
        self.assertEqual(tab.data[0]['C'], 'Cherry')
        self.assertEqual(tab.data[1]['C'], 'Cat')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTabulizer(unittest.TestCase):
    '''
    Basic test cases for Tabulizer use.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_header_list(self):
        '''
        Basic tests for tabulizer.header_list()
        '''
        # - - - - - - - - - - - - - - - - - - - -
        # Sample data.
        # - - - - - - - - - - - - - - - - - - - -
        data_2x2 = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        headers_2 = {'a': 'An eh', 'b': 'A bee'}
        columns_2 = ['a', 'b']

        # - - - - - - - - - - - - - - - - - - - -
        tab = tabulizer.Tabulizer(
            data=data_2x2
            )

        self.assertEqual(
            tab._header_list(),
            ['a', 'b']
            )
        self.assertEqual(
            tab._header_list(columns=['a', 'b']),
            ['a', 'b']
            )
        self.assertEqual(
            tab._header_list(columns=['a']),
            ['a']
            )
        self.assertEqual(
            tab._header_list(columns=['c']),
            ['c']
            )
        self.assertEqual(
            tab._header_list(columns=['a', 'b', 'c']),
            ['a', 'b', 'c']
            )

        # - - - - - - - - - - - - - - - - - - - -
        tab = tabulizer.Tabulizer(
            data=data_2x2,
            headers=headers_2,
            columns=columns_2
            )

        self.assertEqual(
            tab._header_list(),
            ['An eh', 'A bee']
            )
        self.assertEqual(
            tab._header_list(columns=['a', 'b']),
            ['An eh', 'A bee']
            )
        self.assertEqual(
            tab._header_list(columns=['a']),
            ['An eh']
            )
        self.assertEqual(
            tab._header_list(columns=['c']),
            ['c']
            )
        self.assertEqual(
            tab._header_list(columns=['a', 'b', 'c']),
            ['An eh', 'A bee', 'c']
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_row_list(self):
        '''
        Basic tests for tabulizer.row_list()
        '''
        # - - - - - - - - - - - - - - - - - - - -
        # Sample data.
        # - - - - - - - - - - - - - - - - - - - -
        data_2x2 = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
        headers_2 = {'a': 'An eh', 'b': 'A bee'}
        columns_2 = ['a', 'b']

        tab = tabulizer.Tabulizer(
            data=data_2x2,
            headers=headers_2,
            columns=columns_2
            )

        # - - - - - - - - - - - - - - - - - - - -
        # All columns.
        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(
            tab._row_list({'a': 1, 'b': 2}),
            ['1', '2']
            )
        self.assertEqual(
            tab._row_list({'a': 1}),
            ['1', 'None']
            )
        self.assertEqual(
            tab._row_list({'aaa': 1, 'b': 2}),
            ['None', '2']
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Limited columns.
        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(
            tab._row_list({'a': 1, 'b': 2}, columns=['a', 'b']),
            ['1', '2']
            )

        self.assertEqual(
            tab._row_list({'a': 1, 'b': 2}, columns=['a']),
            ['1']
            )

        self.assertEqual(
            tab._row_list({'a': 1, 'b': 2}, columns=['c']),
            ['None']
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Custom placeholder.
        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(
            tab._row_list({'a': 1, 'b': 2}, placeholder="X"),
            ['1', '2']
            )
        self.assertEqual(
            tab._row_list({'a': 1}, placeholder="X"),
            ['1', 'X']
            )
        self.assertEqual(
            tab._row_list({'aaa': 1, 'b': 2}, placeholder="X"),
            ['X', '2']
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_sv(self):
        '''
        Basic tests for tabulizer.sv()
        '''

        # - - - - - - - - - - - - - - - - - - - -
        # Sample data.
        # - - - - - - - - - - - - - - - - - - - -
        data_2x2 = [{'a': 1, 'b': 2}, {'a': 3, 'c': 6}]
        headers_2 = {'a': 'An eh', 'b': 'A bee', 'c': 'I see'}
        columns_2 = ['a', 'b', 'c']

        tab = tabulizer.Tabulizer(
            data=data_2x2,
            headers=headers_2,
            columns=columns_2
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Headers and all columns.
        # - - - - - - - - - - - - - - - - - - - -
        sv = tab.sv()
        self.assertEqual(len(sv), 3)
        self.assertEqual(sv[0], 'An eh,A bee,I see')
        self.assertEqual(sv[1], '1,2,None')
        self.assertEqual(sv[2], '3,None,6')

        # - - - - - - - - - - - - - - - - - - - -
        # Limited columns.
        # - - - - - - - - - - - - - - - - - - - -
        sv = tab.sv(columns=['a'])
        self.assertEqual(len(sv), 3)
        self.assertEqual(sv[0], 'An eh')
        self.assertEqual(sv[1], '1')
        self.assertEqual(sv[2], '3')

        sv = tab.sv(columns=['b'])
        self.assertEqual(len(sv), 3)
        self.assertEqual(sv[0], 'A bee')
        self.assertEqual(sv[1], '2')
        self.assertEqual(sv[2], 'None')

        # - - - - - - - - - - - - - - - - - - - -
        # No headers.
        # - - - - - - - - - - - - - - - - - - - -
        sv = tab.sv(include_headers=False)
        self.assertEqual(len(sv), 2)
        self.assertEqual(sv[0], '1,2,None')
        self.assertEqual(sv[1], '3,None,6')

        # - - - - - - - - - - - - - - - - - - - -
        # Custom placeholder.
        # - - - - - - - - - - - - - - - - - - - -
        sv = tab.sv(include_headers=False, placeholder="X")
        self.assertEqual(len(sv), 2)
        self.assertEqual(sv[0], '1,2,X')
        self.assertEqual(sv[1], '3,X,6')

        # - - - - - - - - - - - - - - - - - - - -
        # Extra columns.
        # - - - - - - - - - - - - - - - - - - - -
        sv = tab.sv(
            columns=['a', 'b', 'c', 'dog']
            )
        self.assertEqual(len(sv), 3)
        self.assertEqual(sv[0], 'An eh,A bee,I see,dog')
        self.assertEqual(sv[1], '1,2,None,None')
        self.assertEqual(sv[2], '3,None,6,None')

        sv = tab.sv(
            include_headers=False,
            placeholder="X",
            columns=['a', 'b', 'dog', 'c']
            )
        self.assertEqual(len(sv), 2)
        self.assertEqual(sv[0], '1,2,X,X')
        self.assertEqual(sv[1], '3,X,X,6')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_sv_empty_data(self):
        '''
        Basic tests for tabulizer.sv() with "degenerate" values of data.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        # Sample data.
        # - - - - - - - - - - - - - - - - - - - -
        headers = {'a': 'An eh', 'b': 'A bee', 'c': 'I see'}
        columns = ['a', 'b', 'c']

        # - - - - - - - - - - - - - - - - - - - -

        # Data only.
        tab_data_empty = tabulizer.Tabulizer(
            data=[]
            )

        sv = tab_data_empty.sv()
        self.assertEqual(len(sv), 0)

        sv = tab_data_empty.sv(include_headers=False)
        self.assertEqual(len(sv), 0)

        sv = tab_data_empty.sv(columns=['a'])
        self.assertEqual(len(sv), 1)
        self.assertEqual(sv[0], 'a')

        # Data and columns.
        tab_data_empty = tabulizer.Tabulizer(
            data=[],
            columns=columns
            )

        sv = tab_data_empty.sv()
        self.assertEqual(len(sv), 1)
        self.assertEqual(sv[0], 'a,b,c')

        sv = tab_data_empty.sv(columns=['a'])
        self.assertEqual(len(sv), 1)
        self.assertEqual(sv[0], 'a')

        sv = tab_data_empty.sv(include_headers=False)
        self.assertEqual(len(sv), 0)

        # - - - - - - - - - - - - - - - - - - - -

        # Data only.
        tab_data_none = tabulizer.Tabulizer(
            data=None
            )

        sv = tab_data_none.sv()
        self.assertEqual(len(sv), 0)

        sv = tab_data_none.sv(include_headers=False)
        self.assertEqual(len(sv), 0)

        sv = tab_data_none.sv(columns=['a'])
        self.assertEqual(len(sv), 1)
        self.assertEqual(sv[0], 'a')

        # Data and columns.
        tab_data_none = tabulizer.Tabulizer(
            data=None,
            columns=columns
            )

        sv = tab_data_none.sv()
        self.assertEqual(len(sv), 1)
        self.assertEqual(sv[0], 'a,b,c')

        sv = tab_data_none.sv(columns=['a'])
        self.assertEqual(len(sv), 1)
        self.assertEqual(sv[0], 'a')

        sv = tab_data_none.sv(include_headers=False)
        self.assertEqual(len(sv), 0)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_csv(self):
        '''
        Basic tests for tabulizer.csv()
        '''

        # - - - - - - - - - - - - - - - - - - - -
        # Sample data.
        # - - - - - - - - - - - - - - - - - - - -
        data_2x2 = [{'a': 1, 'b': 2}, {'a': 3, 'c': 6}]
        headers_2 = {'a': 'An eh', 'b': 'A bee', 'c': 'I see'}
        columns_2 = ['a', 'b', 'c']

        tab = tabulizer.Tabulizer(
            data=data_2x2,
            headers=headers_2,
            columns=columns_2
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Headers and all columns.
        # - - - - - - - - - - - - - - - - - - - -
        csv = tab.csv()
        self.assertEqual(len(csv), 3)
        self.assertEqual(csv[0], 'An eh,A bee,I see')
        self.assertEqual(csv[1], '1,2,None')
        self.assertEqual(csv[2], '3,None,6')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_tsv(self):
        '''
        Basic tests for tabulizer.tsv()
        '''

        # - - - - - - - - - - - - - - - - - - - -
        # Sample data.
        # - - - - - - - - - - - - - - - - - - - -
        data_2x2 = [{'a': 1, 'b': 2}, {'a': 3, 'c': 6}]
        headers_2 = {'a': 'An eh', 'b': 'A bee', 'c': 'I see'}
        columns_2 = ['a', 'b', 'c']

        tab = tabulizer.Tabulizer(
            data=data_2x2,
            headers=headers_2,
            columns=columns_2
            )

        # - - - - - - - - - - - - - - - - - - - -
        # No headers.
        # - - - - - - - - - - - - - - - - - - - -
        tsv = tab.tsv(include_headers=False)
        self.assertEqual(len(tsv), 2)
        self.assertEqual(tsv[0], '1\t2\tNone')
        self.assertEqual(tsv[1], '3\tNone\t6')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTabulizerJsonDumps(unittest.TestCase):
    '''
    Basic test cases for Tabulizer json dumps output.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_json_dumps(self):

        # - - - - - - - - - - - - - - - - - - - -
        # Sample data.
        # - - - - - - - - - - - - - - - - - - - -
        data_2x2 = [{'a': 1, 'b': 2}, {'a': 3, 'c': 6}]
        headers_2 = {'a': 'An eh', 'b': 'A bee', 'c': 'I see'}
        columns_2 = ['a', 'b', 'c']

        tab = tabulizer.Tabulizer(
            data=data_2x2,
            headers=headers_2,
            columns=columns_2
            )

        def sorted(a_list):
            a_list.sort()
            return a_list

        # - - - - - - - - - - - - - - - - - - - -
        # Headers and all columns.
        # - - - - - - - - - - - - - - - - - - - -
        dump = tab.json_dumps()
        reloaded = json.loads(dump)

        self.assertEqual(len(reloaded), 2)
        self.assertEqual(len(reloaded[0]), 3)
        self.assertEqual(len(reloaded[1]), 3)

        self.assertEqual(sorted(reloaded[0].keys()), columns_2)
        self.assertEqual(sorted(reloaded[1].keys()), columns_2)

        self.assertIn(1, reloaded[0].values())
        self.assertIn(2, reloaded[0].values())
        self.assertIn(None, reloaded[0].values())

        self.assertIn(3, reloaded[1].values())
        self.assertIn(6, reloaded[1].values())
        self.assertIn(None, reloaded[1].values())

        # # - - - - - - - - - - - - - - - - - - - -
        # # Limited columns.
        # # - - - - - - - - - - - - - - - - - - - -
        dump = tab.json_dumps(columns=['a'])
        reloaded = json.loads(dump)

        self.assertEqual(len(reloaded), 2)
        self.assertEqual(len(reloaded[0]), 1)
        self.assertEqual(len(reloaded[1]), 1)

        self.assertEqual(sorted(reloaded[0].keys()), ['a'])
        self.assertEqual(sorted(reloaded[1].keys()), ['a'])

        self.assertIn(1, reloaded[0].values())
        self.assertIn(3, reloaded[1].values())

        # # - - - - - - - - - - - - - - - - - - - -
        # # Custom placeholder.
        # # - - - - - - - - - - - - - - - - - - - -
        dump = tab.json_dumps(placeholder='X')
        reloaded = json.loads(dump)

        self.assertEqual(len(reloaded), 2)
        self.assertEqual(len(reloaded[0]), 3)
        self.assertEqual(len(reloaded[1]), 3)

        self.assertEqual(sorted(reloaded[0].keys()), columns_2)
        self.assertEqual(sorted(reloaded[1].keys()), columns_2)

        self.assertIn(1, reloaded[0].values())
        self.assertIn(2, reloaded[0].values())
        self.assertIn('X', reloaded[0].values())

        self.assertIn(3, reloaded[1].values())
        self.assertIn(6, reloaded[1].values())
        self.assertIn('X', reloaded[1].values())

        # - - - - - - - - - - - - - - - - - - - -
        # Extra columns.
        # - - - - - - - - - - - - - - - - - - - -
        columns_4 = ['a', 'b', 'c', 'dog']

        dump = tab.json_dumps(
            columns=columns_4
            )
        reloaded = json.loads(dump)

        self.assertEqual(len(reloaded), 2)
        self.assertEqual(len(reloaded[0]), 4)
        self.assertEqual(len(reloaded[1]), 4)

        self.assertEqual(sorted(reloaded[0].keys()), columns_4)
        self.assertEqual(sorted(reloaded[1].keys()), columns_4)

        self.assertIn(1, reloaded[0].values())
        self.assertIn(2, reloaded[0].values())
        self.assertIn(None, reloaded[0].values())

        self.assertIn(3, reloaded[1].values())
        self.assertIn(6, reloaded[1].values())
        self.assertIn(None, reloaded[1].values())

        # - - - - - - - - - - - - - - - - - - - -
        dump = tab.json_dumps(
            placeholder="X",
            columns=columns_4
            )
        reloaded = json.loads(dump)

        self.assertEqual(len(reloaded), 2)
        self.assertEqual(sorted(reloaded[0].values()), [1, 2, 'X', 'X'])
        self.assertEqual(sorted(reloaded[1].values()), [3, 6, 'X', 'X'])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTabulizerToExcel(unittest.TestCase):
    '''
    Basic test cases for Tabulizer excel output.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''
        Get a temp directory for output.
        '''
        cls.tmpdir = tempfile.mkdtemp()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def tearDownClass(cls):
        '''
        Remove test files and temp directory.
        '''
        for root, dirs, files in os.walk(cls.tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(cls.tmpdir)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_to_worksheet(self):
        '''
        Basic tests for tabulizer.to_worksheet().

        This doesn't actually validate the worksheet, just verify that
        the methods exist and don't generate bogus errors.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        # Sample data.
        # - - - - - - - - - - - - - - - - - - - -
        data_2x2 = [{'a': 1, 'b': 2}, {'a': 3, 'c': 6}]
        headers_2 = {'a': 'An eh', 'b': 'A bee', 'c': 'I see'}
        columns_2 = ['a', 'b', 'c']

        tab = tabulizer.Tabulizer(
            data=data_2x2,
            headers=headers_2,
            columns=columns_2
            )

        tmpfile = os.path.join(self.tmpdir, 'temp1.xls')
        workbook = xlsxwriter.Workbook(tmpfile)

        # - - - - - - - - - - - - - - - - - - - -
        worksheet = workbook.add_worksheet('test1')
        tab.to_worksheet(worksheet)
        worksheet = workbook.add_worksheet('test2')
        tab.to_worksheet(worksheet, columns=['a'])
        worksheet = workbook.add_worksheet('test3')
        tab.to_worksheet(worksheet, columns=['b'])
        worksheet = workbook.add_worksheet('test4')
        tab.to_worksheet(worksheet, include_headers=False)

        workbook.close()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_tabulizer_to_worksheet_table(self):
        '''
        Basic tests for tabulizer.to_worksheet_table().

        This doesn't actually validate the worksheet, just verify that
        the methods exist and don't generate bogus errors.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        # Sample data.
        # - - - - - - - - - - - - - - - - - - - -
        data_2x2 = [{'a': 1, 'b': 2}, {'a': 3, 'c': 6}]
        headers_2 = {'a': 'An eh', 'b': 'A bee', 'c': 'I see'}
        columns_2 = ['a', 'b', 'c']

        tab = tabulizer.Tabulizer(
            data=data_2x2,
            headers=headers_2,
            columns=columns_2
            )

        tmpfile = os.path.join(self.tmpdir, 'temp1.xls')
        workbook = xlsxwriter.Workbook(tmpfile)

        # - - - - - - - - - - - - - - - - - - - -
        worksheet = workbook.add_worksheet('test1')
        tab.to_worksheet_table(worksheet)
        worksheet = workbook.add_worksheet('test2')
        tab.to_worksheet_table(worksheet, columns=['a'])
        worksheet = workbook.add_worksheet('test3')
        tab.to_worksheet_table(worksheet, columns=['b'])
        worksheet = workbook.add_worksheet('test4')
        tab.to_worksheet_table(worksheet, include_headers=False)

        workbook.close()

if __name__ == '__main__':
    unittest.main()
