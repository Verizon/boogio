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

These test cases are very slow, so are isolated in their own file.
'''

import os
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
@unittest.skipIf(
    not os.environ.get('RUN_SLOW_IAM_TESTS'),
    (
        'Enable IAM tests by setting environment variable'
        ' RUN_SLOW_IAM_TESTS to a truthy value.'
        )
    )
class TestIAMInformer(unittest.TestCase):
    '''Basic test cases for IAMInformer.

    IAMInformers have no resource, and store all their data in their
    supplementals. Typically only one IAMInformer need be instantiated
    for a given environment.
    '''

    # # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # @classmethod
    # def setUpClass(cls):
    #     # cls.iam_resource = GLOBAL_MEDIATOR.entities('iam')[0]

    # TODO: Add skiptest based on os.environ['TEST_DURATION_LIMIT']

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_iam_informer_init(self):
        '''Test initialization of iam informers.'''
        # - - - - - - - - - - - - - - - - - - - - - -
        informer = aws_informer.IAMInformer(
            mediator=GLOBAL_MEDIATOR,
            record_types=[]
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))
        self.assertEqual(informer.entity_type, 'iam')

        self.assertEqual(informer.supplementals.keys(), ['meta'])

        self.assertIsNone(informer.region_name)

        # - - - - - - - - - - - - - - - - - - - - - -
        informer = aws_informer.IAMInformer(
            mediator=GLOBAL_MEDIATOR,
            record_types=['AccountAliases']
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))

        self.assertIn('AccountAliases', informer.supplementals)

        # - - - - - - - - - - - - - - - - - - - - - -
        informer = aws_informer.IAMInformer(
            mediator=GLOBAL_MEDIATOR,
            record_types=['Certificates', 'SSHPublicKeys']
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))

        self.assertIn('Certificates', informer.supplementals)
        self.assertIn('SSHPublicKeys', informer.supplementals)

        # - - - - - - - - - - - - - - - - - - - - - -
        informer = aws_informer.IAMInformer(
            mediator=GLOBAL_MEDIATOR
            )
        self.assertIsNotNone(informer)
        self.assertIsNotNone(informer.mediator)
        self.assertTrue(isinstance(informer, aws_informer.AWSInformer))

        self.assertIn('AccountAliases', informer.supplementals)
        self.assertIn('Groups', informer.supplementals)
        self.assertIn('InstanceProfiles', informer.supplementals)
        self.assertIn('MFADevices', informer.supplementals)
        self.assertIn('OpenIDConnectProviderList', informer.supplementals)
        self.assertIn('Policies', informer.supplementals)
        self.assertIn('Roles', informer.supplementals)
        self.assertIn('SAMLProviderList', informer.supplementals)
        self.assertIn('ServerCertificateMetadataList', informer.supplementals)
        # print informer.supplementals
        self.assertIn('Certificates', informer.supplementals)
        self.assertIn('SSHPublicKeys', informer.supplementals)
        self.assertIn('Users', informer.supplementals)
        self.assertIn('VirtualMFADevices', informer.supplementals)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_iam_informer_expand(self):
        '''Test expansion (fetching child resources) of iam informers.'''

        informer = aws_informer.IAMInformer(
            mediator=GLOBAL_MEDIATOR
            )

        self.assertEqual(informer.expansions, {})

        informer.expand()

        for key in informer.expansions:
            self.assertIn(key, informer.resource)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_iam_informer_to_dict(self):
        '''Test basic to_dict() call for iam informers.

        This gets targeted treatment here because IAMInformers have a
        different approach to their resources.
        '''

        informer = aws_informer.IAMInformer(
            mediator=GLOBAL_MEDIATOR
            )

        self.assertTrue(isinstance(informer.to_dict(), dict))


if __name__ == '__main__':
    unittest.main()
