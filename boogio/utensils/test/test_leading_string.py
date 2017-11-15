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

'''Test cases for the leading_string.py module.'''

import unittest

# from boogio.utensils import leading_string
from boogio.utensils.leading_string import index_by_common_leading_string


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestIndexByCommonLeadingString(unittest.TestCase):
    '''Basic test cases for leading_string.index_by_common_leading_string.'''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case common fixture setup.'''
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_index_by_common_leading_string(self):
        '''Test index_by_common_leading_string().'''

        # Empty list.
        strings = []
        indexed = index_by_common_leading_string(strings)
        self.assertEqual(indexed, {})

        # Empty string in list.
        strings = ['']
        indexed = index_by_common_leading_string(strings)
        self.assertEqual(indexed, {'': ['']})

        # Single character in list.
        strings = ['a']
        indexed = index_by_common_leading_string(strings)
        self.assertEqual(indexed, {'': ['a']})

        # Single string in list.
        strings = ['abc']
        indexed = index_by_common_leading_string(strings)
        self.assertEqual(indexed, {'': ['abc']})

        # Multiple characters in list.
        strings = ['a', 'b', 'c']
        indexed = index_by_common_leading_string(strings)
        self.assertItemsEqual(indexed.keys(), [''])
        self.assertItemsEqual(indexed[''], ['a', 'b', 'c'])

        # Mix of characters and strings in list.
        strings = ['a', 'apple', 'b', 'berry']
        indexed = index_by_common_leading_string(strings)
        self.assertItemsEqual(indexed.keys(), ['a', 'b'])
        self.assertItemsEqual(indexed['a'], ['a', 'apple'])
        self.assertItemsEqual(indexed['b'], ['b', 'berry'])

        # Additional tests.
        strings = ['abcd', 'abcD', 'abc_delta']
        indexed = index_by_common_leading_string(strings)
        self.assertItemsEqual(indexed.keys(), ['abc'])
        self.assertItemsEqual(indexed['abc'], ['abcd', 'abcD', 'abc_delta'])

        strings = ['aaa', 'aab', 'abb', 'bbb']
        indexed = index_by_common_leading_string(strings)
        self.assertItemsEqual(indexed.keys(), ['aa', 'a', ''])
        self.assertItemsEqual(indexed[''], ['bbb'])
        self.assertItemsEqual(indexed['a'], ['abb'])
        self.assertItemsEqual(indexed['aa'], ['aaa', 'aab'])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Define test suite.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# pylint: disable=invalid-name
load_case = unittest.TestLoader().loadTestsFromTestCase
all_suites = {
    # Lowercase these.
    'suite_index_by_common_leading_string': load_case(
        TestIndexByCommonLeadingString
        ),
    }

master_suite = unittest.TestSuite(all_suites.values())
# pylint: enable=invalid-name


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    unittest.main()
