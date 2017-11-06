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

'''Manage and manipulate collections of intervals.

The ``IntegerIntervalCollection`` class handles manipulation of collections
of closed intervals of integers.

Examples::

    >>> interval_collection = IntegerIntervalCollection([[10, 20]])
    >>> interval_collection
    IntegerIntervalCollection([[10, 20]])

    >>> (interval_collection.lower_bound, interval_collection.upper_bound)
    (10, 20)

    >>> interval_collection.contains(11)
    True
    >>> interval_collection.contains(21)
    False

    >>> interval_collection.intersection(IntegerIntervalCollection([[12, 24])])
    IntegerIntervalCollection([[12, 20]])

    >>> interval_collection.intersection(IntegerIntervalCollection([[22, 24]]))
    IntegerIntervalCollection([])

    >>> interval_collection = IntegerIntervalCollection([[10, 20], [30, 40]])
    IntegerIntervalCollection([[10, 20], [30, 40]])

    >>> interval_collection.intervals
    2

    >>> (interval_collection.lower_bound, interval_collection.upper_bound)
    (10, 40)

    >>> interval_collection.intersection(IntegerIntervalCollection([[18, 32])])
    IntegerIntervalCollection([[18, 20], [30, 32]])

    >>> interval_collection.union(IntegerIntervalCollection([[18, 30])])
    IntegerIntervalCollection([[10, 40]])

    >>> interval_collection.union(
    ...     IntegerIntervalCollection([[18, 30])
    ...     ).intervals
    1

'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def validate_intervals(intervals):
    '''Check that intervals are well-defined.

    Interval items must be pairs of integers, with the first
    element less than the second.

    '''

    for interval in intervals:

        if not isinstance(interval, list) or len(interval) != 2:
            raise ValueError(
                'IntegerIntervalCollecion intervals must be'
                ' pairs of integers'
                )

        if not (
                isinstance(interval[0], int)
                and isinstance(interval[1], int)
                ):  # pylint: disable=bad-continuation
            raise ValueError(
                'IntegerIntervalCollecion interval endpoints must'
                ' be integers'
                )

        if interval[0] > interval[1]:
            raise ValueError(
                'IntegerIntervalCollecion interval left endpoint'
                ' must not be greater than right endpoint'
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def canonicalize_intervals(intervals):
    '''Put intervals into canonical form.

    Canonical form means in increasing order, with overlaps
    combined into a single interval.

    '''
    validate_intervals(intervals)

    if len(intervals) == 0:
        return intervals

    # Sort on lower edge of each interval.
    intervals = sorted(list(intervals), key=lambda x: x[0])

    # We know the canonicalized list will start where the first
    # of the now sorted intervals starts.
    canonicalized_intervals = [list(intervals[0])]

    # The range will be empty if len(intervals) == 1, etc.
    for index in range(1, len(intervals)):
        # Check if the next interval overlaps or abuts the previous.
        if canonicalized_intervals[-1][1] >= intervals[index][0] - 1:
            # They overlap or abut. Merge them. We know the lower
            # endpoints of the intervals are sorted in ascending order,
            # so we just need to extend the endpoint of the previous.
            canonicalized_intervals[-1][1] = max(
                canonicalized_intervals[-1][1],
                intervals[index][1]
                )
        else:
            # They don't overlap. Just add the next interval to the list.
            canonicalized_intervals.append(list(intervals[index]))

    return canonicalized_intervals


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def union(intervals_1, intervals_2):
    '''Return the union of two sets of intervals.

    Arguments:

        intervals_1, intervals_2 (lists of lists):
            The intervals lists whose union to find.

    Returns:
        (list) A set of canonicalized intervals representing the
        union of intervals_1 and intervals_2.

    '''

    return canonicalize_intervals(intervals_1 + intervals_2)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def intersection(intervals_1, intervals_2, canonicalized=False):
    '''Return the intersection of two sets of intervals.

    Arguments:

        intervals_1, intervals_2 (lists of lists):
            The intervals lists whose intersection to find.

        canonicalized (bool, default=False):
            If ``True``, the ``intervals_1`` and ``intervals_2``
            will be assumed to be already in canonical form. If False,
            ``canonicalized_intervals()`` will be called to ensure
            they are in canonical form.

    Returns:
        (list) A set of canonicalized intervals representing the
        intersection of intervals_1 and intervals_2.

    '''
    if not canonicalized:
        intervals_1 = canonicalize_intervals(intervals_1)
        intervals_2 = canonicalize_intervals(intervals_2)

    intersections = []

    index_1, index_2 = 0, 0

    while index_1 < len(intervals_1) and index_2 < len(intervals_2):

        interval_1 = intervals_1[index_1]
        interval_2 = intervals_2[index_2]

        # interval_1 is entirely to the left of interval_2.
        if interval_1[1] < interval_2[0]:
            index_1 += 1
            continue

        # interval_2 is entirely to the left of interval_1.
        if interval_2[1] < interval_1[0]:
            index_2 += 1
            continue

        # Neither of the above, so they intersect. Record the lower
        # and upper boundary values of their intersection.
        intersect_lb = max(interval_1[0], interval_2[0])
        intersect_ub = min(interval_1[1], interval_2[1])
        intersections.append([intersect_lb, intersect_ub])

        # We're done with either interval whose right endpoint was the
        # right endpoint of the intersection.
        if interval_1[1] == intersect_ub:
            index_1 += 1
        if interval_2[1] == intersect_ub:
            index_2 += 1

        # Superfluous continue, but just for consistency with above.
        continue

    return intersections


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def removed_from(intervals_rmv, intervals_keep, canonicalized=False):
    '''Return the result of removing one set of intervals from another.

    Arguments:

        intervals_rmv, intervals_keep (lists of lists):
            The intervals lists whose difference to find.

        canonicalized (bool, default=False):
            If ``True``, the ``intervals_rmv`` and ``intervals_keep``
            will be assumed to be already in canonical form. If False,
            ``canonicalized_intervals()`` will be called to ensure
            they are in canonical form.

    Returns:
        A set of canonicalized intervals representing the integers in
        intervals_keep that are not in intervals_rmv.

    '''
    if not canonicalized:
        intervals_rmv = canonicalize_intervals(intervals_rmv)
        intervals_keep = canonicalize_intervals(intervals_keep)

    remaining = []

    # print
    # print "------------------------------"

    index_rmv, index_keep = 0, 0
    working_interval = None

    while index_rmv < len(intervals_rmv) and index_keep < len(intervals_keep):

        interval_rmv = intervals_rmv[index_rmv]
        interval_keep = intervals_keep[index_keep]
        if working_interval is None:
            working_interval = list(interval_keep)

        # print "RMV: %s" % intervals_rmv
        # print "KEEP: %s" % intervals_keep
        # print "Working: %s" % working_interval

        # interval_rmv is entirely to the left of working_interval.
        if interval_rmv[1] < working_interval[0]:
            index_rmv += 1
            continue

        # working_interval is entirely to the left of interval_rmv.
        if working_interval[1] < interval_rmv[0]:
            index_keep += 1
            remaining.append(working_interval)
            working_interval = None
            continue

        # Neither of the above, so they intersect.
 
        # We may keep some left hand side of working_interval.
        if working_interval[0] < interval_rmv[0]:
            remaining.append([working_interval[0], interval_rmv[0] - 1])

        # We're only done with working_interval if it ends after
        # interval_rmv ends. Otherwise we keep the remaining
        # working_interval.

        if interval_rmv[1] <= working_interval[1]:
            index_rmv += 1

        if interval_rmv[1] < working_interval[1]:
            working_interval[0] = interval_rmv[1] + 1

        else:
            index_keep += 1
            working_interval = None

        # Superfluous continue, but just for consistency with above.
        continue

    # If we ran out of intervals_rmv before we used up the last
    # working interval and/or any remaining intervals_keep:
    if working_interval is not None:
        remaining.append(working_interval)
        index_keep += 1
    remaining.extend(intervals_keep[index_keep:])

    return remaining


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class IntegerIntervalCollection(object):
    '''Manage collections of integer intervals.

    Arguments:

        intervals (list of lists):
            A list of lists representing the intervals for this
            IntegerIntervalCollection. Each sub-list must be a list of
            two integers in ascending order.

    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, intervals=None):
        '''Initialize an IntegerIntervalCollection instance. '''

        super(IntegerIntervalCollection, self).__init__()
        self._intervals = []
        if intervals is not None:
            self._intervals = canonicalize_intervals(intervals)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Equality related methods thanks to Hal Weiss's answer to
    # https://stackoverflow.com/questions/390250/
    # elegant-ways-to-support-equivalence-equality-in-python-classes
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __repr__(self, other):
        '''Pretty printing. '''
        return '{}({})'.format(self.__class__.__name__, self.intervals)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __eq__(self, other):
        '''Override the default Equals behavior. '''
        if isinstance(other, self.__class__):
            # print "Checking Equality!"
            # print self.__dict__
            # print other.__dict__
            return self.__dict__ == other.__dict__
        return NotImplemented

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __ne__(self, other):
        '''Define a non-equality test. '''
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __hash__(self):
        '''Override the default hash behavior (that returns id or object). '''
        return hash(tuple(sorted(self.__dict__.items())))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def intervals(self):
        '''Return this instance's intervals. '''
        return self._intervals

    @intervals.setter
    def intervals(self, intervals):
        '''Set this instance's intervals. '''
        if intervals is not None:
            self._intervals = canonicalize_intervals(intervals)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def lower_bound(self):
        '''Return the smallest value in any of this instance's intervals. '''
        if len(self._intervals) > 0:
            return self._intervals[0][0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def upper_bound(self):
        '''Return the largest value in any of this instance's intervals. '''
        if len(self._intervals) > 0:
            return self._intervals[-1][1]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def interval_count(self):
        '''Return the number of intervals in this instance's list. '''
        return len(self._intervals)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def is_empty(self):
        '''Answer "is this instance's intervals list empty?" '''
        return len(self._intervals) == 0

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def contains(self, value):
        '''Answer "is this value in some interval in this instance?" '''
        for interval in self._intervals:
            if interval[0] <= value and value <= interval[1]:
                return True
        return False

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def intersection(self, other):
        '''Return the intersection with other's intervals. '''
        return IntegerIntervalCollection(
            intersection(self.intervals, other.intervals)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def union(self, other):
        '''Return the union with other's intervals. '''
        return IntegerIntervalCollection(
            union(self.intervals, other.intervals)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def removed_from(self, other):
        '''Return the complement in other's intervals. '''
        return IntegerIntervalCollection(
            removed_from(self.intervals, other.intervals)
            )
