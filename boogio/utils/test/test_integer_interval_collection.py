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

'''Test cases for the interval_collection.py module.'''

import unittest

from boogio.utils import integer_interval_collection
# from boogio.utils.interval_collection import
IntegerIntervalCollection = (
    integer_interval_collection.IntegerIntervalCollection
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestIntegerIntervalCollection(unittest.TestCase):
    '''
    Basic test cases for IntegerIntervalCollection.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_init(self):
        '''Test IntegerIntervalCollection instance initialization.
        '''
        icoll = IntegerIntervalCollection()
        self.assertEqual(icoll, IntegerIntervalCollection([]))

        icoll = IntegerIntervalCollection([[10, 20]])
        self.assertEqual(icoll, IntegerIntervalCollection([[10, 20]]))

        icoll = IntegerIntervalCollection(
            [[10, 20], [30, 40]]
            )
        self.assertEqual(
            icoll,
            IntegerIntervalCollection([[10, 20], [30, 40]])
            )

        icoll = IntegerIntervalCollection(
            [[30, 40], [10, 20]]
            )
        self.assertEqual(
            icoll,
            IntegerIntervalCollection([[10, 20], [30, 40]])
            )

        icoll = IntegerIntervalCollection(
            [[10, 20], [10, 20]]
            )
        self.assertEqual(
            icoll,
            IntegerIntervalCollection([[10, 20]])
            )
        self.assertEqual(icoll.interval_count, 1)

        icoll = IntegerIntervalCollection(
            [[10, 20], [10, 30]]
            )
        self.assertEqual(
            icoll,
            IntegerIntervalCollection([[10, 30]])
            )
        self.assertEqual(icoll.interval_count, 1)

        icoll = IntegerIntervalCollection(
            [[10, 20], [30, 40], [15, 35]]
            )
        self.assertEqual(
            icoll,
            IntegerIntervalCollection([[10, 40]])
            )
        self.assertEqual(icoll.interval_count, 1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_init_errors(self):
        '''Test IntegerIntervalCollection instance initialization errors.
        '''

        with self.assertRaises(ValueError):
            IntegerIntervalCollection([[]])

        with self.assertRaises(ValueError):
            IntegerIntervalCollection([10])

        with self.assertRaises(ValueError):
            IntegerIntervalCollection([[10]])

        with self.assertRaises(ValueError):
            IntegerIntervalCollection([10, 5])

        with self.assertRaises(ValueError):
            IntegerIntervalCollection([[10, 5]])

        with self.assertRaises(ValueError):
            IntegerIntervalCollection([[10, 20, 30]])

        with self.assertRaises(ValueError):
            IntegerIntervalCollection([[10, 20, 15]])

        with self.assertRaises(ValueError):
            IntegerIntervalCollection([[10, 10.5]])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_empty(self):
        '''Test with an empty IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection()

        self.assertIsNotNone(icoll)

        self.assertEqual(icoll.interval_count, 0)
        self.assertTrue(icoll.is_empty)
        self.assertFalse(icoll.contains(1))

        self.assertIsNone(icoll.lower_bound)
        self.assertIsNone(icoll.upper_bound)

        self.assertEqual(icoll, IntegerIntervalCollection([]))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_empty_interval_intersection(self):
        '''Test intersections with an empty interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection()

        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([])),
            IntegerIntervalCollection([])
            )
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[10, 20]])),
            IntegerIntervalCollection([])
            )
        self.assertEqual(
            icoll.intersection(
                IntegerIntervalCollection([[10, 20], [30, 40]])
                ),
            IntegerIntervalCollection([])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_empty_interval_union(self):
        '''Test unions with an empty interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection()

        self.assertEqual(
            icoll.union(IntegerIntervalCollection([])),
            IntegerIntervalCollection([])
            )
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[10, 20]])),
            IntegerIntervalCollection([[10, 20]])
            )

        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[10, 20], [30, 40]])),
            IntegerIntervalCollection([[10, 20], [30, 40]])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_singleton(self):
        '''Test with a single interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection([[10, 20]])

        self.assertEqual(icoll.interval_count, 1)
        self.assertFalse(icoll.is_empty)

        self.assertFalse(icoll.contains(9))
        self.assertTrue(icoll.contains(10))
        self.assertTrue(icoll.contains(11))
        self.assertTrue(icoll.contains(20))
        self.assertFalse(icoll.contains(21))

        self.assertEqual(icoll.lower_bound, 10)
        self.assertEqual(icoll.upper_bound, 20)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_one_interval_intersection(self):
        '''Test intersections with a one interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection([[10, 20]])

        # Empty.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([])),
            IntegerIntervalCollection([])
            )
        # Disjoint below lower bound.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[2, 4]])),
            IntegerIntervalCollection([])
            )
        # Overlap across lower bound.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[2, 14]])),
            IntegerIntervalCollection([[10, 14]])
            )
        # Overlap across top of lowest interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[18, 24]])),
            IntegerIntervalCollection([[18, 20]])
            )
        # Enveloping lowest interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[2, 24]])),
            IntegerIntervalCollection([[10, 20]])
            )

        # N/A for singletons. # Crossing middle gap.
        # N/A for singletons. # Crossing two middle gaps.

        # N/A for singletons. # Overlap across bottom of middle interval.
        # N/A for singletons. # Adjacent to bottom of middle interval.
        # N/A for singletons. # Enveloping middle interval.
        # N/A for singletons. # Adjacent to top of middle interval.
        # N/A for singletons. # Overlap across top of middle interval.

        # N/A for singletons. # Enveloping highest interval.
        # N/A for singletons. # Overlap across bottom of highest interval.
        # N/A for singletons. # Overlap across upper bound.
        # N/A for singletons. # Disjoint above upper bound.

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_one_interval_union(self):
        '''Test unions with a one interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection([[10, 20]])

        # Disjoint below lower bound.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([])),
            icoll
            )
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[2, 4]])),
            IntegerIntervalCollection([[2, 4], [10, 20]])
            )
        # Overlap across lower bound.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[2, 14]])),
            IntegerIntervalCollection([[2, 20]])
            )
        # Overlap across top of lowest interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[18, 24]])),
            IntegerIntervalCollection([[10, 24]])
            )
        # Enveloping lowest interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[2, 24]])),
            IntegerIntervalCollection([[2, 24]])
            )

        # N/A for singletons. # Crossing middle gap.
        # N/A for singletons. # Crossing two middle gaps.

        # N/A for singletons. # Overlap across bottom of middle interval.
        # N/A for singletons. # Adjacent to bottom of middle interval.
        # N/A for singletons. # Enveloping middle interval.
        # N/A for singletons. # Adjacent to top of middle interval.
        # N/A for singletons. # Overlap across top of middle interval.

        # N/A for singletons. # Enveloping highest interval.
        # N/A for singletons. # Overlap across bottom of highest interval.
        # N/A for singletons. # Overlap across upper bound.
        # N/A for singletons. # Disjoint above upper bound.

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_two_intervals(self):
        '''Test with a two interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection([[10, 20], [30, 40]])

        self.assertEqual(icoll.interval_count, 2)
        self.assertFalse(icoll.is_empty)

        self.assertFalse(icoll.contains(9))
        self.assertTrue(icoll.contains(10))
        self.assertTrue(icoll.contains(11))
        self.assertTrue(icoll.contains(20))
        self.assertFalse(icoll.contains(21))
        self.assertFalse(icoll.contains(25))
        self.assertFalse(icoll.contains(29))
        self.assertTrue(icoll.contains(30))
        self.assertTrue(icoll.contains(31))
        self.assertTrue(icoll.contains(40))
        self.assertFalse(icoll.contains(41))

        self.assertEqual(icoll.lower_bound, 10)
        self.assertEqual(icoll.upper_bound, 40)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_two_intervals_intersection(self):
        '''Test intersections with a two interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection([[10, 20], [30, 40]])

        # Empty.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([])),
            IntegerIntervalCollection([])
            )
        # Disjoint below lower bound.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[2, 4]])),
            IntegerIntervalCollection([])
            )
        # Overlap across lower bound.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[2, 14]])),
            IntegerIntervalCollection([[10, 14]])
            )
        # Overlap across top of lowest interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[18, 24]])),
            IntegerIntervalCollection([[18, 20]])
            )
        # Enveloping lowest interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[2, 24]])),
            IntegerIntervalCollection([[10, 20]])
            )

        # Crossing middle gap.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[15, 35]])),
            IntegerIntervalCollection([[15, 20], [30, 35]])
            )
        # N/A for two intervals. # Crossing two middle gaps.

        # N/A for two intervals. # Overlap across bottom of middle interval.
        # N/A for two intervals. # Adjacent to bottom of middle interval.
        # N/A for two intervals. # Enveloping middle interval.
        # N/A for two intervals. # Adjacent to top of middle interval.
        # N/A for two intervals. # Overlap across top of middle interval.

        # Enveloping highest interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[22, 44]])),
            IntegerIntervalCollection([[30, 40]])
            )
        # Overlap across bottom of highest interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[28, 34]])),
            IntegerIntervalCollection([[30, 34]])
            )
        # Overlap across upper bound.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[38, 44]])),
            IntegerIntervalCollection([[38, 40]])
            )
        # Disjoint above upper bound.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[48, 54]])),
            IntegerIntervalCollection([])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_two_intervals_union(self):
        '''Test unions with a two interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection([[10, 20], [30, 40]])

        self.assertEqual(
            icoll.union(IntegerIntervalCollection([])),
            icoll
            )
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[2, 4]])),
            IntegerIntervalCollection([[2, 4], [10, 20], [30, 40]])
            )
        # Overlap across lower bound.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[2, 14]])),
            IntegerIntervalCollection([[2, 20], [30, 40]])
            )
        # Overlap across top of lowest interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[18, 24]])),
            IntegerIntervalCollection([[10, 24], [30, 40]])
            )
        # Enveloping lowest interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[2, 24]])),
            IntegerIntervalCollection([[2, 24], [30, 40]])
            )

        # Crossing middle gap.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[15, 35]])),
            IntegerIntervalCollection([[10, 40]])
            )
        # N/A for two intervals. # Crossing two middle gaps.

        # N/A for two intervals. # Overlap across bottom of middle interval.
        # N/A for two intervals. # Adjacent to bottom of middle interval.
        # N/A for two intervals. # Enveloping middle interval.
        # N/A for two intervals. # Adjacent to top of middle interval.
        # N/A for two intervals. # Overlap across top of middle interval.

        # Enveloping highest interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[22, 44]])),
            IntegerIntervalCollection([[10, 20], [22, 44]])
            )
        # Overlap across bottom of highest interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[28, 34]])),
            IntegerIntervalCollection([[10, 20], [28, 40]])
            )
        # Overlap across upper bound.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[38, 44]])),
            IntegerIntervalCollection([[10, 20], [30, 44]])
            )
        # Disjoint above upper bound.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[48, 54]])),
            IntegerIntervalCollection([[10, 20], [30, 40], [48, 54]])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_three_intervals(self):
        '''Test with a three interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection([[10, 20], [30, 40], [50, 60]])

        self.assertEqual(icoll.interval_count, 3)
        self.assertFalse(icoll.is_empty)

        self.assertFalse(icoll.contains(9))
        self.assertTrue(icoll.contains(10))
        self.assertTrue(icoll.contains(11))
        self.assertTrue(icoll.contains(20))
        self.assertFalse(icoll.contains(21))
        self.assertFalse(icoll.contains(25))
        self.assertFalse(icoll.contains(29))
        self.assertTrue(icoll.contains(30))
        self.assertTrue(icoll.contains(31))
        self.assertTrue(icoll.contains(40))
        self.assertFalse(icoll.contains(41))
        self.assertFalse(icoll.contains(45))
        self.assertFalse(icoll.contains(49))
        self.assertTrue(icoll.contains(50))
        self.assertTrue(icoll.contains(51))
        self.assertTrue(icoll.contains(60))
        self.assertFalse(icoll.contains(61))

        self.assertEqual(icoll.lower_bound, 10)
        self.assertEqual(icoll.upper_bound, 60)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_three_intervals_intersection(self):
        '''Test intersections with a three interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection([[10, 20], [30, 40], [50, 60]])

        # Empty.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([])),
            IntegerIntervalCollection([])
            )
        # Disjoint below lower bound.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[2, 4]])),
            IntegerIntervalCollection([])
            )
        # Overlap across lower bound.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[2, 14]])),
            IntegerIntervalCollection([[10, 14]])
            )
        # Overlap across top of lowest interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[18, 24]])),
            IntegerIntervalCollection([[18, 20]])
            )
        # Enveloping lowest interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[2, 24]])),
            IntegerIntervalCollection([[10, 20]])
            )

        # Crossing middle gap.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[15, 35]])),
            IntegerIntervalCollection([[15, 20], [30, 35]])
            )
        # Crossing two middle gaps.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[15, 55]])),
            IntegerIntervalCollection([[15, 20], [30, 40], [50, 55]])
            )

        # Overlap across bottom of middle interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[28, 34]])),
            IntegerIntervalCollection([[30, 34]])
            )
        # Adjacent to bottom of middle interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[25, 29]])),
            IntegerIntervalCollection([])
            )
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[25, 30]])),
            IntegerIntervalCollection([[30, 30]])
            )
        # Enveloping middle interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[22, 44]])),
            IntegerIntervalCollection([[30, 40]])
            )
        # Adjacent to top of middle interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[40, 44]])),
            IntegerIntervalCollection([[40, 40]])
            )
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[41, 44]])),
            IntegerIntervalCollection([])
            )
        # Overlap across top of middle interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[38, 44]])),
            IntegerIntervalCollection([[38, 40]])
            )

        # Enveloping highest interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[42, 64]])),
            IntegerIntervalCollection([[50, 60]])
            )
        # Overlap across bottom of highest interval.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[48, 54]])),
            IntegerIntervalCollection([[50, 54]])
            )
        # Overlap across upper bound.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[58, 64]])),
            IntegerIntervalCollection([[58, 60]])
            )
        # Disjoint above upper bound.
        self.assertEqual(
            icoll.intersection(IntegerIntervalCollection([[68, 74]])),
            IntegerIntervalCollection([])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_three_intervals_union(self):
        '''Test unions with a three interval IntegerIntervalCollection.
        '''

        icoll = IntegerIntervalCollection([[10, 20], [30, 40], [50, 60]])

        # Disjoint below lower bound.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([])),
            icoll
            )
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[2, 4]])),
            IntegerIntervalCollection([[2, 4], [10, 20], [30, 40], [50, 60]])
            )
        # Overlap across lower bound.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[2, 14]])),
            IntegerIntervalCollection([[2, 20], [30, 40], [50, 60]])
            )
        # Overlap across top of lowest interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[18, 24]])),
            IntegerIntervalCollection([[10, 24], [30, 40], [50, 60]])
            )
        # Enveloping lowest interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[2, 24]])),
            IntegerIntervalCollection([[2, 24], [30, 40], [50, 60]])
            )

        # Crossing middle gap.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[15, 35]])),
            IntegerIntervalCollection([[10, 40], [50, 60]])
            )
        # Crossing two middle gaps.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[15, 55]])),
            IntegerIntervalCollection([[10, 60]])
            )

        # Overlap across bottom of middle interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[28, 34]])),
            IntegerIntervalCollection([[10, 20], [28, 40], [50, 60]])
            )
        # Adjacent to bottom of middle interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[25, 29]])),
            IntegerIntervalCollection([[10, 20], [25, 40], [50, 60]])
            )
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[25, 30]])),
            IntegerIntervalCollection([[10, 20], [25, 40], [50, 60]])
            )
        # Enveloping middle interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[22, 44]])),
            IntegerIntervalCollection([[10, 20], [22, 44], [50, 60]])
            )
        # Adjacent to top of middle interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[40, 44]])),
            IntegerIntervalCollection([[10, 20], [30, 44], [50, 60]])
            )
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[41, 44]])),
            IntegerIntervalCollection([[10, 20], [30, 44], [50, 60]])
            )
        # Overlap across top of middle interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[38, 44]])),
            IntegerIntervalCollection([[10, 20], [30, 44], [50, 60]])
            )

        # Enveloping highest interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[42, 64]])),
            IntegerIntervalCollection([[10, 20], [30, 40], [42, 64]])
            )
        # Overlap across bottom of highest interval.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[48, 54]])),
            IntegerIntervalCollection([[10, 20], [30, 40], [48, 60]])
            )
        # Overlap across upper bound.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[58, 64]])),
            IntegerIntervalCollection([[10, 20], [30, 40], [50, 64]])
            )
        # Disjoint above upper bound.
        self.assertEqual(
            icoll.union(IntegerIntervalCollection([[68, 74]])),
            IntegerIntervalCollection([[10, 20], [30, 40], [50, 60], [68, 74]])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_removal(self):
        '''Test IntegerIntervalCollection removal (complement).
        '''

        icoll = IntegerIntervalCollection([[10, 20], [30, 40], [50, 60]])

        self.assertEqual(
            IntegerIntervalCollection().removed_from(
                IntegerIntervalCollection()
                ),
            IntegerIntervalCollection()
            )

        self.assertEqual(
            IntegerIntervalCollection().removed_from(icoll),
            icoll
            )

        self.assertEqual(
            icoll.removed_from(IntegerIntervalCollection()),
            IntegerIntervalCollection()
            )

        self.assertEqual(
            icoll.removed_from(IntegerIntervalCollection([[0, 70]])),
            IntegerIntervalCollection([[0, 9], [21, 29], [41, 49], [61, 70]])
            )

        self.assertEqual(
            icoll.removed_from(IntegerIntervalCollection([[10, 60]])),
            IntegerIntervalCollection([[21, 29], [41, 49]])
            )

        self.assertEqual(
            icoll.removed_from(IntegerIntervalCollection([[10, 20]])),
            IntegerIntervalCollection()
            )

        self.assertEqual(
            icoll.removed_from(IntegerIntervalCollection([[10, 30]])),
            IntegerIntervalCollection([[21, 29]])
            )

        self.assertEqual(
            icoll.removed_from(
                IntegerIntervalCollection([[10, 25], [35, 50]])
                ),
            IntegerIntervalCollection([[21, 25], [41, 49]])
            )

        self.assertEqual(
            icoll.removed_from(
                IntegerIntervalCollection([[21, 25], [41, 46]])
                ),
            IntegerIntervalCollection([[21, 25], [41, 46]])
            )

        self.assertEqual(
            IntegerIntervalCollection([
                [10, 20], [30, 40], [50, 60], [70, 80], [90, 100]
                ]).removed_from(
                    IntegerIntervalCollection([
                        [0, 0], [2, 6], [9, 11], [14, 16], [18, 20],
                        [23, 23], [25, 25], [27, 27], [30, 30], [34, 35],
                        [37, 37], [40, 41], [43, 44], [46, 49], [60, 60],
                        [62, 64], [66, 68]
                        ])
                ),
            IntegerIntervalCollection([
                [0, 0], [2, 6], [9, 9],
                [23, 23], [25, 25], [27, 27],
                [41, 41], [43, 44], [46, 49],
                [62, 64], [66, 68]
                ])
            )

        self.assertEqual(
            IntegerIntervalCollection([
                [10, 20], [30, 40], [50, 60], [70, 80], [90, 100]
                ]).removed_from(
                    IntegerIntervalCollection([[0, 0], [2, 6]])
                ),
            IntegerIntervalCollection([[0, 0], [2, 6]])
            )

        self.assertEqual(
            IntegerIntervalCollection([
                [10, 20], [30, 40], [50, 60], [70, 80], [90, 100]
                ]).removed_from(
                    IntegerIntervalCollection([[120, 200], [202, 206]])
                ),
            IntegerIntervalCollection([[120, 200], [202, 206]])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_interval_collection_union_commutativity(self):
        '''Test commutativity of IntegerIntervalCollection.union().
        '''

if __name__ == '__main__':
    unittest.main()
