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

'''Manage connecting to and retrieving information for specified AWS entities.

An instance of ``AWSInformer`` corresponds to some type of AWS entity,
and includes functionality to help manage the data associated with
that entity and its related AWS elements. Some examples include:

    *   An EC2 instance includes references to entities such as VPCs,
        subnets, security groups and so on. Using the
        ``EC2InstanceInformer`` subclass of ``AWSInformer``, you can
        easily associate records for these entities and see their
        relationships with the record for the EC2 instance.

    *   AWS entities have Tags that are represented internally as a
        mapping ``{"Key": key, "Value": value}``. Using
        an informer you can treat these as a mapping
        ``{"key": "value"}`` for easier manipulation.

    *   Elastic Load Balancer entities have a DNS entry field, whose
        corresponding IP address an ``ELBInformer`` instance can look
        up and treat as a full fledged attribute of the informer.

``AWSInformer`` instances retrieve their data through an instance of
the` ``AWSMediator`` class. The ``AWSMediator`` instance caches entity
information so that, for example, multiple EC2 instances with the same
AWS Security Group assigned don't trigger multiple AWS queries for the
Security Group's data.

You can define filters in an ``AWSMediator`` instance that will be
applied to limit the entities retrieved from AWS by that mediator.
Mediator filters are defined per entity type using the
``add_filters()`` method. The allowed filters are generally those for
the relevant client's ``describe_X()`` method, where ``X`` depends on
the entity type. Thus the legal filters for an "eip" entity type are
those documented in the ec2 client's ``describe_addresses()`` method,
etc.

'''

import copy
# import itertools
import json
from multiprocessing import Pool
import os
import socket
import time


import logging
# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        '''Placeholder handler.'''
        def emit(self, record):
            '''Dummy docstring.'''
            pass

import boto3
import botocore

from boogio import site_boogio
from utensils import flatten
# from utensils import prune

logging.getLogger(__name__).addHandler(NullHandler())

DEFAULT_UTC_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S+00:00"


# TODO: These globals should probably be in the boogio __init__.py?
_AWS_DOTDIR_NAME = '.aws'
_AWS_DOTDIR_PATH = os.path.join(os.path.expanduser('~'), _AWS_DOTDIR_NAME)

_DEFAULT_BOOGIO_CONFIG_FILENAME = 'boogio.json'
BOOGIO_CONFIG_FILENAME = os.environ.setdefault(
    'BOOGIO_CONFIG_FILENAME', _DEFAULT_BOOGIO_CONFIG_FILENAME
    )

_DEFAULT_BOOGIO_CONFIG_FILEPATH = os.path.join(
    _AWS_DOTDIR_PATH, BOOGIO_CONFIG_FILENAME
    )
BOOGIO_CONFIG_FILEPATH = os.environ.setdefault(
    'BOOGIO_CONFIG_FILEPATH', _DEFAULT_BOOGIO_CONFIG_FILEPATH
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _load_boogio_config():
    '''Load the boogio json config file, if present.'''
    config_data = {}

    if os.path.exists(BOOGIO_CONFIG_FILEPATH):

        with open(BOOGIO_CONFIG_FILEPATH, 'r') as fptr:
            config_data = json.load(fptr)

    return config_data


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
_BOOGIO_CONFIG = _load_boogio_config()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _entity_type_informer_class_map():
    '''Return a mapping of entity types to AWSInformer classes.'''
    # Update for new AWSInformer subclass.
    return {
        'ec2': EC2InstanceInformer,
        'elb': ELBInformer,
        'security_group': SecurityGroupInformer,
        'vpc': VPCInformer,
        'vpc_peering_connection': VpcPeeringConnectionInformer,
        'internet_gateway': InternetGatewayInformer,
        'nat_gateway': NatGatewayInformer,
        'autoscaling': AutoScalingGroupInformer,
        'subnet': SubnetInformer,
        'network_interface': NetworkInterfaceInformer,
        'network_acl': NetworkAclInformer,
        'route_table': RouteTableInformer,
        'eip': EIPInformer,
        'emr': EMRInformer,
        'sqs': SQSInformer,
        'iam': IAMInformer,
        # 'ip_permissions': IpPermissionsInformer,
        }


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _informer_identifier_key_map():
    '''Return a mapping of AWSInformer classes and their identifier keys.'''
    # Update for new AWSInformer subclass.
    return {
        ELBInformer: 'LoadBalancerName',
        EMRInformer: 'Id',
        EC2InstanceInformer: 'InstanceId',
        SecurityGroupInformer: 'GroupId',
        VPCInformer: 'VpcId',
        VpcPeeringConnectionInformer: 'VpcPeeringConnectionId',
        InternetGatewayInformer: 'InternetGatewayId',
        NatGatewayInformer: 'NatGatewayId',
        AutoScalingGroupInformer: 'AutoScalingGroupARN',
        SubnetInformer: 'SubnetId',
        NetworkInterfaceInformer: 'NetworkInterfaceId',
        NetworkAclInformer: 'NetworkAclId',
        RouteTableInformer: 'RouteTableId',
        EIPInformer: 'PublicIp',
        SQSInformer: 'QueueURL',
        }


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _prevent_duplicate_informer_init_if_cached(original_init):
    '''Only proceed with __init__() if an informer isn't already cached.

    AWSInformer subclass __init__ methods can be called multiple
    times on a single instance, due to the redefinition of
    __new__() to check for an existing informer in the mediator's
    informer_cache. If we find the resource's identifier in the
    mediator's informer_cache, we don't do any initialization
    here. If we don't find it, we both initialize and update the
    mediator's cache.

    '''
    def decorated(self, resource, *args, **kwargs):
        # pylint: disable=missing-docstring

        mediator = kwargs['mediator'] if 'mediator' in kwargs else None

        # We have to figure out if we're already in the mediator's
        # informer cache. Our key would be our resource identifier.
        # pylint: disable=protected-access
        entity_identifier = self._get_init_entity_identifier(resource)

        # If our attempt to look it up failed, entity_identifier could
        # be None, which shouldn't be a key in the mediator's
        # informer_cache anyway.
        if mediator is not None:
            assert None not in mediator.informer_cache

        if (
                mediator is None or
                entity_identifier not in mediator.informer_cache
                ):  # pylint: disable=bad-continuation

            # We didn't find ourself in the cache, so we'll initialize
            # ourself anew.
            original_init(self, resource, *args, **kwargs)

            # Put ourself in the cache for next time.
            mediator.informer_cache[entity_identifier] = self

        else:
            # We found ourself in the cache. Let's make sure it's
            # really us.
            assert mediator.informer_cache[entity_identifier] is self

    return decorated


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def entity_types():
    '''Return a list of entity types that have AWSInformer classes.'''
    return _entity_type_informer_class_map().keys()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def informer_class(etype):
    '''Map entity type to the AWSInformer class name.'''

    # All entity_types() values must be supported here.
    return _entity_type_informer_class_map()[etype]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def informer_entity_type(iclass):
    '''Map AWSInformer class to entity type.'''

    type_class_map = _entity_type_informer_class_map()

    if iclass not in type_class_map.values():
        return None

    possible_types = [
        t for t in type_class_map
        if type_class_map[t] == iclass
        ]
    assert len(possible_types) == 1

    return possible_types[0]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def regional_types():
    '''Return the Informer entity types with instances in each region.'''
    # Update for new AWSInformer subclass.
    return [
        'ec2', 'elb', 'security_group',
        'vpc', 'vpc_peering_connection', 'internet_gateway', 'nat_gateway',
        'autoscaling',
        'subnet', 'network_interface', 'network_acl', 'route_table',
        'eip', 'emr',
        # 'ip_permissions'
        ]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def regionless_types():
    '''Return the Informer entity types with instances not tied to a region.'''
    # Update for new AWSInformer subclass.
    return ['sqs']


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def unitary_types():
    '''Return the Informer entity types with a unique instance.'''
    # Update for new AWSInformer subclass.
    return ['iam']


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def rekey(current, new_key_map):
    '''Change the keys in a dictionary.

    Arguments:

        current (dict):
            A dictionary whose keys are to be changed.

    new_key_map (dict):
        A dictionary whose keys are the *old* keys and whose values
        are the *new* keys.

    Example::

        >>> d = {'this': 42, 'that': 99, 'another': 64}
        >>> new_keys = {'this': 'these', 'that': 'those'}
        >>> rekey(d, new_keys)
        >>> d
        {'these': 42, 'those': 99, 'another': 64}

    '''

    # Check that we won't clobber any existing keys. We need to make
    # sure that no key will be changed to an existing key, which means
    # both the old key and new key from new_key_map occur in current.
    collisions = [
        (k, v) for (k, v) in new_key_map.items()
        if k in current and v in current
        ]

    if len(collisions) > 0:
        raise KeyError(
            'collision between existing and new keys for key changes'
            ' %s' % ', '.join([str(c) for c in collisions])
            )

    for key in current:
        if key in new_key_map:
            current[new_key_map[key]] = current[key]
            del current[key]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_paged_data(
        func,
        data_keys,
        *args,
        **kwargs
        ):  # pylint: disable=bad-continuation
    '''
    Pull paged data from AWS until all pages are retrieved.

    Arguments:

        func (function):
            The function that will be called to retrieve data pages.

        data_keys (str or list of str):
            A list of strings specifying the item keys to be extracted
            from each page of data.

        *args:
            Arbitrary positional arguments.

        **kwargs:
            Arbitrary keyword arguments.

    This method is used in subprocesses by ``get_one_request`` to
    retrieve potentially paged data from an AWS access function. The
    ``*args`` and ``**kwargs`` arguments are passed to the ``func``
    argument when it's called.

    '''
    # Error reporting reference string.
    err_ref_string = '%s, %s, %s, %s' % (
        func.__name__,
        data_keys,
        args,
        kwargs
        )

    # Allow passing a single key without wrapping in a list.
    if isinstance(data_keys, str):
        data_keys = [data_keys]

    # Do this once outside so we get our first Marker if we're paged.
    try:

        data_page = func(
            *args, **kwargs
            )

    except Exception as err:

        raise RuntimeError(
            'Exception %s getting data page 1 for %s' % (
                str(err), err_ref_string
                )
            )

    response = {}

    for data_key in data_keys:
        if data_key in data_page:
            response[data_key] = data_page[data_key]

    while 'IsTruncated' in data_page and data_page['IsTruncated']:

        marker = data_page['Marker']
        try:
            data_page = func(
                Marker=marker,
                MaxItems=600,
                *args, **kwargs
                )
        except Exception as err:
            raise RuntimeError(
                'Exception %s getting data for %s' % (
                    str(err), err_ref_string
                    )
                )
        for data_key in data_keys:
            if data_key in data_page:
                response[data_key] += data_page[data_key]

    return response


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_one_request(request):
    '''Handle one parallelized request.

    This gets called in a subprocess, and has to reconstruct the
    session and client. All of the execution is wrapped in a broad
    "try...except Exception" block because exceptions in subprocesses
    breaks multiprocessing and leaves things hung.

    '''

    err = None

    # Wrap the whole thing in a try/except because any uncaught
    # exception hangs the multiprocessing and leaves zombies when the
    # parent is killed.
    try:
        session = boto3.session.Session(
            **request['session_kwargs']
            )

        client = session.client(request['client_type'])

        method = getattr(client, request['client_method'])

        args = request['method_args']
        kwargs = request['method_kwargs']
        data_keys = request['response_data_keys']

        response = get_paged_data(
            method,
            data_keys,
            *args,
            **kwargs
            )
    except Exception as exc:  # pylint: disable=broad-except

        err = exc
        response = None

    return [request, response, err]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSSessionError(Exception):
    '''An error associated with an AWS Session has occurred.'''

    # pylint: disable=unused-argument
    def __init__(self, msg=None, *args, **kwargs):
        '''Initialize an AWSSessionError instance.'''

        super(AWSSessionError, self).__init__()

        self.value = ""
        if msg is not None:
            self.value = msg

    def __str__(self):
        '''Return a string representation.'''
        return self.value


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSMediatorError(AWSSessionError):
    '''An error associated with an AWS Mediator has occurred.'''

    def __init__(self, msg=None, *args, **kwargs):
        '''Initialize an AWSMediatorError instance.'''

        super(AWSMediatorError, self).__init__(msg=msg, *args, **kwargs)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSInformerError(Exception):
    '''An error associated with an AWS Informer has occurred.'''

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        '''Initialize an AWSInformerError instance.'''

        super(AWSInformerError, self).__init__()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSInformerResourceError(AWSSessionError):
    '''An associated with an AWS Informer resource has occurred.'''

    def __init__(self, msg=None, *args, **kwargs):
        '''Initialize an AWSInformerResourceError instance.'''

        super(
            AWSInformerResourceError, self
            ).__init__(msg=msg, *args, **kwargs)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSInformerResourceTypeError(AWSSessionError):
    '''An error associated with the type of an AWS Informer has occurred.'''

    def __init__(self, msg=None, *args, **kwargs):
        '''Initialize an AWSInformerResourceTypeError instance.'''

        super(
            AWSInformerResourceTypeError, self
            ).__init__(msg=msg, *args, **kwargs)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSInformerRegionError(AWSInformerError):
    '''An AWSInformer error associated with an AWS region has occurred.'''

    def __init__(self, msg=None, *args, **kwargs):
        '''Initialize an AWSInformerRegionError instance.'''

        super(AWSInformerRegionError, self).__init__(msg=msg, *args, **kwargs)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSSession(object):
    '''Manage AWS sessions.

    Arguments:

        region_name (string, optional):
            The name of the AWS region to use for session
            creation. This is passed through to initialize a
            ``boto3.session.Session`` instance.

        profile_name (string, optional):
            The name of the profile record in
            :file:`$HOME/.aws/credentials` to use for session
            creation. This is passed through to initialize a
            ``boto3.session.Session`` instance.

        session (boto3.session.Session, optional):
            An existing ``boto3.session.Session`` instance to
            use for connections.

    Raises:

        ValueError: If an existing session and either a
        profile_name or region_name are provided.

    An ``AWSSession`` is a simple wrapper for the underlying boto3
    session.

    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, region_name=None, profile_name=None, session=None):
        '''Create an AWSSession session manager instance.'''

        logger = logging.getLogger(__name__)

        if session is not None:
            if region_name is not None or profile_name is not None:
                raise ValueError(
                    "region or profile is redundant when session is provided"
                    )

        super(AWSSession, self).__init__()

        if session is not None:
            logger.debug(
                'assigning existing session to new AWSSession instance'
                )
            self._profile_name = session.profile_name
            self.region_name = session.region_name
            self.session = session

        else:

            self._profile_name = profile_name
            # if self._profile_name is None:
            #     self._profile_name = 'default'

            self.region_name = region_name

            self.refresh_session()
            # self.session = boto3.session.Session(
            #     region_name=region_name,
            #     profile_name=profile_name
            #     )

        logger.debug(
            'initialized AWSSession: profile_name "%s", region_name "%s"',
            self.profile_name, self.region_name
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _session_kwargs(self):
        '''A dict with the session.Session() parameters for this session.

        If session parameters aren't explicitly provided, boto will
        fall back to the search order described here:

        http://boto3.readthedocs.io/en/latest/guide/configuration.html

        '''

        session_kwargs = {}

        if self.profile_name:
            session_kwargs.update({'profile_name': self.profile_name})
        if self.region_name:
            session_kwargs.update({'region_name': self.region_name})

        return session_kwargs

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refresh_session(self):
        '''Recreate ``self.session`` with the current parameters.'''

        logger = logging.getLogger(__name__)

        self.session = boto3.session.Session(**self._session_kwargs())

        logger.debug(
            'refreshed AWSSession: profile_name "%s", region_name "%s"',
            self.profile_name, self.region_name
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # We'll need these as properties in the subclass.
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _get_profile_name(self):
        '''Property getter.'''
        return self._profile_name

    def _set_profile_name(self, value):
        '''Property setter.'''
        self._profile_name = value
        self.refresh_session()

    profile_name = property(_get_profile_name, _set_profile_name)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSMediator(AWSSession):
    '''Manage wholesale AWS entity retrieval in a lazy fashion.

    See ``AWSSession`` for argument descriptions.

    The ``AWSMediator`` class extends ``AWSSession`` to provide AWS
    entity data retrieval and caching.

    *   Through its ``entities()`` method, an ``AWSMediator`` instance
        makes transparent the distinction between AWS entities that
        are full fledged AWS services (e.g., *ec2*, *s3*) and entities
        that are retrieved through other services (e.g., *security
        group*, *network interface*).

    *   An ``AWSMediator`` instance caches records it has retrieved so
        that subsequent requests for the same entity don't required an
        additional AWS query. It also caches AWSInformers so that the
        same informers are used when the same mediator is present.

    *   In some cases, an ``AWSMediator`` parallelizes AWS queries for
        faster retrieval.

    Entity retrieval filters can be added to the mediator on a per-
    entity-type basis. These filters will then limit the entities
    retrieved from AWS for that entity type. See the ``add_filters()``
    method for details.

    '''
    # TODO: Set a cache timeout and autoflush.

    PARALLEL_FETCH_PROCESS_COUNT = 48

    # We cache at the AWSMediator class level all informers managed by
    # this mediator, indexed by their unique identifiers, so that we
    # can avoid duplicate records for the same AWS entity and re-use
    # existing records when, e.g., expanding other entities.
    informer_cache = {}

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def _get_account_descriptors(account_id):
        '''Return the account name and description customizations.

        Arguments:

            account_id (str):
                The AWS account ID for the account.

        Returns:

            A dictionary with the name and description of the account
            if found in boogio.json or site-boogio::

                {
                    'name': <account-name>,
                    'description': <account-description>
                    }

        '''

        name = account_id
        description = ''

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Look for account name, starting with the user's boogio
        # config file.
        if (
                'common' in _BOOGIO_CONFIG and
                'name' in _BOOGIO_CONFIG['common']
                ):  # pylint: disable=bad-continuation
            if account_id in _BOOGIO_CONFIG['common']['name']:
                name = (
                    _BOOGIO_CONFIG['common']['name'][account_id]
                    )

        # We didn't find it in the user's boogio config file, so we'll
        # look in site-boogio.
        elif hasattr(site_boogio, 'account_name_by_id'):
            if account_id in site_boogio.account_name_by_id:
                name = (
                    site_boogio.account_name_by_id[account_id]
                    )

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Look for account description, starting with the user's
        # boogio config file.
        if (
                'common' in _BOOGIO_CONFIG and
                'description' in _BOOGIO_CONFIG['common']
                ):  # pylint: disable=bad-continuation
            if account_id in _BOOGIO_CONFIG['common']['description']:
                description = (
                    _BOOGIO_CONFIG['common']['description'][account_id]
                    )

        # We didn't find it in the user's boogio config file, so we'll
        # look in site-boogio.
        elif hasattr(site_boogio, 'account_description_by_id'):
            if account_id in site_boogio.account_description_by_id:
                description = (
                    site_boogio.account_description_by_id[account_id]
                    )

        # - - - - - - - - - - - - - - - - - - - - - - - -
        if name and not description:
            description = name

        return {
            'name': name,
            'description': description,
            }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, **kwargs):
        '''Initialize an AWSMediator instance.'''

        super(AWSMediator, self).__init__(**kwargs)

        # TODO: Move this into _get_account_descriptors, and check for
        # the profile name in config files maybe?
        self.account_id = (
            self.session.client("sts").get_caller_identity()["Account"]
            )

        descriptors = self._get_account_descriptors(self.account_id)
        self.account_name = descriptors['name']
        self.account_desc = descriptors['description']

        self._clients = {}

        # self._resources = {
        #     resource: None
        #     for resource in self.session.get_available_resources()
        #     }

        self._services = {
            service: None
            for service in self.session.get_available_services()
            }

        # Update for new AWSInformer subclass.
        self._other_entities = {
            'security_group': None,
            'vpc': None,
            'vpc_peering_connection': None,
            'internet_gateway': None,
            'nat_gateway': None,
            'subnet': None,
            'network_interface': None,
            'network_acl': None,
            'route_table': None,
            'eip': None
            }

        self.filters = {}

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def profile_name(self):
        '''Get the profile property.'''

        return self._profile_name

    @profile_name.setter
    def profile_name(self, value):
        '''Set the profile property.

        If the profile_name is changed, all cached records will be
        flushed.

        '''
        # We need to flush() if the profile_name gets changed.
        if value != self._profile_name:
            self.flush()
        super(AWSMediator, self)._set_profile_name(value)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_filters(self, entity_type, new_filters):
        '''
        Add AWS entity retrieval filters to the mediator.

        Arguments:

            entity_type (string):

                An informer entity type to which this filter will
                apply.

            new_filters (dict):

                The *Name* strings and *Values* lists for the filters.

        Example::

            >>> mediator = aws_informer.AWSMediator()
            >>> mediator.add_filters(
            ...     'ec2', {'instance-state-name': ['running']}
            ...     )
            >>> mediator.filters
            {'ec2': {'instance-state-name': ['running']}}}

            >>> mediator.add_filters(
            ...     'eip', {
            ...         'public-ip': ['123.45.67.89', '56.78.91.234'],
            ...         'domain': ['vpc']
            ...         }
            ...     )
            >>> mediator.filters
            {'ec2': {'instance-state-name': ['running']}},
            'eip', {'public-ip': ['123.45.67.89', '56.78.91.234'],
            'domain': ['vpc']}}

        '''

        if entity_type not in self.filters:
            self.filters[entity_type] = {}

        for (filter_name, filter_values) in new_filters.items():

            if filter_name not in self.filters[entity_type]:
                self.filters[entity_type][filter_name] = []

            self.filters[entity_type][filter_name] = list(
                set(
                    self.filters[entity_type][filter_name]
                    ).union(set(filter_values))
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def remove_all_filters(self, *remove_types):
        '''Remove AWS entity retrieval filters from the mediator.'''
        existing_types = self.filters.keys()
        for existing_type in existing_types:
            if remove_types == () or existing_type in remove_types:
                del self.filters[existing_type]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _filters_kwarg(self, entity_type, use_filters=True):
        '''Create a structure representing the 'Filters' parameter.

        The parameter is used when fetching entities for this
        entity_type.

        The structure represent this mediator's filters(entity_type)

            {'name1': ['v1', ...], 'name2': [...], 'name3': [...]}
        as

            {'Filters':
                [
                    {'Name': 'name1', 'Values': ['v1', ...]},
                    {'Name': 'name2', 'Values': [...]},
                    {'Name': 'name3', 'Values': [...]},
                    ]
                }

        See, e.g., http://boto3.readthedocs.org/en/latest/reference/
        services/ec2.html#EC2.Client.describe_addresses for an
        example of filtering a client entity retrieval.
        '''
        filters_kwarg = {'Filters': []}

        if use_filters and entity_type in self.filters:
            for (key, vals) in self.filters[entity_type].items():
                filters_kwarg['Filters'].append({'Name': key, 'Values': vals})

        return filters_kwarg

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def flush(self, *cached_entity_types):
        '''
        Remove indicated entity types from the internal cache.

        Arguments:

            cached_entity_types (tuple of string):
                The entity types to flush. If not specified, all
                cached entities will be flushed.

        '''
        logger = logging.getLogger(__name__)

        if len(cached_entity_types) == 0:
            cached_entity_types = (
                self._services.keys() + self._other_entities.keys()
                )
        logger.debug('clearing cache of entity types: %s', cached_entity_types)

        # Delete cached informers.
        to_delete = []
        for (identifier, informer) in self.informer_cache.iteritems():
            if informer.entity_type in cached_entity_types:
                to_delete.append(identifier)
        for identifier in to_delete:
            del self.informer_cache[identifier]

        # Delete entity resource records.
        for entity_type in cached_entity_types:
            if (
                    entity_type is not None and
                    entity_type not in self._services and
                    entity_type not in self._other_entities
                    ):  # pylint: disable=bad-continuation

                errmsg = "Unknown entity type: %s" % (entity_type)
                logger.error(errmsg)
                raise AWSMediatorError(errmsg)

            if entity_type in self._services:
                del self._services[entity_type]
                self._services[entity_type] = None

            # elif entity_type in self._resources:
            #     del self._resources[entity_type]
            #     self._resources[entity_type] = None

            elif entity_type in self._other_entities:
                del self._other_entities[entity_type]
                self._other_entities[entity_type] = None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _fetch(self, entity_type, use_filters=True):
        '''Retrieve all instances of the indicated entity type from AWS.

        Arguments:

            entity_type (string):
                The entity type to retrieve.

            use_filters (bool, default=True):
                If True, filter retrieval of the requested
                entity type using the mediator's filters attribute
                item for that entity type. If False, retrieve all
                entities of the requested entity type.

        '''

        logger = logging.getLogger(__name__)
        logger.info('fetching %s entities...', entity_type)
        if use_filters:
            logger.info('filtering with %s', self.filters)

        # TODO: Helpers for pagination.
        def paginated(
                method, data_key,
                page_key='Marker', next_page_key='NextMarker'
                ):  # pylint: disable=bad-continuation
            '''Call ``method`` until all pages of data are returned.'''
            final_data = []
            more_pages = True
            next_page_marker = None
            while more_pages:
                kwargs = {}
                if next_page_marker:
                    kwargs = {page_key: next_page_marker}
                response = method(**kwargs)
                next_page_marker = response.get(next_page_key)
                if not next_page_marker:
                    more_pages = False
                final_data.extend(response[data_key])
            return final_data

        # Update for new AWSInformer subclass.
        raw_entity_collection = {

            # 'ec2': self.session.resource('ec2').instances.all,
            'ec2': lambda: [
                ec2.meta.data
                for ec2 in list(
                    self.session.resource('ec2').instances.all()
                    )
                ],

            # 's3': self.session.resource('s3').buckets.all,
            's3': lambda: [
                s3.meta.data
                for s3 in list(
                    self.session.resource('s3').buckets.all()
                    )
                ],
            'iam': lambda: [],

            'sqs': lambda: [
                {'QueueURL': q.url}
                for q in list(
                    self.session.resource('sqs').queues.all()
                    )
                ],

            # 'elb': lambda: self.session.client(
            #     'elb'
            #     ).describe_load_balancers()['LoadBalancerDescriptions'],

            'elb': lambda: paginated(
                self.session.client('elb').describe_load_balancers,
                'LoadBalancerDescriptions'
                ),

            'security_group': lambda: self.session.client(
                'ec2'
                ).describe_security_groups()['SecurityGroups'],

            'vpc': lambda: self.session.client(
                'ec2'
                ).describe_vpcs()['Vpcs'],

            'vpc_peering_connection': lambda: self.session.client(
                'ec2'
                ).describe_vpc_peering_connections()['VpcPeeringConnections'],

            'internet_gateway': lambda: self.session.client(
                'ec2'
                ).describe_internet_gateways()['InternetGateways'],

            'nat_gateway': lambda: self.session.client(
                'ec2'
                ).describe_nat_gateways()['NatGateways'],

            'autoscaling': lambda: self.session.client(
                'autoscaling'
                ).describe_auto_scaling_groups()['AutoScalingGroups'],

            'subnet': lambda: self.session.client(
                'ec2'
                ).describe_subnets()['Subnets'],

            'network_interface': lambda: self.session.client(
                'ec2'
                ).describe_network_interfaces()['NetworkInterfaces'],

            'network_acl': lambda: self.session.client(
                'ec2'
                ).describe_network_acls()['NetworkAcls'],

            'route_table': lambda: self.session.client(
                'ec2'
                ).describe_route_tables()['RouteTables'],

            'eip': lambda: self.session.client(
                'ec2'
                ).describe_addresses(
                    **self._filters_kwarg('eip', use_filters)
                    )['Addresses'],

            'emr': lambda: self.session.client(
                'emr'
                ).list_clusters()['Clusters'],

            }[entity_type]()

        logger.info('fetched %s entities', len(raw_entity_collection))

        return list(raw_entity_collection)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def client(self, client_type):
        '''Return a client from the _clients dict, creating one if needed.

        Arguments:

            client_type (string):
                The type of AWS client to create; e.g., ``ec2`` or
                ``s3``.

        An ``AWSMediator`` instance maintains an internal list of AWS
        clients for different AWS services, created using this
        mediator's ``Session`` instance. This method returns the
        client for the indicated entity type, creating a new client
        if one isn't already present.

        Note that client types are a subset of the legal
        ``AWSInformer`` entity types.

        '''
        if client_type not in self._clients:

            try:
                new_client = self.session.client(client_type)
            except botocore.exceptions.DataNotFoundError:
                raise AWSMediatorError(
                    "can't create client for %s" % client_type
                    )

            self._clients[client_type] = new_client

        return self._clients[client_type]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def services(self, service_type):
        '''Retrieve a list of services, if necessary, and return the list.'''
        logger = logging.getLogger(__name__)

        if service_type not in self._services:
            errmsg = "Unknown service type: %s" % (service_type)
            logger.error(errmsg)
            raise AWSMediatorError(errmsg)

        if self._services[service_type] is None:
            self._services[service_type] = self._fetch(service_type)

        return self._services[service_type]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def entities(self, entity_type, use_filters=True):
        '''Retrieve entities from AWS (if necessary) and return them as a list.

        Arguments:

            entity_type (string):
                The entity type requested.

            use_filters (bool, default=True):
                If ``_fetch()`` is called to retrieve entities, this
                will be passed to control entity filtering. Note that
                this only happens if this entity type hasn't
                previously been fetched.

        This is a wrapper that hides the distinction between entity
        types like ``ec2`` and ``s3`` that correspond to AWS services
        and other entity types that don't.

        '''

        logger = logging.getLogger(__name__)

        if (
                entity_type not in self._services and
                entity_type not in self._other_entities
                ):  # pylint: disable=bad-continuation
            errmsg = "Unknown entity type: %s" % (entity_type)
            logger.error(errmsg)
            raise AWSMediatorError(errmsg)

        if entity_type in self._services:

            if self._services[entity_type] is None:
                self._services[entity_type] = self._fetch(
                    entity_type, use_filters
                    )

            entities = self._services[entity_type]

        elif entity_type in self._other_entities:

            if self._other_entities[entity_type] is None:
                self._other_entities[entity_type] = self._fetch(
                    entity_type, use_filters
                    )

            entities = self._other_entities[entity_type]

        return entities

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def get_aws_info_in_parallel(
            cls,
            requests
            ):  # pylint: disable=bad-continuation
        '''
        Use subprocess pools to retrieve multiple data requests in parallel.

        Arguments:

            requests (list of dicts):
                A mapping defining the parameters for the requests
                in question. The expected key/value pairs include:

                *origin*
                    A passback field for the caller to identify to
                    which entity the data returned for this request
                    belongs.

                *client_type*
                    The type of client needed to handle this request.

                *client_method*
                    The client method needed to handle this request.

                *method_args*, *method_kwargs*
                    The args and kwargs to pass to the client method.

                *response_data_keys*
                    The keys for the items in the method response that
                    contain the actual data, rather than response
                    metadata or other information.

        Returns:

            A list of pairs [[request, response]...] where each
            response has the client method return value for this
            request. Each response will be a dict whose keys are
            response_data_keys and whose values are the values of
            those keys in client_method call return dicts.

        '''

        pool_size = cls.PARALLEL_FETCH_PROCESS_COUNT

        if len(requests) < pool_size:
            pool_size = len(requests)

        if pool_size == 0:
            return []

        pools = Pool(pool_size)
        results = pools.map(get_one_request, requests)
        pools.terminate()

        return results


# TODO: Might be helpful to move the fancy __new__() stuff into a
# CachableInformer subclass?
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSInformer(object):
    '''
    Manage selected information for specified AWS entities.

    Arguments:

        resource (dict):
            An AWS resource being handled by this informer.

        profile_name (string):
            The name of the AWS profile to use for this informer's
            mediator.

        region_name (string):
            The name of the AWS region to use for this informer's
            mediator.

        mediator (aws_informer.AWSMediator):
            An AWSMediator instance this resource should use.

        required_resource_type:
            The type() of the AWS resource boto class the informer is
            intended to handle.

    Attributes:

        identifier (str): A string which uniquely identifies this
            informer, appropriate for the entity type. For example,
            the InstanceID for an EC2InstanceInformer or the
            LoadBalancerName for an ELBInformer.

        resource (dict): The original record for the AWS entity this
            Informer instance manages.

        expansions (dict):
            The child resources found when expanding this informer.

        supplementals (dict):
            Additional information assigned to this informer.

        is_expanded (bool):
            ``True`` if this informer's ``expand()`` method has been
            called; ``False`` otherwise.

        promote_to_top_level (list):
            A list of top level ``resource`` keys that will be handled
            specially in ``AWSInformer.to_dict()``. See the
            documentation for ``to_dict()`` for details.

        elisions (list):
            A list of top level ``resource`` keys that will be handled
            specially in ``AWSInformer.to_dict()``. See the
            documentation for ``to_dict()`` for details.


    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def _require_resource_type(cls, resource, resource_type):
        '''Raise an error if the wrong resource type is assigned.'''

        if not isinstance(resource, resource_type):
            raise AWSInformerResourceTypeError(
                "%s (expected instance of %s" % (
                    type(resource),
                    resource_type
                    )
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _get_init_entity_identifier(self, resource):
        '''Look up the appropriate key for our class in our resource.'''

        identifier_key_map = _informer_identifier_key_map()
        entity_identifier = None

        if self.__class__ in identifier_key_map:
            entity_identifier_key = identifier_key_map[self.__class__]
            entity_identifier = resource[entity_identifier_key]

        return entity_identifier

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __new__(
            cls,
            resource=None,
            region_name=None,
            profile_name=None,
            mediator=None,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Check if we should create a fresh informer or reuse a cached one.

        This is only possible if we're being passed a mediator, rather
        than a profile and region with which to create one. In this
        case we check whether the value that will be the new
        informer's identifier is a key in the mediator's
        informer_cache records, and if so we just re-use that
        informer.

        In this case, this __new__() returns the instance found in the
        informer_cache. Because this instance will be of the child
        class type, the child class's __init__() will be called. We
        don't want to re-initialize the instance, so all child classes
        are responsible for checking the mediator's informer_cache,
        and only initializing again if they aren't there. They must
        also make sure to update the cache by adding themself the
        first time they're initialized.

        '''

        logger = logging.getLogger(__name__)

        identifier_key_map = _informer_identifier_key_map()
        entity_identifier = None

        if cls in identifier_key_map and resource is not None:
            entity_identifier_key = identifier_key_map[cls]
            try:
                entity_identifier = resource[entity_identifier_key]
            except KeyError as err:
                err_msg = ('%s entity identifier key "%s" not found in %s')
                logger.error(err_msg, cls, err.message, resource)
                raise ValueError(err_msg % (cls, err.message, resource))

        no_informer_cache = (
            mediator is None or
            entity_identifier not in mediator.informer_cache
            )

        if no_informer_cache:

            return super(AWSInformer, cls).__new__(
                cls,
                resource=None,
                region_name=region_name,
                profile_name=profile_name,
                mediator=mediator,
                **kwargs
                )
        else:
            return mediator.informer_cache[entity_identifier]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(
            self,
            resource,
            region_name=None,
            profile_name=None,
            mediator=None,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize an AWSInformer instance.'''

        super(AWSInformer, self).__init__()

        if 'required_resource_type' in kwargs:
            self._require_resource_type(
                resource,
                kwargs['required_resource_type']
                )

        # self.__class__ will identify the child class AWSInformer
        # that is being initialized.
        self._entity_type = informer_entity_type(self.__class__)
        self.resource = resource
        self.region_name = region_name
        self.profile_name = profile_name

        # Child resources stored as Informers.
        self.expansions = {}
        self.is_expanded = False

        # TODO: The following should be a method.
        self.mediator = None
        if mediator is None:
            if region_name is None or profile_name is None:
                raise AWSInformerRegionError(
                    'Informer region and profile names'
                    ' or AWS Mediator required'
                    )
            self.mediator = AWSMediator(
                region_name=self.region_name,
                profile_name=self.profile_name
                )

        else:
            if (
                    region_name is not None and
                    region_name != mediator.region_name
                    ):  # pylint: disable=bad-continuation
                errmsg = (
                    "Informer region_name %s doesn't match"
                    "mediator region_name %s"
                    ) % (region_name, mediator.region_name)
                raise AWSInformerRegionError(msg=errmsg)
            if (
                    profile_name is not None and
                    profile_name != mediator.profile_name
                    ):  # pylint: disable=bad-continuation
                errmsg = (
                    "Informer profile_name %s doesn't match"
                    "mediator profile_name %s"
                    ) % (profile_name, mediator.profile_name)
                raise AWSInformerRegionError(msg=errmsg)

            self.mediator = mediator

            # Pass-through sugar.
            self.region_name = self.mediator.region_name
            self.profile_name = self.mediator.profile_name

        # Additional records associated with this informer; e.g. the IP
        # address obtained by DNS lookup on a Load Balancer.
        self.supplementals = {
            'meta': {
                'profile_name': self.profile_name,
                'region_name': self.region_name,
                'account_id': self.mediator.account_id,
                'account_name': self.mediator.account_name,
                'account_desc': self.mediator.account_desc
                }
            }

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Structure manipulation control to make things
        # more manageable when exporting data for viewing
        # in, e.g., kibana.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        # Fields to map into the top level as dict entries in
        # to_dict() (and hence JSON) output.
        self.promote_to_top_level = [
            ]

        # # Fields on which to call flatten() when converting to
        # # to_dict() (and hence JSON) output.
        # self.flatten = [
        #     ]

        # Call local site defined initialization code.
        site_boogio.informer_site_init(self)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def entity_type(self):
        '''Return the ``AWSMediator`` entity type for this informer.'''
        return self._entity_type

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def identifier(self):
        '''Return the unique identifier string for this informer.'''

        identifier = None
        iclass = None

        # TODO: Couldn't we just look up self.__class__ directly
        # in _informer_identifier_key_map?
        informer_class_map = _entity_type_informer_class_map()
        identifier_map = _informer_identifier_key_map()

        if self._entity_type in informer_class_map:
            iclass = informer_class_map[self._entity_type]
        if iclass in identifier_map:
            identifier_key = identifier_map[iclass]
            identifier = self.resource[identifier_key]

        return identifier

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def to_dict(self, entity_identifier=False, flat=False):
        '''Return a dict structure using expanded subelements when available.

        Arguments:

            entity_identifier (bool, default=False):
                If ``True``, the dict will include an
                ``entity_identifier`` field whose value is the
                entity's ``identifier`` attribute. If false, the
                ``entity_identifier`` field won't be included.

            flat (bool, default=False):
                If the ``flat`` parameter is True, the data structure
                returned will be a list of flattened (no nested
                structures) dicts. For more information on flattening,
                see the documentation for ``utensils.flatten``.

        The result of ``to_dict()`` is guaranteed to be a serializable
        structure suitable for JSON conversion. If any subentities are
        encountered that raise an error when converting to JSON, they
        will be replaced with their string representation
        via``str()``.

        The result returned by ``to_dict()`` will include the
        informer instance information with the following adjustments.

        *   Any top level keys in the informer's ``elisions`` list
            will be omitted from the result of ``to_dict()``. As
            working with expanded entities can generate significant
            amounts of data, you may sometimes want to use this to
            omit unneeded substructures to speed up subsequent
            processing.

        *   The ``expansions`` value will replace the ``resource``
            value for any top level key present in both.

        *   AWS entities store the names and values of their tags as
            the value of the ``Key`` and ``Value`` items in a dict. In
            the structure returned by ``to_dict()``, a tag
            ``some_tag``

                ::

                    'Tags': {'Key': 'some_tag', 'Value': 'some_value'}

            will be represented as

                ::

                    'Tags:some_tag': 'some_value'

            at the top level of the returned dict.

        *   Any keys in the top level of the informer's resource that
            are present in the informer's ``promote_to_top_level``
            list will be treated similarly to tags. If the value of
            that key is a dict, it will be replaced with a set of top
            level entries. For example, if ``TopKey`` appears in the
            ``promote_to_top_level`` list, then the top level item

                ::

                    'TopKey': {'Key1': 'Val1', 'Key2': 'Val2'}

            will be replaced with the top level items

                ::

                    'TopKey:Key1': 'Val1'
                    'TopKey:Key2': 'Val2'

            at the top level of the returned dict.

            Note that this will raise an error if the value to be
            promoted isn't a dict.

        *   The resulting dict will be updated with the items in the
            informer's ``supplementals`` dict. If any of these are
            themselves informers, their ``to_dict()`` method will be
            called.

        *   The resulting dict will be flat if the ``flat`` argument
            is ``True``.

        '''

        # TODO: Add _dict_cache attribute and only update the
        # supplementals and expansions when to_dict() is called.

        # TODO: keep a list of informer identifiers already
        # encountered (including the top level) to avoid loops. This
        # should be a stack, and increase/decrease as we go up and
        # down.

        # pylint: disable=too-many-branches

        as_dict = {}
        if entity_identifier:
            as_dict = {'entity_identifier': self.identifier}

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Some Informers store the AWS entity representation in their
        # meta.data dict attribute; others are just a dict comtaining the
        # AWS entity representation.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            if self.resource is None:
                resource_dict = {}
            else:
                resource_dict = dict(self.resource.meta.data)
        except (TypeError, AttributeError):
            if isinstance(self.resource, dict):
                resource_dict = self.resource
            else:
                raise TypeError(
                    'unknown resource type in %s' % self.__class__.__name__
                    )

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Any value we add here to as_dict is either the result of calling
        # as_dict on a subordinate resource or has been ensured to be JSON
        # serializable in the else clause.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        for key in resource_dict:

            # TODO: Really should leave tags and promotes alone here
            # if we're not flattening.

            # TODO: Do we need all this deepcopying?

            # - - - - - - - - - - - - - - - - - - - - - - - -
            # Tags need to be moved to the top level for, e.g.,
            # ElasticSearch indexing., but they have a substructure we have
            # to massage separately from the generic "move to top level"
            # elements.
            # - - - - - - - - - - - - - - - - - - - - - - - -
            if key == 'Tags':

                for tag_item in resource_dict[key]:

                    this_tag_key = 'Tags:' + tag_item['Key']
                    this_tag_value = copy.deepcopy(tag_item['Value'])

                    if this_tag_key in as_dict:

                        # We already have at least one value for this tag.
                        try:
                            as_dict[this_tag_key].append(this_tag_value)

                        except AttributeError:
                            # It was only one value, not a list yet.
                            as_dict[this_tag_key] = [
                                as_dict[this_tag_key]
                                ].append(this_tag_value)

                    else:
                        as_dict[this_tag_key] = this_tag_value

                continue

            # - - - - - - - - - - - - - - - - - - - - - - - -
            # Move key-value pairs from items in the value of specified
            # resource entries to top level items in the resource itself,
            # for better accessibility in, e.g., ElasticSearch indexing.
            # - - - - - - - - - - - - - - - - - - - - - - - -
            if key in self.promote_to_top_level:

                for child_key in resource_dict[key]:

                    top_level_key = key + ':' + child_key
                    top_level_value = copy.deepcopy(
                        resource_dict[key][child_key]
                        )

                    if top_level_key in as_dict:

                        # We already have at least one value for this tag.
                        try:
                            as_dict[top_level_key].append(top_level_value)

                        except AttributeError:
                            # It was only one value, not a list yet.
                            as_dict[top_level_key] = [
                                as_dict[top_level_key]
                                ].append(top_level_value)

                    else:
                        as_dict[top_level_key] = top_level_value

                continue

            # - - - - - - - - - - - - - - - - - - - - - - - -
            # Use expansions if available.
            # - - - - - - - - - - - - - - - - - - - - - - - -
            if key in self.expansions:
                # as_dict[key] = self._expansion_to_container(key)
                expansion = self.expansions[key]
                try:
                    as_dict[key] = copy.deepcopy(expansion.to_dict())
                except AttributeError:
                    # Must have been a list.
                    as_dict[key] = [
                        copy.deepcopy(informer.to_dict())
                        for informer in expansion
                        ]

            # - - - - - - - - - - - - - - - - - - - - - - - -
            # This subentity wasn't expanded, so we'll use the original value
            # in the resource. If it's not serializable, we'll replace it with
            # a representation as a string.
            # - - - - - - - - - - - - - - - - - - - - - - - -
            else:
                try:
                    # We just want to see if this will raise an exception, we
                    # don't want the actual value.
                    json.dumps(resource_dict[key])
                    as_dict[key] = copy.deepcopy(resource_dict[key])
                except TypeError:
                    # return str(type(value).__name__)
                    # as_dict[key] = str(
                    #     type(resource_dict[key]).__name__
                    #     )
                    as_dict[key] = str(resource_dict[key])

        for key in self.supplementals:
            # Make sure we didn't accidentally clobber a resource/expansion
            # field.
            if key in as_dict:
                raise KeyError(
                    '%s supplementals contains a duplicate'
                    ' of an informer key: %s' % (type(self), key)
                    )
            if isinstance(self.supplementals[key], AWSInformer):
                as_dict[key] = self.supplementals[key].to_dict()
            else:
                as_dict[key] = copy.deepcopy(self.supplementals[key])

        # Now as_dict[key] holds the "unmassaged" data for this key. We'll
        # flatten lists for this entity and massage accordingly.
        if flat:
            # 20170411: There's a bug (?) in flatten, if a dict has
            # any item at any level whose value is {}, the whole
            # flattening will be an empty list.
            as_dict = flatten.flatten(as_dict)

        return as_dict

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def json_dumps(self, flat=False):
        '''
        Return a JSON representation of the informer.

        Arguments:

            flat (bool):
                If the ``flat`` parameter is True, the data structure
                returned will be a list of flattened (no nested
                structures) dicts obtained by calling the informer's
                ``to_dict()`` method with ``flat=True``.

                For more information on flattening, see the
                documentation for ``utensils.flatten``.

        '''
        data = self.to_dict(flat=flat)
        return json.dumps(data)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details and populate the expansions attribute.

        The expansions attribute is a dictionary whose keys match the
        name of some attribute of the ``resource`` attribute, and
        whose values are either AWSInformer instances or lists of
        AWSInformer instances.

        Expanding an informer pulls the records from AWS (via the
        informer's mediator) for other AWS entities only referenced
        by id in the original resource record.

        Each AWSInformer instance in the expansions will in turn be
        expanded.

        '''

        # TODO: The mediator, or somewhere, should maintain a master
        # list of informers so we don't get copies all over the place.

        # Doing things this way will work as long as each value in the
        # expansions dict is either an informer or a list of informers.
        for key in self.expansions:
            informer_or_list = self.expansions[key]
            try:
                informer_or_list.expand()
            except AttributeError:
                for inf in informer_or_list:
                    inf.expand()

        self.is_expanded = True


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class ELBInformer(AWSInformer):
    '''Manage selected information for an ELB resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def get_dns_address_info(cls, dns_name):
        '''Use a socket library DNS call to get the address for dns_name.'''

        addresses = []

        try:
            addr_info = socket.getaddrinfo(dns_name, 0, socket.AF_INET)
            for (_, _, _, _, saddr) in addr_info:
                addresses.append(saddr[0])
        # except socket.gaierror as exc:
        # TODO: Retry.
        except socket.gaierror:
            # raise RuntimeError(
            #     'Error in socket.getaddrinfo for %s' % dns_name
            #     )
            return []

        # Different parameters to getaddrinfo may return the same
        # IP Address, so we remove duplicates here.
        return list(set(addresses))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize an ELBInformer instance.

        See the documentation for _prevent_duplicate_informer_init_if_cached
        as well.
        '''
        super(ELBInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        # - - - - - - - - - - - - - - - - - - - - - -
        # Resources stored by reference in this resource.
        # - - - - - - - - - - - - - - - - - - - - - -
        if 'SecurityGroups' in self.resource:
            self.expansions['SecurityGroups'] = [
                SecurityGroupInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('security_group')
                if x['GroupId'] in self.resource['SecurityGroups']
                ]

        if 'VPCId' in self.resource:
            vpc_list_reduced = [
                VPCInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('vpc')
                if x['VpcId'] == self.resource['VPCId']
                ]
            if len(vpc_list_reduced) > 0:
                self.expansions['VPCId'] = vpc_list_reduced[0]

        if 'Subnets' in self.resource:
            self.expansions['Subnets'] = [
                SubnetInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('subnet')
                if x['SubnetId'] in self.resource['Subnets']
                ]

        if 'Instances' in self.resource:
            resource_instance_ids = [
                x['InstanceId'] for x in self.resource['Instances']
                ]

            self.expansions['Instances'] = [
                EC2InstanceInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('ec2')
                if x['InstanceId'] in resource_instance_ids
                ]

        # - - - - - - - - - - - - - - - - - - - - - -
        # Look up the IP addresses for this ELBs DNS name.
        # - - - - - - - - - - - - - - - - - - - - - -
        self.supplementals['DNSIpAddress'] = {'INET': []}
        if 'DNSName' in self.to_dict():
            dns_name = self.to_dict()['DNSName']

            self.supplementals['DNSIpAddress']['INET'] = (
                self.get_dns_address_info(dns_name)
                )

        # This must be after the expansions list is populated, as it
        # calls expand() in each element of the list.
        super(ELBInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class EMRInformer(AWSInformer):
    '''Manage selected information for an EMR resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize an EMRInformer instance.'''

        super(EMRInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        # EMR resources add additional fields upon expansion.
        cluster_id = self.resource['Id']

        # Watch for throttling issues. Start with 20 msec backoff if needed.
        description = None
        initial_backoff = .02
        backoff_growth = 1.5
        backoff = initial_backoff
        retries = 0
        max_retries = 12

        while description is None:
            try:
                description = self.mediator.client('emr').describe_cluster(
                    ClusterId=cluster_id
                    )['Cluster']
            except botocore.exceptions.ClientError:
                if retries == max_retries:
                    break
                time.sleep(backoff)
                retries += 1
                backoff *= backoff_growth ** retries

        if isinstance(description, dict):
            self.resource.update(description)

        # This must be after the expansions list is populated, as it
        # calls expand() in each element of the list.
        super(EMRInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class EC2InstanceInformer(AWSInformer):
    '''Manage selected information for an EC2 Instance resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize an EC2InstanceInformer instance.'''

        super(EC2InstanceInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

        self.promote_to_top_level = [
            'Placement'
            ]

        # The NetworkInterface elements, although they also have their
        # own AWSInformer class, come completely defined as
        # subelements of the EC2InstanceInformer resource. They have
        # a non-serializable datetime type as their AttachTime value,
        # which we replace here with a string representation. This is
        # also done in NetworkInterfaceInformer class instance
        # initialization where we also provide an attach_datetime
        # property preserving the original value.
        # TODO: This special handling needs test cases.
        try:
            for nif in self.resource['NetworkInterfaces']:
                attachment = nif['Attachment']
                attachment['AttachTime'] = (
                    attachment['AttachTime'].strftime(
                        DEFAULT_UTC_TIMESTAMP_FORMAT
                        )
                    )
        except KeyError:
            # If the dict references fail, there's nothing to convert.
            pass

        # Also true of BlockDeviceMappings.
        try:
            for mapping in self.resource['BlockDeviceMappings']:
                device = mapping['Ebs']
                if 'AttachTime' not in device:
                    continue
                device['AttachTime'] = (
                    device['AttachTime'].strftime(
                        DEFAULT_UTC_TIMESTAMP_FORMAT
                        )
                    )
        except KeyError:
            # If the dict references fail, there's nothing to convert.
            pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        # - - - - - - - - - - - - - - - - - - - - - -
        # Resources stored by reference in this resource.
        # - - - - - - - - - - - - - - - - - - - - - -
        if 'SecurityGroups' in self.resource:
            self.expansions['SecurityGroups'] = [
                SecurityGroupInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('security_group')
                if x['GroupId'] in [
                    sg['GroupId'] for sg in self.resource['SecurityGroups']
                    ]
                ]

        if 'NetworkInterfaces' in self.resource:
            self.expansions['NetworkInterfaces'] = [
                NetworkInterfaceInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('network_interface')
                if x['NetworkInterfaceId'] in [
                    ni['NetworkInterfaceId']
                    for ni in self.resource['NetworkInterfaces']
                    ]
                ]

        if 'VpcId' in self.resource:
            vpc_list_reduced = [
                VPCInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('vpc')
                if x['VpcId'] == self.resource['VpcId']
                ]
            if len(vpc_list_reduced) > 0:
                self.expansions['VpcId'] = vpc_list_reduced[0]

        if 'SubnetId' in self.resource:
            subnet_list_reduced = [
                SubnetInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('subnet')
                if x['SubnetId'] == self.resource['SubnetId']
                ]
            if len(subnet_list_reduced) > 0:
                self.expansions['SubnetId'] = subnet_list_reduced[0]

        super(EC2InstanceInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SecurityGroupInformer(AWSInformer):
    '''Manage selected information for a SecurityGroup resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize a SecurityGroupInformer instance.'''

        super(SecurityGroupInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

        # We add a "PortRange" item to the IPPermissions for ease of
        # reference later.
        for permtype in ['IpPermissions', 'IpPermissionsEgress']:
            if permtype in self.resource:
                for perm in self.resource[permtype]:
                    port_range = []
                    if 'FromPort' in perm:
                        port_range.append(str(perm['FromPort']))
                    if 'ToPort' in perm and perm['ToPort'] != perm['FromPort']:
                        port_range.append(str(perm['ToPort']))
                    if port_range:
                        perm['PortRange'] = '-'.join(port_range)
                    else:
                        perm['PortRange'] = None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        # self.expansions['IpPermissions'] = [
        #     IpPermissionsInformer(x, mediator=self.mediator)
        #     for x in self.resource['IpPermissions']
        #     ]

        # self.expansions['IpPermissionsEgress'] = [
        #     IpPermissionsInformer(x, mediator=self.mediator)
        #     for x in self.resource['IpPermissionsEgress']
        #     ]

        if 'VpcId' in self.resource:
            vpc_list_reduced = [
                VPCInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('vpc')
                if x['VpcId'] == self.resource['VpcId']
                ]
            if len(vpc_list_reduced) > 0:
                self.expansions['VpcId'] = vpc_list_reduced[0]

        # This must be after the expansions list is populated, as it
        # calls expand() in each element of the list.
        super(SecurityGroupInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class VPCInformer(AWSInformer):
    '''Manage selected information for a VPC resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize a VPCInformer instance.'''

        super(VPCInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

        # Add supplementals for peering connections.

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        super(VPCInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class VpcPeeringConnectionInformer(AWSInformer):
    '''Manage information retrieval for a VPC Peering Connection resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize a VpcPeeringConnectionInformer instance.'''

        super(VpcPeeringConnectionInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

        # Add supplementals for peering connections.

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        super(VpcPeeringConnectionInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class InternetGatewayInformer(AWSInformer):
    '''Manage information retrieval for an Internet Gateway resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize an InternetGatewayInformer instance.'''

        super(InternetGatewayInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

        # Add supplementals for internet gateways.

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        super(InternetGatewayInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class NatGatewayInformer(AWSInformer):
    '''Manage information retrieval for a NAT Gateway resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize a NatGatewayInformer instance.'''

        super(NatGatewayInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

        # Add supplementals for nat gateways.

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        super(NatGatewayInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AutoScalingGroupInformer(AWSInformer):
    '''Manage selected information for an AutoScalingGroup resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize an AutoScalingGroupInformer instance.'''

        super(AutoScalingGroupInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        super(AutoScalingGroupInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SubnetInformer(AWSInformer):
    '''Manage selected information for a Subnet resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize a SubnetInformer instance.'''

        super(SubnetInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        super(SubnetInformer, self).expand()

        if 'VpcId' in self.resource:
            vpc_list_reduced = [
                VPCInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('vpc')
                if x['VpcId'] == self.resource['VpcId']
                ]
            if len(vpc_list_reduced) > 0:
                self.expansions['VpcId'] = vpc_list_reduced[0]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class NetworkInterfaceInformer(AWSInformer):
    '''Manage selected information for an EC2 Network Interface resource.'''

    timestamp_format = DEFAULT_UTC_TIMESTAMP_FORMAT

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize a NetworkInterfaceInformer instance.'''

        super(NetworkInterfaceInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

        self._attach_datetime = None
        # These have un-serializable datetime entities that need to
        # be converted to strings now.
        try:
            self._attach_datetime = self.resource['Attachment']['AttachTime']
            self.resource['Attachment']['AttachTime'] = (
                self._attach_datetime.strftime(self.timestamp_format)
                )
        except KeyError:
            pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def attach_datetime(self):
        '''Return the original datetime type attach time.'''
        return self._attach_datetime

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        if 'Groups' in self.resource:
            self.expansions['Groups'] = [
                SecurityGroupInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('security_group')
                if x['GroupId'] in [
                    sg['GroupId'] for sg in self.resource['Groups']
                    ]
                ]

        super(NetworkInterfaceInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class NetworkAclInformer(AWSInformer):
    '''Manage selected information for an EC2 Network ACL resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize a NetworkAclInformer instance.'''

        super(NetworkAclInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

        # We add a "PortRangeDesc" item to the Entries for ease of
        # reference later.
        # TODO: SecurityGroupInformer should use PortRangeDesc, not PortRange.
        # TODO: This isn't tested.
        if 'Entries' in self.resource:

            for entry in self.resource['Entries']:

                port_range_desc = []

                if 'PortRange' in entry:

                    port_range = entry['PortRange']

                    if 'From' in port_range:
                        port_range_desc.append(str(port_range['From']))
                    if (
                            'To' in port_range and
                            port_range['To'] != port_range['From']
                            ):  # pylint: disable=bad-continuation
                        port_range_desc.append(str(port_range['To']))

                if port_range_desc:
                    entry['PortRangeDesc'] = '-'.join(port_range_desc)
                else:
                    entry['PortRangeDesc'] = '0-65535'

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        if 'Associations' in self.resource:
            self.expansions['AssociatedSubnets'] = [
                SubnetInformer(x, mediator=self.mediator)
                for x in self.mediator.entities('subnet')
                if x['SubnetId'] in [
                    association['SubnetId']
                    for association in self.resource['Associations']
                    ]
                ]

        super(NetworkAclInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class RouteTableInformer(AWSInformer):
    '''Manage selected information for Route Table resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize a RouteTableInformer instance.'''

        super(RouteTableInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        # if 'Associations' in self.resource:
        #     self.expansions['AssociatedSubnets'] = [
        #         SubnetInformer(x, mediator=self.mediator)
        #         for x in self.mediator.entities('subnet')
        #         if x['SubnetId'] in [
        #             association['SubnetId']
        #             for association in self.resource['Associations']
        #             ]
        #         ]

        super(RouteTableInformer, self).expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class EIPInformer(AWSInformer):
    '''Manage selected information for an Elastic IP resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize an EIPInformer instance.'''

        super(EIPInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        super(EIPInformer, self).expand()

        # - - - - - - - - - - - - - - - -
        if 'InstanceId' in self.resource and self.resource['InstanceId']:
            instance_id = self.resource['InstanceId']
            instance_entity = [
                x for x in self.mediator.entities('ec2')
                if x['InstanceId'] == instance_id
                ]
            assert len(instance_entity) == 1
            instance_entity = instance_entity[0]

            self.supplementals['EC2Instance'] = (
                EC2InstanceInformer(instance_entity, mediator=self.mediator)
                )
        else:
            self.supplementals['EC2Instance'] = None

        # - - - - - - - - - - - - - - - -
        if (
                'NetworkInterfaceId' in self.resource and
                self.resource['NetworkInterfaceId']
                ):  # pylint: disable=bad-continuation

            nif_id = self.resource['NetworkInterfaceId']
            nif_entity = [
                x for x in self.mediator.entities('network_interface')
                if x['NetworkInterfaceId'] == nif_id
                ]
            # TODO: This fails sometimes - dying instance maybe?
            assert len(nif_entity) == 1
            nif_entity = nif_entity[0]

            self.supplementals['NetworkInterface'] = (
                NetworkInterfaceInformer(
                    nif_entity, mediator=self.mediator
                    )
                )
        else:
            self.supplementals['NetworkInterface'] = None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SQSInformer(AWSInformer):
    '''Manage selected information for a SQS resource.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @_prevent_duplicate_informer_init_if_cached
    def __init__(
            self,
            resource,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize an SQSInformer instance.'''

        super(SQSInformer, self).__init__(
            resource,
            required_resource_type=dict,
            *args, **kwargs
            )

        self.resource.update(
            self.mediator.session.resource('sqs').Queue(
                self.resource['QueueURL']
                ).attributes
            )

        # Policy comes to us as JSON which we want to convert.
        if 'Policy' in self.resource:
            self.resource['Policy'] = json.loads(
                self.resource['Policy']
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        super(SQSInformer, self).expand()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _get_region_from_arn(self, arnstr):
        '''Helper method for getting region from arn.

        The region should be the fourth colon-separated field in the
        arn. If this is ever not the case, an assertion will fail.

        '''
        region = None
        # print "arnstr is", arnstr
        # if isinstance(arnstr, unicode):

        arn_parts = arnstr.split(':')
        assert len(arn_parts) >= 4

        if len(arn_parts) >= 4:
            region = arn_parts[3]
        return region

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _get_arns_from_policy_statement(self, policy_statement):
        '''Helper method for policy_statement_regions.'''
        if policy_statement is None:
            return []
        if (
                'Condition' not in policy_statement or
                'ArnEquals' not in policy_statement['Condition'] or
                'aws:SourceArn' not in (
                    policy_statement['Condition']['ArnEquals']
                    )
                ):  # pylint: disable=bad-continuation
            return []

        arns = policy_statement['Condition']['ArnEquals']['aws:SourceArn']
        if arns is None:
            return []
        if not isinstance(arns, list):
            arns = [arns]
        assert list(set([type(x) for x in arns])) == [unicode]

        return arns

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # We treat each queue as a separate resource, where AWS keeps all of the
    #    queues in a single list that is retrieved with the session
    #   resource('sqs') Queue() method. This block populates the details of
    #   this particular informer with the attributes of the appropriate queue
    #   in that session resource list
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def get_subscribed_sns_topic_regions(self):  # pylint: disable=invalid-name
        '''Return the SNS topic regions in the instance's subscribed topics.'''
        if (
                'Policy' not in self.resource or
                'Statement' not in self.resource['Policy'] or
                self.resource['Policy']['Statement'] is None
                ):  # pylint: disable=bad-continuation
            return []
        arns = []
        for policy_statement in self.resource['Policy']['Statement']:
            arns += self._get_arns_from_policy_statement(policy_statement)
        regions = [self._get_region_from_arn(a) for a in arns]

        return list(set([r for r in regions if r is not None]))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class IAMInformer(AWSInformer):
    '''
    Manage selected information for an Elastic IP resource.

    IAMInformers have no resource, and store all their data in their
    supplementals. Typically only one IAMInformer need be instantiated
    for a given environment.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(
            self,
            *args,
            **kwargs
            ):  # pylint: disable=bad-continuation
        '''Initialize an IAMInformer instance.'''
        # The parent AWSInformer init requires resource as the second
        # parameter.
        super(IAMInformer, self).__init__(
            None,
            required_resource_type=type(None),
            *args, **kwargs
            )

        # We don't set an identifier for IAMInformers.

        # IAM entities aren't regionized, so we override the region_name
        # if it was set in the super __init__().
        self.region_name = None

        kwargs = dict(
            {'record_types': None},
            **kwargs
            )

        # - - - - - - - - - - - - - - - - - - - -
        # S == covered with special handling.
        # C == covered with common handling.
        # - - - - - - - - - - - - - - - - - - - -
        # S list_access_keys()
        # C list_account_aliases()
        # S list_attached_group_policies()
        # S list_attached_role_policies()
        # S list_attached_user_policies()
        # S list_entities_for_policy()
        # S list_group_policies()
        # C list_groups()
        # S list_groups_for_user()
        # C list_instance_profiles()
        # S list_instance_profiles_for_role()
        # C list_mfa_devices()
        # C list_open_id_connect_providers()
        # C list_policies()
        # S list_policy_versions()
        # S list_role_policies()
        # C list_roles()
        # C list_saml_providers()
        # C list_server_certificates()
        # C list_signing_certificates()
        # C list_ssh_public_keys()
        # S list_user_policies()
        # C list_users()
        # C list_virtual_mfa_devices()
        # - - - - - - - - - - - - - - - - - - - -
        client = self.mediator.session.client('iam')

        # - - - - - - - - - - - - - - - - - - - -
        # Common handling
        # - - - - - - - - - - - - - - - - - - - -
        # pylint: disable=invalid-name
        self.available_record_type_retrievers = {
            'AccountAliases': client.list_account_aliases,
            'Groups': client.list_groups,
            'InstanceProfiles': client.list_instance_profiles,
            'MFADevices': client.list_mfa_devices,
            'OpenIDConnectProviderList': client.list_open_id_connect_providers,
            'Policies': client.list_policies,
            'Roles': client.list_roles,
            'SAMLProviderList': client.list_saml_providers,
            'ServerCertificateMetadataList': client.list_server_certificates,
            'Certificates': client.list_signing_certificates,
            'SSHPublicKeys': client.list_ssh_public_keys,
            'Users': client.list_users,
            'VirtualMFADevices': client.list_virtual_mfa_devices,
            }

        self.record_types = kwargs['record_types']
        self.requested_record_type_retrievers = {
            # pylint: disable=unsupported-membership-test
            k: v
            for (k, v) in self.available_record_type_retrievers.items()
            if self.record_types is None or k in self.record_types
            }

        # - - - - - - - - - - - - - - - - - - - -
        # Parallel retrieval of the "Common Handling" data items.
        # - - - - - - - - - - - - - - - - - - - -
        record_requests = [
            self.request_for_method_response_for_originator(
                None,
                None,
                method.__name__,
                [key]
                )
            for (key, method) in self.requested_record_type_retrievers.items()
            ]

        for request_response_err in self.mediator.get_aws_info_in_parallel(
                record_requests
                ):
            (request, response, err) = request_response_err
            if err is not None:
                raise err
            key = request['response_data_keys'][0]
            self.supplementals[key] = response[key]

        # for (key, method) in self.requested_record_type_retrievers.items():
        #     self.supplementals[key] = get_paged_data(method, key)[key]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Helper methods for retrieving IAM data in multiple parallel
    # calls.
    #
    # We need to pass quite a few parameters in the request dict so
    # that the subprocesses can reconstruct the appropriate session
    # client and call the right method with the necessary
    # parameters. We'll pass a list of requests, one for each IAM
    # User/Group/Role/etc for which we need a method call to
    # retrieve details, to be handled by a pool of subprocesses.
    #
    # The return value from the subprocess pool will again be a list
    # of [request, response, err] which should be in 1-1 ordered
    # correspondance with the list of requests we sent. We include
    # each request in its corresponding response for ease of
    # correlation.
    #
    # If any error was raised somewhere down in the call sequence,
    # response will be None and err will hold the Exception object
    # that was raised.
    #
    # If no error was raised, err will be None.
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # - - - - - - - - - - - - - - - - - - - -
    # pylint: disable=invalid-name
    def request_for_method_response_for_originator(
            self,
            originator,
            origin_id_key,
            client_method,
            response_data_keys,
            method_id_key=None
            ):  # pylint: disable=bad-continuation
        '''Construct the request parameters dict for one request.'''
        if method_id_key is None:
            method_id_key = origin_id_key
        method_kwargs = {} if method_id_key is None else {
            method_id_key: originator[origin_id_key]
            }

        return {
            'origin': originator,
            'session_kwargs': self.mediator._session_kwargs(),
            # 'session_kwargs': {
            #     'profile_name': self.mediator.session.profile_name
            #     },
            'client_type': 'iam',
            'client_method': client_method,
            'method_args': [],
            'method_kwargs': method_kwargs,
            'response_data_keys': response_data_keys
            }

    # - - - - - - - - - - - - - - - - - - - -
    def update_originator_with_response(
            self,
            origin_index,
            origin_id_key,
            request_response_err
            ):  # pylint: disable=bad-continuation
        '''Update the appropriate originator with data from one response.'''
        (request, response, err) = request_response_err
        if err is not None:
            # print "%s: %s" % (type(err), str(err))
            raise err
        elif isinstance(response, dict):
            origin_id = request['origin'][origin_id_key]
            for (data_key, origin_key) in request[
                    'response_data_keys'
                    ].items():
                if data_key in response:
                    origin_index[origin_id][origin_key] = response[
                        data_key
                        ]
                else:
                    raise KeyError(
                        'Expected %s key in response: %s' % (
                            data_key, response
                            )
                        )
        else:
            raise TypeError(
                'Expected iterable in response: %s' % response
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self):
        '''Fetch selected entity details.'''

        # client = self.mediator.session.client('iam')

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Additional User data.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        origin_type = 'Users'
        origin_id_key = 'UserName'
        origin_index = {
            originator[origin_id_key]: originator
            for originator in self.supplementals[origin_type]
            }

        for (client_method, response_data_keys) in [
                (
                    'list_access_keys',
                    {'AccessKeyMetadata': 'AccessKeys'}
                    ),
                (
                    'list_groups_for_user',
                    {'Groups': 'Groups'}
                    ),
                (
                    'list_user_policies',
                    {'PolicyNames': 'PolicyNames'}
                    ),
                (
                    'list_attached_user_policies',
                    {'AttachedPolicies': 'AttachedPolicies'}
                    ),
                ]:  # pylint: disable=bad-continuation

            requests = [
                self.request_for_method_response_for_originator(
                    originator,
                    origin_id_key,
                    client_method,
                    response_data_keys
                    )
                for originator in self.supplementals[origin_type]
                ]

            for request_response_err in self.mediator.get_aws_info_in_parallel(
                    requests
                    ):  # pylint: disable=bad-continuation
                self.update_originator_with_response(
                    origin_index,
                    origin_id_key,
                    request_response_err
                    )

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Additional Group data.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        origin_type = 'Groups'
        origin_id_key = 'GroupName'
        origin_index = {
            originator[origin_id_key]: originator
            for originator in self.supplementals[origin_type]
            }

        for (client_method, response_data_keys) in [
                (
                    'list_group_policies',
                    {'PolicyNames': 'PolicyNames'}
                    ),

                (
                    'list_attached_group_policies',
                    {'AttachedPolicies': 'AttachedPolicies'}
                    ),
                ]:  # pylint: disable=bad-continuation

            requests = [
                self.request_for_method_response_for_originator(
                    originator,
                    origin_id_key,
                    client_method,
                    response_data_keys
                    )
                for originator in self.supplementals[origin_type]
                ]

            for request_response_err in self.mediator.get_aws_info_in_parallel(
                    requests
                    ):  # pylint: disable=bad-continuation
                self.update_originator_with_response(
                    origin_index,
                    origin_id_key,
                    request_response_err
                    )

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Additional Role data.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        origin_type = 'Roles'
        origin_id_key = 'RoleName'
        origin_index = {
            originator[origin_id_key]: originator
            for originator in self.supplementals[origin_type]
            }

        for (client_method, response_data_keys) in [
                (
                    'list_role_policies',
                    {'PolicyNames': 'PolicyNames'}
                    ),
                (
                    'list_attached_role_policies',
                    {'AttachedPolicies': 'AttachedPolicies'}
                    ),
                (
                    'list_instance_profiles_for_role',
                    {'InstanceProfiles': 'InstanceProfiles'}
                    ),
                ]:  # pylint: disable=bad-continuation

            requests = [
                self.request_for_method_response_for_originator(
                    originator,
                    origin_id_key,
                    client_method,
                    response_data_keys
                    )
                for originator in self.supplementals[origin_type]
                ]

            for request_response_err in self.mediator.get_aws_info_in_parallel(
                    requests
                    ):  # pylint: disable=bad-continuation
                self.update_originator_with_response(
                    origin_index,
                    origin_id_key,
                    request_response_err
                    )

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Additional Policy data.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        origin_type = 'Policies'
        origin_id_key = 'Arn'

        origin_index = {
            originator[origin_id_key]: originator
            for originator in self.supplementals[origin_type]
            }

        for (client_method, response_data_keys) in [
                (
                    'list_entities_for_policy',
                    {
                        'PolicyGroups': 'PolicyGroups',
                        'PolicyUsers': 'PolicyUsers',
                        'PolicyRoles': 'PolicyRoles'
                        }
                    ),
                (
                    'list_policy_versions',
                    {'Versions': 'Versions'}
                    ),
                ]:  # pylint: disable=bad-continuation

            requests = [
                self.request_for_method_response_for_originator(
                    originator,
                    origin_id_key,
                    client_method,
                    response_data_keys,
                    method_id_key='PolicyArn'
                    )
                for originator in self.supplementals[origin_type]
                ]

            for request_response_err in self.mediator.get_aws_info_in_parallel(
                    requests
                    ):  # pylint: disable=bad-continuation
                self.update_originator_with_response(
                    origin_index,
                    origin_id_key,
                    request_response_err
                    )

        super(IAMInformer, self).expand()
