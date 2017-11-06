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

'''Flatten nested list and dict structures.

A dictionary is *flat* if all of its values are either scalars or
lists of scalars. The ``flatten()`` function turns a nested structure
into a list of flat dictionaries. The keys in the resulting
dictionaries will be strings formed by the dot-separated ``join()``
of successively nested dictionary keys from the original dictionary.

    Example::

        >>> flatten.flatten({
        ...     'A': {
        ...         'b': 1,
        ...         'c': {
        ...             'x': 2,
        ...             'y': 3
        ...             }
        ...         }
        ...     })
        [{'A.c.y': 3, 'A.c.x': 2, 'A.b': 1}]

When a structure containing lists is flattened, the result will
include multiple flat dictionaries. A single list ``l`` will result in
``len(l)`` flat dictionaries in the result.

    Examples::

        >>> flatten.flatten({
        ...     'A': [
        ...             {'b': {'c': 1}},
        ...             {'b': {'c': 2}}
        ...             ]
        ...     })
        [{'A.b.c': 1}, {'A.b.c': 2}]

        >>> flatten.flatten({
        ...     'A': {
        ...         'b': [
        ...             {'c': 1},
        ...             {'c': 2}
        ...             ]
        ...         }
        ...     })
        [{'A.b.c': 1}, {'A.b.c': 2}]

    Note that the preceding examples show that flattening different
    structures can have the same result.

Multiple lists will result in multiple dictionaries according to the
product of their lengths.

    Example::

        >>> flatten.flatten({
        ...     'A': {
        ...         'b': [{'c': 1}, {'c': 2}, {'c': 3}],
        ...         'u': [{'v': 1}, {'v': 2}]
        ...         }
        ...     })
        [{'A.u.v': 1, 'A.b.c': 1}, {'A.u.v': 2, 'A.b.c': 1},
        {'A.u.v': 1, 'A.b.c': 2}, {'A.u.v': 2, 'A.b.c': 2},
        {'A.u.v': 1, 'A.b.c': 3}, {'A.u.v': 2, 'A.b.c': 3}]

.. note:: To be successfully flattened, a nested structure must satisfy the
    following criterion:

    All lists in the structure must contain only ``dict`` or scalar
    types, and all elements of a given list must be of the same type.

'''

import itertools
import json

DEFAULT_SEPARATOR = '.'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# is_scalar_type
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_scalar_type(the_type):
    '''Answer "is this type scalar?".'''
    return the_type in [
        type(None),
        bool,
        int,
        float,
        str,
        unicode,
        long,
        complex
        ]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# is_scalar
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_scalar(the_thing):
    '''Answer "is the type of this thing a scalar type?".'''

    return is_scalar_type(type(the_thing))


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# # is_or_is_dict_of
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# def is_or_is_dict_of(the_thing, predicate):
#     '''
#     Answer "is this a thing or list of things for which predicate is true?"
#     '''

#     return is_scalar_type(type(the_thing))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# is_primitive_type
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_primitive_type(the_type):
    '''Answer "is this type primitive?".'''
    return is_scalar(the_type) or the_type in [
        type({}),
        type([])
        ]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# is_primitive
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_primitive(the_thing):
    '''Answer "is the type of this thing a primitive type?".'''

    return is_primitive(type(the_thing))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def flatten(
        entity,
        path_prefix=None,
        require_serializable=False,
        flatten_leaves=False,
        to_depth=None,
        separator=DEFAULT_SEPARATOR
        ):  # pylint: disable=bad-continuation
    '''Construct a list of flat dicts representing a nested structure.

    Parameters:

        entity (list or dict)
            The python entity to be flattened.

        path_prefix (str)
            A dot-separated string path. If defined, this will be
            prepended to the paths extracted from ``entity``.

        require_serializable (bool)
            If ``True``, a ``TypeError`` will be raised if an
            unserializable type is encountered while flattening
            ``entity``. If ``False``, a serializable replacement
            representation of the unserializable structure will be
            substituted (e.g., the result of calling ``str()`` on the
            structure.)

        flatten_leaves (bool)
            If ``False``, lists of scalars will be treated as leaf
            nodes. If ``True``, lists of scalars will be flattened.

            Example::

                >>> flatten.flatten({'A': [1,2,3]})
                [{'A': [1, 2, 3]}]
                >>> flatten.flatten({'A': [1,2,3]}, flatten_leaves=True)
                [{'A': 1}, {'A': 2}, {'A': 3}]

        to_depth (int)
            The maximum depth to which to flatten.

    The return value from ``flatten`` will be a list of dicts, where
    each of the dicts values is either a scalar value or a simple list
    of scalar values.

    The entity being flattened must be a dictionary, list or scalar
    value. It can contain no "immediately nested" lists; all lists it
    contains must occur as the value for the key of a dict, and must
    contain only other dicts or only scalars. A ``TypeError`` will be
    raised if any other list is encountered.

    If the ``path_prefix`` parameter is ``None``, entity must be an instance
    of dict or a list of instances of dict, or a ``ValueError`` will
    be raised.

    If ``flatten`` encounters an unserializable type at a leaf of a
    dict, the behavior is determined by the value of the
    ``require_serializable`` parameter:

        **True:** Raise the ``TypeError`` resulting from attempting to
        serialize the structure with ``json.dumps()``.

        **False:** First see if the structure responds to a
        ``to_dict()`` method and use the result of that in place of
        the original structure. If this approach doesn't succeed,
        replace the original structure with the result of calling
        ``str()`` on it.

    '''
    # if to_depth is None:
    #     print "Flattening(%s): %s" % (to_depth, entity)

    if to_depth is not None and to_depth <= 0:
        # print "DEEP: %s" % entity
        return entity

    # Scalar: return a single item dict wrapped in an list.
    # Anything else that's not handled further down: try to serialize
    # into JSON. If that fails either raise a TypeError or return the
    # stringification of the entity.
    if not isinstance(entity, list) and not isinstance(entity, dict):
        if not is_scalar(entity):
            try:
                entity = json.dumps(entity)
            except TypeError as err:
                if require_serializable:
                    raise err
                else:
                    entity = str(entity)
        # print "(scalar) %s" % entity

        return entity if path_prefix is None else [{path_prefix: entity}]

    elif isinstance(entity, list):

        # --=----=----=----=----=----=----=----=----=----=----=----=--
        # TODO: Can we handle heterogenous lists?

        # # Flatten non-scalars separately, then merge.
        # scalars = [s for s in entity if is_scalar(s)]
        # non_scalars = [s for s in entity if not is_scalar(s)]

        # # Flatten the resulting list elements.
        # return [
        #     x for x in itertools.chain(
        #         *[flatten(
        #             d,
        #             path_prefix=path_prefix,
        #             require_serializable=require_serializable,
        #             to_depth=to_depth
        #             ) for d in non_scalars
        #             ]
        #         )
        #     ] + scalars if path_prefix is None else [{path_prefix: scalars}]

        # --=----=----=----=----=----=----=----=----=----=----=----=--

        # print "((%s) list: %s -> %s)" % (flatten_leaves, path_prefix, entity)
        # List of scalars: return a single item dict wrapped in a list.
        if False not in [is_scalar(x) for x in entity]:
            if path_prefix is None:
                return entity
            elif (
                    flatten_leaves is True or (
                        isinstance(flatten_leaves, list) and
                        path_prefix in flatten_leaves
                        )
                    ):  # pylint: disable=bad-continuation
                return [{path_prefix: e} for e in entity]
            else:
                return [{path_prefix: entity}]

        # List of dicts: return a list of flattened dicts.
        # if True not in [isinstance(x, scalar) for x in entity]:
        if False not in [isinstance(x, dict) for x in entity]:
            return [
                x for x in itertools.chain(
                    *[
                        flatten(
                            d,
                            path_prefix=path_prefix,
                            require_serializable=require_serializable,
                            flatten_leaves=flatten_leaves,
                            to_depth=to_depth,
                            separator=separator
                            ) for d in entity
                        ]
                    )
                ]

        # # List of lists: raise the child lists up a level.
        if False not in [isinstance(x, list) for x in entity]:
            return flatten(
                reduce(lambda m, n: m + n, [l for l in entity]),
                path_prefix=path_prefix,
                require_serializable=require_serializable,
                flatten_leaves=flatten_leaves,
                to_depth=to_depth,
                separator=separator
                )

        # Any other list: raise a TypeError.
        raise TypeError(
            'only homogenous lists of scalars, dicts or other lists'
            ' can be flattened.'
            )

    elif isinstance(entity, dict):
        # print "(dict: %s -> %s)" % (path_prefix, entity)
        if to_depth == 1:
            # This will be the last flattening level.
            if path_prefix is None:
                return [entity]
            else:
                return [{
                    separator.join([path_prefix, k]): v
                    for (k, v) in entity.items()
                    }]

        else:
            to_depth_next = None if to_depth is None else to_depth - 1
            # print to_depth

            # First convert all values to lists of sorted dicts as
            # results from the flatten call. This adds each key k to the
            # path_prefixs that are the keys in the new dict values, to its
            # own value, so the existing keys become superfluous.
            # print "Flattening values..."
            with_flattened_values = {
                k: flatten(
                    entity[k],
                    path_prefix=(
                        k if path_prefix is None
                        else separator.join([path_prefix, k])
                        ),
                    require_serializable=require_serializable,
                    flatten_leaves=flatten_leaves,
                    to_depth=to_depth_next,
                    separator=separator
                    )
                for k in entity
                }
            # for k in entity:
            #     print "%s: %s" % (k, entity[k])
            # print "Flattened: %s" % with_flattened_values

            # values_product = [
            #     z
            #     for z in itertools.product(*with_flattened_values.values())
            #     ]
            # print values_product
            # print [isinstance(x, dict) for x in values_product[0]]

            # Then return all combinations of an element of each list of
            # dicts. dict(x, **y) is dict constructor syntax for
            # x.update(y), so the reduce operation takes a list of
            # separate dicts and combines them into a single dict. This
            # would clobber earlier entires if their key occurs as a
            # later entry; we depend on the uniqueness of the path_prefixs to
            # ensure this doesn't happen.
            # print to_depth
            values_product = itertools.product(*with_flattened_values.values())

            return [
                reduce(lambda x, y: dict(x, **y), z)
                for z in values_product
                if z
                ]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def flatten_disjoint(
        *entities,
        **kwargs
        ):  # pylint: disable=bad-continuation
    '''Flatten multiple structures and return a single flat list of dicts.

    Arguments:

        entities (tuple):
            A tuple of entities to be flattened.

        kwargs:
            Any named arguments will be passed to the calls to
            ``flatten()`` for each entity in ``entities`.

    '''

    flattened = []

    # This is a special case. If to_depth is 0, flatten() returns the
    # entities unchanged.

    to_depth = kwargs.get('to_depth')
    if to_depth is not None and to_depth <= 0:
        return entities

    for entity in entities:
        flattened.extend(flatten(entity, **kwargs))

    return flattened
