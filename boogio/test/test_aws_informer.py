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

'''Test cases for the aws_informer module.'''

import json
import os
import random
import tempfile

import unittest

from boogio import aws_informer
from boogio import site_boogio
from utensils import flatten

# Sharing this will mean reducing fetch time when the same resources are needed
# in multiple test cases.
GLOBAL_MEDIATOR = aws_informer.AWSMediator(
    region_name=site_boogio.test_region_name,
    profile_name=site_boogio.test_profile_name
    )

FLATTEN_COLLAPSES = (flatten.flatten({'a': {'b': {}}, 'c': 1}) == [])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSInformerModule(unittest.TestCase):
    '''Basic test cases for aws_informer module level definitions.'''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Set up temporary files/directories.'''
        cls.tmpdir = tempfile.mkdtemp()

        cls.boogio_config_filepath = os.path.join(
            cls.tmpdir, 'boogio.json'
            )

        config_data = {
            'common': {},
            'aws_informer': {}
            }

        with open(cls.boogio_config_filepath, 'w') as fptr:
            json.dump(config_data, fptr)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def tearDownClass(cls):
        '''Remove test files and temp directory.'''
        for root, dirs, files in os.walk(cls.tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(cls.tmpdir)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Common test setup code.'''

        # We muck with this.
        self.original_boogio_config_filepath = (
            aws_informer.BOOGIO_CONFIG_FILEPATH
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def tearDown(self):
        '''Make sure tests are properly cleaned up.'''
        aws_informer.BOOGIO_CONFIG_FILEPATH = (
            self.original_boogio_config_filepath
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_boogio_config_path(self):
        '''Test cases for boogio config path module variables.'''

        # pylint: disable=protected-access

        self.assertEqual(
            aws_informer.BOOGIO_CONFIG_FILENAME,
            aws_informer._DEFAULT_BOOGIO_CONFIG_FILENAME
            )

        self.assertEqual(
            'boogio.json',
            aws_informer.BOOGIO_CONFIG_FILENAME
            )

        self.assertEqual(
            aws_informer.BOOGIO_CONFIG_FILEPATH,
            aws_informer._DEFAULT_BOOGIO_CONFIG_FILEPATH
            )

        self.assertIn(
            'boogio.json',
            aws_informer.BOOGIO_CONFIG_FILEPATH
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_load_boogio_config(self):
        '''Test the load_boogio_config() method.'''

        # pylint: disable=protected-access

        config_data = aws_informer._load_boogio_config()

        self.assertIsNotNone(config_data)
        self.assertEqual(type(config_data), dict)

        # - - - - - - - - - - - - - - - -

        # This is in setUp, but to be extra careful...
        original_boogio_config_filepath = aws_informer.BOOGIO_CONFIG_FILEPATH

        aws_informer.BOOGIO_CONFIG_FILEPATH = self.boogio_config_filepath
        config_data = aws_informer._load_boogio_config()

        self.assertIn('common', config_data)
        self.assertIn('aws_informer', config_data)

        # This is in setUp, but to be extra careful...
        aws_informer.BOOGIO_CONFIG_FILEPATH = original_boogio_config_filepath

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_informer_class_map(self):
        '''Test cases for aws_informer.informer_class_map().'''

        # pylint: disable=protected-access

        # All of the values in the informer class map are some subclass
        # of AWSInformer.
        values = aws_informer._entity_type_informer_class_map().values()

        for value in values:
            self.assertEqual(
                value.__bases__[0],
                aws_informer.AWSInformer
                )

        aws_informer_subclasses = []
        for item in dir(aws_informer):

            if not hasattr(getattr(aws_informer, item), '__bases__'):
                continue

            if aws_informer.AWSInformer in getattr(
                    aws_informer, item
                    ).__bases__:  # pylint: disable=bad-continuation
                aws_informer_subclasses.append(getattr(aws_informer, item))

        self.assertItemsEqual(
            aws_informer._entity_type_informer_class_map().values(),
            aws_informer_subclasses
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_entity_types(self):
        '''Test cases for aws_informer.entity_types().'''

        # A perfunctory check for some obvious types.
        entity_types = aws_informer.entity_types()

        self.assertIn('ec2', entity_types)
        self.assertIn('elb', entity_types)
        self.assertIn('iam', entity_types)
        self.assertIn('vpc', entity_types)
        self.assertIn('subnet', entity_types)
        self.assertIn('sqs', entity_types)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_informer_class(self):
        '''Test cases for aws_informer.informer_class().'''

        self.assertIsNone(
            aws_informer.informer_entity_type('AWSInformer'),
            None
            )

        self.assertIsNone(
            aws_informer.informer_entity_type('EC2InstanceInformer'),
            'ec2'
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_informer_entity_type(self):
        '''Test cases for aws_informer.informer_class().'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_region_type_classifications(self):
        '''Test cases for aws_informer.regional_types().'''

        entity_types = aws_informer.entity_types()

        regional_types = aws_informer.regional_types()
        regionless_types = aws_informer.regionless_types()
        unitary_types = aws_informer.unitary_types()

        # Nothing missing.
        self.assertItemsEqual(
            regional_types + regionless_types + unitary_types,
            entity_types
            )

        # No overlap.
        self.assertEqual(
            set(regional_types).intersection(set(regionless_types)),
            set([])
            )
        self.assertEqual(
            set(regional_types).intersection(set(unitary_types)),
            set([])
            )
        self.assertEqual(
            set(regionless_types).intersection(set(unitary_types)),
            set([])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_rekey(self):
        '''Test cases for aws_informer.rekey().'''
        old_map = {
            'key_a': 'value_a',
            'key_b': 'value_b',
            }

        new_key_map_a = {'key_a': 'new_key_a'}
        new_key_map_ab = {'key_a': 'new_key_a', 'key_b': 'new_key_b'}
        new_key_map_clobber = {'key_a': 'key_b'}
        new_key_map_nochange = {'key_y': 'key_b'}

        working_map = dict(old_map)
        aws_informer.rekey(working_map, new_key_map_a)
        self.assertEqual(
            working_map,
            {'new_key_a': 'value_a', 'key_b': 'value_b'}
            )

        working_map = dict(old_map)
        aws_informer.rekey(working_map, new_key_map_ab)
        self.assertEqual(
            working_map,
            {'new_key_a': 'value_a', 'new_key_b': 'value_b'}
            )

        working_map = dict(old_map)
        aws_informer.rekey(working_map, new_key_map_nochange)
        self.assertEqual(
            working_map,
            old_map
            )

        working_map = dict(old_map)
        with self.assertRaises(KeyError):
            aws_informer.rekey(working_map, new_key_map_clobber)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSInformerInit(unittest.TestCase):
    '''Basic test cases for AWSInformer initialization.'''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.ec2_resource = GLOBAL_MEDIATOR.entities('ec2')[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_init_errors(self):
        '''Test AWSInformer initialization errors.'''

        with self.assertRaises(TypeError):
            # Omitting all parameters.
            # pylint: disable=no-value-for-parameter
            aws_informer.AWSInformer()

        with self.assertRaises(TypeError):
            # Omitting resource.
            # pylint: disable=no-value-for-parameter
            aws_informer.AWSInformer(region_name='us-east-1')

        with self.assertRaises(TypeError):
            # pylint: disable=no-value-for-parameter
            aws_informer.AWSInformer(mediator=GLOBAL_MEDIATOR)

        with self.assertRaises(TypeError):
            # pylint: disable=no-value-for-parameter
            aws_informer.AWSInformer(
                region_name='us-east-1',
                mediator=GLOBAL_MEDIATOR
                )

        with self.assertRaises(aws_informer.AWSInformerRegionError):
            aws_informer.AWSInformer(
                '_',
                region_name='us-west-1',
                mediator=GLOBAL_MEDIATOR
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_init(self):
        '''Test initialization of aws informers.'''

        informer = aws_informer.AWSInformer(
            self.ec2_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertEqual(informer.expansions, {})
        self.assertFalse(informer.is_expanded)
        self.assertIsNone(informer.entity_type)

        self.assertEqual(type(informer.supplementals), dict)
        self.assertEqual(
            informer.supplementals.keys(), ['meta', 'site-specific']
            )

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_network_interface_informer_init(self):
        '''Test network interface informer initialization.

        These have special handling for datetime conversion to string
        so that they're serializable.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        nif_resources = GLOBAL_MEDIATOR.entities('network_interface')
        attached_nifs = [
            nif for nif in nif_resources
            if 'Attachment' in nif and
            nif['Attachment']['Status'] == 'attached'
            ]
        unattached_nifs = [
            nif for nif in nif_resources
            if 'Attachment' not in nif or
            nif['Attachment']['Status'] != 'attached'
            ]

        attached_nif = attached_nifs[0]
        informer = aws_informer.NetworkInterfaceInformer(
            attached_nif,
            mediator=GLOBAL_MEDIATOR
            )

        attached_nif_a_time = informer.resource['Attachment']['AttachTime']
        self.assertTrue(isinstance(attached_nif_a_time, str))

        import datetime
        self.assertTrue(
            isinstance(informer.attach_datetime, datetime.datetime)
            )

        if len(unattached_nifs) > 0:
            unattached_nif = unattached_nifs[0]
            informer = aws_informer.NetworkInterfaceInformer(
                unattached_nif,
                mediator=GLOBAL_MEDIATOR
                )

            self.assertIsNone(informer.attach_datetime)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_vpc_informer_init(self):
        '''Test initialization of vpc informers.

        VPC informers add peering connections as a supplemental.
        '''
        vpc_resources = GLOBAL_MEDIATOR.entities('vpc')
        vpc_ids = [r['VpcId'] for r in vpc_resources]

        ec2_resource = GLOBAL_MEDIATOR.session.resource('ec2')
        pc_index = {
            vpc_id: list(
                ec2_resource.Vpc(vpc_id).accepted_vpc_peering_connections.all()
                )
            for vpc_id in vpc_ids
            }

        peered_vpc_ids = [
            vpc_id for vpc_id in pc_index
            if len(pc_index[vpc_id]) > 0
            ]
        # print len(peered_vpc_ids)
        peered_vpc_resource = [
            vpc for vpc in vpc_resources if vpc['VpcId'] in peered_vpc_ids
            ][0]

        informer = aws_informer.VPCInformer(
            peered_vpc_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertIsNotNone(informer.supplementals['VpcPeeringConnections'])
        self.assertNotEqual(
            informer.supplementals['VpcPeeringConnections'], []
            )

        # attached_nifs = [
        #     nif for nif in nif_resources
        #     if 'Attachment' in nif
        #     and nif['Attachment']['Status'] == 'attached'
        #     ]

        # informer = aws_informer.AWSInformer(
        #     self.ec2_resource,
        #     mediator=GLOBAL_MEDIATOR
        #     )

        # self.assertIsNotNone(informer)
        # self.assertIsNotNone(informer.mediator)
        # self.assertEqual(informer.expansions, {})
        # self.assertEqual(informer.supplementals, {})
        # self.assertFalse(informer.is_expanded)
        # self.assertIsNone(informer.entity_type)

        # self.assertIsNotNone(informer.region_name)
        # self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSInformerExpand(unittest.TestCase):
    '''Basic test cases for AWSInformer.expand().'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.ec2_resource = GLOBAL_MEDIATOR.entities('ec2')[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_expand(self):
        '''Test expansion of aws informers.'''

        informer = aws_informer.AWSInformer(
            self.ec2_resource,
            mediator=GLOBAL_MEDIATOR
            )

        informer.expand()

        self.assertEqual(informer.expansions, {})
        self.assertTrue(informer.is_expanded)

        self.assertEqual(type(informer.supplementals), dict)
        self.assertEqual(
            informer.supplementals.keys(), ['meta', 'site-specific']
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSInformerToDict(unittest.TestCase):
    '''Basic test cases for AWSInformer and subclasses to_dict() output.'''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_to_dict(self):
        '''Test basic to_dict output without specific resource knowledge.'''

        resource = GLOBAL_MEDIATOR.entities('elb')[0]
        informer = aws_informer.AWSInformer(
            resource,
            mediator=GLOBAL_MEDIATOR
            )

        as_dict = informer.to_dict()
        self.assertTrue(isinstance(as_dict, dict))

        informer.expand()
        as_dict = informer.to_dict()
        self.assertTrue(isinstance(as_dict, dict))

        # - - - - - - - - - - - - - - - -

        resource = GLOBAL_MEDIATOR.entities('security_group')[0]
        informer = aws_informer.AWSInformer(
            resource,
            mediator=GLOBAL_MEDIATOR
            )

        as_dict = informer.to_dict()
        self.assertTrue(isinstance(as_dict, dict))

        informer.expand()
        as_dict = informer.to_dict()
        self.assertTrue(isinstance(as_dict, dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @unittest.skipIf(
        FLATTEN_COLLAPSES,
        'If a dict contains {} as a value anywhere, flatten() collapses.'
        )
    def test_aws_informer_to_flat_dict(self):
        '''Test flat to_dict output without specific resource knowledge.'''

        resource = GLOBAL_MEDIATOR.entities('elb')[0]
        informer = aws_informer.AWSInformer(
            resource,
            mediator=GLOBAL_MEDIATOR
            )

        as_flat_dict = informer.to_dict(flat=True)
        self.assertTrue(isinstance(as_flat_dict, list))
        self.assertTrue(isinstance(as_flat_dict[0], dict))

        informer.expand()
        as_flat_dict = informer.to_dict(flat=True)
        self.assertTrue(isinstance(as_flat_dict, list))
        self.assertTrue(isinstance(as_flat_dict[0], dict))

        # - - - - - - - - - - - - - - - -

        resource = GLOBAL_MEDIATOR.entities('security_group')[0]
        informer = aws_informer.AWSInformer(
            resource,
            mediator=GLOBAL_MEDIATOR
            )

        as_flat_dict = informer.to_dict(flat=True)
        self.assertTrue(isinstance(as_flat_dict, list))
        self.assertTrue(isinstance(as_flat_dict[0], dict))

        informer.expand()
        as_flat_dict = informer.to_dict(flat=True)
        self.assertTrue(isinstance(as_flat_dict, list))
        self.assertTrue(isinstance(as_flat_dict[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_elb_informer_to_dict(self):
        '''Test elb resource to_dict output .'''

        # We don't know what a particular resource might look like, and
        # different resource configurations can hit different issues. So
        # we'll try a few and hope for the best.

        # - - - - - - - - - - - - - - - - - - - -
        resource = GLOBAL_MEDIATOR.entities('elb')[-1]
        informer = aws_informer.ELBInformer(
            resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertTrue(isinstance(informer.to_dict(), dict))
        informer.expand()
        self.assertTrue(isinstance(informer.to_dict(), dict))

        if 'Vpcs' in informer.expansions:
            self.assertEqual(
                informer.to_dict()['Vpcs'],
                informer.expansions['Vpcs'].to_dict()
                )

        # - - - - - - - - - - - - - - - - - - - -
        r_index = random.randint(1, len(GLOBAL_MEDIATOR.entities('elb')))
        resource = GLOBAL_MEDIATOR.entities('elb')[r_index]
        informer = aws_informer.ELBInformer(
            resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertTrue(isinstance(informer.to_dict(), dict))
        informer.expand()
        self.assertTrue(isinstance(informer.to_dict(), dict))

        if 'Vpcs' in informer.expansions:
            self.assertEqual(
                informer.to_dict()['Vpcs'],
                informer.expansions['Vpcs'].to_dict()
                )

        # - - - - - - - - - - - - - - - - - - - -
        r_index = random.randint(1, len(GLOBAL_MEDIATOR.entities('elb')))
        resource = GLOBAL_MEDIATOR.entities('elb')[r_index]
        informer = aws_informer.ELBInformer(
            resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertTrue(isinstance(informer.to_dict(), dict))
        informer.expand()
        self.assertTrue(isinstance(informer.to_dict(), dict))

        if 'Vpcs' in informer.expansions:
            self.assertEqual(
                informer.to_dict()['Vpcs'],
                informer.expansions['Vpcs'].to_dict()
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_network_interface_informer_to_dict(self):
        '''Test network interface informer to_dict output.

        These have special handling for datetime conversion to string
        so that they're serializable.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        nif_resources = GLOBAL_MEDIATOR.entities('network_interface')
        attached_nifs = [
            nif for nif in nif_resources
            if 'Attachment' in nif and
            nif['Attachment']['Status'] == 'attached'
            ]
        unattached_nifs = [
            nif for nif in nif_resources
            if 'Attachment' not in nif or
            nif['Attachment']['Status'] != 'attached'
            ]

        attached_nif = attached_nifs[0]
        informer = aws_informer.NetworkInterfaceInformer(
            attached_nif,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertTrue(isinstance(informer.to_dict(), dict))
        informer.expand()
        self.assertTrue(isinstance(informer.to_dict(), dict))

        attached_nif_a_time = informer.resource['Attachment']['AttachTime']
        dict_a_time = informer.to_dict()['Attachment']['AttachTime']

        self.assertEqual(attached_nif_a_time, dict_a_time)

        if len(unattached_nifs) > 0:
            unattached_nif = unattached_nifs[0]
            informer = aws_informer.NetworkInterfaceInformer(
                unattached_nif,
                mediator=GLOBAL_MEDIATOR
                )

            self.assertTrue(isinstance(informer.to_dict(), dict))
            informer.expand()
            self.assertTrue(isinstance(informer.to_dict(), dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_eip_informer_to_dict(self):
        '''Test Elastic IP informer to_dict output.

        These have informers in their supplementals.
        '''

        # - - - - - - - - - - - - - - - - - - - -
        eip_resources = GLOBAL_MEDIATOR.entities('eip')

        eip_resources_with_ec2 = [
            eip for eip in eip_resources
            if 'InstanceId' in eip and eip['InstanceId']
            ]

        eip_resource_with_ec2 = eip_resources_with_ec2[0]
        informer = aws_informer.EIPInformer(
            eip_resource_with_ec2,
            mediator=GLOBAL_MEDIATOR
            )
        informer.expand()

        ec2_informer = informer.supplementals['EC2Instance']
        ec2_record = informer.to_dict()['EC2Instance']

        self.assertTrue(
            isinstance(ec2_informer, aws_informer.EC2InstanceInformer)
            )
        self.assertTrue(isinstance(ec2_record, dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_informer_to_dict_entity_identifier(self):
        '''Test the entity_identifier option to to_dict().'''
        vpc_informers = [
            aws_informer.VPCInformer(resource, mediator=GLOBAL_MEDIATOR)
            for resource in GLOBAL_MEDIATOR.entities('vpc')
            ]
        elb_informers = [
            aws_informer.ELBInformer(resource, mediator=GLOBAL_MEDIATOR)
            for resource in GLOBAL_MEDIATOR.entities('elb')
            ]
        network_interface_informers = [
            aws_informer.NetworkInterfaceInformer(
                resource, mediator=GLOBAL_MEDIATOR
                )
            for resource in GLOBAL_MEDIATOR.entities('network_interface')
            ]
        eip_informers = [
            aws_informer.EIPInformer(resource, mediator=GLOBAL_MEDIATOR)
            for resource in GLOBAL_MEDIATOR.entities('eip')
            ]

        # - - - - - - - - - - - - - - - -
        vpc_dicts = [
            (i, i.to_dict(entity_identifier=True))
            for i in vpc_informers
            ]
        for entity, entity_dict in vpc_dicts:
            self.assertIn('entity_identifier', entity_dict)
            self.assertEqual(
                entity.identifier, entity_dict['entity_identifier']
                )
            self.assertEqual(
                dict(
                    entity.to_dict(),
                    **{'entity_identifier': entity.identifier}
                    ),
                entity_dict
                )

        # - - - - - - - - - - - - - - - -
        elb_dicts = [
            (i, i.to_dict(entity_identifier=True))
            for i in elb_informers
            ]
        for entity, entity_dict in elb_dicts:
            self.assertIn('entity_identifier', entity_dict)
            self.assertEqual(
                entity.identifier, entity_dict['entity_identifier']
                )
            self.assertEqual(
                dict(
                    entity.to_dict(),
                    **{'entity_identifier': entity.identifier}
                    ),
                entity_dict
                )

        # - - - - - - - - - - - - - - - -
        network_interface_dicts = [
            (i, i.to_dict(entity_identifier=True))
            for i in network_interface_informers
            ]
        for entity, entity_dict in network_interface_dicts:
            self.assertIn('entity_identifier', entity_dict)
            self.assertEqual(
                entity.identifier, entity_dict['entity_identifier']
                )
            self.assertEqual(
                dict(
                    entity.to_dict(),
                    **{'entity_identifier': entity.identifier}
                    ),
                entity_dict
                )

        # - - - - - - - - - - - - - - - -
        eip_dicts = [
            (i, i.to_dict(entity_identifier=True))
            for i in eip_informers
            ]
        for entity, entity_dict in eip_dicts:
            self.assertIn('entity_identifier', entity_dict)
            self.assertEqual(
                entity.identifier, entity_dict['entity_identifier']
                )
            self.assertEqual(
                dict(
                    entity.to_dict(),
                    **{'entity_identifier': entity.identifier}
                    ),
                entity_dict
                )


if __name__ == '__main__':
    unittest.main()
