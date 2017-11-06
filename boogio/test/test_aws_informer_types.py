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

'''Test cases for the aws_informer individual entity type informers.

Note: Due to informer caching in mediators, which was not supported
when this test file was originally created, some of the tests here
behave slightly differently when their informers are cached. As this
depends on the order of test case execution it may not be obvious
when this is occuring. Rather than slow these tests down by flushing
the cache all the time, it's preferable to accept the behavior as is
in this test file and add more careful tests elsewhere if needed.

'''

import unittest

from boogio import aws_informer
from boogio import site_boogio

# Sharing this will mean reducing fetch time when the same resources are needed
# in multiple test cases.
GLOBAL_MEDIATOR = aws_informer.AWSMediator(
    region_name=site_boogio.test_region_name,
    profile_name=site_boogio.test_profile_name
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestELBInformer(unittest.TestCase):
    '''Basic test cases for ELBInformer.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        # cls.elb_resource = [
        #     elb for elb in GLOBAL_MEDIATOR.entities('elb')
        #     if (len(elb['SecurityGroups']) > 0) and (elb.vpc_id is not None)
        #     ][0]
        cls.elb_resource = [
            elb for elb in GLOBAL_MEDIATOR.entities('elb')
            if (
                len(elb['SecurityGroups']) > 0 and
                len(elb['Subnets']) > 0 and
                len(elb['Instances']) > 0
                )
            ][0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_elb_informer_init(self):
        '''Test initialization of elb informers.'''

        informer = aws_informer.ELBInformer(
            self.elb_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'elb')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['LoadBalancerName']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.ELBInformer(
            self.elb_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_elb_informer_expand(self):
        '''Test expansion of elb informers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.ELBInformer(
            self.elb_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})
        self.assertFalse(informer.is_expanded)

        informer.expand()

        self.assertTrue(informer.is_expanded)

        # Confirming that cached informers don't get re-initialized.
        # We don't test this for all classes, just once here.
        informer2 = aws_informer.ELBInformer(
            self.elb_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2.is_expanded)

        for key in informer.expansions:
            self.assertIn(key, informer.resource)

        # - - - - - - - - - - - - - - - - - - - -
        # Security Group resources.
        # - - - - - - - - - - - - - - - - - - - -

        self.assertIn('SecurityGroups', informer.expansions)
        self.assertEqual(
            len(informer.expansions['SecurityGroups']),
            len(informer.resource['SecurityGroups'])
            )

        # We need to have retrieved some security groups for the rest
        # of the tests in this section to make sense.
        self.assertTrue(len(informer.expansions['SecurityGroups']) > 0)
        self.assertTrue(isinstance(
            informer.expansions['SecurityGroups'][0],
            aws_informer.SecurityGroupInformer
            ))
        self.assertIs(
            informer.expansions['SecurityGroups'][0].mediator,
            informer.mediator
            )
        self.assertTrue(
            True in [
                sg.is_expanded
                for sg in informer.expansions['SecurityGroups']
                ]
            )
        self.assertTrue(
            False not in [
                sg.is_expanded
                for sg in informer.expansions['SecurityGroups']
                ]
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Make sure we get as many entities in the expanded
        # informer's to_dict() as we have in the basic resource.
        # - - - - - - - - - - - - - - - - - - - -
        self.assertTrue(informer.is_expanded)

        self.assertEqual(
            len(informer.resource['SecurityGroups']),
            len(informer.to_dict()['SecurityGroups'])
            )

        self.assertEqual(
            len(informer.resource['Subnets']),
            len(informer.to_dict()['Subnets'])
            )

        self.assertEqual(
            len(informer.resource['Instances']),
            len(informer.to_dict()['Instances'])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_elb_informer_supplementals(self):
        '''Test supplemental data of elb informers.'''

        informer = aws_informer.ELBInformer(
            self.elb_resource,
            mediator=GLOBAL_MEDIATOR
            )

        informer.expand()

        self.assertIn('DNSIpAddress', informer.supplementals)
        self.assertIn('DNSIpAddress', informer.to_dict())

        self.assertIn('INET', informer.supplementals['DNSIpAddress'])
        self.assertIn('INET', informer.to_dict()['DNSIpAddress'])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestEC2InstanceInformer(unittest.TestCase):
    '''Basic test cases for EC2InstanceInformer.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.ec2_resource = [
            ec2 for ec2 in GLOBAL_MEDIATOR.entities('ec2')
            if (len(ec2['SecurityGroups']) > 0)
            ][0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_ec2instance_informer_init(self):
        '''Test initialization of ec2 informers.'''

        informer = aws_informer.EC2InstanceInformer(
            self.ec2_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'ec2')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['InstanceId']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.EC2InstanceInformer(
            self.ec2_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_ec2instance_informer_output(self):
        '''Test handling of ec2 informer output structure manipulation.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_ec2instance_informer_expand(self):
        '''Test expansion of ec2 informers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.EC2InstanceInformer(
            self.ec2_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        self.assertTrue(informer.is_expanded)

        for key in informer.expansions:
            self.assertIn(key, informer.resource)

        # - - - - - - - - - - - - - - - - - - - -
        # Security Group resources.
        # - - - - - - - - - - - - - - - - - - - -

        self.assertIn('SecurityGroups', informer.expansions)
        self.assertEqual(
            len(informer.expansions['SecurityGroups']),
            len(informer.resource['SecurityGroups'])
            )

        # We need to have retrieved some security groups for the rest
        # of the tests in this section to make sense.
        self.assertTrue(len(informer.expansions['SecurityGroups']) > 0)
        self.assertTrue(isinstance(
            informer.expansions['SecurityGroups'][0],
            aws_informer.SecurityGroupInformer
            ))
        self.assertIs(
            informer.expansions['SecurityGroups'][0].mediator,
            informer.mediator
            )
        self.assertTrue(
            True in [
                sg.is_expanded
                for sg in informer.expansions['SecurityGroups']
                ]
            )
        self.assertTrue(
            False not in [
                sg.is_expanded
                for sg in informer.expansions['SecurityGroups']
                ]
            )

        # # - - - - - - - - - - - - - - - - - - - -
        # # VPC resources.
        # # - - - - - - - - - - - - - - - - - - - -

        # self.assertIn('vpc_id', informer.expansions)

        # self.assertTrue(isinstance(
        #     informer.expansions['vpc_id'],
        #     aws_informer.VPCInformer
        #     ))
        # self.assertIs(
        #     informer.expansions['vpc_id'].mediator,
        #     informer.mediator
        #     )
        # self.assertTrue(informer.expansions['vpc_id'].is_expanded)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestEMRInformer(unittest.TestCase):
    '''Basic test cases for EMRInformer.'''

    emr_entities = [
        emr for emr in GLOBAL_MEDIATOR.entities('emr')
        ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.emr_resource = None
        if cls.emr_entities:
            cls.emr_resource = cls.emr_entities[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @unittest.skipUnless(emr_entities, 'No EMR resources found')
    def test_emr_informer_init(self):
        '''Test initialization of emr informers.'''

        informer = aws_informer.EMRInformer(
            self.emr_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'emr')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['Id']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.EMRInformer(
            self.emr_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @unittest.skipUnless(emr_entities, 'No EMR resources found')
    def test_emr_informer_expand(self):
        '''Test expansion of emr informers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.EMRInformer(
            self.emr_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})
        emr_resource_keys = informer.resource.keys()

        informer.expand()

        self.assertTrue(informer.is_expanded)

        for key in informer.expansions:
            self.assertIn(key, informer.resource)

        for key in emr_resource_keys:
            self.assertIn(key, informer.resource)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @unittest.skipUnless(emr_entities, 'No EMR resources found')
    def test_emr_informer_supplementals(self):
        '''Test supplemental data of emr informers.'''

        informer = aws_informer.EMRInformer(
            self.emr_resource,
            mediator=GLOBAL_MEDIATOR
            )

        informer.expand()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestSecurityGroupInformer(unittest.TestCase):
    '''Basic test cases for SecurityGroupInformer.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.sg_resource = [
            sg for sg in GLOBAL_MEDIATOR.entities('security_group')
            if len(sg['IpPermissions']) > 1
            ][0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_sg_informer_init(self):
        '''Test initialization of security group informers.'''

        informer = aws_informer.SecurityGroupInformer(
            self.sg_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'security_group')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['GroupId']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.SecurityGroupInformer(
            self.sg_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_sg_informer_expand(self):
        '''Test expansion of security groupinformers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.SecurityGroupInformer(
            self.sg_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)

        # - - - - - - - - - - - - - - - - - - - -
        # IpPermissions.
        # - - - - - - - - - - - - - - - - - - - -

        # self.assertIn('IpPermissions', informer.expansions)
        # self.assertEqual(
        #     len(informer.expansions['IpPermissions']),
        #     len(informer.resource['IpPermissions'])
        #     )

        # self.assertIn('IpPermissionsEgress', informer.expansions)
        # self.assertEqual(
        #     len(informer.expansions['IpPermissionsEgress']),
        #     len(informer.resource['IpPermissionsEgress'])
        #     )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestVPCInformer(unittest.TestCase):
    '''Basic test cases for VPCInformer.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.vpc_resource = GLOBAL_MEDIATOR.entities('vpc')[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_vpc_informer_init(self):
        '''Test initialization of vpc informers.'''

        informer = aws_informer.VPCInformer(
            self.vpc_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'vpc')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['VpcId']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.VPCInformer(
            self.vpc_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_vpc_informer_expand(self):
        '''Test expansion of vpc informers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.VPCInformer(
            self.vpc_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestVpcPeeringConnectionInformer(unittest.TestCase):
    '''Basic test cases for VpcPeeringConnectionInformer.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.vpc_peering_connection_resource = (
            GLOBAL_MEDIATOR.entities('vpc_peering_connection')[0]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_vpc_peering_connection_informer_init(self):
        '''Test initialization of vpc informers.'''

        informer = aws_informer.VpcPeeringConnectionInformer(
            self.vpc_peering_connection_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'vpc_peering_connection')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['VpcPeeringConnectionId']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.VpcPeeringConnectionInformer(
            self.vpc_peering_connection_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_vpc_peering_connection_informer_expand(self):
        '''Test expansion of VPC Peering Connection informers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.VpcPeeringConnectionInformer(
            self.vpc_peering_connection_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestRouteTableInformer(unittest.TestCase):
    '''Basic test cases for RouteTableInformer.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.route_table_resource = (
            GLOBAL_MEDIATOR.entities('route_table')[0]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_route_table_informer_init(self):
        '''Test initialization of vpc informers.'''

        informer = aws_informer.RouteTableInformer(
            self.route_table_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'route_table')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['RouteTableId']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.RouteTableInformer(
            self.route_table_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_route_table_informer_expand(self):
        '''Test expansion of Route Table informers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.RouteTableInformer(
            self.route_table_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestInternetGatewayInformer(unittest.TestCase):
    '''Basic test cases for InternetGatewayInformer.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.internet_gateway_resource = (
            GLOBAL_MEDIATOR.entities('internet_gateway')[0]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_internet_gateway_informer_init(self):
        '''Test initialization of Internet Gateway informers.'''

        informer = aws_informer.InternetGatewayInformer(
            self.internet_gateway_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'internet_gateway')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['InternetGatewayId']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.InternetGatewayInformer(
            self.internet_gateway_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_internet_gateway_informer_expand(self):
        '''Test expansion of Internet Gateway informers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.InternetGatewayInformer(
            self.internet_gateway_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestNatGatewayInformer(unittest.TestCase):
    '''Basic test cases for NatGatewayInformer.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.nat_gateway_resource = (
            GLOBAL_MEDIATOR.entities('nat_gateway')[0]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_nat_gateway_informer_init(self):
        '''Test initialization of NAT Gateway informers.'''

        informer = aws_informer.NatGatewayInformer(
            self.nat_gateway_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'nat_gateway')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['NatGatewayId']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.NatGatewayInformer(
            self.nat_gateway_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_nat_gateway_informer_expand(self):
        '''Test expansion of NAT Gateway informers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.NatGatewayInformer(
            self.nat_gateway_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAutoScalingGroupInformer(unittest.TestCase):
    '''Basic test cases for AutoScalingGroupInformer.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.as_resource = GLOBAL_MEDIATOR.entities('autoscaling')[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_auto_scaling_group_informer_init(self):
        '''Test initialization of auto_scaling_group informers.'''

        informer = aws_informer.AutoScalingGroupInformer(
            self.as_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'autoscaling')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['AutoScalingGroupARN']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.AutoScalingGroupInformer(
            self.as_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_auto_scaling_group_informer_expand(self):
        '''Test expansion of auto_scaling_groupinformers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.AutoScalingGroupInformer(
            self.as_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestSubnetInformer(unittest.TestCase):
    '''Basic test cases for SubnetInformer.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.sn_resource = GLOBAL_MEDIATOR.entities('subnet')[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_subnet_informer_init(self):
        '''Test initialization of subnet informers.'''

        informer = aws_informer.SubnetInformer(
            self.sn_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'subnet')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['SubnetId']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.SubnetInformer(
            self.sn_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_subnet_informer_expand(self):
        '''Test expansion of subnet informers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.SubnetInformer(
            self.sn_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# #
# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# class TestIpPermissionsInformer(unittest.TestCase):
#     '''
#     Basic test cases for IpPermissionsInformer.
#     '''

#     # Some of the test case function names get pretty long.
#     # pylint: disable=invalid-name

#     # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     @classmethod
#     def setUpClass(cls):
'''Test class level common fixture.'''

#         cls.sg_resource = [
#             sg for sg in GLOBAL_MEDIATOR.entities('security_group')
#             if len(sg['IpPermissions']) > 0
#             ][0]
#         cls.ip_permissions_resource = cls.sg_resource['IpPermissions'][0]

#     # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     def test_ip_permissions_informer_init(self):
#         '''
#         Test initialization of ip_permissions informers.
#         '''

#         informer = aws_informer.IpPermissionsInformer(
#             self.ip_permissions_resource,
#             mediator=GLOBAL_MEDIATOR
#             )
#         self.assertIsNotNone(informer)
#         self.assertIsNotNone(informer.mediator)
#         self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
#         self.assertEqual(informer.entity_type, 'ip_permissions')

#         self.assertIsNotNone(informer.region_name)
#         self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

#     # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     def test_ip_permissions_informer_expand(self):
#         '''
#         Test expansion of
#         ip_permissions informers.
#         '''

#         informer = aws_informer.IpPermissionsInformer(
#             self.ip_permissions_resource,
#             mediator=GLOBAL_MEDIATOR
#             )

#         self.assertEqual(informer.expansions, {})

#         informer.expand()

#         for key in informer.expansions:
#             self.assertIn(key, informer.resource)

#         # - - - - - - - - - - - - - - - - - - - -
#         # Grants.
#         # - - - - - - - - - - - - - - - - - - - -

#         # self.assertIn('grants', informer.expansions)
#         # self.assertEqual(
#         #     len(informer.expansions['grants']),
#         #     len(informer.resource.grants)
#         #     )
#         # self.assertTrue(
#         #     isinstance(
#         #         informer.expansions['grants'][0],
#         #         aws_informer.GroupOrCIDRInformer
#         #         )
#         #     )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestNetworkInterfaceInformer(unittest.TestCase):
    '''Basic test cases for NetworkInterfaceInformer.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.ec2_resource = [
            ec2 for ec2 in GLOBAL_MEDIATOR.entities('ec2')
            if len(ec2['NetworkInterfaces']) > 0
            ][0]
        cls.network_interface_resource = cls.ec2_resource[
            'NetworkInterfaces'
            ][0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_network_interface_informer_init(self):
        '''Test initialization of network_interface informers.'''

        informer = aws_informer.NetworkInterfaceInformer(
            self.network_interface_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'network_interface')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['NetworkInterfaceId']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.NetworkInterfaceInformer(
            self.network_interface_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_network_interface_informer_expand(self):
        '''Test expansion of network_interfaceinformers.'''

        informer = aws_informer.NetworkInterfaceInformer(
            self.network_interface_resource,
            mediator=GLOBAL_MEDIATOR
            )

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestNetworkAclInformer(unittest.TestCase):
    '''Basic test cases for NetworkAclInformer.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.network_acl_resource = [
            nacl for nacl in GLOBAL_MEDIATOR.entities('network_acl')
            if len(nacl['Associations']) > 0
            ][0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_network_acl_informer_init(self):
        '''Test initialization of network_acl informers.'''

        informer = aws_informer.NetworkAclInformer(
            self.network_acl_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'network_acl')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['NetworkAclId']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.NetworkAclInformer(
            self.network_acl_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_network_acl_informer_expand(self):
        '''Test expansion of network_aclinformers.'''

        informer = aws_informer.NetworkAclInformer(
            self.network_acl_resource,
            mediator=GLOBAL_MEDIATOR
            )

        informer.expand()

        for key in informer.expansions:
            self.assertIn(
                key,
                informer.resource.keys() + ['AssociatedSubnets']
                )

        self.assertIn('AssociatedSubnets', informer.expansions)

        associated_subnet_ids = [
            subnet_informer.resource['SubnetId']
            for subnet_informer in informer.expansions['AssociatedSubnets']
            ]

        for association in informer.resource['Associations']:
            subnet_id = association['SubnetId']
            self.assertIn(subnet_id, associated_subnet_ids)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestEIPInformer(unittest.TestCase):
    '''Basic test cases for EIPInformer.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.eip_resource = GLOBAL_MEDIATOR.entities('eip')[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_eip_informer_init(self):
        '''Test initialization of eip informers.'''

        informer = aws_informer.EIPInformer(
            self.eip_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'eip')

        self.assertIsNotNone(informer.region_name)
        self.assertEqual(informer.region_name, GLOBAL_MEDIATOR.region_name)

        self.assertEqual(
            informer.identifier,
            informer.resource['PublicIp']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.EIPInformer(
            self.eip_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_eip_informer_expand(self):
        '''Test expansion of eipinformers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.EIPInformer(
            self.eip_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestSQSInformer(unittest.TestCase):
    '''Basic test cases for SQSInformer.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.sqs_resource = GLOBAL_MEDIATOR.entities('sqs')[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_sqs_informer_init(self):
        '''Test initialization of sqs informers.'''

        informer = aws_informer.SQSInformer(
            self.sqs_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'sqs')

        self.assertEqual(informer.region_name, 'us-east-1')

        self.assertEqual(
            informer.identifier,
            informer.resource['QueueURL']
            )
        self.assertIn(
            informer.identifier,
            informer.mediator.informer_cache.keys()
            )

        # Let's make sure informer caching works. We shouldn't add any
        # new cache entries if we create another informer for this
        # resource - it should be re-used.
        informer_cache_length = len(informer.mediator.informer_cache)
        informer2 = aws_informer.SQSInformer(
            self.sqs_resource,
            mediator=GLOBAL_MEDIATOR
            )
        self.assertTrue(informer2 is informer)
        self.assertEqual(
            len(informer.mediator.informer_cache),
            informer_cache_length
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_sqs_informer_expand(self):
        '''Test expansion of sqsinformers.'''

        GLOBAL_MEDIATOR.flush()
        informer = aws_informer.SQSInformer(
            self.sqs_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_sqs_informer_policy_regions(self):
        '''Test retrieving regions from the SQS Informer Policy Statement.'''

        informer = aws_informer.SQSInformer(
            self.sqs_resource,
            mediator=GLOBAL_MEDIATOR
            )
        # region_list = informer.policy_regions()
        # self.assertTrue(isinstance(region_list, list))


if __name__ == '__main__':
    unittest.main()
