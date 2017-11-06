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

'''Indexing utilities.'''

from collections import defaultdict, Hashable
import itertools
import logging
# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        '''Placeholder handler.'''
        def emit(self, record):
            '''Dummy docstring for flake8.'''
            pass

from utensils import prune

logging.getLogger(__name__).addHandler(NullHandler())


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def invert_index(index):
    '''Swap index keys and values.

    Arguments:

        index (dict):
            A dictionary whose values are lists of hashable types.

    Returns:

        (dict) A dictionary ``inverted`` whose keys are the items in
        the original ``index`` dictionary's values, and whose values
        are lists of the original ``index``'s keys. If ``(k, V)`` is a
        key-value pair in ``index``, every ``v`` in ``V`` will be a
        *key* in ``inverted``, and ``k`` will be an element of the
        *value* list for each ``v`` in ``V``.

    Raises:

        TypeError: if any of the values to be used as keys are not
        hashable.

    Example::

        >>> index1 = {'k1': ['v1', 'v2', v3], 'k2': ['v2', 'v3', v4]}
        >>> invert_index(index1)
        {'v1': ['k1'], 'v2': ['k1', 'k2'], 'v3': ['k1', 'k2'], 'v4': ['k2']}

    '''
    inverted = {}

    for (key, values) in index.iteritems():

        for value in values:

            if value not in inverted:
                inverted[value] = []

            inverted[value].append(key)

    return inverted


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def uid_index(forest, uid_path=None, uid_method=None):
    '''Index a set of nested structures by a specified unique id.

    Arguments:

        forest (list):
            A list of nested structures composed of lists, dicts and
            scalars to be indexed by unique id.

        uid_path (str):
            A prune path specification specifying the path to the
            unique ID value for each structure in ``forest``. See the
            ``utensils.prune`` module documentation for details.

        uid_method (function):
            A function that takes a single argument and when passed a
            structure in ``forest`` returns the unique ID value for
            that structure.

    Exactly one of uid_path and uid_method is required.

    Returns:

        (dict) A dictionary where each item key is the value selected
        by ``uid_path`` in each element of ``forest``, and the
        corresponding item value is the element of ``forest`` from
        which that value was selected.

    Raises:

        KeyError: if the value selected by ``uid_path`` from an
        element of ``forest`` was already selected from a previous
        element of ``forest``. This would indicate a duplication of
        the supposedly unique IDs.

        TypeError: if neither uid_path nor uid_method is provided, or
        if both are.

    '''
    logger = logging.getLogger(__name__)

    index = {}

    # Exactly one of uid_path and uid_method must be defined.
    defined_extractor_count = 2 - (uid_path, uid_method).count(None)
    if defined_extractor_count != 1:
        err_msg = (
            'uid_index: exactly one of uid_path and uid_method is required;'
            ' found %s' % ('neither', '', 'both')[defined_extractor_count]
            )
        logger.error(err_msg)
        raise TypeError(err_msg)

    for tree in forest:

        index_keys = []

        if uid_path:

            # It's unclear whether this ought to enforce getting a
            # single element list for index_keys.
            pruner = prune.Pruner({'path': prune.dotpath(uid_path)})
            for (_, pruned_keys) in pruner.prune_leaves(tree).items():
                index_keys.extend(pruned_keys)

        else:
            # Wrap this for consistency with the prune_leaves return
            # value type.
            index_keys = [uid_method(tree)]

        for index_key in list(set(index_keys)):

            if index_key in index:
                msg = (
                    'uid_index: duplicate occurrence of unique ID %s'
                    )
                logger.error(msg, index_key)
                raise KeyError(msg % index_key)

            index[index_key] = tree

    return index


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def index_by_method(forest, method):
    '''Build an index by values returned by applying a method to structures.

    Arguments:

        forest:
            A list of nested structures composed of lists, dicts and
            scalars.

        method:
            A method that returns a hashable type or a list of
            hashable types when applied to each member of ``forest``.

    Returns:

        (dict) A dictionary in which each key is a value returned by
        ``method`` in one or more of the elements of ``forest``, and
        in which each value is a list of all elements for which that
        value was returned either singly or as an element of a list.

    '''

    index = defaultdict(list)

    for tree in forest:
        result = method(tree)
        if isinstance(result, Hashable):
            result = [result]
        for key in result:
            index[key].append(tree)

    return dict(index)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def index_by_path(forest, path, **kwargs):
    '''Build an index by the values at a path into a nested structure.

    Arguments:

        forest (list):
            A list of nested structures composed of lists, dicts and
            scalars.

        path:
            A prune path specification. See the
            ``utensils.prune`` module documentation for details.

        duplicates (boolean, optional):
            If ``False`` (the default), no duplicate values will
            appear in the lists of values for each key in the index
            returned. If ``True``, duplicates can occur.

        prep_method (function):
            If defined, the index's keys will be the values at the
            specified paths in the output of ``prep_method`` applied to
            each member of ``forest``. The values of the index will be
            the original members of ``forest``.

        key_method (function, optional):
            If defined,  each key ``K`` that would appear as a key in
            the resulting index will be replaced by the result of
            evaluating ``key_method(K)``.

        value_method (function, optional):
            If defined,  each value ``V`` that would appear in the
            list of values for any key in the resulting index will be
            replaced by the result of evaluating ``value_method(V)``.

    Returns:

        (dict) A dictionary in which each key is a value that occurs
        at the location specified by ``path`` in one or more of the
        elements of ``forest``, and in which each value is a list of
        all elements for which that value occurs there.

    '''

    index = index_by_paths(forest, [path], **kwargs)
    if index:
        return index[prune.dotpath(path, no_lists=True)]
    else:
        return {}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def index_by_paths(
        forest, paths, duplicates=False,
        prep_method=None, key_method=None, value_method=None,
        ):  # pylint: disable=bad-continuation
    '''Build indices by values at specified paths into nested structures.

    Arguments:

        forest (list):
            A list of nested structures composed of lists, dicts and
            scalars.

        paths (list):
            A list of prune path specifications. See the
            ``utensils.prune`` module documentation for details.

        duplicates (boolean, optional):
            If ``False`` (the default), no duplicate values will
            appear in the lists of values for each key in the indices
            returned. If ``True``, duplicates can occur.

        prep_method (function, optional):
            If defined, the indices' keys will be the values at the
            specified paths in the output of ``prep_method`` applied
            to each member of ``forest``. The values of the indices
            will be the original members of ``forest``.

        key_method (function, optional):
            If defined,  each key ``K` that would appear as a key in
            the resulting indices will be replaced by the result of
            evaluating ``key_method(K)``.

        value_method (function, optional):
            If defined,  each value ``V`` that would appear in the
            list of values for any key in the resulting indices will
            be replaced by the result of evaluating
            ``value_method(V)``.

    Returns:

        (dict) A dictionary in which each value is an index of the
        structures in ``forest`` by the values of the elements
        selected by one ``path`` in ``paths``. The dictionary key for
        a given index value will be the "list-reduced dot separated"
        representation of ``path``. This is the string returned by
        the function call
        ``utensils.prune.dotpath(path, no_lists=True)``.


    The resulting structure will look like this::

        {
        path:
                {
                path_valueA: [tree1, tree2, ...],
                path_valueB: [...],
                ...
                },
            ...
            }

    Here, the path_valueX keys are the values that occur at path
    in any of the elements of forest, and the list for each key is
    exactly the elements of forest for which the path_valueX value
    occurs at path. Note that the values selected by a path in
    ``paths``, or the values returned by ``key_method()``, if defined,
    must be hashable, as they will be keys in an index.

    '''
    pruner = prune.Pruner(
        *[{'path': prune.dotpath(p)} for p in paths]
        )
    indices = {}
    # print [{'path': p} for p in paths]

    for tree in forest:

        prepped_tree = prep_method(tree) if prep_method else tree

        for (path, path_values) in pruner.prune_leaves(prepped_tree).items():

            if path not in indices:
                indices[path] = {}

            for index_key in list(set(
                    [key_method(v) if key_method else v for v in path_values]
                    )):  # pylint: disable=bad-continuation

                if index_key not in indices[path]:
                    indices[path][index_key] = []

                value = value_method(tree) if value_method else tree

                if value not in indices[path][index_key] or duplicates:
                    indices[path][index_key].append(value)

    return indices


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def index_subtrees_by_paths(
        forest, paths, subtree_paths, duplicates=False,
        prep_method=None, key_method=None, value_method=None,
        ):  # pylint: disable=bad-continuation
    '''Build indices of subtrees of nested structures.

    Arguments:

        forest:
            A nested structure composed of lists, dicts and scalars.

        paths:
            A list of prune path specifications. See the
            ``utensils.prune`` module documentation for details.

        subtree_paths:
            A list of prune-style path specifications to the subelements
            to be indexed.

        duplicates (boolean, optional):
            If ``False`` (the default), no duplicate values will
            appear in the lists of values for each key in the indices
            returned. If ``True``, duplicates can occur.

        prep_method (function):
            If defined, each element of ``forest`` will be replaced
            locally with the result of passing it to the
            ``prep_method`` method. Thus,
            ``index_subtrees_by_paths([t1, t2], p, sp, prep_method=m)``
            will return the same value as
            ``index_subtrees_by_paths([m(t1), m(t2)], p, sp)``.

        key_method (function, optional):
            If defined,  each key ``K`` that would appear as a key in
            the resulting index will be replaced by the result of
            evaluating ``key_method(K)``.

        value_method (function, optional):
            If defined,  each value ``V`` that would appear in the
            list of values for any key in the resulting index will be
            replaced by the result of evaluating ``value_method(V)``.


    Returns:

        (dict) A dict whose keys are the list-reduced elements of paths,
        and whose values are dicts. The structure will look like this::

            {
            index_path:
                {
                    path_valueA: [subtree1, subtree2, ...],
                    path_valueB: [...],
                    ...
                    },
                ...
            }

        Here, the path_valueX keys are the values that occur at path
        in any of the elements of forest, and the list for each key is
        the specified subtrees taken from the elements of forest for
        which the path_valueX value occurs at path.

    '''
    index_pruner = prune.Pruner(
        *[{'path': prune.dotpath(p)} for p in paths]
        )
    subtree_pruner = prune.Pruner(
        *[{'path': prune.dotpath(p)} for p in subtree_paths]
        )

    indices = {}
    # print [{'path': p} for p in paths]

    for tree in forest:

        prepped_tree = prep_method(tree) if prep_method else tree

        index_leaves = index_pruner.prune_leaves(prepped_tree)
        subtrees = subtree_pruner.prune_leaves(prepped_tree)
        # print subtrees

        for (index_path, path_values) in index_leaves.items():

            if index_path not in indices:
                indices[index_path] = {}

            # for path_value in list(set(path_values)):

            for index_key in list(set(
                    [key_method(v) if key_method else v for v in path_values]
                    )):  # pylint: disable=bad-continuation

                if index_key not in indices[index_path]:
                    indices[index_path][index_key] = []

                for (_, subtree) in subtrees.items():
                    if value_method:
                        subtree = [value_method(t) for t in subtree]
                    # if (
                    #         value not in indices[index_path][index_key] or
                    #         duplicates
                    #         ):  # pylint: disable=bad-continuation
                    #     # print value
                    #     # print indices[index_path][index_key]
                    #     # print value not in indices[index_path][index_key]
                    indices[index_path][index_key].extend(
                        [
                            v for v in subtree
                            if (
                                v not in indices[index_path][index_key] or
                                duplicates
                                )
                            ]
                        )
                    # print indices[index_path][index_key]
                    # print

    return indices


# TODO: Add the prep_method parameter?
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def subindex_list(
        dictlist, index_keys=None, index_items=None, balanced=False
        ):  # pylint: disable=bad-continuation
    '''Split a list of dicts into multiple indexed sublists.

    Arguments:

        dictlist (list of dict):
            The list to subindex.

        index_keys (list):
            A list of keys on which to subindex. One indexed sublist
            will be created for each tuple of values found in the
            elements of dictlist.

        index_items (dict):
            A dict whose keys are the keys on which to subindex, and
            whose values are lists of the values for which to separate
            the subindex.

        balanced (bool):
            If ``True`` and ``index_items`` is defined, include empty
            entries for every value in ``index_items`` not found in
            ``dictlist`` in the returned list.

    Exactly one of ``index_keys`` and ``index_items`` must be defined.

    If ``index_items`` is defined, the items in the sublist created
    will be added in the order defined by the value lists.

    All of the values in any element of ``dictlist`` of keys on which
    to index must be hashable.

    Returns:

        (list) A list of dictionaries. Each dictionary contains the
        following fields.

            *   indexed_items (list of list):A list of key-value
                pairs representing the keys and values on which
                ``dictlist`` was indexed. The key in each pair will be
                one of the entries in ``index_keys`` or a key in
                ``index_items``.

            *   'elements' (list): The selected elements of
                ``dictlist`` that make up this sublist. Each element
                will contain an item ``(key, value)`` for every pair
                in indexed_items.

        E.g.::

            [
                {
                    'indexed_items': [
                        ['field1', 'value1a'],
                        ['field2', 'value2a'],
                        ...
                        ],
                    # All of these elements will have
                    # {'field1': 'value1a' and 'field2': 'value 2a'}
                    'elements': [item1, item2, ...]
                    },
                {
                    'indexed_items': [
                        ['field1', 'value1b'],
                        ['field2', 'value2b'],
                        ...
                        ],
                    # All of these elements will have
                    # {'field1': 'value1b' and 'field2': 'value 2b'}
                    'elements': [item1, item2, ...]
                    },
                    ...
                ]

    '''

    logger = logging.getLogger(__name__)

    logger.debug(
        'subindexing dictlist with index_keys=%s, index_items=%s',
        index_keys, index_items
        )

    if bool(index_keys) == bool(index_items):
        err_msg = 'exactly one of index_keys and index_items expected'
        err_msg += {
            True: ' (found both)',
            False: ' (found neither)'
            }[bool(index_keys)]
        logger.error(err_msg)
        raise ValueError(err_msg)

    # TODO: It may be useful to add an "index_sort" parameter, which
    # would pass a dictionary of functions to use to sort the values
    # list for each index_item key.

    # If we didn't receive an index_items dict, create one from
    # index_keys, where all the values that occur for each key are
    # the item values. Otherwise, grab index_keys from index_items.
    if not index_keys:
        index_keys = index_items.keys()
        logger.debug('using defined index_items: %s', index_items)
    elif not index_items:
        index_items = defaultdict(set)
        for element in dictlist:
            for key in index_keys:
                if key in element:
                    index_items[key].add(element[key])
        for key, value in index_items.iteritems():
            index_items[key] = sorted(list(value))
            logger.debug('using extracted index_items: %s', index_items)

    # This will provide a reference list of all tuples of possible
    # keys and values, sorted in order according to index_keys and the
    # values lists in index_items.values().
    kv_pairs = []
    for index_key in index_keys:
        logger.debug('index_items[index_key]: %s', index_items[index_key])
        kv_pairs.append([
            (index_key, value) for value in index_items[index_key]
            ])
    # We now need to generate all elements of the cartesian product of
    # all index_values, in order by index_key and index_values.
    possible_dictlist_index_keys = itertools.product(*kv_pairs)

    # We'll build the sublist structures as an index, then convert to
    # the list structure at the end.
    dictlist_index = defaultdict(list)

    for element in dictlist:
        # Each index key will consist of a tuple of (key, value) pairs
        # where element[key] == value, or (key, None) if key is not
        # present in element.
        element_key = tuple([
            (k, element[k] if k in element else None)
            for k in index_keys
            ])
        dictlist_index[element_key].append(element)
    logger.debug('dictlist_index keys: %s', dictlist_index.keys())

    subindexed_list = []

    for index_key in possible_dictlist_index_keys:
        if balanced or (index_key in dictlist_index):
            if index_key in dictlist_index:
                elements = dictlist_index[index_key]
            else:
                elements = []
            subindexed_list.append({
                'indexed_items': index_key,
                'elements': elements
                })

    return subindexed_list


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def compound_subindex_list(dictlist, indexers):
    '''Recursively index dictlist according to a series of indexers.

    Arguments:

        dictlist (list of dict):
            The list to subindex.

        indexers (list of dict):
            A list whose elements are keyword argument dictionaries to
            pass to ``subindex_list()``. Each (key, value) item in
            ``indexers`` must be a valid parameter and its value for
            that function. The ``dictlist`` parameter is not included
            in the indexer parameter kwargs.

    '''

    subindexed_list = subindex_list(dictlist, **indexers[0])

    next_indexers = indexers[1:]
    if next_indexers:
        for subindexed_sublist in subindexed_list:
            subindexed_sublist['elements'] = compound_subindex_list(
                subindexed_sublist['elements'],
                indexers=next_indexers
                )

    return subindexed_list
