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

'''Site-specific code for customization of boogio entities.

Code customized to site specific needs can be placed in this package.
See below for specific methods that will be called when different
entity types are being initialized.

Place site-specific definitions for the items in the DEFAULT_SITE_CONFIG
dictionary in site_boogio.yml, which should be located in $HOME or
colocated with this file.
'''

import logging
import os.path
import re
import yaml

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        '''Placeholder handler.'''
        def emit(self, record):
            '''Dummy docstring.'''
            pass

logging.getLogger(__name__).addHandler(NullHandler())

logger = logging.getLogger(__name__)

site_config_filename = 'site_boogio.yml'
site_config_locations = [
    os.path.dirname(os.path.realpath(__file__)),
    os.path.expanduser("~")
    ]

DEFAULT_SITE_CONFIG = {
    'test_region_name': 'us-east-1',
    'test_profile_name': 'default',
    'default_regions': ['us-east-1'],
    'default_region_name': 'us-east-1',
    'default_profiles': ['default'],
    'prod_profile_name': 'default',

    # This will be used if a profile is needed to retrieve a list of
    # regions.
    'surveyor_default_profile_name': 'default',

    # Key pairs <id>: <name>.
    'account_name_by_id': {},

    # Key pairs <id>: <description>.
    'account_description_by_id': {},

    # Regexes to apply in turn to the GroupName to try to find values
    # for the SG_NAME_FIELDS. Pay careful attention to order and to
    # which have optional or mandatory fields.
    'SG_NAME_PATTERN_OPTIONS': [],

    # Regexes to apply in turn to the Tags:Name to try to find values
    # for the EC2_NAME_FIELDS. Pay careful attention to order and to
    # which have optional or mandatory fields.
    'EC2_NAME_PATTERN_OPTIONS': [],

    # Regexes to apply in turn to the Tags:Name to try to find values
    # for the EC2_NAME_FIELDS. Pay careful attention to order and to
    # which have optional or mandatory fields.
    'ELB_NAME_PATTERN_OPTIONS': [],
    }

site_config = dict(DEFAULT_SITE_CONFIG)

for config_path in [
        os.path.join(x, site_config_filename) for x in site_config_locations
        ]:  # pylint: disable=bad-continuation
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as fptr:
                site_config = yaml.load(fptr)
        except (IOError, yaml.parser.ParserError) as err:
            logger.error('unable to parse {}'.format(config_path))
            raise err

for attr_name in DEFAULT_SITE_CONFIG:
    vars()[attr_name] = site_config[attr_name]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
SG_NAME_FIELDS = [
    'genus', 'stack_suffix', 'sg_service_name', 'version', 'environment',
    ]

EC2_NAME_FIELDS = [
    'environment', 'service_name', 'service_version',
    ]

ELB_NAME_FIELDS = [
    'environment', 'genus', 'stack_suffix',
    ]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def informer_site_init(informer):
    '''Add site specific supplementals to AWSInformer instances.

    Arguments:

        informer (AWSInformer):
             The informer being initialized.

    This is called as the last step of informer instance
    initialization, so all common ``AWSInformer`` data is available in
    ``informer``.

    '''

    # Note that the boogio classes will not be defined when this code
    # executes, so we can't extend class methods.

    _informer_common_site_init(informer)

    # Dispatch based on informer class.
    # Update for new AWSInformer subclass.
    informer_class_site_init_dispatch = {
        'ELBInformer': _elb_informer_site_init,
        'EMRInformer': _emr_informer_site_init,
        'EC2InstanceInformer': _ec2instance_informer_site_init,
        'SecurityGroupInformer': _securitygroup_informer_site_init,
        'VPCInformer': _vpc_informer_site_init,
        'VpcPeeringConnectionInformer': (
            _vpcpeeringconnection_informer_site_init
            ),
        'NatGatewayInformer': _nat_gateway_informer_init,
        'AutoScalingGroupInformer': _autoscalinggroup_informer_site_init,
        'SubnetInformer': _subnet_informer_site_init,
        'NetworkInterfaceInformer': _networkinterface_informer_site_init,
        'NetworkAclInformer': _networkacl_informer_site_init,
        'RouteTableInformer': _routetable_informer_site_init,
        'EIPInformer': _eip_informer_site_init,
        'SQSInformer': _sqs_informer_site_init,
        'IAMInformer': _iam_informer_site_init,
        }

    class_name = informer.__class__.__name__
    if class_name in informer_class_site_init_dispatch:
        informer_class_site_init_dispatch[class_name](informer)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _informer_common_site_init(informer):
    '''Common site supplementals for all informer types.'''
    informer.supplementals['site-specific'] = {}


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _elb_informer_site_init(informer):
    '''Add site supplementals to a ELBInformer.'''

    set_elb_informer_name_supplementals(informer)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _emr_informer_site_init(informer):
    '''Add site supplementals to a EMRInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _ec2instance_informer_site_init(informer):
    '''Add site supplementals to a EC2InstanceInformer.'''

    set_ec2_informer_name_supplementals(informer)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _securitygroup_informer_site_init(informer):
    '''Add site supplementals to a SecurityGroupInformer.'''

    set_sg_informer_name_supplementals(informer)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _vpc_informer_site_init(informer):
    '''Add site supplementals to a VPCInformer.'''
    # print "Hello world! I'm a %s" % informer.__class__.__name__


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _vpcpeeringconnection_informer_site_init(informer):
    '''Add site supplementals to a VpcPeeringConnectionInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _nat_gateway_informer_init(informer):
    '''Add site supplementals to a NatGatewayInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _autoscalinggroup_informer_site_init(informer):
    '''Add site supplementals to a AutoScalingGroupInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _subnet_informer_site_init(informer):
    '''Add site supplementals to a SubnetInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _networkinterface_informer_site_init(informer):
    '''Add site supplementals to a NetworkInterfaceInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _networkacl_informer_site_init(informer):
    '''Add site supplementals to a NetworkAclInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _routetable_informer_site_init(informer):
    '''Add site supplementals to a RouteTableInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _eip_informer_site_init(informer):
    '''Add site supplementals to a EIPInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _sqs_informer_site_init(informer):
    '''Add site supplementals to a SQSInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _iam_informer_site_init(informer):
    '''Add site supplementals to a IAMInformer.'''


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
#     All top level symbols above this point must be left unchanged,
#     although their values can be changed as noted in each case.
#
#     Add any local customizations below this point.
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Below this point: Functions called automatically by the
# _entity_type_site_init methods.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def set_ec2_informer_keyname_environment(informer):
    '''Set an "environment" site specific supplemental for an ec2 informer.'''

    # Note: for the environment consistency check, make sure that
    # set_ec2_informer_name_supplementals() ran first.

    logger = logging.getLogger(__name__)

    site_specific = informer.supplementals['site-specific']
    environment = 'unknown'

    if (
            'KeyName' in informer.resource and
            informer.resource['KeyName'][:len('oncue')] == 'oncue'
            ):  # pylint: disable=bad-continuation

        environment = informer.resource['KeyName'].lstrip('oncue')

        site_environment = site_specific.get('environment')
        if (site_environment and site_environment != environment):
            err_msg = (
                'EC2 informer %s: environment is ambiguous'
                ' (keyname environment is %s, Tags:name environment is %s)'
                )
            logger.info(
                err_msg, informer.identifier, environment,
                site_specific['environment']
                )

    # The KeyName environment is definitive.
    site_specific['environment'] = environment


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def set_ec2_informer_name_supplementals(informer):
    '''Do name analysis and populate supplementals.'''

    site_specific = informer.supplementals['site-specific']
    for field in EC2_NAME_FIELDS:
        site_specific[field] = ''

    if 'Tags' not in informer.resource:
        return

    tagdict = {
        x['Key']: x['Value'] for x in informer.resource['Tags']
        }

    appname = tagdict.get('AppName') or ''
    site_specific['service_name'] = appname

    appversion = tagdict.get('AppVersion')
    site_specific['service_version'] = appversion

    name = tagdict.get('Name')
    # print "HELLO!"
    # exit()

    if name:

        for pattern in site_config['EC2_NAME_PATTERN_OPTIONS']:
            match = re.match(pattern, name)
            if match:
                break
        if not match:
            return

        for field in EC2_NAME_FIELDS:
            if match.group(field) and not site_specific[field]:
                site_specific[field] = match.group(field)

    # Having a common 'genus' field is useful, if somewhat ad-hoc.
    site_specific['genus'] = site_specific['service_name']

    # Note: for the environment consistency check, make sure that
    # this comes after the name check.
    set_ec2_informer_keyname_environment(informer)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def set_sg_informer_name_supplementals(informer):
    '''Do name analysis and populate supplementals.'''

    site_specific = informer.supplementals['site-specific']
    for field in SG_NAME_FIELDS:
        site_specific[field] = ''

    # genus is one of the SG_NAME_FIELDS, canonical_name is not.
    site_specific['genus'] = informer.resource['GroupName']
    site_specific['canonical_name'] = site_specific['genus']

    assert 'GroupName' in informer.resource
    name = informer.resource['GroupName']

    for pattern in site_config['SG_NAME_PATTERN_OPTIONS']:
        match = re.match(pattern, name)
        if match:
            break
    if not match:
        return

    for field in SG_NAME_FIELDS:
        if match.group(field):
            site_specific[field] = match.group(field)

    site_specific['canonical_name'] = '-'.join(
        [
            x for x in [
                site_specific['sg_service_name'],
                site_specific['genus']
                ]
            if x
            ]
        )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def set_elb_informer_name_supplementals(informer):
    '''Do name analysis and populate supplementals.'''

    site_specific = informer.supplementals['site-specific']
    for field in ELB_NAME_FIELDS:
        site_specific[field] = ''

    assert 'LoadBalancerName' in informer.resource
    name = informer.resource['LoadBalancerName']

    for pattern in site_config['ELB_NAME_PATTERN_OPTIONS']:
        match = re.match(pattern, name)
        if match:
            break
    if not match:
        return

    for field in ELB_NAME_FIELDS:
        if match.group(field):
            site_specific[field] = match.group(field)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Below this point: Functions available to call on demand.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def set_elb_informer_instances_keyname_environments(informer):
    '''Set the "instance_environments" supplemental for an elb informer.

    This requires that ec2 instances have already been loaded.
    '''
    logger = logging.getLogger(__name__)

    # If the mediator hasn't loaded EC2 instances yet, this method
    # should not have been called.
    if informer.mediator._services['ec2'] is None:
        err_msg = (
            'elb  %s informer: keyname environments called before'
            ' fetching ec2 instances'
            )
        logger.error(err_msg, informer.identifier)
        raise RuntimeError(err_msg % informer.identifier)

    informer_cache = informer.mediator.informer_cache

    informer_instance_environments = set([])
    supplementals = informer.supplementals

    for instance_id in [
            x['InstanceId'] for x in informer.resource['Instances']
            ]:  # pylint: disable=bad-continuation
        if instance_id not in informer_cache:
            err_msg = (
                'InstanceID %s assigned to informer %s not found in'
                ' AWSMediator informer cache'
                )
            logger.warning(
                err_msg, instance_id, informer.resource['LoadBalancerName']
                )
            continue
        ec2_informer = informer_cache[instance_id]
        instance_environment = ec2_informer.supplementals['site-specific'].get(
            'environment'
            )
        if instance_environment:
            informer_instance_environments.add(instance_environment)

    # This is calculated from the ELB name at __init__() time.
    site_environment = supplementals['site-specific'].get('environment')
    if (site_environment):
        if (informer_instance_environments != set([site_environment])):
            article = 'an'
            if (site_environment not in informer_instance_environments):
                article = 'any'
            err_msg = (
                'ELB informer %s: environment "%s" doesn\'t match'
                ' %s instance environment in instance_environments %s'
                )
            logger.warning(
                err_msg, informer.identifier, site_environment,
                article, informer_instance_environments
                )

    informer.supplementals['instance_environments'] = list(
        informer_instance_environments
        )
