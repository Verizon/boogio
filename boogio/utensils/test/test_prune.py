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

'''Test cases for the prune module.'''

# pylint: disable=invalid-name

import itertools

import unittest

from boogio.utensils import prune
# from boogio.utensils import flatten

# test data
import world_structure

LI = prune.Pruner.LIST_INDICATOR
LI2 = '.'.join([LI] * 2)
LI3 = '.'.join([LI] * 3)
LI4 = '.'.join([LI] * 4)

dp = prune.dotpath


def to_sorted(arr):
    '''Sort and return a copy of a list or dict.'''
    sarr = [a for a in arr]
    sarr.sort()
    if isinstance(arr, list):
        return sarr
    else:
        return {a: arr[a] for a in sarr}


def to_spec(*paths):
    '''Make a list of paths into a prune spec.'''
    return [{'path': x} for x in paths]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestPruner(unittest.TestCase):
    '''
    Basic test cases for Pruner.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''
        Define common vaues used by multiple test cases.
        '''
        # Keep tracing from getting out of control when cases failed
        # and so didn't have a chance to turn this off.
        prune.stop_trace()

        self.linear_tree_1 = {
            'A1': {'B1': {'C1': 1}}
            }

        self.linear_tree_1_flat = [{'A1.B1.C1': 1}]

        self.linear_tree_2 = {
            'A2': {'B2': {'C2': 2}}
            }

        self.linear_tree_1_branches = [{'A1.B1.C1': 1}]
        self.linear_tree_2_branches = [{'A2.B2.C2': 2}]

        # - - - - - - - - - - - - - - - - - - - -
        self.simple_tree = {
            'A1': {'B1': {'C1': 1}},
            'A2': {'B2': {'C2': 2}},
            'A3': {'B3': {'C3': 3}},
            }

        self.simple_tree12 = {
            'A1': {'B1': {'C1': 1}},
            'A2': {'B2': {'C2': 2}},
            }

        self.shallow_tree_1 = {
            'A1': [
                {'B1': '1.1'},
                {'B1': '1.2'},
                ],
            }

        self.shallow_tree_1_flat = [
            {'A1.B1': '1.1'},
            {'A1.B1': '1.2'},
            ]

        self.shallow_tree_12 = {
            'A1': [
                {'B1': '1.1'},
                {'B1': '1.2'},
                ],
            'A2': [
                {'B2': '2.1'},
                {'B2': '2.2'},
                ],
            }

        self.array_tree_sA1B1 = [
            {'A1': {'B1': '1.1'}},
            {'A1': {'B1': '1.2'}},
            ]

        self.array_tree_sA1B1C1 = [
            {'A1': {'B1': '1.1', 'C1': '2.1'}},
            {'A1': {'B1': '1.2', 'C1': '2.2'}},
            ]

        self.array_tree_sA1sB1 = [
            {
                'A1': [
                    {'B1': '1.11'},
                    {'B1': '1.21'},
                    ],
                },
            {
                'A1': [
                    {'B1': '1.12'},
                    {'B1': '1.22'},
                    ],
                },
            ]

        self.array_tree_sA1sB1C1 = [
            {
                'A1': [
                    {'B1': '1.11', 'C1': '2.11'},
                    {'B1': '1.21', 'C1': '2.21'},
                    ],
                },
            {
                'A1': [
                    {'B1': '1.12', 'C1': '2.12'},
                    {'B1': '1.22', 'C1': '2.22'},
                    ],
                },
            ]

        self.medium_tree_A1B1sC1 = {
            'A1': {
                'B1': [
                    {'C1': '1.1'},
                    {'C1': '1.2'},
                    {'C1': '1.3'},
                    ]
                }
            }

        self.medium_tree_A2B2sC2sD2 = {
            'A2': {
                'B2': [
                    {
                        'C2': [
                            {'D2': '2.1'},
                            {'D2': '2.2'},
                            {'D2': '2.3'},
                            ]
                        },
                    ]
                }
            }

        self.medium_tree_A1B1sC1C2_A2B2sC2sD2E2C3sD2 = {
            'A1': {
                'B1': [
                    {'C1': '1.1', 'C2': '2.1'},
                    {'C1': '1.2', 'C2': '2.2'},
                    {'C1': '1.3', 'C2': '2.3'},
                    ]
                },
            'A2': {
                'B2': [
                    {
                        'C2': [
                            {'D2': '2.1', 'E2': '5.1'},
                            {'D2': '2.2', 'E2': '5.2'},
                            {'D2': '2.3', 'E2': '5.3'},
                            ]
                        },
                    {
                        'C3': [
                            {'D2': '20.1'},
                            {'D2': '20.2'},
                            {'D2': '20.3'},
                            ]
                        },
                    ]
                }
            }

        self.medium_tree_sA1B1sC1C2_A1B1sC1sD2E2C3sD2 = [
            {
                'A1': {
                    'B1': [
                        {'C1': '1.1', 'C2': '2.1'},
                        {'C1': '1.2', 'C2': '2.2'},
                        {'C1': '1.3', 'C2': '2.3'},
                        ]
                    },
                },
            {
                'A1': {
                    'B1': [
                        {
                            'C1': [
                                {'D2': '2.1', 'E2': '5.1'},
                                {'D2': '2.2', 'E2': '5.2'},
                                {'D2': '2.3', 'E2': '5.3'},
                                ]
                            },
                        {
                            'C3': [
                                {'D2': '20.1'},
                                {'D2': '20.2'},
                                {'D2': '20.3'},
                                ]
                            },
                        ]
                    }
                }
            ]

        self.medium_tree_sA1B1sC1C2_A1B1sC1sD2E2C3sD2_flat = [
            {'A1.B1.C2': '2.1', 'A1.B1.C1': '1.1'},
            {'A1.B1.C2': '2.2', 'A1.B1.C1': '1.2'},
            {'A1.B1.C2': '2.3', 'A1.B1.C1': '1.3'},
            {'A1.B1.C1.E2': '5.1', 'A1.B1.C1.D2': '2.1'},
            {'A1.B1.C1.E2': '5.2', 'A1.B1.C1.D2': '2.2'},
            {'A1.B1.C1.E2': '5.3', 'A1.B1.C1.D2': '2.3'},
            {'A1.B1.C3.D2': '20.1'},
            {'A1.B1.C3.D2': '20.2'},
            {'A1.B1.C3.D2': '20.3'}
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_pruner_init(self):
        '''
        Test basic initialization of Pruner instances.
        '''

        path_A1B1C1 = 'A1.B1.C1'
        path_A2B2C2 = 'A2.B2.C2'

        spec_A1B1C1 = {'path': path_A1B1C1}
        spec_A2B2C2 = {'path': path_A2B2C2}

        pruner = prune.Pruner()
        self.assertIsNotNone(pruner)
        self.assertEqual(len(pruner.prune_specs), 0)

        pruner = prune.Pruner(spec_A1B1C1)
        self.assertEqual(len(pruner.prune_specs), 1)

        pruner = prune.Pruner(spec_A1B1C1, spec_A2B2C2)
        self.assertEqual(len(pruner.prune_specs), 2)

        # prune_specs can be repeated.
        pruner = prune.Pruner(spec_A1B1C1, spec_A1B1C1)
        self.assertEqual(len(pruner.prune_specs), 2)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_path_formatters(self):
        '''
        Test converting paths back and forth between dot-string
        and list.
        '''

        self.assertEqual(prune.listpath([]), [])
        self.assertEqual(prune.listpath(['A']), ['A'])
        self.assertEqual(prune.listpath(['A', 'B']), ['A', 'B'])
        self.assertEqual(prune.listpath(['A', 'B', 'C']), ['A', 'B', 'C'])

        self.assertEqual(prune.listpath(''), [''])
        self.assertEqual(prune.listpath('A'), ['A'])
        self.assertEqual(prune.listpath('A.B'), ['A', 'B'])
        self.assertEqual(prune.listpath('A.B.C'), ['A', 'B', 'C'])

        self.assertEqual(
            prune.listpath('A.' + LI + '.C', no_lists=True),
            ['A', 'C']
            )
        self.assertEqual(
            prune.listpath(['A', LI, 'C'], no_lists=True),
            ['A', 'C']
            )

        self.assertEqual(prune.dotpath([]), '')
        self.assertEqual(prune.dotpath(['A']), 'A')
        self.assertEqual(prune.dotpath(['A', 'B']), 'A.B')
        self.assertEqual(prune.dotpath(['A', 'B', 'C']), 'A.B.C')

        self.assertEqual(prune.dotpath(''), '')
        self.assertEqual(prune.dotpath('A'), 'A')
        self.assertEqual(prune.dotpath('A.B'), 'A.B')
        self.assertEqual(prune.dotpath('A.B.C'), 'A.B.C')

        self.assertEqual(
            prune.dotpath('A.' + LI + '.C', no_lists=True),
            'A.C'
            )
        self.assertEqual(
            prune.dotpath(['A', LI, 'C'], no_lists=True),
            'A.C'
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_paths(self):
        '''
        Test finding paths through a tree.
        '''
        # Lists only.
        self.assertEqual(prune.paths([]), [])
        self.assertEqual(prune.paths([[]]), [LI])
        self.assertEqual(prune.paths([[[]]]), [LI2])
        self.assertEqual(prune.paths([1]), [LI])
        self.assertEqual(prune.paths([[1]]), [LI2])
        self.assertEqual(prune.paths([[[1]]]), [LI3])
        self.assertEqual(prune.paths([1, 2]), [LI])
        self.assertEqual(prune.paths([[1], [2]]), [LI2])
        self.assertEqual(
            to_sorted(prune.paths([[1], [[2]]])),
            to_sorted([LI2, LI3])
            )
        self.assertEqual(
            to_sorted(prune.paths([[[1]], [[[2]]]])),
            to_sorted([LI3, LI4])
            )

        self.assertEqual(
            prune.paths([[]], show_list_size=True),
            ['[1]']
            )
        self.assertEqual(
            prune.paths([1], show_list_size=True),
            ['[1]']
            )
        self.assertEqual(
            prune.paths([1, 2, 3], show_list_size=True),
            ['[3]']
            )
        self.assertEqual(
            prune.paths([1, 2, [3, 4]], show_list_size=True),
            ['[3]', '[3].[2]']
            )

        # Dicts only.
        self.assertEqual(prune.paths({}), [])
        self.assertEqual(prune.paths({'a': 1}), ['a'])
        self.assertEqual(prune.paths({'a': 1, 'b': 2}), ['a', 'b'])
        self.assertEqual(prune.paths({'a': {'b': 1}}), ['a.b'])
        self.assertEqual(prune.paths({'a': {'b': 1, 'c': 2}}), ['a.b', 'a.c'])
        self.assertEqual(
            prune.paths(
                {'a': {'b': 1, 'c': {'d': 2}}}
                ),
            ['a.b', 'a.c.d']
            )

        # Mixes of lists and dicts.
        self.assertEqual(prune.paths([{}]), [LI])
        self.assertEqual(prune.paths([{}, []]), [LI])
        self.assertEqual(prune.paths({'a': []}), ['a'])
        self.assertEqual(prune.paths({'a': [1]}), ['a.' + LI])
        self.assertEqual(prune.paths([{'a': []}]), [LI + '.a'])
        self.assertEqual(prune.paths([{'a': []}, 1]), [LI + '.a', LI])
        self.assertEqual(prune.paths([{'a': []}]), [LI + '.a'])
        self.assertEqual(prune.paths([{'a': []}, {'a': []}]), [LI + '.a'])
        self.assertEqual(
            prune.paths([{'a': []}, 1, {'a': []}]),
            [LI + '.a', LI]
            )
        self.assertEqual(
            to_sorted(prune.paths([{'a': []}, {'b': []}])),
            to_sorted([LI + '.a', LI + '.b'])
            )
        self.assertEqual(
            to_sorted(prune.paths(
                [
                    {'a': []},
                    {'a': [1]},
                    {'a': [{'a': []}]},
                    {'b': [{'a': []}]}
                    ]
                )),
            to_sorted([
                dp([LI, 'a']),
                dp([LI, 'a', LI, 'a']),
                dp([LI, 'a', LI]),
                dp([LI, 'b', LI, 'a'])
                ])
            )
        self.assertEqual(
            to_sorted(prune.paths(
                [[
                    {'a': []},
                    {'a': [1]},
                    {'a': [{'a': []}]},
                    {'b': [{'a': []}]}
                    ]]
                )),
            to_sorted([
                dp([LI, LI, 'a']),
                dp([LI, LI, 'a', LI, 'a']),
                dp([LI, LI, 'a', LI]),
                dp([LI, LI, 'b', LI, 'a'])
                ])
            )
        self.assertEqual(
            to_sorted(prune.paths(
                [[
                    {'a': []},
                    {'a': [1]},
                    {'a': [{'a': []}]},
                    {'b': [{'a': []}]},
                    {'a': []},
                    {'a': [1]},
                    {'a': [{'a': []}]},
                    {'b': [{'a': []}]}
                    ]]
                )),
            to_sorted([
                dp([LI, LI, 'a']),
                dp([LI, LI, 'a', LI, 'a']),
                dp([LI, LI, 'a', LI]),
                dp([LI, LI, 'b', LI, 'a'])
                ])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_prune_spec_to_tree(self):
        '''
        Test conversion of prune_specs to dicts with specified values.
        '''

        path_A1B1C1 = ['A1', 'B1', 'C1']
        path_A1sB1 = ['A1', LI, 'B1']
        path_A1B1s = ['A1', 'B1', LI]
        path_A1B1sC1 = ['A1', 'B1', LI, 'C1']
        path_A2B2sC2sD2 = [
            'A2', 'B2', LI, 'C2', LI, 'D2'
            ]

        # pylint: disable=missing-docstring
        def dict_A1B1C1(val):
            return {'A1': {'B1': {'C1': val}}}

        def dict_A1sB1(val):
            return {'A1': [{'B1': val}]}

        def dict_A1B1s(val):
            return {'A1': {'B1': [val]}}

        def dict_A1B1sC1(val):
            return {'A1': {'B1': [{'C1': val}]}}

        def dict_A2B2sC2sD2(val):
            return {'A2': {'B2': [{'C2': [{'D2': val}]}]}}

        # - - - - - - - - - - - - - - - - - - - -
        # None as the value.
        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(
            prune.Pruner.path_to_tree(path_A1B1C1),
            dict_A1B1C1(None)
            )

        self.assertEqual(
            prune.Pruner.path_to_tree(path_A1sB1),
            dict_A1sB1(None)
            )

        self.assertEqual(
            prune.Pruner.path_to_tree(path_A1B1s),
            dict_A1B1s(None)
            )

        self.assertEqual(
            prune.Pruner.path_to_tree(path_A1B1sC1),
            dict_A1B1sC1(None)
            )

        self.assertEqual(
            prune.Pruner.path_to_tree(path_A2B2sC2sD2),
            dict_A2B2sC2sD2(None)
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Specify a value.
        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(
            prune.Pruner.path_to_tree(path_A1B1C1, 42),
            dict_A1B1C1(42)
            )

        self.assertEqual(
            prune.Pruner.path_to_tree(path_A1sB1, 42),
            dict_A1sB1(42)
            )

        self.assertEqual(
            prune.Pruner.path_to_tree(path_A1B1s, 42),
            dict_A1B1s(42)
            )

        self.assertEqual(
            prune.Pruner.path_to_tree(path_A1B1sC1, 42),
            dict_A1B1sC1(42)
            )

        self.assertEqual(
            prune.Pruner.path_to_tree(path_A2B2sC2sD2, 42),
            dict_A2B2sC2sD2(42)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_subtree_dict_only(self):
        '''
        Test subtree extraction from nested dicts with no lists
        present in source.
        '''

        pruner = prune.Pruner()

        # - - - - - - - - - - - - - - - - - - - -
        # Simple extraction.

        path_A1B1C1 = dp(['A1', 'B1', 'C1'])
        path_A2B2C2 = dp(['A2', 'B2', 'C2'])
        path_A1B1C2 = dp(['A1', 'B1', 'C2'])
        path_A1B2C2 = dp(['A1', 'B2', 'C2'])

        # - - - - - - - - - - - - - - - - - - - -
        pruned_tree = pruner.get_subtree(
            self.linear_tree_1,
            to_spec(path_A1B1C1)
            )
        self.assertEqual(pruned_tree, self.linear_tree_1)

        pruned_tree = pruner.get_subtree(
            self.simple_tree,
            to_spec(path_A1B1C1)
            )
        self.assertEqual(pruned_tree, self.linear_tree_1)

        # - - - - - - - - - - - - - - - - - - - -
        pruned_tree = pruner.get_subtree(
            self.linear_tree_2,
            to_spec(path_A2B2C2)
            )
        self.assertEqual(pruned_tree, self.linear_tree_2)

        pruned_tree = pruner.get_subtree(
            self.simple_tree,
            to_spec(path_A2B2C2)
            )
        self.assertEqual(pruned_tree, self.linear_tree_2)

        # - - - - - - - - - - - - - - - - - - - -
        pruned_tree = pruner.get_subtree(
            self.linear_tree_1,
            to_spec(path_A2B2C2)
            )
        self.assertEqual(pruned_tree, None)

        pruned_tree = pruner.get_subtree(
            self.linear_tree_2,
            to_spec(path_A1B1C1)
            )
        self.assertEqual(pruned_tree, None)

        pruned_tree = pruner.get_subtree(
            self.linear_tree_1,
            to_spec(path_A1B2C2)
            )
        self.assertEqual(pruned_tree, None)

        pruned_tree = pruner.get_subtree(
            self.linear_tree_1,
            to_spec(path_A1B1C2)
            )
        self.assertEqual(pruned_tree, None)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_subtree_dicts_and_lists(self):
        '''
        Test subtree extraction from trees that include a mix of
        lists and dicts.
        '''

        pruner = prune.Pruner()

        # - - - - - - - - - - - - - - - - - - - -

        path_A1sB1 = dp(['A1', LI, 'B1'])
        path_A1sB2 = dp(['A1', LI, 'B2'])

        pruned_tree = pruner.get_subtree(
            self.shallow_tree_1,
            to_spec(path_A1sB1)
            )
        self.assertEqual(pruned_tree, self.shallow_tree_1)

        pruned_tree = pruner.get_subtree(
            self.shallow_tree_12,
            to_spec(path_A1sB1)
            )
        self.assertEqual(pruned_tree, self.shallow_tree_1)

        pruned_tree = pruner.get_subtree(
            self.shallow_tree_1,
            to_spec(path_A1sB2)
            )
        self.assertEqual(pruned_tree, None)

        pruned_tree = pruner.get_subtree(
            self.shallow_tree_12,
            to_spec(path_A1sB2)
            )
        self.assertEqual(pruned_tree, None)

        # # - - - - - - - - - - - - - - - - - - - -

        path_A1B1sC1 = dp(['A1', 'B1', LI, 'C1'])
        path_A2B2sC2sD2 = dp([
            'A2', 'B2', LI, 'C2', LI, 'D2'
            ])
        path_A2B2sC3sE2 = dp([
            'A2', 'B2', LI, 'C3', LI, 'E2'
            ])

        pruned_tree = pruner.get_subtree(
            self.medium_tree_A1B1sC1C2_A2B2sC2sD2E2C3sD2,
            to_spec(path_A1B1sC1)
            )
        self.assertEqual(pruned_tree, self.medium_tree_A1B1sC1)

        pruned_tree = pruner.get_subtree(
            self.medium_tree_A1B1sC1C2_A2B2sC2sD2E2C3sD2,
            to_spec(path_A2B2sC2sD2)
            )
        self.assertEqual(pruned_tree, self.medium_tree_A2B2sC2sD2)

        pruned_tree = pruner.get_subtree(
            self.medium_tree_A1B1sC1C2_A2B2sC2sD2E2C3sD2,
            to_spec(path_A2B2sC3sE2)
            )
        self.assertEqual(pruned_tree, None)

        # - - - - - - - - - - - - - - - - - - - -

        path_s = dp([LI])
        path_sB1 = dp([LI, 'B1'])
        path_sA1B1 = dp([LI, 'A1', 'B1'])
        path_sA1s = dp([LI, 'A1', LI])
        path_sA1sB1 = dp([LI, 'A1', LI, 'B1'])

        pruned_tree = pruner.get_subtree(
            self.array_tree_sA1B1,
            to_spec(path_sB1)
            )
        self.assertEqual(pruned_tree, None)

        pruned_tree = pruner.get_subtree(
            self.array_tree_sA1B1,
            to_spec(path_s)
            )
        self.assertEqual(pruned_tree, self.array_tree_sA1B1)

        pruned_tree = pruner.get_subtree(
            self.array_tree_sA1B1,
            to_spec(path_sA1B1)
            )
        self.assertEqual(pruned_tree, self.array_tree_sA1B1)

        pruned_tree = pruner.get_subtree(
            self.array_tree_sA1sB1,
            to_spec(path_sA1s)
            )
        self.assertEqual(pruned_tree, self.array_tree_sA1sB1)

        pruned_tree = pruner.get_subtree(
            self.array_tree_sA1B1C1,
            to_spec(path_sA1B1)
            )
        self.assertEqual(pruned_tree, self.array_tree_sA1B1)

        pruned_tree = pruner.get_subtree(
            self.array_tree_sA1sB1C1,
            to_spec(path_sB1)
            )
        self.assertEqual(pruned_tree, None)

        pruned_tree = pruner.get_subtree(
            self.array_tree_sA1sB1C1,
            to_spec(path_sA1s)
            )
        self.assertEqual(pruned_tree, self.array_tree_sA1sB1C1)

        pruned_tree = pruner.get_subtree(
            self.array_tree_sA1sB1C1,
            to_spec(path_sA1sB1)
            )
        self.assertEqual(pruned_tree, self.array_tree_sA1sB1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_leaf_satisfies(self):
        '''Test prune.leaf_satisfies(). '''

        # pylint: disable=missing-docstring
        pruner = prune.Pruner()

        def scalar_is_positive_choke_on_negative(x):
            if x < 0:
                raise ValueError('Choke!')
            return isinstance(x, int) and x > 0

        def scalar_is_positive(x):
            return isinstance(x, int) and x > 0

        def list_is_empty(x):
            return x == []

        def dict_values_include_5(x):
            return 5 in x.values()

        # sat = pruner.leaf_satisfies([], '[]', list_is_empty)
        # self.assertTrue(sat)

        sat = pruner.leaf_satisfies(5, None, scalar_is_positive)
        self.assertTrue(sat)

        sat = pruner.leaf_satisfies(0, None, scalar_is_positive)
        self.assertEqual(sat, False)

        sat = pruner.leaf_satisfies([5], None, scalar_is_positive)
        self.assertEqual(sat, False)

        sat = pruner.leaf_satisfies(
            [-2, 0, 5],
            '[]', scalar_is_positive
            )
        self.assertTrue(sat)

        # These next two tests together demonstrate that leaf_satisfies
        # will return without evaluating further into a list as soon as
        # it finds a value that satisfies its criterion.
        with self.assertRaises(ValueError):
            sat = pruner.leaf_satisfies(
                [0, -1, 5],
                ['[]'], scalar_is_positive_choke_on_negative
                )

        sat = pruner.leaf_satisfies(
            [5, 0, -1],
            '[]', scalar_is_positive_choke_on_negative
            )
        self.assertTrue(sat)

        # Missing matches down the path.
        sat = pruner.leaf_satisfies(
            {'A': {'x': -2, 'y': 0, 'z': 5}},
            'B.x', scalar_is_positive
            )
        self.assertEqual(sat, False)
        sat = pruner.leaf_satisfies(
            {'A': [], 'B': {'x': -2, 'y': 0, 'z': 5}},
            'A.[].x', scalar_is_positive
            )
        self.assertEqual(sat, False)

        sat = pruner.leaf_satisfies(
            {'A': [{'x': []}]},
            'A.[].x.[].y', scalar_is_positive
            )
        self.assertEqual(sat, False)

        sat = pruner.leaf_satisfies(
            {'x': -2, 'y': 0, 'z': 5},
            None, dict_values_include_5
            )
        self.assertTrue(sat)

        sat = pruner.leaf_satisfies(
            [5],
            '[]', scalar_is_positive)
        self.assertTrue(sat)

        sat = pruner.leaf_satisfies(
            [{'x': -2, 'y': 0, 'z': 5}],
            '[]', dict_values_include_5
            )
        self.assertTrue(sat)

        sat = pruner.leaf_satisfies(
            [{'x': -2, 'z': 5}, {'x': -2, 'z': -3}],
            '[]', dict_values_include_5
            )
        self.assertTrue(sat)

        sat = pruner.leaf_satisfies(
            [{'x': -2, 'y': 0, 'z': 5}],
            '[].x', scalar_is_positive
            )

        sat = pruner.leaf_satisfies(
            [{'x': -2, 'y': 0, 'z': 5}],
            '[].z', scalar_is_positive
            )
        self.assertTrue(sat)

        sat = pruner.leaf_satisfies(
            [{'x': -2, 'z': 5}, {'x': -2, 'z': -3}],
            '[].z', scalar_is_positive
            )
        self.assertTrue(sat)

        sat = pruner.leaf_satisfies(
            [{'x': -2, 'z': 0}, {'x': -2, 'z': -3}],
            ['[]', 'z'], scalar_is_positive
            )
        self.assertEqual(sat, False)

        sat = pruner.leaf_satisfies(
            {'x': -2, 'y': 0, 'z': [0, 5]},
            ['z', '[]'], scalar_is_positive
            )
        self.assertTrue(sat)

        sat = pruner.leaf_satisfies(
            {'a': {'x': -2, 'y': 0, 'z': [0, 5]}, 'b': [1, 2]},
            ['a', 'z', '[]'], scalar_is_positive
            )
        self.assertTrue(sat)

        sat = pruner.leaf_satisfies(
            {'a': {'x': -2, 'y': 0, 'z': []}, 'b': [1, 2]},
            ['a', 'z'], list_is_empty
            )
        self.assertTrue(sat)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_prune_leaves(self):
        '''
        Test extraction of values at a specifed path into a tree.
        '''

        pruner = prune.Pruner()

        # - - - - - - - - - - - - - - - - - - - -
        # Simple extraction.

        path_A1B1C1 = ['A1', 'B1', 'C1']
        path_A2B2C2 = ['A2', 'B2', 'C2']
        path_sA1B1 = ['[]', 'A1', 'B1']
        path_sA1 = ['[]', 'A1']
        path_sA1sB1 = ['[]', 'A1', '[]', 'B1']

        self.assertEqual(
            pruner.prune_leaves(
                self.linear_tree_1,
                [{'path': path_A1B1C1}]
                ),
            {
                prune.dotpath(path_A1B1C1):
                [self.linear_tree_1['A1']['B1']['C1']]
                }
            )

        self.assertEqual(
            pruner.prune_leaves(
                self.simple_tree,
                [{'path': path_A1B1C1}, {'path': path_A2B2C2}]
                ),
            {
                prune.dotpath(path_A1B1C1):
                [self.simple_tree['A1']['B1']['C1']],
                prune.dotpath(path_A2B2C2):
                [self.simple_tree['A2']['B2']['C2']]
                }
            )

        self.assertEqual(
            pruner.prune_leaves(
                self.array_tree_sA1B1,
                [{'path': path_sA1B1}]
                ),
            {
                prune.dotpath(path_sA1B1, no_lists=True):
                [x['A1']['B1'] for x in self.array_tree_sA1B1]
                }
            )

        self.assertEqual(
            pruner.prune_leaves(
                self.array_tree_sA1sB1,
                [{'path': path_sA1}]
                ),
            {
                prune.dotpath(path_sA1, no_lists=True):
                [x['A1'] for x in self.array_tree_sA1sB1]
                }
            )

        self.assertEqual(
            pruner.prune_leaves(
                self.array_tree_sA1sB1,
                [{'path': path_sA1sB1}]
                ),
            {
                prune.dotpath(path_sA1sB1, no_lists=True):
                [
                    y['B1'] for y in itertools.chain(
                        *[x['A1'] for x in self.array_tree_sA1sB1]
                        )
                    ]
                }
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_rake_leaves(self):
        '''
        Test extraction of values at a specifed path into a tree.
        '''

        pruner = prune.Pruner()

        # - - - - - - - - - - - - - - - - - - - -
        # Simple extraction.

        path_A1B1C1 = ['A1', 'B1', 'C1']
        path_A2B2C2 = ['A2', 'B2', 'C2']
        path_sA1B1 = ['[]', 'A1', 'B1']
        path_sA1 = ['[]', 'A1']
        path_sA1sB1 = ['[]', 'A1', '[]', 'B1']

        self.assertItemsEqual(
            pruner.rake_leaves(
                self.linear_tree_1,
                [{'path': path_A1B1C1}]
                ),
            [self.linear_tree_1['A1']['B1']['C1']]
            )

        self.assertItemsEqual(
            pruner.rake_leaves(
                self.simple_tree,
                [{'path': path_A1B1C1}, {'path': path_A2B2C2}]
                ),
            [
                self.simple_tree['A1']['B1']['C1'],
                self.simple_tree['A2']['B2']['C2']
                ]
            )

        self.assertItemsEqual(
            pruner.rake_leaves(
                self.array_tree_sA1B1,
                [{'path': path_sA1B1}]
                ),
            [x['A1']['B1'] for x in self.array_tree_sA1B1]
            )

        self.assertItemsEqual(
            pruner.rake_leaves(
                self.array_tree_sA1sB1,
                [{'path': path_sA1}]
                ),
            [x['A1'] for x in self.array_tree_sA1sB1]
            )

        self.assertItemsEqual(
            pruner.rake_leaves(
                self.array_tree_sA1sB1,
                [{'path': path_sA1sB1}]
                ),
            [
                y['B1'] for y in itertools.chain(
                    *[x['A1'] for x in self.array_tree_sA1sB1]
                    )
                ]
            )

        # self.array_tree_sA1sB1 = [
        #     {
        #         'A1': [
        #             {'B1': '1.11'},
        #             {'B1': '1.21'},
        #             ],
        #         },
        #     {
        #         'A1': [
        #             {'B1': '1.12'},
        #             {'B1': '1.22'},
        #             ],
        #         },
        #     ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_prune_tree_simple(self):
        '''
        Test prune_tree() from nested dicts with no lists present in
        source, and doing no output manipulation.
        '''

        path_A1B1C1 = 'A1.B1.C1'
        path_A2B2C2 = 'A2.B2.C2'
        # path_A1B1C2 = 'A1.B1.C2'
        path_A1B2C2 = 'A1.B2.C2'

        prune_spec_A1B1C1 = {'path': path_A1B1C1}
        prune_spec_A2B2C2 = {'path': path_A2B2C2}
        # prune_spec_A1B1C2 = {'path': path_A1B1C2}
        prune_spec_A1B2C2 = {'path': path_A1B2C2}

        # self.linear_tree_1 = {
        #     'A1': {'B1': {'C1': 1}}
        #     }

        # self.linear_tree_1_flat = [{'A1.B1.C1': 1}]

        # self.linear_tree_2 = {
        #     'A2': {'B2': {'C2': 2}}
        #     }

        # self.simple_tree = {
        #     'A1': {'B1': {'C1': 1}},
        #     'A2': {'B2': {'C2': 2}},
        #     'A3': {'B3': {'C3': 3}},
        #     }

        # - - - - - - - - - - - - - - - - - - - -
        pruner = prune.Pruner(prune_spec_A1B1C1)
        self.assertIsNotNone(pruner)

        prunings = pruner.prune_tree(self.linear_tree_1)
        self.assertEqual(prunings, self.linear_tree_1)

        prunings = pruner.prune_tree(self.simple_tree)
        self.assertEqual(prunings, self.linear_tree_1)

        # - - - - - - - - - - - - - - - - - - - -
        pruner = prune.Pruner(prune_spec_A2B2C2)
        self.assertIsNotNone(pruner)

        prunings = pruner.prune_tree(self.linear_tree_2)
        self.assertEqual(prunings, self.linear_tree_2)

        prunings = pruner.prune_tree(self.simple_tree)
        self.assertEqual(prunings, self.linear_tree_2)

        # - - - - - - - - - - - - - - - - - - - -
        pruner = prune.Pruner(prune_spec_A1B1C1, prune_spec_A2B2C2)
        self.assertIsNotNone(pruner)

        prunings = pruner.prune_tree(self.linear_tree_1)
        self.assertEqual(prunings, self.linear_tree_1)

        prunings = pruner.prune_tree(self.linear_tree_2)
        self.assertEqual(prunings, self.linear_tree_2)

        prunings = pruner.prune_tree(self.simple_tree)
        self.assertEqual(prunings, self.simple_tree12)

        # - - - - - - - - - - - - - - - - - - - -
        pruner = prune.Pruner(prune_spec_A1B1C1, prune_spec_A1B2C2)
        self.assertIsNotNone(pruner)

        prunings = pruner.prune_tree(self.linear_tree_1)
        self.assertEqual(prunings, self.linear_tree_1)

        prunings = pruner.prune_tree(self.linear_tree_2)
        self.assertEqual(prunings, None)

        prunings = pruner.prune_tree(self.simple_tree)
        self.assertEqual(prunings, self.linear_tree_1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_prune_branches_simple(self):
        '''
        Test prune_branches() from nested dicts with no lists present in
        source, and doing no output manipulation.
        '''

        path_A1B1C1 = 'A1.B1.C1'
        path_A2B2C2 = 'A2.B2.C2'
        # path_A1B1C2 = 'A1.B1.C2'
        path_A1B2C2 = 'A1.B2.C2'

        prune_spec_A1B1C1 = {'path': path_A1B1C1}
        prune_spec_A2B2C2 = {'path': path_A2B2C2}
        # prune_spec_A1B1C2 = {'path': path_A1B1C2}
        prune_spec_A1B2C2 = {'path': path_A1B2C2}
        pruner = prune.Pruner(prune_spec_A1B1C1)
        self.assertIsNotNone(pruner)

        prunings = pruner.prune_branches(self.linear_tree_1)
        self.assertEqual(prunings, self.linear_tree_1_branches)

        prunings = pruner.prune_branches(self.simple_tree)
        self.assertEqual(prunings, self.linear_tree_1_branches)

        # - - - - - - - - - - - - - - - - - - - -
        pruner = prune.Pruner(prune_spec_A2B2C2)
        self.assertIsNotNone(pruner)

        prunings = pruner.prune_branches(self.linear_tree_2)
        self.assertEqual(prunings, self.linear_tree_2_branches)

        prunings = pruner.prune_branches(self.simple_tree)
        self.assertEqual(prunings, self.linear_tree_2_branches)

        # - - - - - - - - - - - - - - - - - - - -
        pruner = prune.Pruner(prune_spec_A1B1C1, prune_spec_A2B2C2)
        self.assertIsNotNone(pruner)

        prunings = pruner.prune_branches(self.linear_tree_1)
        self.assertEqual(prunings, self.linear_tree_1_branches)

        prunings = pruner.prune_branches(self.linear_tree_2)
        self.assertEqual(prunings, self.linear_tree_2_branches)

        prunings = pruner.prune_branches(self.simple_tree)
        self.assertEqual(
            prunings,
            [dict(
                self.linear_tree_1_branches[0],
                **self.linear_tree_2_branches[0]
                )]
            )

        # - - - - - - - - - - - - - - - - - - - -
        pruner = prune.Pruner(prune_spec_A1B1C1, prune_spec_A1B2C2)
        self.assertIsNotNone(pruner)

        prunings = pruner.prune_branches(self.linear_tree_1)
        self.assertEqual(prunings, self.linear_tree_1_branches)

        prunings = pruner.prune_branches(self.linear_tree_2)
        self.assertEqual(prunings, None)

        prunings = pruner.prune_branches(self.simple_tree)
        self.assertEqual(prunings, self.linear_tree_1_branches)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_prune_values_simple_OBSOLETE_COMMENTED_OUT(self):
        '''
        Test prune_values() from nested dicts with no lists present in
        source, and doing no output manipulation.
        '''

        # path_A1B1C1 = 'A1.B1.C1'
        # path_A2B2C2 = 'A2.B2.C2'
        # path_A1B1C2 = 'A1.B1.C2'
        # path_A1B2C2 = 'A1.B2.C2'

        # prune_spec_A1B1C1 = {'path': path_A1B1C1}
        # prune_spec_A2B2C2 = {'path': path_A2B2C2}
        # prune_spec_A1B1C2 = {'path': path_A1B1C2}
        # prune_spec_A1B2C2 = {'path': path_A1B2C2}

        # # self.simple_tree = {
        # #     'A1': {'B1': {'C1': 1}},
        # #     'A2': {'B2': {'C2': 2}},
        # #     'A3': {'B3': {'C3': 3}},
        # #     }

        # # self.linear_tree_1 = {
        # #     'A1': {'B1': {'C1': 1}}
        # #     }

        # self.linear_tree_1_values = [1]

        # # self.linear_tree_2 = {
        # #     'A2': {'B2': {'C2': 2}}
        # #     }

        # self.linear_tree_2_values = [2]

        # # - - - - - - - - - - - - - - - - - - - -
        # pruner = prune.Pruner(prune_spec_A1B1C1)
        # self.assertIsNotNone(pruner)

        # prunings = pruner.prune_values(self.linear_tree_1)
        # self.assertEqual(prunings, [self.linear_tree_1_values])

        # prunings = pruner.prune_values(self.simple_tree)
        # self.assertEqual(prunings, [self.linear_tree_1_values])

        # # - - - - - - - - - - - - - - - - - - - -
        # pruner = prune.Pruner(prune_spec_A2B2C2)
        # self.assertIsNotNone(pruner)

        # prunings = pruner.prune_values(self.linear_tree_2)
        # self.assertEqual(prunings, [self.linear_tree_2_values])

        # prunings = pruner.prune_values(self.simple_tree)
        # self.assertEqual(prunings, [self.linear_tree_2_values])

        # # - - - - - - - - - - - - - - - - - - - -
        # pruner = prune.Pruner(prune_spec_A1B1C1, prune_spec_A2B2C2)
        # self.assertIsNotNone(pruner)

        # prunings = pruner.prune_values(self.linear_tree_1)
        # self.assertEqual(prunings, [self.linear_tree_1_values, None])

        # prunings = pruner.prune_values(self.linear_tree_2)
        # self.assertEqual(prunings, [None, self.linear_tree_2_values])

        # prunings = pruner.prune_values(self.simple_tree)
        # self.assertEqual(
        #     prunings,
        #     [self.linear_tree_1_values, self.linear_tree_2_values]
        #     )

        # # - - - - - - - - - - - - - - - - - - - -
        # pruner = prune.Pruner(prune_spec_A1B1C1, prune_spec_A1B2C2)
        # self.assertIsNotNone(pruner)

        # prunings = pruner.prune_values(self.linear_tree_1)
        # self.assertEqual(prunings, [self.linear_tree_1_values, None])

        # prunings = pruner.prune_values(self.linear_tree_2)
        # self.assertEqual(prunings, [None, None])

        # prunings = pruner.prune_values(self.simple_tree)
        # self.assertEqual(prunings, [self.linear_tree_1_values, None])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestPrunerWorldStructure(unittest.TestCase):
    '''
    More complex test cases for Pruner using the structure in
    world_structure.py.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_prune_branches_world(self):
        '''
        Test pruning from nested dicts with more complicated structure.

        See world_structure.py for structure definition.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        # Make sure the structure hasn't lost anything we might
        # depend on.
        # - - - - - - - - - - - - - - - - - - - -
        for path in [
                'nations.[].Name',
                'nations.[].Language',
                'nations.[].Cities.[].Name',
                'nations.[].Continent',
                'nations.[].Cities.[].Population',
                'nations.[].HistoricDates.[]',
                'nations.[].Cities.[].Royalty.[].Palace',
                'nations.[].Cities.[].Royalty.[].Title'
                ]:  # pylint: disable=bad-continuation
            self.assertIn(path, prune.paths(world_structure.world))

        # - - - - - - - - - - - - - - - - - - - -
        nation_name_prune_spec = {
            'path': dp(['Name'])
            }
        nation_language_prune_spec = {
            'path': dp(['Language'])
            }
        nation_historic_dates_prune_spec = {
            'path': dp(['HistoricDates', LI])
            }
        nation_historic_dates_flat_prune_spec = {
            'path': dp(['HistoricDates', LI]),
            'flatten_leaves': True
            }

        nation_pruner = prune.Pruner(
            nation_name_prune_spec,
            nation_language_prune_spec,
            nation_historic_dates_prune_spec
            )

        nation_flat_dates_pruner = prune.Pruner(
            nation_name_prune_spec,
            nation_language_prune_spec,
            nation_historic_dates_flat_prune_spec
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Check that we get what's expected from each component nation.
        # With dates not flattened.
        # - - - - - - - - - - - - - - - - - - - -
        nation_branches_1 = nation_pruner.prune_branches(
            world_structure.nation_1
            )
        nation_branches_1_expected = [
            {
                'Name': 'England',
                'Language': 'English (UK)',
                'HistoricDates': [1066, 1605, 1859]
                },
            ]
        for expected in nation_branches_1_expected:
            self.assertIn(expected, nation_branches_1)

        # - - - - - - - - - - - - - - - - - - - -
        # With dates flattened.
        # - - - - - - - - - - - - - - - - - - - -

        nation_branches_1 = nation_flat_dates_pruner.prune_branches(
            world_structure.nation_1
            )
        nation_branches_1_expected = [
            {
                'Name': 'England',
                'Language': 'English (UK)',
                'HistoricDates': 1066,
                },
            {
                'Name': 'England',
                'Language': 'English (UK)',
                'HistoricDates': 1605,
                },
            {
                'Name': 'England',
                'Language': 'English (UK)',
                'HistoricDates': 1859,
                },
            ]

        for expected in nation_branches_1_expected:
            self.assertIn(expected, nation_branches_1)

        # - - - - - - - - - - - - - - - - - - - -
        nation_branches_2 = nation_flat_dates_pruner.prune_branches(
            world_structure.nation_2
            )

        nation_branches_2_expected = [
            {
                'Name': 'France',
                'Language': 'French',
                'HistoricDates': 1789
                },
            {
                'Name': 'France',
                'Language': 'French',
                'HistoricDates': 1917
                },
            ]

        for expected in nation_branches_2_expected:
            self.assertIn(expected, nation_branches_2)

        # - - - - - - - - - - - - - - - - - - - -
        nation_branches_3 = nation_flat_dates_pruner.prune_branches(
            world_structure.nation_3
            )

        nation_branches_3_expected = [
            {
                'Name': 'Spain',
                'Language': 'Spanish',
                'HistoricDates': 1492
                }
            ]

        for expected in nation_branches_3_expected:
            self.assertIn(expected, nation_branches_3)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_prune_branches_world_value_massaging(self):
        '''
        Test pruning from nested dicts with more complicated structure,
        with value massaging methods in prune specs.

        See world_structure.py for structure definition.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        nation_name_prune_spec = {
            'path': dp(['Name'])
            }
        nation_language_prune_spec = {
            'path': dp(['Language'])
            }
        nation_dates_massaged_prune_spec = {
            'path': dp(['HistoricDates']),
            'value_refiner': lambda x: ' '.join([str(y) for y in x])
            }

        nation_dates_massaged_pruner = prune.Pruner(
            nation_name_prune_spec,
            nation_language_prune_spec,
            nation_dates_massaged_prune_spec
            )

        nation_branches_1 = nation_dates_massaged_pruner.prune_branches(
            world_structure.nation_1
            )
        nation_branches_1_expected = [
            {
                'Name': 'England',
                'Language': 'English (UK)',
                'HistoricDates': '1066 1605 1859'
                },
            ]

        for expected in nation_branches_1_expected:
            self.assertIn(expected, nation_branches_1)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestPrunerWorldStructureSubPruning(unittest.TestCase):
    '''
    More complex test cases for Pruner using the structure in
    world_structure.py.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_prune_branches_world_value_pruning(self):
        '''
        Test pruning from nested dicts with more complicated structure.

        See world_structure.py for structure definition.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        # Test prune_branches() with value_pruning.
        # - - - - - - - - - - - - - - - - - - - -
        name_path = 'Name'
        cities_name_path = dp(['Cities', LI, 'Name'])
        cities_pop_path = dp(['Cities', LI, 'Population'])

        cities_values_pruner = prune.Pruner(
            {
                'path': name_path,
                'path_to_none': True
                },
            {
                'path': cities_name_path,
                'path_to_none': True
                },
            {
                'path': cities_pop_path,
                'path_to_none': True
                }
            )

        # - - - - - - - - - - - - - - - - - - - -
        cities_pruning_1 = cities_values_pruner.prune_branches(
            world_structure.nation_1
            )

        cities_pruning_1_expected = [
            {
                'Name': 'England',
                'Cities.Name': 'London',
                'Cities.Population': 96
                },
            {
                'Name': 'England',
                'Cities.Name': 'Balmoral',
                'Cities.Population': 42
                },
            ]

        self.assertEqual(
            cities_pruning_1,
            cities_pruning_1_expected
            )
        for expected in cities_pruning_1_expected:
            self.assertIn(expected, cities_pruning_1)

        # - - - - - - - - - - - - - - - - - - - -
        cities_pruning_2 = cities_values_pruner.prune_branches(
            world_structure.nation_2
            )

        cities_pruning_2_expected = [
            {
                'Name': 'France',
                'Cities.Name': 'Paris',
                'Cities.Population': 17
                },
            {
                'Name': 'France',
                'Cities.Name': 'Marseille',
                'Cities.Population': 91
                },
            {
                'Name': 'France',
                'Cities.Name': 'Lyon',
                },
            ]

        self.assertEqual(
            cities_pruning_2,
            cities_pruning_2_expected
            )
        for expected in cities_pruning_2_expected:
            self.assertIn(expected, cities_pruning_2)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_prune_branches_world_value_pruning_balanced(self):
        '''
        Test pruning from nested dicts with more complicated structure.

        See world_structure.py for structure definition.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        # Test prune_branches() with value_pruning.
        # - - - - - - - - - - - - - - - - - - - -
        name_path = 'Name'
        # cities_path = 'Cities'
        cities_name_path = dp(['Cities', LI, 'Name'])
        cities_pop_path = dp(['Cities', LI, 'Population'])

        cities_values_pruner = prune.Pruner(
            {
                'path': name_path,
                'path_to_none': True
                },
            {
                'path': cities_name_path,
                'path_to_none': True
                },
            {
                'path': cities_pop_path,
                'path_to_none': True
                }
            )

        # - - - - - - - - - - - - - - - - - - - -
        cities_pruning_1 = cities_values_pruner.prune_branches(
            world_structure.nation_1,
            balanced=True
            )

        cities_pruning_1_expected = [
            {
                'Name': 'England',
                'Cities.Name': 'London',
                'Cities.Population': 96
                },
            {
                'Name': 'England',
                'Cities.Name': 'Balmoral',
                'Cities.Population': 42
                },
            ]

        self.assertEqual(
            cities_pruning_1,
            cities_pruning_1_expected
            )
        for expected in cities_pruning_1_expected:
            self.assertIn(expected, cities_pruning_1)

        # - - - - - - - - - - - - - - - - - - - -
        cities_pruning_2 = cities_values_pruner.prune_branches(
            world_structure.nation_2,
            balanced=True
            )

        cities_pruning_2_expected = [
            {
                'Name': 'France',
                'Cities.Name': 'Paris',
                'Cities.Population': 17
                },
            {
                'Name': 'France',
                'Cities.Name': 'Marseille',
                'Cities.Population': 91
                },
            {
                'Name': 'France',
                'Cities.Name': 'Lyon',
                'Cities.Population': None
                },
            ]

        self.assertEqual(
            cities_pruning_2,
            cities_pruning_2_expected
            )
        for expected in cities_pruning_2_expected:
            self.assertIn(expected, cities_pruning_2)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestPrunerWorldStructureSubSubPruning(unittest.TestCase):
    '''
    More complex test cases for Pruner using the structure in
    world_structure.py.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_prune_branches_world_value_pruning(self):
        '''
        Test pruning from nested dicts with more complicated structure.

        See world_structure.py for structure definition.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        # Test prune_branches() with value_pruning.
        # - - - - - - - - - - - - - - - - - - - -
        nation_name_path = 'Name'
        cities_name_path = dp(['Cities', LI, 'Name'])
        cities_pop_path = dp(['Cities', LI, 'Population'])
        palace_path = dp(['Cities', LI, 'Royalty', LI, 'Palace'])
        title_path = dp(['Cities', LI, 'Royalty', LI, 'Title'])

        royalty_values_pruner = prune.Pruner(
            {
                'path': nation_name_path,
                'path_to_none': True
                },
            {
                'path': cities_name_path,
                'path_to_none': True
                },
            {
                'path': cities_pop_path,
                'path_to_none': True
                },
            {
                'path': palace_path,
                'path_to_none': True
                },
            {
                'path': title_path,
                'path_to_none': True
                },
            )

        # - - - - - - - - - - - - - - - - - - - -
        royalty_pruning_1 = royalty_values_pruner.prune_branches(
            world_structure.nation_1,
            balanced=True
            )

        royalty_pruning_1_expected = [
            {
                'Cities.Population': 96,
                'Cities.Royalty.Palace': 'Buckingham',
                'Cities.Royalty.Title': 'King',
                'Cities.Name': 'London', 'Name': 'England'
                },
            {
                'Cities.Population': 96,
                'Cities.Royalty.Palace': 'Buckingham',
                'Cities.Royalty.Title': 'Queen',
                'Cities.Name': 'London', 'Name': 'England'
                },
            {
                'Cities.Population': 96,
                'Cities.Royalty.Palace': 'Buckingham',
                'Cities.Royalty.Title': 'Princess',
                'Cities.Name': 'London', 'Name': 'England'
                },
            {
                'Cities.Population': 42,
                'Cities.Royalty.Palace': 'Delnadamph Lodge',
                'Cities.Royalty.Title': 'Duke',
                'Cities.Name': 'Balmoral', 'Name': 'England'
                }
            ]

        self.assertEqual(
            royalty_pruning_1,
            royalty_pruning_1_expected
            )
        for expected in royalty_pruning_1_expected:
            self.assertIn(expected, royalty_pruning_1)

        # - - - - - - - - - - - - - - - - - - - -


if __name__ == '__main__':
    unittest.main()
