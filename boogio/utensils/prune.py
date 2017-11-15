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

'''Extract and manipulate branches and leaves of trees.

Intuitively, a *branch* in a *tree* (a structure that consists of
nested dictionaries, lists and scalar primitives) is a path, specified
as a sequence of dictionary keys and list elements, through structures
in the  tree. A *maximal branch* is a path to a single scalar value,
which will be a leaf of the tree. See the terminology section below
for a more "formal" definition.

Terminology
---------------

Throughout this documentation, the following terms are used.

    Scalar
        A python value of one of the following types: bool, int,
        float, str, unicode, long, complex or NoneType.

    Tree
        A python structure consisting of nested dictionaries, lists
        and scalars.

    Subtree
        A tree constructed from what is left after some elements are
        removed from a specified tree.

    Leaf
        A scalar value or a list of scalar values in a tree.

    Branch
        A tree in which all dictionaries and lists are of length 1. A
        *branch in a tree* is a branch which is contained in the tree.
        A *maximal branch* in a tree is a branch in the tree which is
        not properly contained in any other branch in the tree.

    Flat
        The result of calling ``go980sec_utils.flatten.flatten()`` on
        a structure.

        *   The result of flattening a branch is a list whose only
            element is a dictionary with one key formed by joining all
            the dictionary keys of the branch and whose value is the
            leaf value of the branch.

        *   The result of flattening a tree is a list whose elements
            are the dictionaries resulting from flattening all the
            branches of the tree.

    Path and Path Targets
        A specification of dictionary keys and positions where lists
        occur in a tree, either as a list of strings or as a single
        dot-separated string. The *LIST_INDICATOR* symbol ``[]`` is
        used to indicate the position of lists in a path.

        A tree ``T`` *contains* a path ``P`` (represented as a list)
        means:

            *   ``P[0]`` is a top level key in ``T``. The *target* of
                ``P[0]`` in ``T`` is the value ``T[P[0]]``.

            *   For any ``n`` less than ``len(P)``,

                *   If the target of ``P[:n]`` is one or more
                    dictionaries, ``P[n+1]`` is a key in one or more
                    of these dictionaries. A *target* of ``P[:n+1]``
                    in ``T`` is any value ``D[P[n]]`` where ``D`` is
                    one of these dictionaries containing ``P[n]``.

                *   If the target of ``P[:n]`` is a list, ``P[n+1]``
                    is the LIST_INDICATOR symbol ``[]``. A *target* of
                    ``P[:n+1]`` is any element of the list.

'''

import logging
# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        '''Placeholder handler.'''
        def emit(self, record):
            '''Dummy doctstring for flake8.'''
            pass

# import itertools
from boogio.utensils import flatten

logging.getLogger(__name__).addHandler(NullHandler())

# Set this to true to see tracing between start_trace() and stop_trace().
globals()['trace_on'] = False

# A module level logger for use in trace().
_LOGGER = logging.getLogger(__name__)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def start_trace():
    '''Turn on tracing output.

    Because of the extensive recursion used when pruning, detailed
    debug logging is normally disabled. Call ``start_trace()`` to
    enable detailed logging at run time.

    '''

    globals()['trace_on'] = True


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def stop_trace():
    '''Turn off tracing output.

    Because of the extensive recursion used when pruning, detailed
    debug logging is normally disabled. Call ``stop_trace()`` to
    disable detailed logging that has been enabled by
    ``start_trace()``.

    '''

    globals()['trace_on'] = False


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def trace(msg, log_level=logging.DEBUG):
    '''Print tracing output.

    Arguments:

        msg (str):
            The message to log.

        log_level (int):
            The ``logging`` module log level at which to log ``msg``.

    '''

    if globals()['trace_on']:

        _LOGGER.log(log_level, msg)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def listpath(path, no_lists=False):
    '''Convert a path to a list of path elements.

    Arguments:

        path (list or str):
            The path to convert to a list representation.

        no_lists (bool):
            If true, all "expect list at this level" indicators will
            be stripped out of the resulting path elements.

    If ``path`` is already in list form, the only effect of
    ``listpath()`` is removing "list at this level" indicators if
    ``no_lists`` is ``True``.

    Examples::

        >>> listpath('A.B.[].C')
        ['A', 'B', '[]', C']

        >>> listpath('A.B.[].C', no_lists=True)
        ['A', 'B', C']

        >>> listpath(['A', 'B', '[]', C'])
        ['A', 'B', '[]', C']

        >>> listpath(['A', 'B', '[]', C'], no_lists=True)
        ['A', 'B', C']

    '''

    if isinstance(path, list):
        as_list = path
    elif isinstance(path, str):
        as_list = path.split('.')
    else:
        raise TypeError(
            "can't convert type '%s' to listpath" % type(path).__name__
            )
    if no_lists:
        as_list = [x for x in as_list if x != Pruner.LIST_INDICATOR]
    return as_list


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def dotpath(path, no_lists=False):
    '''Convert a path to a dot-separated representation.

    Arguments:

        path (list or str):
            The path to convert to a list representation.

        no_lists (bool):
            If true, all "expect list at this level" indicators will
            be stripped out of the resulting path elements.

    If ``path`` is already in dot-separated form, the only effect of
    ``dotpath()`` is removing "list at this level" indicators if
    ``no_lists`` is ``True``.

    Examples::

        >>> dotpath(['A', 'B', '[]', C'])
        'A.B.[].C'

        >>> dotpath(['A', 'B', '[]', C'], no_lists=True)
        'A.B.C'

        >>> dotpath('A.B.[].C')
        'A.B.[].C'

        >>> dotpath('A.B.[].C', no_lists=True)
        'A.B.C'

    '''

    if isinstance(path, list):
        if no_lists:
            path = [x for x in path if x != Pruner.LIST_INDICATOR]
        return '.'.join(path)
    elif isinstance(path, str):
        if no_lists:
            path = dotpath(listpath(path, no_lists=no_lists))
        return path
    else:
        raise TypeError(
            "can't convert type '%s' to dotpath" % type(path).__name__
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def paths(tree, depth=None, show_list_size=False):
    '''Return a list of all paths through containers in a tree.

    Arguments:

        tree:
            A structure containing only lists, dicts and scalars.

        depth (int, >=0):
            How far down the containers to go, at most.

        show_list_size (bool):
            If True, lists of length n will be represented as '[n]'.
            if False, lists will be represented as LIST_INDICATOR.

    Returns: A list of strings representing all paths of length at
    most depth down into tree.

    Examples::

        >>> paths({'A': ['b', {'c': 3, 'd': 4}]})
        ['A.[].c', 'A.[].d', 'A.[]']

        >>> prune.paths({'A': ['b', {'c': 3, 'd': 4}]}, show_list_size=True)
        ['A.[2]', 'A.[2].d', 'A.[2].c']

        >>> prune.paths({'A': ['b', {'c': 3, 'd': 4}]}, depth=1)
        ['A']

        >>> prune.paths({'A': ['b', {'c': 3, 'd': 4}]}, depth=2)
        ['A.[]']

    '''

    # - - - - - - - - - - - - - - - - - - - - - - - -
    def list_representation(a_list):
        '''List representation based on show_list_size.

        Note that show_list_size is captured from the outer scope, not
        explicitly passed.
        '''
        return (
            '[%s]' % len(a_list)
            if show_list_size
            else Pruner.LIST_INDICATOR
            )

    # - - - - - - - - - - - - - - - - - - - - - - - -
    def _element_paths(parent_rep, element, depth):
        '''Find all paths in element to a given depth and prepend parent_rep.

        Arguments:

            parent_rep:
                The representation of the list of which ``element`` is
                a member, either LIST_INDICATOR or [#] (where # is the
                length  of the parent list).

            element (tree):
                The tree in which to find paths.

            depth (int or None):
                The depth to which to find paths in tree.

        Returns:

            (list) A list of path representations formed by
            prepending ``parent_rep`` to each path representation of
            entries in ``element``.

        '''
        return_paths = paths(element, depth, show_list_size)
        return (
            [parent_rep] if len(return_paths) == 0
            # else ['.'.join([LIST_INDICATOR, p]) for p in return_paths]
            else [
                '.'.join([parent_rep, p])
                for p in return_paths
                ]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - -
    def _item_paths(key, value, depth):
        '''Find paths to a given depth in a dict item's value and prepend key.

        Arguments:

            key (string):
                The key in the dict item, repesenting the deepest
                node yet added to the paths which are the final goal
                of the calling method.

            value (tree):
                The value in the dict item, in which to find paths.

            depth (int or None):
                The depth to which to find paths in tree.

        Returns:

            (list) A list of path representations formed by
            prepending ``key`` to each path representation found in
            ``value``.

        '''

        return_paths = paths(value, depth, show_list_size)
        return (
            [key] if len(return_paths) == 0
            else ['.'.join([key, p]) for p in return_paths]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - -

    # The depth to pass into the next call to paths().
    new_depth = None if depth is None else depth - 1

    # print "(%s) %s" % (depth, tree)

    # Only these containers are represented in path strings.
    if (
            not (isinstance(tree, dict) or isinstance(tree, list)) or
            len(tree) == 0
            ):  # pylint: disable=bad-continuation
        # print "  SCALAR: %s" % tree
        return_paths = []

    elif depth == 0:
        # We're not supposed to go deeper, so ignore the tree and
        # just return no paths.
        return_paths = []

    # - - - - - - - - - - - - - - - - - - - - - - - -
    elif isinstance(tree, dict):
        # print "  DICT: %s" % tree
        # Get a list of all paths in sub-trees.
        return_paths = reduce(
            lambda x, y: x + y,
            [
                # ['.'.join([k, p]) for p in paths(v, new_depth)]
                _item_paths(k, v, new_depth)
                for (k, v) in tree.items()
                ]
            )
        if len(return_paths) == 0:
            # return_paths = tree.keys()
            pass  # Checking - return_paths should never be empty.
        else:
            return_paths = list(set(return_paths))

    # - - - - - - - - - - - - - - - - - - - - - - - -
    elif isinstance(tree, list):
        # print "  LIST: %s" % tree
        # Get a list of all paths in sub-trees.
        return_paths = reduce(
            lambda x, y: x + y,
            [
                # [p for p in paths(l, new_depth) if p is not None]
                _element_paths(list_representation(tree), l, new_depth)
                for l in tree
                ]
            )
        if len(return_paths) == 0:
            # return_paths = [list_representation(tree)]
            pass  # Checking - return_paths should never be empty.
        else:
            # Remove duplicates.
            return_paths = list(set(return_paths))

    # else:
    #     return None
    # print return_paths
    return return_paths


# TODO: This would probably be useful.
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# class PruneSpec(object):
#     '''Manage a prune specification.

#     Arguments:

#         path_to_none (bool):
#             If True, convert "None" prunings to a dict with the
#             current dotted-string path as key and 'None' as the value.

#         flatten (bool):
#             If True, prunings will be flattened.

#         rename:
#             Flattened prunings will have their path keys changed to
#             the value of the rename option.

#     '''
#     def __init__(self, path_spec):
#         '''
#         Initialize a PruneSpec instance.
#         '''
#         pass


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Pruner(object):
    '''Manage specifications and execution of tree pruning.

    Arguments:

        prune_specs (tuple of dict):
            Dictionaries that define the target of a pruning
            and any additional manipulations to be carried out on the
            target.

                A prune_spec (pruning specification) supports the
                following fields:

                **path** (list or str): The path to the source
                element(s) to be extracted from the source.

                **flatten_leaves** (bool): If ``True``, any lists
                encountered as leaf nodes in pruning will be converted
                to a list of branches with leaf values from the list
                of leaf nodes.

                **value_refiner** (function): If defined, the targets
                of the pruning specification's path will be replaced
                by the result of passing them to this function
                whenever they are included in the return value for a
                method that uses the pruning specification.

    '''

    LIST_INDICATOR = '[]'

    @classmethod
    def path_to_tree(cls, path, value=None):
        '''Convert the path to a tree with the final value as specified.

        The resulting tree is such that pruning the tree with ``path``
        as the pruning specification would be the identity operation.

        Arguments:

            path (list):
                A list of keys or indexes defining the path to the
                source content that is the target to be extracted.

            value:
                The value to use as the "deepest" value in the most-
                nested dict or list constructed.

        '''
        path = listpath(path)

        if len(path) == 0:
            return value

        if path[0] == cls.LIST_INDICATOR:
            return [cls.path_to_tree(path[1:], value)]

        else:
            return {path[0]: cls.path_to_tree(path[1:], value)}

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, *prune_specs):
        '''Initialize a Pruner instance.'''

        self.prune_specs = list(prune_specs)

        # This is used as an accumulator during recursion when
        # extracting values from a subtree.
        self._subtree_values_buffer = None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _extract_from_source(
            self,
            source,
            specs=None,
            get_values=False,
            _depth=0
            ):  # pylint: disable=bad-continuation
        '''Extract elements of source specified by path_spec.

        Arguments:

            source (dict):
                A nested container tree.

            specs (list of prune specs, optional):
                A list of specs to prune from the tree. If not passed,
                ``self.specs`` will be applied. In the course of
                pruning, ``get_subtree()`` is called recursively and
                the specs that are still relevant in the next call
                are passed along.

            get_values (bool):
                If ``True``, return a dict whose keys are the path
                specs (with no list indicators) in the depth zero
                list of specs and whose values are lists of all the
                values for those paths that occur in ``source``.

            _depth (int):
                An internal counter to track how many recursive calls
                of get_subtree are nested above this one.

        Returns:

            A tree all of whose branches match the paths in the
            indicated specs.

        '''

        # TODO: Better document get_values effect.

        # '''
        # path_to_none -- A flag which if set to True indicates that if path[0]
        #     is a miss for this source, get_subtree() should return a dict
        #     {k: None}, where k is the remainder of path.
        # '''

        pre = '  ' * _depth
        trace(pre + "--> DEPTH: %s" % _depth)
        trace(pre + "SPECS: %s" % specs)
        trace(pre + "SOURCE: %s" % source)
        trace(pre + "SELF.PRUNE_SPECS: %s" % self.prune_specs)

        # Initialize our return value.
        final_extraction = None

        if _depth == 0:

            # Initialize our specs list.
            if specs is None:
                specs = self.prune_specs
                trace(pre + 'ASSIGNED SPECS: %s' % specs)

            # Initialize our values accumulator.
            if get_values:
                self._subtree_values_buffer = {
                    dotpath(spec['path'], no_lists=True): []
                    for spec in specs
                    }

        # Extract still-'running' specs.
        unfinished_specs = [
            ps for ps in specs
            if len(listpath(ps['path'])) > _depth
            ]
        finishing_specs = [
            ps for ps in specs
            if len(listpath(ps['path'])) == _depth
            ]
        trace(pre + 'FINISHING SPECS: %s' % finishing_specs)
        trace(pre + 'UNFINISHED SPECS: %s' % unfinished_specs)
        # - - - - - - - - - - - - - - - - - - - - - - - -
        # If there are any running specs that are at their terminus,
        # they must be pointing to this source as their value. There should
        # only ever be one such spec, as otherwise the assignment of values
        # to paths would fail in the calling instance of this method.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        if len(finishing_specs) > 0:

            assert len(finishing_specs) == 1
            finishing_spec = finishing_specs[0]
            trace(pre + 'VALUE: %s' % source)

            if 'value_refiner' in finishing_specs[0]:
                source = finishing_spec['value_refiner'](source)

            if get_values:
                path = dotpath(finishing_spec['path'], no_lists=True)
                self._subtree_values_buffer[path].append(source)
                trace(
                    pre + "ACCUMULATED: %s" % self._subtree_values_buffer[path]
                    )
                # if isinstance(source, list):
                #     self._subtree_values_buffer[finishing_spec].extend(
                #         source
                #         )
                # else:
                #
            else:
                final_extraction = source

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Map all running specs across this list.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        elif isinstance(source, list):
            trace(pre + 'LIST')
            matching_specs = [
                ps for ps in unfinished_specs
                if listpath(ps['path'])[_depth] == self.LIST_INDICATOR
                ]
            # If any specs don't mention a list at this point, it indicates
            # an incorrect/invalid path was in such a spec.
            unexpected_specs = [
                ps for ps in unfinished_specs
                if listpath(ps['path'])[_depth] != self.LIST_INDICATOR
                ]

            if len(unexpected_specs) > 0:
                unexpected_paths = [ps['path'] for ps in unexpected_specs]
                raise KeyError(
                    "array wildcard '%s' expected in paths %s at %s" % (
                        self.LIST_INDICATOR, unexpected_paths, source
                        )
                    )
            # unexpected_specs is empty, so matching_specs is nonempty
            extraction = [
                self.get_subtree(
                    s,
                    matching_specs,
                    get_values=get_values,
                    _depth=_depth + 1
                    )
                for s in source
                ]
            # Don't pass back every subtree that didn't match some path spec.
            extraction = [e for e in extraction if e is not None]

            if len(extraction) == 0:
                trace(pre + "LIST: Empty extraction")
                if not get_values:
                    final_extraction = None
            else:
                trace(pre + "LIST: extraction %s" % extraction)
                if not get_values:
                    final_extraction = extraction

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # This source isn't a list, so process it as a dict.
        # TODO: If it's something else or None?
        # - - - - - - - - - - - - - - - - - - - - - - - -
        # else:
        elif isinstance(source, dict):

            trace(pre + 'DICT')
            matching_specs = [
                ps for ps in unfinished_specs
                if listpath(ps['path'])[_depth] in source
                ]

            if len(matching_specs) == 0:
                trace(pre + "DICT: NO MATCHING PATHS.")
                if not get_values:
                    final_extraction = None

            else:
                trace(pre + "DICT: MATCHING PATHS: %s" % matching_specs)
                extraction = {
                    k: self.get_subtree(
                        source[k],
                        [
                            ps for ps in matching_specs
                            if listpath(ps['path'])[_depth] == k
                            ],
                        get_values=get_values,
                        _depth=_depth + 1
                        )
                    for k in source
                    if k in [
                        listpath(ps['path'])[_depth]
                        for ps in matching_specs
                        ]
                    }

                if len([
                        v for v in extraction.values() if v is not None
                        ]) == 0:
                    trace(pre + "DICT: Empty extraction")
                    if not get_values:
                        final_extraction = None
                else:
                    trace(pre + "DICT: extraction %s" % extraction)
                    if not get_values:
                        final_extraction = extraction

        trace(pre + "<--\n")
        if get_values and _depth == 0:
            return self._subtree_values_buffer
        else:
            return final_extraction

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def get_subtree(self, *args, **kwargs):
        '''Extract subtrees of source according to specs.

        Arguments:

            source (dict):
                A nested container tree.

            specs (list of prune specs, optional):
                A list of specs to prune from the tree. If not passed,
                ``self.specs`` will be applied. In the course of
                pruning, ``get_subtree()`` is called recursively and
                the specs that are still relevant in the next call
                are passed along.

        Returns:

            dict: A tree all of whose branches match the indicated
            path.

        '''
        return self._extract_from_source(*args, **kwargs)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def prune_tree(self, source):
        '''Prune source and return the subtree matching the prune specs.'''
        return self.get_subtree(
            source
            )
        # return self.prune(source, prune_type='tree')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def prune_branches(
            self,
            source,
            balanced=False,
            require_serializable=False
            ):
        '''Prune source and return the branches matching the prune specs.

        Arguments:

            balanced (bool):
                If True, the superset of all keys that occur in any
                branch will be included in all branches returned. If a
                branch was missing one of these keys it will be added
                with a placeholder value of None. Thus all the dicts
                in the list returned will have an identical set of
                keys.

            require_serializable (bool):
                This will be passed through to flatten. If True,
                flatten raises an exception if an unserializable value
                is encountered.

        Returns:

            (list of dicts): A flattened list of dicts with keys
            derived from prune_spec paths for the pruner and values
            the corresponding leaf values for those paths.

        '''
        pruned = self.get_subtree(
            source
            )
        trace("PRUNED: %s" % pruned)
        flatten_leaves_path_prefix = [
            dotpath(ps['path'], no_lists=True)
            for ps in self.prune_specs
            if 'flatten_leaves' in ps and ps['flatten_leaves']
            ]
        pruned = flatten.flatten(
            pruned,
            flatten_leaves=flatten_leaves_path_prefix,
            require_serializable=require_serializable
            )

        if balanced:
            all_keys = {
                dotpath(ps['path'], no_lists=True): None
                for ps in self.prune_specs
                }

            if pruned is None or pruned == []:
                pruned = [{}]
            pruned = [dict(all_keys, **p) for p in pruned]

        return pruned

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def prune_leaves(self, *args, **kwargs):
        '''Extract path: values items from source according to specs.

        Arguments:

            source (dict):
                A nested container tree.

            specs (list of prune specs, optional):
                A list of specs to prune from the tree. If not passed,
                ``self.specs`` will be applied.

        Returns:

            dict: A dictionary whose keys are the spec paths, less
            list indicators, and whose values are the source values
            that occur at those paths in ``source``. Each source value
            may occur multiple times in each list of values in the
            returned dictionary.

        '''
        return self._extract_from_source(
            get_values=True, *args, **kwargs
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rake_leaves(self, *args, **kwargs):
        '''Extract values from source according to specs.

        Arguments:

            source (dict):
                A nested container tree.

            specs (list of prune specs, optional):
                A list of specs to prune from the tree. If not passed,
                ``self.specs`` will be applied. In the course of
                pruning, ``get_subtree()`` is called recursively and
                the specs that are still relevant in the next call
                are passed along.

        Returns:

            list: A list of values that occur at the spec paths in
            ``source``. Each value will occur only once, and the order
            is indeterminate.

        '''
        pruned_leaves = self._extract_from_source(
            get_values=True, *args, **kwargs
            )

        raked_leaves = set()
        # We'll try the faster set hashing first. If that fails, we'll
        # fall back to walking item by item.
        hashable = True

        for leaves in pruned_leaves.values():
            if hashable:
                try:
                    raked_leaves = raked_leaves.union(set(leaves))
                except TypeError:
                    hashable = False
                    # pylint: disable=redefined-variable-type
                    raked_leaves = list(raked_leaves)
            if not hashable:
                for leaf in leaves:
                    if leaf in raked_leaves:
                        continue
                    raked_leaves.append(leaf)

        return list(raked_leaves)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def leaf_satisfies(self, tree, branch_path, criterion):
        '''Check if a leaf of a tree satisfies a criterion.

        Arguments:

            tree (list, dict or scalar):
                The tree against which to check the criterion.

            branch_path (list or string, or ``None``):
                A path specification of the leaves of ``tree`` against
                which to check the criterion, or ``None``.

                If ``branch_path`` is ``None``, ``criterion(tree)``
                will be returned.

                If ``branch_path`` is not ``None``, it must be a path
                at least one level deep; empty paths are not allowed.

            criterion (function):
                A function taking a single argument and returning a
                boolean.

        Returns:

            (bool) ``True`` if ``criterion`` returns ``True`` when
            passed the value of some leaf of ``tree`` specified by
            ``branch_path``. ``False`` if no such leaf exists.

        '''

        if branch_path is None:
            return criterion(tree)

        branch_path = listpath(branch_path)
        assert len(branch_path) > 0

        current_path = branch_path[0]
        next_level_path = None if len(branch_path) == 1 else branch_path[1:]
        # print
        # print tree
        # print '%s %s' % (current_path, next_level_path)
        # print

        # Index dict with string, iterate over list.
        if current_path == self.LIST_INDICATOR:
            assert isinstance(tree, list)
            for node in tree:
                if self.leaf_satisfies(node, next_level_path, criterion):
                    return True

            # No node satisfied, so return False.
            return False

        else:
            return (
                current_path in tree and
                self.leaf_satisfies(
                    tree[current_path], next_level_path, criterion
                    )
                )
