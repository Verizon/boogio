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

'''Test cases for the excelerator.py module.

These are pretty minimal, as long as the Excel file is created
without error they'll pass.
'''

import unittest

import json
import os
import tempfile

from boogio.utensils import excelerator


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestExcelerator(unittest.TestCase):
    '''
    Basic test cases for Excelerator.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''
        Get a temp directory for output.
        '''
        cls.tmpdir = tempfile.mkdtemp()
        # cls.filename = os.path.join('/tmp', 'file1.xls')
        cls.filename = os.path.join(cls.tmpdir, 'file1.xls')

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
    def test_excelerator_data(self):
        '''
        Basic test cases for excelerator with directly passed data.
        '''

        # filename = os.path.join(self.tmpdir, 'file1.xls')
        filename = self.filename

        excelerator.excelerate(
            filename,
            {
                'data': [
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ]
                }
            )
        self.assertTrue(os.path.exists(filename))

        excelerator.excelerate(
            filename,
            {
                'data': [
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ],
                'columns': ['A', 'B', 'C']
                }
            )
        self.assertTrue(os.path.exists(filename))

        excelerator.excelerate(
            filename,
            {
                'data': [
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ],
                'columns': ['A', 'B', 'C'],
                'headers': {
                    'A': 'alpha',
                    'B': 'beta'
                    }
                }
            )
        self.assertTrue(os.path.exists(filename))

        excelerator.excelerate(
            filename,
            {
                'data': [
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ],
                'headers': {
                    'A': 'alpha',
                    'B': 'beta',
                    'C': 'gamma'
                    }
                }
            )
        self.assertTrue(os.path.exists(filename))

        excelerator.excelerate(
            filename,
            {
                'sheetname': "George",
                'data': [
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ],
                'headers': {
                    'A': 'alpha',
                    'B': 'beta',
                    'C': 'gamma'
                    },
                'placeholder': 'XXX'
                },
            {
                'data': [
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ],
                'columns': ['A', 'B', 'C'],
                'headers': {
                    'A': 'alpha',
                    'B': 'beta',
                    'C': 'gamma'
                    }
                },
            placeholder=""
            )
        self.assertTrue(os.path.exists(filename))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_excelerator_json(self):
        '''
        Basic test cases for excelerator with data in a json string.
        '''
        filename = self.filename

        excelerator.excelerate(
            filename,
            {
                'sheetname': "George",
                'json': json.dumps([
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ]),
                'placeholder': 'XXX'
                },
            {
                'data': [
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ],
                'columns': ['A', 'B', 'C'],
                'headers': {
                    'A': 'alpha',
                    'B': 'beta',
                    'C': 'gamma'
                    }
                },
            placeholder=""
            )
        self.assertTrue(os.path.exists(filename))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_excelerator_jsonfile(self):
        '''
        Basic test cases for excelerator with data in a json file.
        '''
        filename = self.filename

        jsonfile = os.path.join(self.tmpdir, 'data.json')
        data = [{'A': 11, 'B': 12}, {'A': 21, 'C': 23}]

        with open(jsonfile, 'w') as fp:
            json.dump(data, fp)

        excelerator.excelerate(
            filename,
            {
                'sheetname': "George",
                'jsonfile': jsonfile,
                'headers': {
                    'A': 'alpha',
                    'B': 'beta',
                    'C': 'gamma'
                    },
                'placeholder': 'XXX'
                },
            {
                'json': json.dumps([
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ]),
                'columns': ['A', 'B', 'C'],
                'headers': {
                    'A': 'alpha',
                    'B': 'beta',
                    'C': 'gamma'
                    }
                },
            placeholder=""
            )
        self.assertTrue(os.path.exists(filename))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_excelerator_sheetspec(self):
        '''
        Basic test cases for excelerator with sheetspecs.
        '''
        filename = self.filename + "_sheetspec"

        sheetspec_file1 = os.path.join(self.tmpdir, 'sheetspec1.json')
        sheetspec_data1 = {'George': {'columns': ['B', 'C']}}

        with open(sheetspec_file1, 'w') as fp:
            json.dump(sheetspec_data1, fp)

        sheetspec_file2 = os.path.join(self.tmpdir, 'sheetspec2.json')
        sheetspec_data2 = {
            'Mary': {
                'columns': ['A', 'C'],
                'headers': {'A': 'Ehh', 'B': 'Bee', 'C': 'See'}
                }
            }

        with open(sheetspec_file2, 'w') as fp:
            json.dump(sheetspec_data2, fp)

        excelerator.excelerate(
            filename,
            {
                'sheetname': "George",
                'data': [
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ],
                'placeholder': 'XXX'
                },
            {
                'json': json.dumps([
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ]),
                'columns': ['A', 'B', 'C'],
                'headers': {
                    'A': 'alpha',
                    'B': 'beta',
                    'C': 'gamma'
                    }
                },
            sheetspecs=[sheetspec_data1]
            )
        self.assertTrue(os.path.exists(filename))

        excelerator.excelerate(
            filename,
            {
                'sheetname': "George",
                'data': [
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ],
                'headers': {
                    'A': 'alpha',
                    'B': 'beta',
                    'C': 'gamma'
                    },
                'placeholder': 'XXX'
                },
            {
                'sheetname': "Mary",
                'json': json.dumps([
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ]),
                },
            sheetspecs=[sheetspec_file1, sheetspec_data2]
            # sheetspecs=[sheetspec_file1]
            )
        self.assertTrue(os.path.exists(filename))

        excelerator.excelerate(
            filename,
            {
                'sheetname': "George",
                'data': [
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ],
                'headers': {
                    'A': 'alpha',
                    'B': 'beta',
                    'C': 'gamma'
                    },
                'placeholder': 'XXX'
                },
            {
                'sheetname': "Mary",
                'json': json.dumps([
                    {'A': 11, 'B': 12},
                    {'A': 21, 'C': 23}
                    ]),
                'columns': ['A', 'B', 'C'],
                },
            sheetspecs=[sheetspec_file1, sheetspec_data2]
            # sheetspecs=[sheetspec_file1]
            )
        self.assertTrue(os.path.exists(filename))


if __name__ == '__main__':
    unittest.main()
