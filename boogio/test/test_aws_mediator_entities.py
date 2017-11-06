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

'''Test cases for aws_informer.py AWSMediator entities.'''

import unittest

from boogio import aws_informer
from boogio import site_boogio


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSMediatorEntities(unittest.TestCase):
    '''Basic test cases for AWSMediator.'''

    # pylint: disable=protected-access, invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test class level common fixture.'''

        self.mediator = aws_informer.AWSMediator(
            profile_name=site_boogio.test_profile_name,
            region_name=site_boogio.test_region_name
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Service entities.
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_ec2_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # ec2
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._services['ec2'])
        self.assertIsNotNone(self.mediator.services('ec2'))
        self.assertNotEqual(len(self.mediator.services('ec2')), 0)
        self.assertEqual(
            len(self.mediator.services('ec2')),
            len(self.mediator.entities('ec2'))
            )
        self.assertTrue(isinstance(self.mediator.services('ec2')[0], dict))

        self.mediator.flush('ec2')
        self.assertIsNone(self.mediator._services['ec2'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_s3_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # s3
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._services['s3'])
        self.assertIsNotNone(self.mediator.services('s3'))
        self.assertNotEqual(len(self.mediator.services('s3')), 0)
        self.assertEqual(
            len(self.mediator.services('s3')),
            len(self.mediator.entities('s3'))
            )
        self.assertTrue(isinstance(self.mediator.services('s3')[0], dict))

        self.mediator.flush('s3')
        self.assertIsNone(self.mediator._services['s3'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_elb_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # elb
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._services['elb'])
        self.assertIsNotNone(self.mediator.services('elb'))
        self.assertNotEqual(len(self.mediator.services('elb')), 0)
        self.assertEqual(
            len(self.mediator.services('elb')),
            len(self.mediator.entities('elb'))
            )
        self.assertTrue(isinstance(self.mediator.services('elb')[0], dict))

        self.mediator.flush('elb')
        self.assertIsNone(self.mediator._services['elb'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @unittest.skip('emr not in use')
    def test_aws_mediator_emr_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # emr
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._services['emr'])
        self.assertIsNotNone(self.mediator.services('emr'))
        self.assertNotEqual(len(self.mediator.services('emr')), 0)
        self.assertEqual(
            len(self.mediator.services('emr')),
            len(self.mediator.entities('emr'))
            )
        self.assertTrue(isinstance(self.mediator.services('emr')[0], dict))

        self.mediator.flush('emr')
        self.assertIsNone(self.mediator._services['emr'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_iam_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # iam
        #
        # This has no service instances.
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._services['iam'])
        self.assertEqual(self.mediator.services('iam'), [])
        self.assertEqual(self.mediator.entities('iam'), [])
        # self.assertNotEqual(len(self.mediator.services('iam')), 0)
        # self.assertEqual(
        #     len(self.mediator.services('iam')),
        #     len(self.mediator.entities('iam'))
        #     )
        # self.assertTrue(isinstance(self.mediator.services('iam')[0], dict))

        self.mediator.flush('iam')
        self.assertIsNone(self.mediator._services['iam'])
        self.assertEqual(self.mediator.services('iam'), [])
        self.assertEqual(self.mediator.entities('iam'), [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Other entities.
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_security_group_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # security group
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._other_entities['security_group'])
        self.assertIsNotNone(self.mediator.entities('security_group'))
        self.assertNotEqual(len(self.mediator.entities('security_group')), 0)
        self.assertTrue(
            isinstance(self.mediator.entities('security_group')[0], dict)
            )

        self.mediator.flush('security_group')
        self.assertIsNone(self.mediator._other_entities['security_group'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_vpc_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # vpc
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._other_entities['vpc'])
        self.assertIsNotNone(self.mediator.entities('vpc'))
        self.assertNotEqual(len(self.mediator.entities('vpc')), 0)
        self.assertTrue(
            isinstance(self.mediator.entities('vpc')[0], dict)
            )

        self.mediator.flush('vpc')
        self.assertIsNone(self.mediator._other_entities['vpc'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_subnet_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # subnet
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._other_entities['subnet'])
        self.assertIsNotNone(self.mediator.entities('subnet'))
        self.assertNotEqual(len(self.mediator.entities('subnet')), 0)
        self.assertTrue(
            isinstance(self.mediator.entities('subnet')[0], dict)
            )

        self.mediator.flush('subnet')
        self.assertIsNone(self.mediator._other_entities['subnet'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_network_interface_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # network_interface
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._other_entities['network_interface'])
        self.assertIsNotNone(self.mediator.entities('network_interface'))
        self.assertNotEqual(
            len(self.mediator.entities('network_interface')), 0
            )
        self.assertTrue(
            isinstance(self.mediator.entities('network_interface')[0], dict)
            )

        self.mediator.flush('network_interface')
        self.assertIsNone(self.mediator._other_entities['network_interface'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_eip_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # eip
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._other_entities['eip'])
        self.assertIsNotNone(self.mediator.entities('eip'))
        self.assertNotEqual(
            len(self.mediator.entities('eip')), 0
            )
        self.assertTrue(
            isinstance(self.mediator.entities('eip')[0], dict)
            )

        self.mediator.flush('eip')
        self.assertIsNone(self.mediator._other_entities['eip'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_sqs_entities(self):
        '''Test aws mediator entity retrieval.'''

        self.assertIsNotNone(self.mediator)

        # - - - - - - - - - - - - - - - - - -
        # sqs
        # - - - - - - - - - - - - - - - - - -
        self.assertIsNone(self.mediator._services['sqs'])
        self.assertIsNotNone(self.mediator.services('sqs'))
        self.assertIsNotNone(self.mediator.entities('sqs'))
        self.assertNotEqual(
            len(self.mediator.entities('sqs')), 0
            )
        self.assertTrue(
            isinstance(self.mediator.entities('sqs')[0], dict)
            )

        self.mediator.flush('sqs')
        self.assertIsNone(self.mediator._services['sqs'])


if __name__ == '__main__':
    unittest.main()
