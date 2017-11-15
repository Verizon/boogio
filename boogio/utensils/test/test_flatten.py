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

'''Test cases for the flatten.py module.'''

import unittest

from boogio.utensils import flatten


def sorted(arr):
    '''Sort for either a list or a dict.'''
    sarr = [a for a in arr]
    sarr.sort()
    if isinstance(arr, list):
        return sarr
    else:
        return {a: arr[a] for a in sarr}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestFlatten(unittest.TestCase):
    '''Test cases for flatten.flatten.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Shared test case definitions..'''
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_init_errors(self):
        '''Test flatten.flatten initialization errors..'''
        pass

        # # These raise a ValueError for the missing path_prefix.
        # with self.assertRaises(ValueError):

        #     flatten.flatten(self.S)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_s(self):
        '''Structure: 1.'''

        structure_s = 1
        structure_s_flat = {
            None: structure_s,
            'some.path': [{'some.path': 1}]
            }

        (nested, flat) = (structure_s, structure_s_flat)

        self.assertEqual(
            flatten.flatten(nested),
            flat[None]
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            nested
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_a(self):
        '''Structure: [].'''

        structure_a = [1, 2, 3]
        structure_a_flat = {
            None: structure_a,
            'some.path': [{'some.path': [1, 2, 3]}]
            }

        (nested, flat) = (structure_a, structure_a_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            nested
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_d(self):
        '''Structure: {}.'''

        structure_d = {'a': 1, 'b': 2}
        structure_d_flat = {
            None: [structure_d],
            'some.path': [
                {'some.path.a': 1, 'some.path.b': 2}
                ]
            }

        (nested, flat) = (structure_d, structure_d_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            nested
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_d_a(self):
        '''Structure: {[]}.'''

        structure_d_a = {
            'a': [1, 3, 3]
            }
        structure_d_a_flat = {
            None: [
                structure_d_a,
                [{'a': [1, 3, 3]}]
                ],
            'some.path': [
                structure_d_a,
                [{'some.path.a': [1, 3, 3]}],
                ],
            'flat_leaves': [
                structure_d_a,
                [{'a': 1}, {'a': 3}, {'a': 3}],
                ],
            }

        (nested, flat) = (structure_d_a, structure_d_a_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=2)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][1])
            )

        # self.assertEqual(
        #     sorted(flatten.flatten(nested, flatten_leaves=True, to_depth=0)),
        #     sorted(flat['flat_leaves'][0])
        #     )

        self.assertEqual(
            sorted(flatten.flatten(nested, flatten_leaves=True)),
            sorted(flat['flat_leaves'][1])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_d_aa(self):
        '''Structure: {[], []}.'''

        structure_d_aa = {
            'a': [1, 3, 3],
            'b': [4, 5, 6]
            }
        structure_d_aa_flat = {
            None: [
                structure_d_aa,
                [{'a': [1, 3, 3], 'b': [4, 5, 6]}]
                ],
            'some.path': [
                structure_d_aa,
                [{'some.path.a': [1, 3, 3], 'some.path.b': [4, 5, 6]}],
                ],
            'flat_leaves': [
                structure_d_aa,
                [
                    {'a': 1, 'b': 4}, {'a': 1, 'b': 5}, {'a': 1, 'b': 6},
                    {'a': 3, 'b': 4}, {'a': 3, 'b': 5}, {'a': 3, 'b': 6},
                    {'a': 3, 'b': 4}, {'a': 3, 'b': 5}, {'a': 3, 'b': 6}
                    ],
                ],
            }

        (nested, flat) = (structure_d_aa, structure_d_aa_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=2)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][1])
            )

        # self.assertEqual(
        #     sorted(flatten.flatten(nested, flatten_leaves=True, to_depth=0)),
        #     sorted(flat['flat_leaves'][0])
        #     )

        self.assertEqual(
            sorted(flatten.flatten(nested, flatten_leaves=True)),
            sorted(flat['flat_leaves'][1])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_d_dd(self):
        '''Structure: {{}, {}}.'''

        structure_d_dd = {
            'u': {'a': 1, 'b': 2},
            'v': {'a': 3, 'b': 4}
            }
        structure_d_dd_flat = {
            None: [
                structure_d_dd,
                [{'u': {'a': 1, 'b': 2}, 'v': {'a': 3, 'b': 4}}],
                [{'u.a': 1, 'u.b': 2, 'v.a': 3, 'v.b': 4}]
                ],
            'some.path': [
                structure_d_dd,
                [{
                    'some.path.u': {'a': 1, 'b': 2},
                    'some.path.v': {'a': 3, 'b': 4}
                    }],
                [{
                    'some.path.u.a': 1, 'some.path.u.b': 2,
                    'some.path.v.a': 3, 'some.path.v.b': 4
                    }]
                ]
            }

        (nested, flat) = (structure_d_dd, structure_d_dd_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=2)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=3)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            flat['some.path'][0]
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=3
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][2])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_d_sdd(self):
        '''Structure: {1, {}, {}}.'''

        structure_d_sdd = {
            's': 'S',
            'u': {'a': 1, 'b': 2},
            'v': {'a': 3, 'd': 4}
            }
        structure_d_sdd_flat = {
            None: [
                structure_d_sdd,
                [structure_d_sdd],
                [{'s': 'S', 'u.a': 1, 'u.b': 2, 'v.a': 3, 'v.d': 4}],
                ],
            'some.path': [
                structure_d_sdd,
                [{
                    'some.path.s': 'S',
                    'some.path.u': {'a': 1, 'b': 2},
                    'some.path.v': {'a': 3, 'd': 4}
                    }],
                [{
                    'some.path.s': 'S',
                    'some.path.u.a': 1, 'some.path.u.b': 2,
                    'some.path.v.a': 3, 'some.path.v.d': 4
                    }]
                ],
            }

        (nested, flat) = (structure_d_sdd, structure_d_sdd_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][2])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_d_ad(self):
        '''Structure: {[], {}}.'''

        structure_d_ad = {
            'u': {'a': 1, 'b': 2},
            'y': ['n', 'o']
            }
        structure_d_ad_flat = {
            None: [
                structure_d_ad,
                [structure_d_ad],
                [{'u.a': 1, 'u.b': 2, 'y': ['n', 'o']}],
                ],
            'some.path': [
                structure_d_ad,
                [{
                    'some.path.u': {'a': 1, 'b': 2},
                    'some.path.y': ['n', 'o']}],
                [{
                    'some.path.u.a': 1, 'some.path.u.b': 2,
                    'some.path.y': ['n', 'o']
                    }],
                ],
            }

        (nested, flat) = (structure_d_ad, structure_d_ad_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=2)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][2])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_d_aadd(self):
        '''Structure: {[], [], {}, {}}.'''

        structure_d_aadd = {
            'u': {'a': 1, 'b': 2},
            'v': {'c': 3, 'd': 4},
            'x': ['k', 'l', 'm'],
            'y': ['n', 'o']
            }
        structure_d_aadd_flat = {
            None: [
                structure_d_aadd,
                [structure_d_aadd],
                [{
                    'u.a': 1, 'u.b': 2, 'v.d': 4, 'v.c': 3,
                    'y': ['n', 'o'], 'x': ['k', 'l', 'm']
                    }],
                ],
            'some.path': [
                structure_d_aadd,
                [{
                    'some.path.u': {'a': 1, 'b': 2},
                    'some.path.v': {'c': 3, 'd': 4},
                    'some.path.x': ['k', 'l', 'm'],
                    'some.path.y': ['n', 'o']
                    }],
                [{
                    'some.path.u.a': 1, 'some.path.u.b': 2,
                    'some.path.v.d': 4, 'some.path.v.c': 3,
                    'some.path.y': ['n', 'o'],
                    'some.path.x': ['k', 'l', 'm']
                    }],
                ],
            }

        (nested, flat) = (structure_d_aadd, structure_d_aadd_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=2)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][2])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_d_saadd(self):
        '''Structure: {1, [], [], {}, {}}.'''
        structure_d_saadd = {
            's': 'S',
            'u': {'a': 1, 'b': 2},
            'v': {'c': 3, 'd': 4},
            'x': ['k', 'l', 'm'],
            'y': ['n', 'o']
            }
        structure_d_saadd_flat = {
            None: [
                structure_d_saadd,
                [structure_d_saadd],
                [{
                    's': 'S',
                    'u.a': 1, 'u.b': 2, 'v.d': 4, 'v.c': 3,
                    'y': ['n', 'o'], 'x': ['k', 'l', 'm']
                    }]
                ],
            'some.path': [
                structure_d_saadd,
                [{
                    'some.path.s': 'S',
                    'some.path.u': {'a': 1, 'b': 2},
                    'some.path.v': {'c': 3, 'd': 4},
                    'some.path.x': ['k', 'l', 'm'],
                    'some.path.y': ['n', 'o']
                    }],
                [{
                    'some.path.s': 'S',
                    'some.path.u.a': 1, 'some.path.u.b': 2,
                    'some.path.v.d': 4, 'some.path.v.c': 3,
                    'some.path.y': ['n', 'o'],
                    'some.path.x': ['k', 'l', 'm']
                    }]
                ],
            }

        (nested, flat) = (structure_d_saadd, structure_d_saadd_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=2)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][2])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_d_saa(self):
        '''Structure: {1, [], []}.'''

        structure_d_saa = {
            's': 'S',
            'a': [1, 3, 3],
            'b': [4, 5, 6]
            }

        structure_d_saa_flat = {
            None: [
                structure_d_saa,
                [structure_d_saa],
                ],
            'some.path': [
                structure_d_saa,
                [{
                    'some.path.s': 'S',
                    'some.path.a': [1, 3, 3],
                    'some.path.b': [4, 5, 6]
                    }]
                ],
            }
        (nested, flat) = (structure_d_saa, structure_d_saa_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][1])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_a_d(self):
        '''Structure: [{}].'''

        structure_a_d = [
            {'a': 1, 'b': 2},
            {'a': 3, 'b': 4}
            ]
        structure_a_d_flat = {
            None: [
                structure_a_d,
                structure_a_d,
                ],
            'some.path': [
                structure_a_d,
                [
                    {'some.path.a': 1, 'some.path.b': 2},
                    {'some.path.a': 3, 'some.path.b': 4},
                    ],
                ],
            }

        (nested, flat) = (structure_a_d, structure_a_d_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][1])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_deep1(self):
        '''Structure: {{[{}, {}}],[{, {}}]}}.'''

        structure_deep1 = {
            'a': [
                {'x': 1, 'y': 2},
                {'x': 11, 'y': 12}
                ],
            'b': [
                {'x': 3, 'y': 4},
                {'x': 13, 'y': 14}
                ]
            }
        structure_deep1_flat = {
            None: [
                structure_deep1,
                [structure_deep1],
                [
                    {
                        'a.x': 1, 'a.y': 2,
                        'b.x': 3, 'b.y': 4
                        },
                    {
                        'a.x': 1, 'a.y': 2,
                        'b.x': 13, 'b.y': 14
                        },
                    {
                        'a.x': 11, 'a.y': 12,
                        'b.x': 3, 'b.y': 4
                        },
                    {
                        'a.x': 11, 'a.y': 12,
                        'b.x': 13, 'b.y': 14
                        }
                    ],
                ],
            'some.path': [
                structure_deep1,
                [{
                    'some.path.a': [
                        {'x': 1, 'y': 2},
                        {'x': 11, 'y': 12}
                        ],
                    'some.path.b': [
                        {'x': 3, 'y': 4},
                        {'x': 13, 'y': 14}
                        ]
                    }],
                [
                    {
                        'some.path.a.x': 1, 'some.path.a.y': 2,
                        'some.path.b.x': 3, 'some.path.b.y': 4
                        },
                    {
                        'some.path.a.x': 1, 'some.path.a.y': 2,
                        'some.path.b.x': 13, 'some.path.b.y': 14
                        },
                    {
                        'some.path.a.x': 11, 'some.path.a.y': 12,
                        'some.path.b.x': 3, 'some.path.b.y': 4
                        },
                    {
                        'some.path.a.x': 11, 'some.path.a.y': 12,
                        'some.path.b.x': 13, 'some.path.b.y': 14
                        }
                    ],
                ],
            }

        (nested, flat) = (structure_deep1, structure_deep1_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=2)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][2])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_deep2(self):
        '''Structure: {[{}, {}], [{}, {}], 1, 1}.'''

        structure_deep2 = {
            'a': [
                {'x': 1, 'y': 2},
                {'x': 11, 'y': 12}
                ],
            'b': [
                {'x': 3, 'y': 4},
                {'x': 13, 'y': 14}
                ],
            'c': 42,
            'd': 66
            }
        structure_deep2_flat = {
            None: [
                structure_deep2,
                [structure_deep2],
                [
                    {
                        'a.x': 1, 'a.y': 2,
                        'b.x': 3, 'b.y': 4,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 1, 'a.y': 2,
                        'b.x': 13, 'b.y': 14,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 11, 'a.y': 12,
                        'b.x': 3, 'b.y': 4,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 11, 'a.y': 12,
                        'b.x': 13, 'b.y': 14,
                        'c': 42, 'd': 66
                        }
                    ]
                ],
            'some.path': [
                structure_deep2,
                [{
                    'some.path.a': [
                        {'x': 1, 'y': 2},
                        {'x': 11, 'y': 12}
                        ],
                    'some.path.b': [
                        {'x': 3, 'y': 4},
                        {'x': 13, 'y': 14}
                        ],
                    'some.path.c': 42,
                    'some.path.d': 66
                    }],
                [
                    {
                        'some.path.a.x': 1, 'some.path.a.y': 2,
                        'some.path.b.x': 3, 'some.path.b.y': 4,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 1, 'some.path.a.y': 2,
                        'some.path.b.x': 13, 'some.path.b.y': 14,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 11, 'some.path.a.y': 12,
                        'some.path.b.x': 3, 'some.path.b.y': 4,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 11, 'some.path.a.y': 12,
                        'some.path.b.x': 13, 'some.path.b.y': 14,
                        'some.path.c': 42, 'some.path.d': 66
                        }
                    ],
                ],
            }

        (nested, flat) = (structure_deep2, structure_deep2_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=2)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][2])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_deep3(self):
        '''Structure: {[{[{}, {}]}], [{},{}], 1, 1}.'''

        structure_deep3 = {
            'a': [
                {'x': 1, 'y': [{'u': 111}, {'u': 222}]},
                {'x': 11, 'y': 12}
                ],
            'b': [
                {'x': 3, 'y': 4},
                {'x': 13, 'y': 14}
                ],
            'c': 42,
            'd': 66
            }
        structure_deep3_flat = {
            None: [
                structure_deep3,
                [structure_deep3],
                [
                    {
                        'a.x': 1, 'a.y': [{'u': 111}, {'u': 222}],
                        'b.x': 3, 'b.y': 4,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 11, 'a.y': 12,
                        'b.x': 3, 'b.y': 4,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 1, 'a.y': [{'u': 111}, {'u': 222}],
                        'b.x': 13, 'b.y': 14,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 11, 'a.y': 12,
                        'b.x': 13, 'b.y': 14,
                        'c': 42, 'd': 66
                        }
                    ],
                [
                    {
                        'a.x': 1, 'a.y.u': 111,
                        'b.x': 3, 'b.y': 4,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 1, 'a.y.u': 222,
                        'b.x': 3, 'b.y': 4,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 11, 'a.y': 12,
                        'b.x': 3, 'b.y': 4,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 1, 'a.y.u': 111,
                        'b.x': 13, 'b.y': 14,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 1, 'a.y.u': 222,
                        'b.x': 13, 'b.y': 14,
                        'c': 42, 'd': 66
                        },
                    {
                        'a.x': 11, 'a.y': 12,
                        'b.x': 13, 'b.y': 14,
                        'c': 42, 'd': 66
                        }
                    ]
                ],
            'some.path': [
                structure_deep3,
                [{
                    'some.path.a': [
                        {'x': 1, 'y': [{'u': 111}, {'u': 222}]},
                        {'x': 11, 'y': 12}
                        ],
                    'some.path.b': [
                        {'x': 3, 'y': 4},
                        {'x': 13, 'y': 14}
                        ],
                    'some.path.c': 42,
                    'some.path.d': 66
                    }],
                [
                    {
                        'some.path.a.x': 1,
                        'some.path.a.y': [{'u': 111}, {'u': 222}],
                        'some.path.b.x': 3, 'some.path.b.y': 4,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 11, 'some.path.a.y': 12,
                        'some.path.b.x': 3, 'some.path.b.y': 4,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 1,
                        'some.path.a.y': [{'u': 111}, {'u': 222}],
                        'some.path.b.x': 13, 'some.path.b.y': 14,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 11, 'some.path.a.y': 12,
                        'some.path.b.x': 13, 'some.path.b.y': 14,
                        'some.path.c': 42, 'some.path.d': 66
                        }
                    ],
                [
                    {
                        'some.path.a.x': 1, 'some.path.a.y.u': 111,
                        'some.path.b.x': 3, 'some.path.b.y': 4,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 1, 'some.path.a.y.u': 222,
                        'some.path.b.x': 3, 'some.path.b.y': 4,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 11, 'some.path.a.y': 12,
                        'some.path.b.x': 3, 'some.path.b.y': 4,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 1, 'some.path.a.y.u': 111,
                        'some.path.b.x': 13, 'some.path.b.y': 14,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 1, 'some.path.a.y.u': 222,
                        'some.path.b.x': 13, 'some.path.b.y': 14,
                        'some.path.c': 42, 'some.path.d': 66
                        },
                    {
                        'some.path.a.x': 11, 'some.path.a.y': 12,
                        'some.path.b.x': 13, 'some.path.b.y': 14,
                        'some.path.c': 42, 'some.path.d': 66
                        }
                    ],
                ],
            }

        (nested, flat) = (structure_deep3, structure_deep3_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=2)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=3)),
            sorted(flat[None][3])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][3])
            )

        self.assertEqual(
            flatten.flatten(nested, path_prefix='some.path', to_depth=0),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=3
                )),
            sorted(flat['some.path'][3])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][3])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_a_aa(self):
        '''Structure: [[], []].'''

        structure_a_aa = [['a', 'b'], [3, 4]]
        structure_a_aa_flat = {
            None: [
                structure_a_aa,
                ['a', 'b', 3, 4],
                ],
            'some.path': [
                structure_a_aa,
                [{'some.path': ['a', 'b', 3, 4]}]
                ],
            }

        (nested, flat) = (structure_a_aa, structure_a_aa_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=0
                )),
            sorted(flat['some.path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, path_prefix='some.path', to_depth=1
                )),
            sorted(flat['some.path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, path_prefix='some.path')),
            sorted(flat['some.path'][1])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_a_ad(self):
        '''Structure: [[], {}].'''

        structure_a_ad = [
            {'a': 1, 'b': 2},
            ['k', 'l']
            ]
        structure_a_ad_flat = {
            None: [
                structure_a_ad,
                [{'a': 1, 'b': 2}, 'k', 'l']
                ],
            'some.path': [
                structure_a_ad,
                []
                ],
            }

        (nested, flat) = (structure_a_ad, structure_a_ad_flat)

        with self.assertRaises(TypeError):
            self.assertEqual(
                sorted(flatten.flatten(nested, to_depth=0)),
                sorted(flat[None][0])
                )

            self.assertEqual(
                sorted(flatten.flatten(nested, to_depth=1)),
                sorted(flat[None][1])
                )

            self.assertEqual(
                sorted(flatten.flatten(nested)),
                sorted(flat[None][1])
                )

            self.assertEqual(
                sorted(flatten.flatten(
                    nested, path_prefix='some.path', to_depth=0
                    )),
                sorted(flat['some.path'][0])
                )

            self.assertEqual(
                sorted(flatten.flatten(
                    nested, path_prefix='some.path', to_depth=1
                    )),
                sorted(flat['some.path'][1])
                )

            self.assertEqual(
                sorted(flatten.flatten(nested, path_prefix='some.path')),
                sorted(flat['some.path'][1])
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_flatten_d_saadd_with_separator(self):
        '''Structure: {1, [], [], {}, {}}.'''
        structure_d_saadd = {
            's': 'S',
            'u': {'a': 1, 'b': 2},
            'v': {'c': 3, 'd': 4},
            'x': ['k', 'l', 'm'],
            'y': ['n', 'o']
            }
        structure_d_saadd_flat = {
            None: [
                structure_d_saadd,
                [structure_d_saadd],
                [{
                    's': 'S',
                    'u:a': 1, 'u:b': 2, 'v:d': 4, 'v:c': 3,
                    'y': ['n', 'o'], 'x': ['k', 'l', 'm']
                    }]
                ],
            'some:path': [
                structure_d_saadd,
                [{
                    'some:path:s': 'S',
                    'some:path:u': {'a': 1, 'b': 2},
                    'some:path:v': {'c': 3, 'd': 4},
                    'some:path:x': ['k', 'l', 'm'],
                    'some:path:y': ['n', 'o']
                    }],
                # [{
                #     'some:path:s': 'S',
                #     'some:path:u:a': 1, 'some:path:u:b': 2,
                #     'some:path:v:d': 4, 'some:path:v:c': 3,
                #     'some:path.y': ['n', 'o'],
                #     'some:path.x': ['k', 'l', 'm']
                #     }]
                [{
                    'some:path:v:d': 4,
                    'some:path:u:b': 2,
                    'some:path:u:a': 1,
                    'some:path:x': ['k', 'l', 'm'],
                    'some:path:y': ['n', 'o'],
                    'some:path:s': 'S',
                    'some:path:v:c': 3,
                    }]
                ],
            }

        (nested, flat) = (structure_d_saadd, structure_d_saadd_flat)

        self.assertEqual(
            sorted(flatten.flatten(nested, separator=':', to_depth=0)),
            sorted(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, separator=':', to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, separator=':', to_depth=2)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(nested, separator=':')),
            sorted(flat[None][2])
            )

        self.assertEqual(
            flatten.flatten(
                nested, separator=':', path_prefix='some:path', to_depth=0
                ),
            sorted(flat['some:path'][0])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, separator=':', path_prefix='some:path', to_depth=1
                )),
            sorted(flat['some:path'][1])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, separator=':', path_prefix='some:path', to_depth=2
                )),
            sorted(flat['some:path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten(
                nested, separator=':', path_prefix='some:path'
                )),
            sorted(flat['some:path'][2])
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestFlattenDisjoint(unittest.TestCase):
    '''Test cases for flatten.flatten_disjoint().'''

    def test_flatten_disjoint_d_dd__d_dd(self):
        '''Structure: {{}, {}}, {{}, {}}.'''
        structure_1 = {'a': [{'b': 1}, {'b': 2}]}
        structure_2 = {'a': [{'c': 1}, {'c': 2}]}

        structures_flat = {
            None: [
                [structure_1, structure_2],
                [structure_1, structure_2],
                [
                    {'a.b': 1}, {'a.b': 2},
                    {'a.c': 1}, {'a.c': 2},
                    ]
                ],
            'some.path': [
                [structure_1, structure_2],
                [
                    {'some.path.a': [{'b': 1}, {'b': 2}]},
                    {'some.path.a': [{'c': 1}, {'c': 2}]}
                    ],
                [
                    {'some.path.a.b': 1}, {'some.path.a.b': 2},
                    {'some.path.a.c': 1}, {'some.path.a.c': 2},
                    ]
                ]
            }

        (nested, flat) = ([structure_1, structure_2], structures_flat)

        self.assertEqual(
            flatten.flatten_disjoint(*nested, to_depth=0),
            tuple(flat[None][0])
            )

        self.assertEqual(
            sorted(flatten.flatten_disjoint(*nested, to_depth=1)),
            sorted(flat[None][1])
            )

        self.assertEqual(
            sorted(flatten.flatten_disjoint(*nested, to_depth=2)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten_disjoint(*nested, to_depth=3)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            sorted(flatten.flatten_disjoint(*nested)),
            sorted(flat[None][2])
            )

        self.assertEqual(
            flatten.flatten_disjoint(
                *nested, path_prefix='some.path', to_depth=0
                ),
            tuple(flat['some.path'][0])
            )

        self.assertItemsEqual(
            sorted(flatten.flatten_disjoint(
                *nested, path_prefix='some.path', to_depth=1
                )),
            [sorted(x) for x in (flat['some.path'][1])]
            )

        self.assertEqual(
            sorted(flatten.flatten_disjoint(
                *nested, path_prefix='some.path', to_depth=2
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten_disjoint(
                *nested, path_prefix='some.path', to_depth=3
                )),
            sorted(flat['some.path'][2])
            )

        self.assertEqual(
            sorted(flatten.flatten_disjoint(
                *nested, path_prefix='some.path'
                )),
            sorted(flat['some.path'][2])
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    unittest.main()
