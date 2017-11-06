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
'''Manage sets of ``AWSInformer`` instances across accounts and regions.

An ``AWSSurveyor`` instance manages AWSMediator and ``AWSInformer``
instances across multiple profiles and regions.

Use ``AWSSurveyor`` instances with a workflow like the following.

    #.  Initialize an ``AWSSurveyor`` instance, defining values for
        profiles, regions and entity types if desired.

    #.  Use ``AWSSurveyor.survey()`` to retrieve records from AWS and
        create ``AWSInformer`` instances to manage them. You can use
        the existing presets for profiles, regions and entity types,
        update the presets, or specify survey-specific values.

    #.  Use ``AWSSurveyor.informers()`` to retrieve informers from the
        surveyor for further use.

.. _aws_surveyor_initialization_package_label:

AWSSurveyor Initialization
--------------------------

An ``AWSSurveyor`` maintains preset lists of the profiles, regions and
entity types that will be used by default when ``survey()`` is called.
These preset values can be assigned when a surveyor is created and can
be updated afterwards. Common preset values can be saved in
configuration files as blocks of JSON such as the following.

    ::

        {
            "profiles": ["some_profile", "another_profile"],
            "regions": ["us-east-1", "us-west-1", "us-west-2"],
            "entity_types": ["ec2", "security_group", "subnet", "vpc"]
        }

If no presets are provided when an ``AWSSurveyor`` instance is created
and :file:`$HOME/.aws/aws_surveyor.cfg`` exists, it will be parsed as
a JSON file to determine presets.

To read from another configuration file, pass the local or absolute
path to the file as the value of the ``config_path`` initialization
argument.

To suppress reading of preset values from
:file:`$HOME/.aws/aws_surveyor.cfg``, pass an empty string as the
value of the ``config_path`` argument at initialization.



    **Examples**

    *   Initialize presets from :file:`$HOME/.aws/aws_surveyor.cfg`:

        ::

            >>> surveyor = AWSSurveyor()

    *   Initialize presets from :file:`aws_surveyor.cfg` in the
        current working directory:

        ::

            >>> surveyor = AWSSurveyor(config_path='aws_surveyor.cfg')

    *   Don't read any configuration file at initialization, even if
        the default configuration file
        :file:`$HOME/.aws/aws_surveyor.cfg` exists:

        ::

            >>> surveyor = AWSSurveyor(config_path='')

You can also configure any of the ``profiles``, ``regions`` and
``entity_types`` presets individually via initialization arguments.
Any values for these presets that would otherwise be read from a
configuration file will be overwritten by initialization arguments. To
add to, rather than overwriting, configuration file presets set the
``add_to_config`` argument to ``True``.

    **Examples**

    *   Define ``profiles``, ``regions`` and ``entity_types`` presets
        at initialization, overriding any of their presets defined in
        :file:`$HOME/.aws/aws_surveyor.cfg`::

            >>> surveyor = AWSSurveyor(
            ...     profiles=['some_profile', 'another_profile'],
            ...     regions=['us-east-1', 'us-west-1', 'us-west-2'],
            ...     entity_types=['ec2', 'security_group', 'subnet', 'vpc']
            ...     )

        Examine the ``presets`` property to see the current presets::

            >>> surveyor.presets
            {'profiles': ['some_profile', 'another_profile'], 'regions': [
            'us-east-1', 'us-west-1', 'us-west-2'], 'entity_types': ['ec2',
            'security_group', 'subnet', 'vpc']}

    *   Define the ``entity_types`` preset at initialization, overriding
        the ``entity_types`` preset if one is defined in the default
        configuration file :file:`$HOME/.aws/aws_surveyor.cfg`. This
        will still use the default configuration file presets for
        ``profiles`` and ``regions``::

            >>> surveyor = AWSSurveyor(
            ...     entity_types=['ec2', 'security_group', 'subnet', 'vpc']
            ...     )

    *   Read the presets for ``profiles``, ``regions`` and
        ``entity_types`` from the specified configuration file, and
        add an additional "elb" entity type preset::

            >>> surveyor = AWSSurveyor(
            ...     entity_types=['elb'],
            ...     config_path='my_aws_surveyor.cfg',
            ...     add_to_config_path=True
            ...     )

    When creating an ``AWSSurveyor`` instance, you can also configure
    the ``regions`` preset by setting the ``set_all_regions`` flag to
    ``True``.

    *   Read presets from the default configuration file and then
        update the ``regions`` preset to include all regions::

            >>> surveyor = AWSSurveyor(
            ...     set_all_regions=True
            ...     )


.. _aws_surveyor_config_files_label:

Configuration Files
-------------------

AWSSurveyor configuration files define the preset values for the AWS
credentials profiles, the AWS regions and the AWS entity types
(corresponding to ``AWSInformer`` subclasses) that the ``survey()``
method will use.

    An example of a typical ``AWSSurveyor`` configuration file::

        {
            "profiles": ["some_profile", "another_profile"],
            "regions": ["us-east-1", "us-west-1", "us-west-2"],
            "entity_types": ["ec2", "security_group", "subnet", "vpc"]
        }

The default location for an ``AWSSurveyor`` configuration file is
:file:`$HOME/.aws/aws_surveyor.cfg`. If this file exists, it will be
read automatically unless explicitly suppressed. You can also use
configuration files in other locations or use initialization
arguments for configuration. See
:ref:`aws_surveyor_initialization_package_label` for more detailed
information on surveyor initialization and configuration.


.. _aws_surveyor_updating_configuration_package_label:

Updating AWSSurveyor Configuration
----------------------------------

If you want to change the presets for an existing AWSSurveyor
instance, you can assign directly to the ``presets`` property. You can
also set the ``profiles``, ``regions`` and ``entity_types`` explicily,
or use the ``add_*`` and ``remove_*`` methods.

    **Examples**

    *   Set the ``presets`` property directly::

            >>> surveyor = AWSSurveyor()
            >>> surveyor.presets = {
            ...     'profiles': ['some_profile', 'another_profile'],
            ...     'regions': ['us-east-1', 'us-west-1', 'us-west-2'],
            ...     'entity_types': ['ec2', 'security_group', 'subnet', 'vpc']
            ...     }
            >>> surveyor.presets
            {'profiles': ['some_profile', 'another_profile'], 'regions': [
            'us-east-1', 'us-west-1', 'us-west-2'], 'entity_types': ['ec2',
            'security_group', 'subnet', 'vpc']}

    *   Assign values to individual presets::

            >>> surveyor = AWSSurveyor()
            >>> surveyor.profiles = ['this_profile', 'that_profile']
            >>> surveyor.profiles
            ['this_profile', 'that_profile']

            >>> surveyor.remove_profile(['that_profile'])
            >>> surveyor.add_profiles(['another_profile'])
            >>> surveyor.profiles
            ['this_profile', 'another_profile']

    *   Adding duplicate preset values or trying to remove values that aren't
        already present will have no effect on existing presets::

            >>> surveyor = AWSSurveyor()
            >>> surveyor.profiles = ['this_profile', 'that_profile']
            >>> surveyor.profiles
            ['this_profile', 'that_profile']

            >>> surveyor.remove_profile(['another_profile'])
            >>> surveyor.profiles
            ['this_profile', 'that_profile']

            >>> surveyor.regions = ['us-west-1']
            >>> surveyor.regions
            ['us-west-1']

            >>> surveyor.add_regions(['us-west-1'])
            >>> surveyor.regions
            ['us-west-1']

.. _aws_surveyor_executing_surveys_package_label:

Executing Surveys
-----------------

Use the ``AWSSurveyor.survey()`` method to query Amazon Web Services
and create ``AWSInformer`` instances for entity types in regions and
using profiles currently configured as presets or to a subset of the
preset regions and profiles as defined in arguments passed to
``survey()``.

.. note:: Arguments for ``profiles`` and ``regions`` passed to
    ``survey()`` must already be present in the ``AWSSurveyor``
    instance's presets. If you want to survey new profiles or regions
    you must first use the ``add_profiles()`` and ``add_regions()``
    methods to update the presets.

Use the ``AWSSurveyor.instances()`` method to retrieve the results of
the survey as a list of ``AWSInformer`` instances.

    **Examples**

    *   Survey using presets defined at instance initialization::

            >>> surveyor = AWSSurveyor(
            ...     profiles=['some_profile'],
            ...     regions=['us-east-1'],
            ...     entity_types=['ec2']
            ...     )
            >>> surveyor.survey()
            >>> instances = surveyor.instances()

    *   Pass arguments to ``survey()`` to override presets. This will
        survey *vpc* entity_types in region *us-west-2* using
        credentials defined for *another_profile*, regardless of the
        configuration in the :file:`aws_surveyor` configuration file::

            >>> surveyor = AWSSurveyor(config_path='aws_surveyor.cfg')
            >>> surveyor.survey(
            ...     profiles=['another_profile'],
            ...     regions=['us-west-2'],
            ...     entity_types=['vpc']
            ...     )
            >>> instances = surveyor.instances()

        This surveyor will survey *vpc* entity_types using the
        settings for `profile` and `region` in the
        :file:`aws_surveyor` configuration file::

            >>> surveyor = AWSSurveyor(config_path='aws_surveyor.cfg')
            >>> surveyor.survey(
            ...     entity_types=['vpc']
            ...     )
            >>> instances = surveyor.instances()


'''

from datetime import datetime
import itertools
import json
import os

import logging
# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        '''Placeholder handler.'''
        def emit(self, record):
            '''Pylint-compliant docstring.'''
            pass

from boogio import aws_informer

from utensils import flatten
from utensils import prune

logging.getLogger(__name__).addHandler(NullHandler())

# We will cache the result of looking this up in AWS.
_ALL_REGIONS = None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def all_regions(profile_name=None, region_name=None, *filters):
    '''
    Return all region names matching any of the strings in filters.

    Arguments:

        profile_name (str):
            An AWS credentials profile name to use call the boto3
            ``describe_regions()`` API to retrieve the names of all
            regions currently supported.

        region_name (str):
            An AWS region name to use call the boto3
            ``describe_regions()`` API to retrieve the names of all
            regions currently supported.

        filters (list of str):
            A list of strings which occur as substrings of the desired
            regions.

    Returns:

        (list of str): All available regions that contain at least one
        filter as a substring.

    Examples::

        >>> all_regions('us')
        ['us-east-1', 'us-west-1', 'us-west-2']

        >>> all_regions('north', 'south')
        ['ap-northeast-1', 'ap-southeast-1', 'ap-southeast-2']

        >>> all_regions('-2')
        ['ap-southeast-2', 'us-west-2']

    '''
    import boto3
    logger = logging.getLogger(__name__)

    # This is what was returned for a particular profile and environment at
    # a point in time; we're using it as a baseline.
    minimal_expected_regions = [
        'ap-northeast-1',
        'ap-southeast-1',
        'ap-southeast-2',
        'eu-central-1',
        'eu-west-1',
        'sa-east-1',
        'us-east-1',
        'us-east-2',
        'us-west-1',
        'us-west-2'
        ]

    global _ALL_REGIONS  # pylint: disable=global-statement

    # We only fetch this from AWS once; thereafter it's cached in the
    # global module variable _ALL_REGIONS.
    logger.debug(
        'all_regions: profile_name %s, region_name %s',
        profile_name, region_name
        )
    logger.debug('_ALL_REGIONS: %s', _ALL_REGIONS)
    if _ALL_REGIONS is None:

        boto_kwargs = {}

        if profile_name:
            boto_kwargs.setdefault('profile_name', profile_name)
        if region_name:
            boto_kwargs.setdefault('region_name', region_name)
        else:
            boto_kwargs.setdefault('region_name', 'us-east-1')

        sess = boto3.session.Session(**boto_kwargs)

        kwargs_msg = (
            str(boto_kwargs) if len(boto_kwargs)
            else 'default profile and region'
            )
        logger.debug('retrieving master regions list with %s', kwargs_msg)

        logger.debug(
            'setting _ALL_REGIONS with describe_regions()'
            ' (default credentials required)'
            )
        _ALL_REGIONS = [
            x['RegionName']
            for x in sess.client('ec2').describe_regions()['Regions']
            ]
        logger.debug('_ALL_REGIONS set to: %s', _ALL_REGIONS)

    regions = list(_ALL_REGIONS)
    logger.debug('master regions list: %s', regions)

    # Fail if we didn't get at least the baseline.
    assert(
        len([
            x for x in minimal_expected_regions
            if x not in regions
            ]) == 0
        )

    # Apply filters.
    if len(filters) > 0:
        regions = [
            r for r in regions
            if max([r.find(f) for f in filters]) >= 0
            ]

    logger.debug('filtered regions list: %s', regions)
    return regions


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSSurveyor(object):
    '''Manage AWS queries and ``AWSInformer`` instances with the results.

    Arguments:

        profiles (list of str, optional):
            A list of the AWS credentials profiles to use for AWS
            sessions.

        regions (list of str, optional):
            A list of the AWS regions to connect to with AWS
            sessions.

        entity_types (list of str, optional):
            A list of the entity types to retrieve when
            ``AWSSurveyor.survey()`` is called.

        config_path (string, optional):
            The path to a JSON format configuration file. See
            :ref:`aws_surveyor_config_files_label`.

        add_to_config (bool, default=False):
            If `True`, any presets values defined by arguments will be
            added to the presets values read from any configuration
            files. If `False`, values passed as arguments will
            overwrite values from configuration files.

        set_all_regions (bool, default=False):
            If `True`, the ``regions`` preset will be set to a list of
            all currently available regions. This requires a call to
            ``aws_surveyor.all_regions()``, which connects to AWS.

    Attributes:

        mediators (list of AWSMediator):
            A list of AWSMediator instances, one for each profile and
            region assigned to the surveyor or obtained from default
            configuration selection (e.g. the default profile or an
            EC2 instance profile).

    '''

    _default_config_filename = 'aws_surveyor.cfg'
    _default_config_dir = None

    _presets_attributes = ['profiles', 'regions', 'entity_types']

    # Set this to True to prevent attempts to create AWS sessions at
    # initialization. This will prevent population of the _mediators
    # attribute.
    _hold_sessions = False

    timestamp_format = "%Y%m%dT%H%M%S"

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def default_config_filename(cls, value=None):
        '''Set or get the class default configuration filename.

        Arguments:

            value (string, optional):
                If provided, the string to set as the default
                configuration filename.

        Returns:
            (string) The current value (updated with the new value, if
            provided) of the default configuration filename.

        '''

        if value is not None:
            cls._default_config_filename = value

        return cls._default_config_filename

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def default_config_dir(cls, value=None):
        '''Set or get the class default configuration file directory.

        Arguments:

            value (string, optional):
                If provided, the string to set as the default
                configuration directory.

        Returns:

            (string) The current value (updated with the new
            value, if provided) of the default configuration
            directory.

        '''

        if value is not None:
            cls._default_config_dir = value

        elif cls._default_config_dir is None:
            cls._default_config_dir = os.path.join(
                os.path.expanduser('~'), '.aws'
                )

        return cls._default_config_dir

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def default_config_path(cls):
        '''Return the path to the default configuration file.

        Return the path formed by joining the default configuration
        filename to the default configuration directory.

        '''

        return os.path.join(
            cls.default_config_dir(),
            cls.default_config_filename()
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def _surveyable_types(cls, *types):
        '''Return a list of the AWSInformer types that are surveyable.

        If any types are passed, return just the ones from that list
        which are surveyable.
        '''

        surveyable_types = (
            aws_informer.regional_types() +
            aws_informer.regionless_types() +
            aws_informer.unitary_types()
            )

        if len(types) > 0:
            surveyable_types = [
                t for t in types
                if t in surveyable_types
                ]

        return surveyable_types

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(
            self,
            profiles=None,
            regions=None,
            entity_types=None,
            config_path=None,
            add_to_config=False,
            set_all_regions=False
            ):  # pylint: disable=bad-continuation
        '''Initialize an AWSSurveyor instance.'''
        logger = logging.getLogger(__name__)

        self._survey_timestamp = None

        # This gets re-done, but lets e.g. pylint recognize the attributes.
        self._profiles = []
        self._regions = []
        self._entity_types = []

        self._initialize_presets_from_file(config_path)

        logger.debug('AWS Surveyor initializing...')
        logger.debug('profiles: %s', profiles)
        logger.debug('regions: %s', regions)
        logger.debug('entity_types: %s', entity_types)
        logger.debug('config_path: %s', config_path)
        logger.debug('add_to_config: %s', add_to_config)
        logger.debug('set_all_regions: %s', set_all_regions)

        # Override or augment presets from file.
        if profiles:
            if not add_to_config:
                self._profiles = []
            self.add_profiles(profiles)

        if regions:
            if not add_to_config:
                self._regions = []
            self.add_regions(regions)

        if entity_types:
            if not add_to_config:
                self._entity_types = []
            self.add_entity_types(entity_types)

        if set_all_regions:
            all_regions_kwargs = {}
            if profiles:
                all_regions_kwargs.setdefault('profile_name', profiles[0])
            if regions:
                all_regions_kwargs.setdefault('region_name', regions[0])
            self._regions = all_regions(**all_regions_kwargs)

        self._mediators = []
        self._accounts = []

        if not self._hold_sessions:
            # This will initialize both mediators and accounts.
            self._initialize_mediators()

        # This gets populated by survey().
        self._informers = []

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _initialize_presets_from_file(self, config_path):
        '''Configure presets from config_path, if not empty.'''

        # Set this empty, then override that with the config file
        # contents, if a config file was provided.
        config_content = {}

        if config_path != '':

            if (
                    config_path is None and
                    os.path.exists(self.default_config_path())
                    ):  # pylint: disable=bad-continuation
                config_path = self.default_config_path()

            else:  # Use the value of config.
                config_path = config_path

            if config_path is not None:
                with open(config_path, 'r') as fptr:
                    config_content = json.load(fptr)

        # It's OK to initialize all at once this way, but we need to use
        # the add_* methods so we get any error checking.
        for preset in self._presets_attributes:
            setattr(self, preset, [])

        if 'profiles' in config_content:
            self.add_profiles(config_content['profiles'])

        if 'regions' in config_content:
            self.add_regions(config_content['regions'])

        if 'entity_types' in config_content:
            self.add_entity_types(config_content['entity_types'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _get_initialized_mediators(self):
        '''Return the list of ``AWSMediator`` instances to use.'''

        all_profile_kwargs = [{}]
        if self.profiles:
            all_profile_kwargs = [{'profile_name': p} for p in self.profiles]

        all_region_kwargs = [{}]
        if self.regions:
            all_region_kwargs = [{'region_name': r} for r in self.regions]

        all_mediator_kwargs = [
            dict(x[0], **x[1])
            for x in itertools.product(all_profile_kwargs, all_region_kwargs)
            ]

        return [
            aws_informer.AWSMediator(**mediator_kwargs)
            for mediator_kwargs in all_mediator_kwargs
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _initialize_mediators(self):
        '''Perform mediator initialization and accounts record update.'''

        self._mediators = self._get_initialized_mediators()
        self._accounts = [
            {
                'account_id': m.account_id,
                'account_name': m.account_name,
                'account_desc': m.account_desc,
                'region_name': m.region_name
                } for m in self._mediators
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def survey_timestamp(self):
        '''Get the _survey_timestamp attribute.'''
        return self._survey_timestamp

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def profiles(self):
        '''Get or set the profiles attribute.'''
        return self._profiles

    @profiles.setter
    def profiles(self, value):
        '''Set the profiles attribute.'''
        self._profiles = list(set(value))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def regions(self):
        '''Get or set the regions attribute.'''
        return self._regions

    @regions.setter
    def regions(self, value):
        '''Set the regions attribute.'''
        self._regions = list(set(value))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def entity_types(self):
        '''Get or set the entity_types attribute.'''
        return self._entity_types

    @entity_types.setter
    def entity_types(self, value):
        '''Set the entity_types attribute.'''

        if len(value) > 0:
            bad_entity_types = [
                t for t in value
                if t not in self._surveyable_types(*value)
                ]

            if len(bad_entity_types) > 0:
                raise ValueError(
                    'unsurveyable entity types:'
                    ' %s' % ', '.join(bad_entity_types)
                    )
        self._entity_types = list(set(value))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def presets(self):
        '''Get or set all of the presets attributes at once.

        The presets attributes are ``profiles``, ``regions`` and
        ``entity_types`` The ``presets`` derived property returns them
        as a dictionary with the attribute names as keys and the
        attribute values as values.

        Setting presets to a dictionary with the same keys will assign
        the corresponding values, *and assign an empty list for any
        of the presets attributes not present in the dictionary*.

        Examples:

            *   Set all presets to the values shown::

                    >>> surveyor = AWSSurveyor()
                    >>> surveyor.presets = {
                    ...     'profiles': ['some_profile', 'another_profile'],
                    ...     'regions': ['us-east-1', 'us-west-1'],
                    ...     'entity_types': ['vpc', 'subnet']
                    ...     }

            *   Set the profile preset to ``[another_profile]`` and
                empty the other presets::

                    >>> surveyor = AWSSurveyor()
                    >>> surveyor.presets = {'profiles': ['another_profile']}

        '''
        return {
            'profiles': self.profiles,
            'regions': self.regions,
            'entity_types': self.entity_types
            }

    @presets.setter
    def presets(self, value):
        '''Set the presets attributes.'''
        self._initialize_presets_from_file('')
        for preset in self._presets_attributes:
            if preset in value:
                setattr(self, preset, value[preset])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def mediators(self):
        '''Return the list of ``AWSMediator`` instances in use.'''
        return self._mediators

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def accounts(self):
        '''The surveyors' ``AWSMediator``'s AWS account attributes.

        Each element of the list is a dict with the account
        information for one of the surveyor's mediators, of the form:

        ::

            {
            'account_id': <AWS Account ID>,
            'account_name': <Account Name, if defined in boogio.json>,
            'account_desc': <account_name if defined, or account_id>,
            'region_name': <mediator's region_name attribute>
            }

        '''
        return self._accounts

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_profiles(self, profiles):
        '''Add new values to the ``profiles`` attribute.

        Arguments:

            profiles (list of str):
                The profile values to add.
        '''
        self.profiles = list(
            set(self.profiles + profiles)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def remove_profiles(self, profiles):
        '''Remove values from the ``profiles`` attribute.

        Arguments:

            profiles (list of str):
                The profile values to remove.
        '''
        self.profiles = list(
            set(self.profiles).difference(set(profiles))
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_regions(self, regions):
        '''Add new values to the ``regions`` attribute.

        Arguments:

            regions (list of str):
                The region values to add.
        '''
        self.regions = list(
            set(self.regions + regions)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def remove_regions(self, regions):
        '''Remove values from the ``regions`` attribute.

        Arguments:

            regions (list of str):
                The region values to remove.
        '''
        self.regions = list(
            set(self.regions).difference(set(regions))
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_entity_types(self, entity_types):
        '''Add new values to the ``entity_types`` attribute.

        Arguments:

            entity_types (list of str):
                The entity_type values to add.
        '''

        self.entity_types = list(
            set(self.entity_types + entity_types)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def remove_entity_types(self, entity_types):
        '''Remove values from the ``entity_types`` attribute.

        Arguments:

            entity_types (list of str):
                The entity_type values to remove.
        '''
        self.entity_types = list(
            set(self.entity_types).difference(set(entity_types))
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_filters(self, entity_type, filters):
        '''
        Add AWS entity retrieval filters to the surveyor's mediators.

        Arguments:

            entity_type (string):

                An informer entity type to which this filter will
                apply.

            new_filters (dict):

                The *Name* strings and *Values* lists for the filters.

        See the documentation for ``AWSMediator`` for further details.

        '''
        for mediator in self.mediators():
            mediator.add_filters(entity_type, filters)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def remove_all_filters(self, *remove_types):
        '''Remove AWS entity filters from the surveyor's mediators.'''
        for mediator in self.mediators():
            mediator.remove_all_filters(*remove_types)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def survey(self, *entity_types, **kwargs):
        '''Conduct a survey of preset or specified AWS targets.

        Arguments:

            *entity_types (str):
                A tuple of the entity types to retrieve for this
                survey, instead of any instance presets.

            profiles (list of str, optional):
                A subset of instance profiles to use for this survey.

            regions (list of str, optional):
                A subset of instance regions to use for this survey.

            refresh (optional):
                If ``True`` (the default), delete all existing
                informer records and load anew. If ``False``, preserve
                existing records for any entity type that has already
                been loaded.

        Raises:

            ValueError: If any item in ``profiles`` or ``regions``
                isn't already present in the corresponding presets.

            ValueError: If any of the entity types in ``entity_types``
                isn't a valid ``AWSInformer`` entity type.

        The ``survey()`` method populates the internal list of
        ``AWSInformer`` instances maintained by this ``AWSSurveyor``
        instance, which can then be accessed via the ``instances()``
        method.

        By default, the ``profiles``, ``regions`` and ``entity_types``
        used will be the presets values. Any values passed in as
        arguments will override the corresponding presets values.
        *This can be used to limit the profiles and regions surveyed
        to a subset of those already configured as presets, but no new
        profiles or regions can be added.* There is no such
        restriction for ``entity_types``, and any new types will be
        added to the instance's ``entity_types`` preset.

        If no profile was specified (so that default, environment
        variable specified or instance profile associated credentials
        will be used), any profiles passed to ``survey()`` will be
        ignored.

        '''

        logger = logging.getLogger(__name__)

        default_kwargs = {
            'profiles': None,
            'regions': None,
            'refresh': True
            }
        kwargs = dict(default_kwargs, **kwargs)

        profiles = kwargs['profiles']
        regions = kwargs['regions']
        refresh = kwargs['refresh']

        if profiles and not self.profiles:
            err_msg = (
                'survey limiting profiles not allowed when using'
                ' unspecified surveyor profile'
                )
            logger.error(err_msg)
            raise ValueError(err_msg)

        # - - - - - - - - - - - - - - - - - - - -
        # Profiles and regions must be a subset of presets.
        # - - - - - - - - - - - - - - - - - - - -

        if profiles is None:
            bad_profiles = []
            profiles = self._profiles
        else:
            bad_profiles = [p for p in profiles if p not in self.profiles]

        if regions is None:
            bad_regions = []
            regions = self._regions
        else:
            bad_regions = [p for p in regions if p not in self.regions]

        if len(bad_profiles) > 0 or len(bad_regions) > 0:
            err_msg = (
                'survey profiles and regions must be subsets of'
                ' AWSSurveyor instance preset profiles and regions'
                )
            logger.error(err_msg)
            raise ValueError(err_msg)

        # - - - - - - - - - - - - - - - - - - - -
        # Entity types must be surveyable.
        # - - - - - - - - - - - - - - - - - - - -

        if len(entity_types) == 0:
            new_entity_types = []
            entity_types = self.entity_types
        else:
            new_entity_types = [
                p for p in entity_types
                if p not in self.entity_types
                ]

        if len(new_entity_types) > 0:
            # This will check for valid entity types.
            self.add_entity_types(new_entity_types)

        # - - - - - - - - - - - - - - - - - - - -
        # Select the required mediators.
        # - - - - - - - - - - - - - - - - - - - -

        # As noted above, we raised an error if self.profiles is not
        # defined and profiles was specified.
        logger.debug('selecting mediators...')
        mediators = [
            m for m in self._mediators
            if (m.profile_name in profiles or not self.profiles) and
            m.region_name in regions
            ]

        # A set of mediators for nonregionized types, where we only need
        # one representative for each profile.
        nonregionized_mediators = [
            m for m in mediators
            if m.region_name == regions[0]
            ]

        # Check for empty polling.
        if not(entity_types):
            err_msg = 'survey() requires non-empty entity types list'
            logger.warn(err_msg)
        if (
                not regions and not set(
                    aws_informer.unitary_types()
                    ).intersection(set(entity_types))
                ):  # pylint: disable=bad-continuation
            err_msg = (
                'survey() of one or more of entity types %s'
                ' requires defined regions list'
                )
            logger.warn(err_msg, entity_types)

        # - - - - - - - - - - - - - - - - - - - -
        # Polling begins.
        # - - - - - - - - - - - - - - - - - - - -
        # If we're not refreshing, we have to preserve the existing
        # entities.
        informers_index_by_entity_type = {
            x: self.informers(x) for x in self._surveyable_types()
            }
        existing_surveyed_types = [
            x for x, i in informers_index_by_entity_type.iteritems()
            if i != []
            ]

        informer_list = []
        # If we're not refreshing, we keep anything already surveyed.
        if not refresh:
            for entity_type, informers in (
                    informers_index_by_entity_type.iteritems()
                    ):  # pylint: disable=bad-continuation
                informer_list.extend(informers)

        self._survey_timestamp = datetime.utcnow().strftime(
            self.timestamp_format
            )

        logger.debug('starting polling...')
        for entity_type in entity_types:

            if entity_type in existing_surveyed_types and not refresh:
                continue

            logger.debug('polling entity type %s...', entity_type)
            # - - - - - - - - - - - -
            # These have a separate set by region.
            # - - - - - - - - - - - -
            if entity_type in aws_informer.regional_types():

                for mediator in mediators:
                    informer_list.extend([
                        aws_informer.informer_class(entity_type)(
                            entity, mediator=mediator
                            )
                        for entity in mediator.entities(entity_type)
                        ])

            # - - - - - - - - - - - -
            # These aren't separated out by region.
            # The canonical example is SQS.
            # - - - - - - - - - - - -
            elif entity_type in aws_informer.regionless_types():

                for mediator in nonregionized_mediators:
                    informer_list.extend([
                        aws_informer.informer_class(entity_type)(
                            entity, mediator=mediator
                            )
                        for entity in mediator.entities(entity_type)
                        ])

            # - - - - - - - - - - - -
            # These don't have "multiple entities".
            # The canonical example is IAM.
            # - - - - - - - - - - - -
            elif entity_type in aws_informer.unitary_types():
                informer_list.extend([
                    aws_informer.informer_class(
                        entity_type
                        )(None, mediator=mediators[0])
                    ])

        self._informers = informer_list

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def informers(self, *entity_types):
        '''Return the current list of surveyed ``AWSInformer`` instances.

        Arguments:

            entity_types (list of str): A list of informer entity
                types.

        Returns:

            list: A list of the informers of the specified entity
                types retrieved in the last call to ``survey()``.
        '''

        if len(entity_types) == 0:
            return self._informers

        informer_classes = set([
            aws_informer.informer_class(entity_type)
            for entity_type in entity_types
            ])

        return [
            i for i in self._informers
            if isinstance(i, tuple(informer_classes))
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand_informers(self, *entity_types):
        '''Expand the current list of surveyed ``AWSInformer`` instances.

        Arguments:

            entity_types (list of str): A list of informer entity
                types.

        Calling the ``AWSSurveyor.expand_informers()`` method will
        call the ``expand()`` method on each instance in the current
        list of surveyed informers, or on each instance of one of the
        entity types indicated.

        '''

        informer_classes_to_expand = set([
            aws_informer.informer_class(entity_type)
            for entity_type in entity_types
            ])

        [
            i.expand() for i in self._informers
            if isinstance(i, tuple(informer_classes_to_expand)) or
            len(informer_classes_to_expand) == 0
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def all_paths(self, *entity_types):
        '''Find prunable paths available in informers of given types.

        Find all the prune specification paths present in the list of
        ``to_dict()`` output for a list of ``AWSInformer`` instances.

        Arguments:

            entity_types (tuple of str): A tuple of informer entity
                types.

        Returns:

            list: A list of all the ``prune`` path specifications
                found in and informer in this instance's
                ``informers()`` list.


        See the documentation for the utensils ``prune`` module
        for information on pruning and prune paths.

        '''
        # TODO: Need test cases.

        if len(entity_types) == 0:
            entity_types = tuple(set(
                (i.entity_type for i in self.informers())
                ))

        # TODO: This may lead to ugly results for multiple entity types.
        return sorted(flatten.flatten(
            prune.paths(
                [x.to_dict() for x in self.informers(*entity_types)]
                )
            ))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def set_ec2_elb_supplementals(self):
        '''Record LoadBalancer names in EC2 Instance supplementals.

        Calling ``set_ec2_elb_supplementals()`` will add a
        ``load_balancer_names`` item to each EC2InstanceInformer in
        the surveyor's informers.

        Note that this will retrieve ELB records from AWS if they
        aren't already loaded.

        '''
        # Create empty load_balancer_names entries in each EC2
        # informer supplementals.
        for x in self.informers('ec2'):
            x.supplementals.setdefault('load_balancer_names', [])
            x.supplementals.setdefault('load_balancer_genuses', [])

        # Populate the ELB informers, don't lose what's already there.
        self.survey('elb', refresh=False)

        # Add elb informer names and base names to each instance supplemental.
        informer_cache = aws_informer.AWSMediator.informer_cache
        for elb_informer in self.informers('elb'):

            load_balancer_name = elb_informer.resource['LoadBalancerName']

            load_balancer_genus = None
            load_balancer_site_specific = elb_informer.supplementals.get(
                'site-specific'
                )
            if load_balancer_site_specific:
                load_balancer_genus = (
                    load_balancer_site_specific.get('genus')
                    )

            ec2_instance_ids = [
                x['InstanceId'] for x in elb_informer.resource['Instances']
                ]
            for ec2_instance_id in ec2_instance_ids:

                ec2_informer = informer_cache.get(ec2_instance_id)

                # Ignore misses for now? ELBs can reference EC2
                # instances that no longer exist.
                if ec2_informer:
                    supplementals = ec2_informer.supplementals
                    supplementals['load_balancer_names'].append(
                        load_balancer_name
                        )
                    if load_balancer_genus is not None:
                        supplementals['load_balancer_genuses'].append(
                            load_balancer_genus
                            )
