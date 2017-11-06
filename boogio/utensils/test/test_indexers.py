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

'''Test cases for the indexers.py module.'''

import unittest

import json

from utensils import indexers

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Uncomment to show lower level logging statements.
# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# shandler = logging.StreamHandler()
# shandler.setLevel(logging.INFO)  # Pick one.
# shandler.setLevel(logging.DEBUG)  # Pick one.
# logger.addHandler(shandler)

FOREST_EMPTY = []
FOREST_EMPTY_D1 = [{}]
FOREST_EMPTY_D3 = [{}, {}, {}]
FOREST_EMPTY_L1 = [[]]
FOREST_EMPTY_L3 = [[], [], []]
FOREST_EMPTY_L2D2 = [[], {}, [], {}]

FOREST_D1_1 = [{'x': 'X'}]
FOREST_D1_3 = [{'i': 'I', 'x': 'X', 'y': 'Y', 'z': 'Z'}]
FOREST_D3_3 = [
    {'i': 'I1', 'x': 'X1', 'y': 'Y1', 'z': 'Z1'},
    {'i': 'I2', 'x': 'X2', 'y': 'Y2', 'z': 'Z2'},
    {'i': 'I3', 'x': 'X3', 'y': 'Y3', 'z': 'Z3'},
    ]
FOREST_D3_3_incomplete = [
    {'x': 'X1', 'y': 'Y1', 'z': 'Z1'},
    {'x': 'X2', 'y': 'Y2'},
    {'x': 'X3'},
    ]
FOREST_L1_1 = [['x']]
FOREST_L1_3 = [['x', 'y', 'z']]
FOREST_L2_3 = [['x', 'y', 'z']]

FOREST_WIDE_1 = [
    {'A': [{'B': 'b1', 'C': 'c1'}]},
    {'A': [{'B': 'b1', 'C': 'c2'}]},
    {'A': [{'B': 'b2', 'C': 'c2'}]},
    {'A': [{'B': 'b1'}]},
    {'A': [{'B': 'b2'}]},
    {'A': [{'C': 'c4'}]},
    {'A': []},
    ]

SIMPLE_DATA = [
    {'name': 'name_a', 'type': 'type_1', 'size': 1},
    {'name': 'name_b', 'type': 'type_1', 'size': 2},
    {'name': 'name_c', 'type': 'type_1', 'size': 3},
    {'name': 'name_d', 'type': 'type_2', 'size': 1},
    {'name': 'name_e', 'type': 'type_2', 'size': 2},
    {'name': 'name_f', 'type': 'type_2', 'size': 3},
    ]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def one_tree(tree_id):
    '''Generate a deep structure for more detailed path testing.'''
    tree = {
        'id': tree_id,
        'x': str(id) + '_X',
        'D3_3': FOREST_D3_3
        }
    return tree

FOREST_DEEP_1 = [one_tree('t1'), one_tree('t2'), one_tree('t3'), ]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestIndexByPaths(unittest.TestCase):
    '''Basic test cases for indexers.index_by_paths().'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Common class level setup.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_index_by_paths(self):
        '''Test indexers.index_by_paths().'''

        paths = ['type']
        index = indexers.index_by_paths(SIMPLE_DATA, paths)
        types = list(set([d['type'] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), 1)
        self.assertItemsEqual(index.keys(), paths)
        self.assertEqual(len(index['type']), len(types))

        for key in types:
            self.assertIn(key, index['type'])
            self.assertEqual(
                len(index['type'][key]), len(SIMPLE_DATA) / len(types)
                )

        # - - - - - - - - - - - - - - - -

        paths = ['type', 'size']
        index = indexers.index_by_paths(SIMPLE_DATA, paths)
        types = list(set([d['type'] for d in SIMPLE_DATA]))
        sizes = list(set([d['size'] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), 2)
        self.assertItemsEqual(index.keys(), paths)
        self.assertEqual(len(index['type']), len(types))
        self.assertEqual(len(index['size']), len(sizes))

        for key in types:
            self.assertIn(key, index['type'])
            self.assertEqual(
                len(index['type'][key]), len(SIMPLE_DATA) / len(types)
                )
        for key in sizes:
            self.assertIn(key, index['size'])
            self.assertEqual(
                len(index['size'][key]), len(SIMPLE_DATA) / len(sizes)
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_index_by_paths_with_prep_method(self):
        '''Test indexers.index_by_paths() with a prep_method.'''

        paths = ['type', 'size']
        index = indexers.index_by_paths(
            [{'foo': d} for d in SIMPLE_DATA],
            paths,
            prep_method=lambda x: x['foo']
            )
        types = list(set([d['type'] for d in SIMPLE_DATA]))
        sizes = list(set([d['size'] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), 2)
        self.assertItemsEqual(index.keys(), paths)
        self.assertEqual(len(index['type']), len(types))
        self.assertEqual(len(index['size']), len(sizes))

        for key in types:
            self.assertIn(key, index['type'])
            self.assertEqual(
                len(index['type'][key]), len(SIMPLE_DATA) / len(types)
                )
            self.assertEqual(index['type'][key][0].keys(), ['foo'])
        for key in sizes:
            self.assertIn(key, index['size'])
            self.assertEqual(
                len(index['size'][key]), len(SIMPLE_DATA) / len(sizes)
                )
            self.assertEqual(index['size'][key][0].keys(), ['foo'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_index_by_paths_with_key_method(self):
        '''Test indexers.index_by_paths() with a key_method.'''

        paths = ['type']
        index = indexers.index_by_paths(
            SIMPLE_DATA, paths, key_method=lambda x: x[-1]
            )
        types = list(set([d['type'][-1] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), 1)
        self.assertItemsEqual(index.keys(), paths)
        self.assertEqual(len(index['type']), len(types))

        for key in types:
            self.assertIn(key, index['type'])
            self.assertEqual(
                len(index['type'][key]), len(SIMPLE_DATA) / len(types)
                )

        # - - - - - - - - - - - - - - - -

        paths = ['type', 'size']
        index = indexers.index_by_paths(
            SIMPLE_DATA,
            paths,
            key_method=lambda x: x if type(x) == int else x[-1]
            )
        types = list(set([d['type'][-1] for d in SIMPLE_DATA]))
        sizes = list(set([d['size'] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), 2)
        self.assertItemsEqual(index.keys(), paths)
        self.assertEqual(len(index['type']), len(types))
        self.assertEqual(len(index['size']), len(sizes))

        for key in types:
            self.assertIn(key, index['type'])
            self.assertEqual(
                len(index['type'][key]), len(SIMPLE_DATA) / len(types)
                )
        for key in sizes:
            self.assertIn(key, index['size'])
            self.assertEqual(
                len(index['size'][key]), len(SIMPLE_DATA) / len(sizes)
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_index_by_paths_with_value_method(self):
        '''Test indexers.index_by_paths() with a value_method.'''

        paths = ['type']
        index = indexers.index_by_paths(
            SIMPLE_DATA,
            paths,
            value_method=lambda x: sorted(x.keys())
            )
        types = list(set([d['type'] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), 1)
        self.assertItemsEqual(index.keys(), paths)
        self.assertEqual(len(index['type']), len(types))

        for key in types:
            self.assertIn(key, index['type'])
            # Since the kayes are the same, the index value should
            # only have one entry.
            self.assertEqual(len(index['type'][key]), 1)
            self.assertEqual(
                index['type'][key],
                [sorted(['name', 'type', 'size'])]
                )

        # - - - - - - - - - - - - - - - -

        paths = ['type']
        index = indexers.index_by_paths(
            SIMPLE_DATA,
            paths,
            value_method=lambda x: sorted(x.values())
            )
        types = list(set([d['type'] for d in SIMPLE_DATA]))
        results = {
            'type_1': [
                sorted(['name_a', 'type_1', 1]),
                sorted(['name_b', 'type_1', 2]),
                sorted(['name_c', 'type_1', 3]),
                ],
            'type_2': [
                sorted(['name_d', 'type_2', 1]),
                sorted(['name_e', 'type_2', 2]),
                sorted(['name_f', 'type_2', 3]),
                ]
            }

        self.assertEqual(len(index), 1)
        self.assertItemsEqual(index.keys(), paths)
        self.assertEqual(len(index['type']), len(types))

        for key in types:
            self.assertIn(key, index['type'])
            self.assertEqual(
                len(index['type'][key]), len(SIMPLE_DATA) / len(types)
                )
            self.assertItemsEqual(index['type'][key], results[key])

        # - - - - - - - - - - - - - - - -

        paths = ['type']
        index = indexers.index_by_paths(
            SIMPLE_DATA,
            paths,
            key_method=lambda x: x[-1],
            value_method=lambda x: sorted(x.keys())
            )
        types = list(set([d['type'][-1] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), 1)
        self.assertItemsEqual(index.keys(), paths)
        self.assertEqual(len(index['type']), len(types))

        for key in types:
            self.assertIn(key, index['type'])
            # Since the kayes are the same, the index value should
            # only have one entry.
            self.assertEqual(len(index['type'][key]), 1)
            self.assertEqual(
                index['type'][key],
                [sorted(['name', 'type', 'size'])]
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestIndexByPath(unittest.TestCase):
    '''Basic test cases for indexers.index_by_path().'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Common class level setup.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_index_by_path(self):
        '''Test indexers.index_by_path().'''

        # - - - - - - - - - - - - - - - -

        index = indexers.index_by_path({}, 'name')
        self.assertEqual(index, {})

        # - - - - - - - - - - - - - - - -

        index = indexers.index_by_path(SIMPLE_DATA, 'name')

        self.assertEqual(len(index), len(SIMPLE_DATA))
        for key in [d['name'] for d in SIMPLE_DATA]:
            self.assertIn(key, index)

        # - - - - - - - - - - - - - - - -

        index = indexers.index_by_path(SIMPLE_DATA, 'type')
        types = list(set([d['type'] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), len(types))
        for key in types:
            self.assertIn(key, index)
            self.assertEqual(
                len(index[key]), len(SIMPLE_DATA) / len(types)
                )

        # - - - - - - - - - - - - - - - -

        index = indexers.index_by_path(SIMPLE_DATA, 'size')
        sizes = list(set([d['size'] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), len(sizes))
        for key in sizes:
            self.assertIn(key, index)
            self.assertEqual(
                len(index[key]), len(SIMPLE_DATA) / len(sizes)
                )

        # - - - - - - - - - - - - - - - -

        index = indexers.index_by_path(FOREST_WIDE_1, 'A.[].B')

        self.assertItemsEqual(index.keys(), ['b1', 'b2'])
        self.assertEqual(len(index['b1']), 3)
        self.assertEqual(len(index['b2']), 2)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_index_by_path_with_prep_method(self):
        '''Test indexers.index_by_path() with a prep_method.'''

        index = indexers.index_by_path(
            [{'foo': d} for d in FOREST_WIDE_1],
            'A.[].B',
            prep_method=lambda x: x['foo']
            )

        self.assertItemsEqual(index.keys(), ['b1', 'b2'])
        self.assertEqual(len(index['b1']), 3)
        self.assertEqual(len(index['b2']), 2)
        self.assertEqual(index['b1'][0].keys(), ['foo'])
        self.assertEqual(index['b2'][0].keys(), ['foo'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_index_by_path_with_key_method(self):
        '''Test indexers.index_by_path() with a key_method.'''

        index = indexers.index_by_path(
            SIMPLE_DATA, 'name', key_method=lambda x: x[-1]
            )

        self.assertEqual(len(index), len(SIMPLE_DATA))
        for key in [d['name'][-1] for d in SIMPLE_DATA]:
            self.assertIn(key, index)

        # - - - - - - - - - - - - - - - -

        index = indexers.index_by_path(
            SIMPLE_DATA, 'type', key_method=lambda x: x[-1]
            )
        types = list(set([d['type'][-1] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), len(types))
        for key in types:
            self.assertIn(key, index)
            self.assertEqual(
                len(index[key]), len(SIMPLE_DATA) / len(types)
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_index_by_path_with_value_method(self):
        '''Test indexers.index_by_path() with a value_method.'''

        index = indexers.index_by_path(
            SIMPLE_DATA,
            'type',
            value_method=lambda x: sorted(x.keys())
            )
        types = list(set([d['type'] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), len(types))

        for key in types:
            self.assertIn(key, index)
            # Since the kayes are the same, the index value should
            # only have one entry.
            self.assertEqual(len(index[key]), 1)
            self.assertEqual(
                index[key],
                [sorted(['name', 'type', 'size'])]
                )

        # - - - - - - - - - - - - - - - -

        index = indexers.index_by_path(
            SIMPLE_DATA,
            'type',
            value_method=lambda x: sorted(x.values())
            )

        types = list(set([d['type'] for d in SIMPLE_DATA]))
        results = {
            'type_1': [
                sorted(['name_a', 'type_1', 1]),
                sorted(['name_b', 'type_1', 2]),
                sorted(['name_c', 'type_1', 3]),
                ],
            'type_2': [
                sorted(['name_d', 'type_2', 1]),
                sorted(['name_e', 'type_2', 2]),
                sorted(['name_f', 'type_2', 3]),
                ]
            }

        self.assertEqual(len(index), len(types))

        for key in types:
            self.assertIn(key, index)
            self.assertEqual(
                len(index[key]), len(SIMPLE_DATA) / len(types)
                )
            self.assertItemsEqual(index[key], results[key])

        # - - - - - - - - - - - - - - - -

        index = indexers.index_by_path(
            SIMPLE_DATA,
            'type',
            key_method=lambda x: x[-1],
            value_method=lambda x: sorted(x.keys())
            )
        types = list(set([d['type'][-1] for d in SIMPLE_DATA]))

        self.assertEqual(len(index), len(types))

        for key in types:
            self.assertIn(key, index)
            # Since the kayes are the same, the index value should
            # only have one entry.
            self.assertEqual(len(index[key]), 1)
            self.assertEqual(
                index[key],
                [sorted(['name', 'type', 'size'])]
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestIndexByMethod(unittest.TestCase):
    '''Basic test cases for indexers.index_by_method().'''

    SIMPLE_DATA = [
        {'name': 'name_a', 'type': 'type_1', 'size': 1},
        {'name': 'name_b', 'type': 'type_1', 'size': 2},
        {'name': 'name_c', 'type': 'type_1', 'size': 3},
        {'name': 'name_d', 'type': 'type_2', 'size': 1},
        {'name': 'name_e', 'type': 'type_2', 'size': 2},
        {'name': 'name_f', 'type': 'type_2', 'size': 3},
        ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Common class level setup.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_index_by_method(self):
        '''Test indexers.index_by_method().'''

        # - - - - - - - - - - - - - - - -
        # Return a scalar.
        index = indexers.index_by_method(
            SIMPLE_DATA, lambda x: x['name']
            )
        self.assertEqual(len(index), len(SIMPLE_DATA))
        for key in [d['name'] for d in SIMPLE_DATA]:
            self.assertIn(key, index)

        # - - - - - - - - - - - - - - - -
        # Return a singleton list.
        index = indexers.index_by_method(
            SIMPLE_DATA, lambda x: [x['name']]
            )
        self.assertEqual(len(index), len(SIMPLE_DATA))
        for key in [d['name'] for d in SIMPLE_DATA]:
            self.assertIn(key, index)

        # - - - - - - - - - - - - - - - -
        # Return a multiple item list.
        index = indexers.index_by_method(
            SIMPLE_DATA,
            lambda x: [x['name'], x['type']]
            )
        self.assertEqual(
            len(index),
            len(SIMPLE_DATA) + 2.  # Name is unique, there are two types.
            )
        for key in [d['name'] for d in SIMPLE_DATA]:
            self.assertIn(key, index)
        for key in [d['type'] for d in SIMPLE_DATA]:
            self.assertIn(key, index)
        for key in [d['name'] for d in SIMPLE_DATA]:
            self.assertEqual(len(index[key]), 1)
        for key in [d['type'] for d in SIMPLE_DATA]:
            self.assertEqual(len(index[key]), 3)

        # - - - - - - - - - - - - - - - -
        # Return a scalar.
        index = indexers.index_by_method(
            FOREST_WIDE_1,
            lambda x: len(x['A'])
            )

        self.assertItemsEqual(index.keys(), [0, 1])
        self.assertEqual(len(index[0]), 1)
        self.assertEqual(len(index[1]), 6)

        # - - - - - - - - - - - - - - - -
        # Return a singleton list.
        index = indexers.index_by_method(
            FOREST_WIDE_1,
            lambda x: [len(x['A'])]
            )

        self.assertItemsEqual(index.keys(), [0, 1])
        self.assertEqual(len(index[0]), 1)
        self.assertEqual(len(index[1]), 6)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestIndexSubtreesByPaths(unittest.TestCase):
    '''Basic test cases for indexers.index_subtrees_by_paths().'''

    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        def make_forest(cls, size=6):
            '''Generate a sample forest for indexing.'''
            return [
                {
                    'name': 'record_%s' % num,
                    'group': 'group_%s' % (num % 3),
                    'slithy': {'A': num % 2, 'B': 'b%s' % num},
                    'tove': json.dumps({'A': num % 2, 'B': 'b%s' % num})
                    }
                for num in range(size)
                ]

        cls.make_forest = make_forest

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_index_subtrees_by_paths(self):
        '''Test indexers.index_subtrees_by_paths().'''

        # indexers.index_subtrees_by_paths(
        #     forest, paths, subtree_paths,
        #     prep_method=None, key_method=None, value_method=None,
        #     )

        forest = self.make_forest()
        index = indexers.index_subtrees_by_paths(
            forest, ['name'], ['name']
            )

        self.assertEqual(index.keys(), ['name'])
        self.assertEqual(len(index['name']), 6)

        for k, v in index['name'].items():
            self.assertIn(k, [x['name'] for x in forest])
            self.assertEqual(v, [k])

        # - - - - - - - - - - - - - - - -

        forest = self.make_forest()
        index = indexers.index_subtrees_by_paths(
            forest, ['group'], ['group']
            )

        self.assertEqual(index.keys(), ['group'])
        self.assertEqual(len(index['group']), 3)

        for k, v in index['group'].items():
            self.assertIn(k, [x['group'] for x in forest])
            self.assertEqual(v, [k])

        # - - - - - - - - - - - - - - - -

        forest = self.make_forest()
        index = indexers.index_subtrees_by_paths(
            forest, ['group'], ['name']
            )

        self.assertEqual(index.keys(), ['group'])
        self.assertEqual(len(index['group']), 3)

        for k, v in index['group'].items():
            self.assertIn(k, [x['group'] for x in forest])
            self.assertItemsEqual(
                v,
                [x['name'] for x in forest if x['group'] == k]
                )

        # - - - - - - - - - - - - - - - -

        forest = self.make_forest()
        index = indexers.index_subtrees_by_paths(
            forest, ['name'], ['slithy']
            )

        self.assertEqual(index.keys(), ['name'])
        self.assertEqual(len(index['name']), 6)

        for k, v in index['name'].items():
            self.assertIn(k, [x['name'] for x in forest])
            self.assertItemsEqual(
                v,
                [x['slithy'] for x in forest if x['name'] == k]
                )

        # - - - - - - - - - - - - - - - -

        forest = self.make_forest()
        index = indexers.index_subtrees_by_paths(
            forest, ['group'], ['slithy']
            )

        self.assertEqual(index.keys(), ['group'])
        self.assertEqual(len(index['group']), 3)

        for k, v in index['group'].items():
            self.assertIn(k, [x['group'] for x in forest])
            self.assertItemsEqual(
                v,
                [x['slithy'] for x in forest if x['group'] == k]
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_index_subtrees_by_paths_with_prep_method(self):
        '''Test indexers.index_subtrees_by_paths with a prep_method.'''

        def tove_from_json(tree):
            '''Replace the tove value with it's json_loads().'''
            tree['tove'] = json.loads(tree['tove'])
            return tree

        forest = self.make_forest()
        index = indexers.index_subtrees_by_paths(
            forest, ['group'], ['tove'],
            prep_method=lambda x: tove_from_json(x)
            )

        self.assertEqual(index.keys(), ['group'])
        self.assertEqual(len(index['group']), 3)

        for k, v in index['group'].items():
            self.assertIn(k, [x['group'] for x in forest])
            self.assertItemsEqual(
                v,
                [x['slithy'] for x in forest if x['group'] == k]
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_index_subtrees_by_paths_with_key_method(self):
        '''Test indexers.index_subtrees_by_paths with a key_method.'''

        forest = self.make_forest()
        index = indexers.index_subtrees_by_paths(
            forest, ['group'], ['name'],
            key_method=lambda x: x[-1]
            )

        self.assertEqual(index.keys(), ['group'])
        self.assertEqual(len(index['group']), 3)

        for k, v in index['group'].items():
            self.assertIn(k, [x['group'][-1] for x in forest])
            self.assertItemsEqual(
                v,
                [
                    x['name'] for x in forest
                    if x['group'] == 'group_%s' % k
                    ]
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_index_subtrees_by_paths_with_value_method(self):
        '''Test indexers.index_subtrees_by_paths with a key_method.'''

        forest = self.make_forest()
        index = indexers.index_subtrees_by_paths(
            forest, ['group'], ['tove'],
            value_method=lambda x: json.loads(x)
            )

        self.assertEqual(index.keys(), ['group'])
        self.assertEqual(len(index['group']), 3)

        for k, v in index['group'].items():
            self.assertIn(k, [x['group'] for x in forest])
            self.assertItemsEqual(
                v,
                [x['slithy'] for x in forest if x['group'] == k]
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestUidIndex(unittest.TestCase):
    '''Basic test cases for indexers.uid_index().'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Common class level fixture.'''
        cls.uid_a = [
            {'a': 1, 'b': 2},
            {'a': 2, 'b': 2},
            {'a': 'apple', 'b': 2},
            ]
        cls.indexed_uid_a = {
            1: {'a': 1, 'b': 2},
            2: {'a': 2, 'b': 2},
            'apple': {'a': 'apple', 'b': 2}
            }

        # - - - - - - - - - - - - - - - -
        cls.uid_deep_a = [
            {'x': {'a': 1}, 'b': 2},
            {'x': {'a': 2}, 'b': 2},
            {'x': {'a': 'apple'}, 'b': 2},
            ]
        cls.indexed_uid_deep_a = {
            1: {'x': {'a': 1}, 'b': 2},
            2: {'x': {'a': 2}, 'b': 2},
            'apple': {'x': {'a': 'apple'}, 'b': 2}
            }

        # # - - - - - - - - - - - - - - - -
        # TODO: We ought to use these in some tests...
        # cls.uid_multi_a = [
        #     {'x': {'a': 1}, 'b': 2},
        #     {'x': {'a': 2}, 'b': 2},
        #     {'x': {'a': 'apple'}, 'b': 2},
        #     ]
        # cls.indexed_uid_multi_a = {
        #     1: {'x': {'a': 1}, 'b': 2},
        #     2: {'x': {'a': 2}, 'b': 2},
        #     'apple': {'x': {'a': 'apple'}, 'b': 2}
        #     }

        # - - - - - - - - - - - - - - - -
        cls.uids_not_unique = [
            {'a': 1, 'b': 2},
            {'a': 2, 'b': 2},
            {'a': 1, 'b': 2},
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_uid_index_error(self):
        '''Test indexers.uid_index() errors.'''
        # pylint: disable=no-value-for-parameter
        # pylint: disable=unexpected-keyword-arg

        # No uid path or method defined.
        with self.assertRaises(TypeError):
            indexers.uid_index(self.uid_a)

        # Both uid path and method defined.
        with self.assertRaises(TypeError):
            indexers.uid_index(
                self.uid_a, uid_path='a', uid_method=lambda x: x['a']
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_uid_index_by_keys(self):
        '''Test indexers.uid_index() by key.'''

        indexed = indexers.uid_index(self.uid_a, uid_path='a')
        self.assertEqual(indexed, self.indexed_uid_a)

        indexed = indexers.uid_index(self.uid_deep_a, uid_path='x.a')
        self.assertEqual(indexed, self.indexed_uid_deep_a)

        with self.assertRaises(KeyError):
            indexers.uid_index(self.uid_a, uid_path='b')

        with self.assertRaises(KeyError):
            indexers.uid_index(self.uids_not_unique, uid_path='a')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_indexers_uid_index_by_method(self):
        '''Test indexers.uid_index() by method.'''

        indexed = indexers.uid_index(
            self.uid_a, uid_method=lambda x: x['a']
            )
        self.assertEqual(indexed, self.indexed_uid_a)

        indexed = indexers.uid_index(
            self.uid_deep_a, uid_method=lambda x: x['x']['a']
            )
        self.assertEqual(indexed, self.indexed_uid_deep_a)

        with self.assertRaises(KeyError):
            indexers.uid_index(
                self.uid_a, uid_method=lambda x: x['b']
                )

        with self.assertRaises(KeyError):
            indexers.uid_index(
                self.uids_not_unique, uid_method=lambda x: x['a']
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestSubindexList(unittest.TestCase):
    '''Basic test cases for indexers.subindex_list().'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_subindex_list_parameter_errors(self):
        '''Test subindex_list() function call parameter errors.'''

        with self.assertRaises(ValueError):
            indexers.subindex_list([])

        with self.assertRaises(ValueError):
            indexers.subindex_list([], index_keys=[])

        with self.assertRaises(ValueError):
            indexers.subindex_list([], index_keys=None, index_items=None)

        with self.assertRaises(ValueError):
            indexers.subindex_list([], index_items={})

        with self.assertRaises(ValueError):
            indexers.subindex_list([], index_keys=['a'], index_items={'a': 1})

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_subindex_list_empty(self):
        '''Test subindex_list() with an empty list of dicts.'''

        result = indexers.subindex_list([], index_keys=['a'])
        self.assertEqual(result, [])

        result = indexers.subindex_list([], index_items={'a': [1]})
        self.assertEqual(result, [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_subindex_list_singleton_dataset(self):
        '''Test subindex_list() with a single singleton dict.'''

        singleton_dataset = [
            {'a': 1}, {'a': 2}, {'a': 3}, {'a': 2}, {'a': 1},
            ]

        # - - - - - - - - - - - - - - - -
        result = indexers.subindex_list(
            singleton_dataset, index_keys=['c']
            )
        self.assertEqual(len(result), 0)

        # - - - - - - - - - - - - - - - -
        result = indexers.subindex_list(
            singleton_dataset, index_keys=['a']
            )
        self.assertEqual(len(result), 3)
        # [
        #     {'indexed_items': [['a', 1]], 'elements': [{'a': 1}, {'a': 1}]},
        #     {'indexed_items': [['a', 2]], 'elements': [{'a': 2}, {'a': 2}]},
        #     {'indexed_items': [['a', 3]], 'elements': [{'a': 3}]}
        #     ]

        self.assertEqual(result[0]['indexed_items'], (('a', 1),))
        self.assertEqual(result[1]['indexed_items'], (('a', 2),))
        self.assertEqual(result[2]['indexed_items'], (('a', 3),))
        self.assertEqual(result[0]['elements'], [{'a': 1}, {'a': 1}])
        self.assertEqual(result[1]['elements'], [{'a': 2}, {'a': 2}])
        self.assertEqual(result[2]['elements'], [{'a': 3}])

        # - - - - - - - - - - - - - - - -
        result = indexers.subindex_list(
            singleton_dataset, index_items={'a': [3, 2]}
            )
        self.assertEqual(len(result), 2)
        # [
        #     {'indexed_items': [['a', 1]], 'elements': [{'a': 1}, {'a': 1}]},
        #     {'indexed_items': [['a', 2]], 'elements': [{'a': 2}, {'a': 2}]},
        #     {'indexed_items': [['a', 3]], 'elements': [{'a': 3}]}
        #     ]

        self.assertEqual(result[0]['indexed_items'], (('a', 3),))
        self.assertEqual(result[1]['indexed_items'], (('a', 2),))
        self.assertEqual(result[0]['elements'], [{'a': 3}])
        self.assertEqual(result[1]['elements'], [{'a': 2}, {'a': 2}])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_subindex_list_doubleton_dataset(self):
        '''Test subindex_list() with doubleton_dataset.'''

        doubleton_dataset = [
            {'a': 1, 'b': 1},
            {'a': 2, 'b': 1},
            {'a': 3, 'b': 2},
            {'a': 2, 'b': 2},
            {'a': 1, 'b': 3},
            ]

        result = indexers.subindex_list(
            doubleton_dataset, index_keys=['a']
            )
        self.assertEqual(len(result), 3)
        # [
        #     {
        #         'indexed_items': [['a', 1]],
        #         'elements': [{'a': 1, 'b': 1}, {'a': 1, 'b': 3}]
        #         },
        #     {
        #         'indexed_items': [['a', 2]],
        #         'elements': [{'a': 2, 'b': 1}, {'a': 2, 'b': 2}]
        #         },
        #     {
        #         'indexed_items': [['a', 3]],
        #         'elements': [{'a': 3, 'b': 2}]
        #         }
        #     ]

        self.assertEqual(result[0]['indexed_items'], (('a', 1),))
        self.assertEqual(result[1]['indexed_items'], (('a', 2),))
        self.assertEqual(result[2]['indexed_items'], (('a', 3),))

        self.assertEqual(
            result[0]['elements'],
            [{'a': 1, 'b': 1}, {'a': 1, 'b': 3}]
            )
        self.assertEqual(
            result[1]['elements'],
            [{'a': 2, 'b': 1}, {'a': 2, 'b': 2}]
            )
        self.assertEqual(
            result[2]['elements'],
            [{'a': 3, 'b': 2}]
            )

        # - - - - - - - - - - - - - - - -
        result = indexers.subindex_list(
            doubleton_dataset, index_keys=['a', 'b']
            )
        self.assertEqual(len(result), 5)
        # [
        #     {
        #         'indexed_items': [['a', 1], ['b', 1]],
        #         'elements': [{'a': 1, 'b': 1}]
        #         },
        #     {
        #         'indexed_items': [['a', 1], ['b', 3]],
        #         'elements': [{'a': 1, 'b': 3}]
        #         },
        #     {
        #         'indexed_items': [['a', 2], ['b', 1]],
        #         'elements': [{'a': 2, 'b': 1}]
        #         },
        #     {
        #         'indexed_items': [['a', 2], ['b', 2]],
        #         'elements': [{'a': 2, 'b': 2}]
        #         },
        #     {
        #         'indexed_items': [['a', 3], ['b', 2]],
        #         'elements': [{'a': 3, 'b': 2}]
        #         }
        #     ]

        self.assertEqual(result[0]['indexed_items'], (('a', 1), ('b', 1)))
        self.assertEqual(result[1]['indexed_items'], (('a', 1), ('b', 3)))
        self.assertEqual(result[2]['indexed_items'], (('a', 2), ('b', 1)))
        self.assertEqual(result[3]['indexed_items'], (('a', 2), ('b', 2)))
        self.assertEqual(result[4]['indexed_items'], (('a', 3), ('b', 2)))

        self.assertEqual(result[0]['elements'], [{'a': 1, 'b': 1}])
        self.assertEqual(result[1]['elements'], [{'a': 1, 'b': 3}])
        self.assertEqual(result[2]['elements'], [{'a': 2, 'b': 1}])
        self.assertEqual(result[3]['elements'], [{'a': 2, 'b': 2}])
        self.assertEqual(result[4]['elements'], [{'a': 3, 'b': 2}])

        # - - - - - - - - - - - - - - - -
        result = indexers.subindex_list(
            doubleton_dataset,
            index_items={'a': [1, 2, 3], 'b': [1, 2, 3]}
            )
        self.assertEqual(len(result), 5)
        # [
        #     {
        #         'indexed_items': [['a', 1], ['b', 1]],
        #         'elements': [{'a': 1, 'b': 1}]
        #         },
        #     {
        #         'indexed_items': [['a', 1], ['b', 3]],
        #         'elements': [{'a': 1, 'b': 3}]
        #         },
        #     {
        #         'indexed_items': [['a', 2], ['b', 1]],
        #         'elements': [{'a': 2, 'b': 1}]
        #         },
        #     {
        #         'indexed_items': [['a', 2], ['b', 2]],
        #         'elements': [{'a': 2, 'b': 2}]
        #         },
        #     {
        #         'indexed_items': [['a', 3], ['b', 2]],
        #         'elements': [{'a': 3, 'b': 2}]
        #         }
        #     ]

        self.assertEqual(result[0]['indexed_items'], (('a', 1), ('b', 1)))
        self.assertEqual(result[1]['indexed_items'], (('a', 1), ('b', 3)))
        self.assertEqual(result[2]['indexed_items'], (('a', 2), ('b', 1)))
        self.assertEqual(result[3]['indexed_items'], (('a', 2), ('b', 2)))
        self.assertEqual(result[4]['indexed_items'], (('a', 3), ('b', 2)))

        self.assertEqual(result[0]['elements'], [{'a': 1, 'b': 1}])
        self.assertEqual(result[1]['elements'], [{'a': 1, 'b': 3}])
        self.assertEqual(result[2]['elements'], [{'a': 2, 'b': 1}])
        self.assertEqual(result[3]['elements'], [{'a': 2, 'b': 2}])
        self.assertEqual(result[4]['elements'], [{'a': 3, 'b': 2}])

        # - - - - - - - - - - - - - - - -
        result = indexers.subindex_list(
            doubleton_dataset,
            index_items={'a': [1, 3, 2], 'b': [3, 2, 1]}
            )
        self.assertEqual(len(result), 5)
        # [
        #     {
        #         'indexed_items': [['a', 1], ['b', 1]],
        #         'elements': [{'a': 1, 'b': 1}]
        #         },
        #     {
        #         'indexed_items': [['a', 1], ['b', 3]],
        #         'elements': [{'a': 1, 'b': 3}]
        #         },
        #     {
        #         'indexed_items': [['a', 2], ['b', 1]],
        #         'elements': [{'a': 2, 'b': 1}]
        #         },
        #     {
        #         'indexed_items': [['a', 2], ['b', 2]],
        #         'elements': [{'a': 2, 'b': 2}]
        #         },
        #     {
        #         'indexed_items': [['a', 3], ['b', 2]],
        #         'elements': [{'a': 3, 'b': 2}]
        #         }
        #     ]

        self.assertEqual(result[0]['indexed_items'], (('a', 1), ('b', 3)))
        self.assertEqual(result[1]['indexed_items'], (('a', 1), ('b', 1)))
        self.assertEqual(result[2]['indexed_items'], (('a', 3), ('b', 2)))
        self.assertEqual(result[3]['indexed_items'], (('a', 2), ('b', 2)))
        self.assertEqual(result[4]['indexed_items'], (('a', 2), ('b', 1)))

        self.assertEqual(result[0]['elements'], [{'a': 1, 'b': 3}])
        self.assertEqual(result[1]['elements'], [{'a': 1, 'b': 1}])
        self.assertEqual(result[2]['elements'], [{'a': 3, 'b': 2}])
        self.assertEqual(result[3]['elements'], [{'a': 2, 'b': 2}])
        self.assertEqual(result[4]['elements'], [{'a': 2, 'b': 1}])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_subindex_list_irregular_dataset(self):
        '''Test subindex_list() with irregular_dataset.'''

        irregular_dataset = [
            {'a': 1, 'b': 1},
            {'a': 2},
            {'b': 2},
            {'a': 2, 'b': 2},
            {'a': 1, 'b': 3},
            ]

        # - - - - - - - - - - - - - - - -
        result = indexers.subindex_list(
            irregular_dataset, index_keys=['a']
            )
        self.assertEqual(len(result), 2)

        # [
        #     {
        #         'indexed_items': [['a', 1]],
        #         'elements': [{'a': 1, 'b': 1}, {'a': 1, 'b': 3}]
        #         },
        #     {
        #         'indexed_items': [['a', 2]],
        #         'elements': [{'a': 2}, {'a': 2, 'b': 2}]
        #         }
        #     ]

        self.assertEqual(result[0]['indexed_items'], (('a', 1),))
        self.assertEqual(result[1]['indexed_items'], (('a', 2),))
        self.assertEqual(
            result[0]['elements'],
            [{'a': 1, 'b': 1}, {'a': 1, 'b': 3}]
            )
        self.assertEqual(
            result[1]['elements'],
            [{'a': 2}, {'a': 2, 'b': 2}]
            )

        # - - - - - - - - - - - - - - - -
        result = indexers.subindex_list(
            irregular_dataset, index_keys=['a', 'b']
            )
        self.assertEqual(len(result), 3)
        # [
        #     {
        #         'indexed_items': [['a', 1], ['b', 1]],
        #         'elements': [{'a': 1, 'b': 1}]
        #         },
        #     {
        #         'indexed_items': [['a', 1], ['b', 3]],
        #         'elements': [{'a': 1, 'b': 3}]
        #         },
        #     {
        #         'indexed_items': [['a', 2], ['b', 2]],
        #         'elements': [{'a': 2, 'b': 2}]
        #         }
        #     ]

        self.assertEqual(result[0]['indexed_items'], (('a', 1), ('b', 1)))
        self.assertEqual(result[1]['indexed_items'], (('a', 1), ('b', 3)))
        self.assertEqual(result[2]['indexed_items'], (('a', 2), ('b', 2)))

        self.assertEqual(result[0]['elements'], [{'a': 1, 'b': 1}])
        self.assertEqual(result[1]['elements'], [{'a': 1, 'b': 3}])
        self.assertEqual(result[2]['elements'], [{'a': 2, 'b': 2}])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestCompoundSubindexList(unittest.TestCase):
    '''Basic test cases for indexers.compound_subindex_list().'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_subindex_list_parameter_errors(self):
        '''Test compound_subindex_list() function call parameter errors.'''

        # with self.assertRaises(ValueError):
        #     indexers.compound_subindex_list([])

        with self.assertRaises(ValueError):
            indexers.compound_subindex_list(
                [], indexers=[{'index_keys': []}]
                )

        with self.assertRaises(ValueError):
            indexers.compound_subindex_list(
                [], indexers=[{'index_keys': None, 'index_items': None}]
                )

        with self.assertRaises(ValueError):
            indexers.compound_subindex_list(
                [], indexers=[{'index_items': {}}]
                )

        with self.assertRaises(ValueError):
            indexers.compound_subindex_list(
                [], indexers=[{'index_keys': ['a'], 'index_items': {'a': 1}}]
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_compound_subindex_list_empty(self):
        '''Test compound_subindex_list() with an empty list of dicts.'''

        result = indexers.compound_subindex_list(
            [], indexers=[{'index_keys': ['a']}]
            )
        self.assertEqual(result, [])

        result = indexers.compound_subindex_list(
            [], indexers=[{'index_items': {'a': [1]}}]
            )
        self.assertEqual(result, [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_compound_subindex_list_singleton_dataset(self):
        '''Test compound_subindex_list() with a single singleton dict.'''

        singleton_dataset = [
            {'a': 1}, {'a': 2}, {'a': 3}, {'a': 2}, {'a': 1},
            ]

        compound_result = indexers.compound_subindex_list(
            singleton_dataset, indexers=[{'index_keys': ['a']}]
            )
        simple_result = indexers.subindex_list(
            singleton_dataset, index_keys=['a']
            )

        self.assertEqual(compound_result, simple_result)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_compound_subindex_list_doubleton_dataset(self):
        '''Test compound_subindex_list() with a single doubleton dict.'''

        doubleton_dataset = [
            {'a': 1, 'b': 1},
            {'a': 2, 'b': 1},
            {'a': 3, 'b': 2},
            {'a': 2, 'b': 2},
            {'a': 1, 'b': 3},
            ]

        # - - - - - - - - - - - - - - - -
        result = indexers.compound_subindex_list(
            doubleton_dataset, indexers=[{'index_keys': ['a']}]
            )
        simple_result = indexers.subindex_list(
            doubleton_dataset, index_keys=['a']
            )

        self.assertEqual(result, simple_result)

        # - - - - - - - - - - - - - - - -
        result = indexers.compound_subindex_list(
            doubleton_dataset, indexers=[{'index_keys': ['a', 'b']}]
            )
        simple_result = indexers.subindex_list(
            doubleton_dataset, index_keys=['a', 'b']
            )

        self.assertEqual(result, simple_result)

        # - - - - - - - - - - - - - - - -
        result = indexers.compound_subindex_list(
            doubleton_dataset,
            indexers=[
                {'index_keys': ['a']},
                {'index_keys': ['b']}
                ]
            )
        # [
        #     {
        #         'indexed_items': [['a', 1]],
        #         'elements': [
        #             {
        #                 'indexed_items': [['b', 1]],
        #                 'elements': [{'a': 1, 'b': 1}]
        #                 },
        #             {
        #                 'indexed_items': [['b', 3]],
        #                 'elements': [{'a': 1, 'b': 3}]
        #                 }
        #             ]
        #         },
        #     {
        #         'indexed_items': [['a', 2]],
        #         'elements': [
        #             {
        #                 'indexed_items': [['b', 1]],
        #                 'elements': [{'a': 2, 'b': 1}]
        #                 },
        #             {
        #                 'indexed_items': [['b', 2]],
        #                 'elements': [{'a': 2, 'b': 2}]
        #                 }
        #             ]
        #         },
        #     {
        #         'indexed_items': [['a', 3]],
        #         'elements': [
        #             {
        #                 'indexed_items': [['b', 2]],
        #                 'elements': [{'a': 3, 'b': 2}]
        #                 }
        #             ]
        #         }
        #     ]
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]['elements']), 2)
        self.assertEqual(len(result[1]['elements']), 2)
        self.assertEqual(len(result[2]['elements']), 1)

        self.assertEqual(result[0]['indexed_items'], (('a', 1),))
        self.assertEqual(result[1]['indexed_items'], (('a', 2),))
        self.assertEqual(result[2]['indexed_items'], (('a', 3),))

        self.assertEqual(
            result[0]['elements'][0]['indexed_items'], (('b', 1),)
            )
        self.assertEqual(
            result[0]['elements'][1]['indexed_items'], (('b', 3),)
            )
        self.assertEqual(
            result[1]['elements'][0]['indexed_items'], (('b', 1),)
            )
        self.assertEqual(
            result[1]['elements'][1]['indexed_items'], (('b', 2),)
            )
        self.assertEqual(
            result[2]['elements'][0]['indexed_items'], (('b', 2),)
            )

        self.assertEqual(
            result[0]['elements'][0]['elements'], [{'a': 1, 'b': 1}]
            )
        self.assertEqual(
            result[0]['elements'][1]['elements'], [{'a': 1, 'b': 3}]
            )
        self.assertEqual(
            result[1]['elements'][0]['elements'], [{'a': 2, 'b': 1}]
            )
        self.assertEqual(
            result[1]['elements'][1]['elements'], [{'a': 2, 'b': 2}]
            )
        self.assertEqual(
            result[2]['elements'][0]['elements'], [{'a': 3, 'b': 2}]
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestInvertIndex(unittest.TestCase):
    '''Basic test cases for indexers.invert_index().'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_invert_index(self):
        '''Test indexers.invert_index().'''

        index = {}
        self.assertEqual(indexers.invert_index(index), {})

        index = {'a': []}
        self.assertEqual(indexers.invert_index(index), {})

        index = {'a': ['A'], 'b': ['B']}
        self.assertEqual(
            indexers.invert_index(index),
            {'A': ['a'], 'B': ['b']}
            )

        index = {'a1': ['A'], 'a2': ['A']}
        self.assertEqual(
            indexers.invert_index(index),
            {'A': ['a1', 'a2']}
            )

        index = {'a1': ['A1'], 'a2': ['A1', 'A2']}
        self.assertEqual(
            indexers.invert_index(index),
            {'A1': ['a1', 'a2'], 'A2': ['a2']}
            )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Define test suite.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# pylint: disable=invalid-name
load_case = unittest.TestLoader().loadTestsFromTestCase
all_suites = {
    # Lowercase these.
    'suite_TestIndexByPaths': load_case(TestIndexByPaths),
    'suite_TestIndexByPath': load_case(TestIndexByPath),
    'suite_TestIndexByMethod': load_case(TestIndexByMethod),
    'suite_TestUidIndex': load_case(TestUidIndex),
    'suite_TestSubindexList': load_case(TestSubindexList),
    'suite_TestCompoundSubindexList': load_case(TestCompoundSubindexList),
    'suite_TestInvertIndex': load_case(TestInvertIndex),
    'suite_TestIndexSubtreesByPaths': load_case(TestIndexSubtreesByPaths),
    }

master_suite = unittest.TestSuite(all_suites.values())
# pylint: enable=invalid-name

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    unittest.main()
