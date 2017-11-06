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

'''Construct an index of a set of strings by their common leading substring.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def index_by_common_leading_string(strings_to_index):
    '''Index strings by their common leading substring.

    Arguments:

        strings_to_index (list of str):
            The strings to further index.

    Returns:

        (dict): An index of groups of strings by their common leading
        substring.

    The longest leading substrings common to two or more of
    ``strings_to_index`` will be used as the indices. Thus if a group
    of the strings to index share a leading substring, and a subset of
    that group share a longer leading substring, that subset will be
    indexed separately from any of the strings indexed by the shorter
    leading substring.

    Example::

        >>> leading_string.index_by_common_leading_string(
        ...     ['abc123', 'abc456', 'abXY', 'abXZ', 'abCCC', 'abDDD', 'aA']
        ...     )
        {'abX': ['abXY', 'abXZ'], 'a': ['aA'],
        'abc': ['abc123', 'abc456'],'ab': ['abCCC', 'abDDD']}

    '''
    return _index_by_common_leading_string(strings_to_index)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _index_by_common_leading_string(strings_to_index, leader='', depth=0):
    '''Recursion engine for index_by_common_leading_string.

    Arguments:

        leader (str):
            The current common indexing initial substring for all
            strings in strings_to_index.

        depth (int):
            The current recursion depth.

    See ``index_by_common_leading_string`` for additional parameter and
    return value information.

    '''

    # Initially, remove any duplicate strings. This simplifies some
    # recursion code paths below.
    if depth == 0:
        strings_to_index = list(set(strings_to_index))

    # Syntax sugar: index_posn is the character position to use for
    # the next level of indexing of each string.
    index_posn = len(leader)

    # Create a temporary index by the character at index_posn in
    # each string. Keys are characters that occur at index_posn,
    # values are lists of all strings with that character at
    # index_posn. If the current leader is also a complete string in
    # strings_to_index, it will be added to by_char_index as the
    # only value in the list with key the empty string.
    by_char_index = {}
    for string in strings_to_index:

        # The leader should occur as the leading substring in all the
        # strings to index. If this assertion ever failed, we called
        # this method with invalid parameters.
        assert len(string) >= index_posn

        if len(string) == index_posn:

            # In this case, this string is equal to leader, and will
            # occur in its own index. Because we eliminated
            # duplicates at depth 0, it occurs uniquely, and so
            # will be handled as a singleton below. So we'll index it
            # with an empty string and let it be handled there.
            assert '' not in by_char_index
            index_char = ''

        else:
            index_char = string[index_posn]

        if index_char not in by_char_index:
            by_char_index[index_char] = []

        by_char_index[index_char].append(string)

    # We'll store a recursively constructed common-initial-substring
    # index for all the strings_to_index in refined_index. This will
    # be our return value once complete.
    refined_index = {}

    # The singletons list will be all of the strings for which leader
    # is already the common leading substring; these are identified
    # by being the only string in one of the string lists in the
    # values in by_char_index.
    #
    # Note that one of these may be the occurrence
    # of a string equal to leader, in which case (char, char_values)
    # in the iteration below will be ('', leader).
    singletons = []

    for (char, char_values) in by_char_index.iteritems():

        # print '{:<3}\'{}\': ({}, {})'.format(
        #     depth, leader, char, char_values
        #     )

        if len(char_values) == 1:
            # The longest initial substring of all of the strings that
            # occur as a singleton char_values list is leader. We
            # don't want to recurse on these, so we record them
            # separately here so we can assign them to the index of
            # leader below.
            singletons.extend(char_values)

        else:
            # Because we eliminated duplicates at depth 0, the only
            # possible case where char == '' is a singleton where
            # char_values == [leader]. This matters, as it means we
            # won't get into an infinite recursion, since new_leader
            # is always strictly longer than leader.
            assert char != ''
            new_leader = leader + char

            # With this recursion, we'll walk down all the strings
            # that have longer leading substrings until in a deeper
            # recursive call they're handled by the singeltons case
            # below.
            refined_index.update(
                _index_by_common_leading_string(
                    char_values,
                    leader=new_leader,
                    depth=depth + 1
                    )
                )

    # Again, new_leader was always strictly longer than leader above,
    # so leader isn't a key in refined_index yet.
    if len(singletons) > 0:
        refined_index[leader] = singletons

    return refined_index


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TODO: This needs test cases.
def without_common_leading_substring(strings):
    '''Find what's left when a common leading substring is removed.

    Arguments:

        strings (list):
            A list of strings.

    Returns:

        (list): A list of the remaining tails of strings after the
        common leading substring is removed from each.

    Example::

        >>> without_common_leading_substring(
        ...     ['abc123', 'abc456', 'abXY', 'abXZ', 'abCCC', 'abDDD']
        ...     )
        ['c123', 'c456', 'XY', 'XZ', 'CCC', 'DDD']

    '''

    common_len_max = min([len(s) for s in strings])

    # Run through strings until we hit a position where they differ.
    posn = 0
    while posn < common_len_max:
        if len(set([s[posn] for s in strings])) > 1:
            break
        posn += 1

    # posn now holds the index of the first not-common character in
    # strings. E.g. for ['abcd', 'abc', 'abcxyz'] posn would now be 3.
    return [s[posn:] for s in strings]
