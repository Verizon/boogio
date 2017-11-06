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

'''Test site-specific code for customization of boogio entities.'''

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
# Uncomment to show lower level logging statements.
# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# shandler = logging.StreamHandler()
# shandler.setLevel(logging.INFO)  # Pick one.
# shandler.setLevel(logging.DEBUG)  # Pick one.
# logger.addHandler(shandler)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestSiteBoogio(unittest.TestCase):
    '''Basic test cases for aws_informer site_boogio interaction.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case common fixture setup.'''
        pass
        # self.original_sys_path = list(sys.path)
        # sys.path[:0] = self.tmpdir

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def tearDown(self):
        '''Test case common fixture removal.'''
        pass
        # sys.path = list(self.original_sys_path)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_site_boogio_imported(self):
        '''Test import of site_boogio and use with boogio entities.'''

        self.assertIn('site_boogio', dir(aws_informer))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_ec2_informer_site_init(self):
        '''Test EC2 informer site customizations.'''

        # - - - - - - - - - - - - - - - -
        # Test set_ec2_informer_keyname_environment().
        # - - - - - - - - - - - - - - - -
        ec2_entities_with_keyname = [
            x for x in GLOBAL_MEDIATOR.entities('ec2')
            if (
                'KeyName' in x and
                x['KeyName'][:len('oncue')] == 'oncue'
                )
            ]

        if not ec2_entities_with_keyname:
            raise RuntimeError('no EC2 entities with an oncue KeyName')

        ec2_keyname_resource = ec2_entities_with_keyname[0]
        keyname_informer = aws_informer.EC2InstanceInformer(
            ec2_keyname_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertIn('site-specific', keyname_informer.supplementals)
        self.assertIn('environment', keyname_informer.supplementals['site-specific'])

        # - - - - - - - - - - - - - - - -
        # Test set_ec2_informer_name_supplementals().
        # - - - - - - - - - - - - - - - -
        ec2_entities_with_tags_name = [
            x for x in GLOBAL_MEDIATOR.entities('ec2')
            if (
                'Tags' in x and
                'Name' in [t['Key'] for t in x['Tags']]
                )
            ]

        if not ec2_entities_with_tags_name:
            raise RuntimeError('no EC2 entities with a KeyName')

        ec2_tags_name_resource = ec2_entities_with_tags_name[0]
        tags_name_informer = aws_informer.EC2InstanceInformer(
            ec2_tags_name_resource,
            mediator=GLOBAL_MEDIATOR
            )
        for field in site_boogio.EC2_NAME_FIELDS:
            self.assertIn(field, tags_name_informer.supplementals['site-specific'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_sg_informer_site_init(self):
        '''Test Security Group informer site customizations.'''

        # - - - - - - - - - - - - - - - -
        # Test set_sg_informer_name_supplementals().
        # - - - - - - - - - - - - - - - -
        sg_resource = GLOBAL_MEDIATOR.entities('security_group')[0]
        sg_informer = aws_informer.SecurityGroupInformer(
            sg_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertIn('site-specific', sg_informer.supplementals)
        for field in site_boogio.SG_NAME_FIELDS:
            self.assertIn(field, sg_informer.supplementals['site-specific'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_elb_informer_site_init(self):
        '''Test Load Balancer informer site customizations.'''

        # - - - - - - - - - - - - - - - -
        # Test set_elb_informer_name_supplementals().
        # - - - - - - - - - - - - - - - -
        elb_resource = GLOBAL_MEDIATOR.entities('elb')[0]
        elb_informer = aws_informer.ELBInformer(
            elb_resource,
            mediator=GLOBAL_MEDIATOR
            )

        self.assertIn('site-specific', elb_informer.supplementals)
        for field in site_boogio.ELB_NAME_FIELDS:
            self.assertIn(field, elb_informer.supplementals['site-specific'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_set_elb_informer_instances_keyname_environments(self):
        '''Test ELB assigned EC2 environment supplementals.'''

        mediator = aws_informer.AWSMediator(
            region_name=site_boogio.test_region_name,
            profile_name=site_boogio.test_profile_name
            )
        mediator.flush()
        self.assertEqual(mediator.informer_cache, {})

        elb_resource = mediator.entities('elb')[0]
        elb_informer = aws_informer.ELBInformer(
            elb_resource,
            mediator=mediator
            )

        # Without EC2 entities already fetched, this fails.
        with self.assertRaises(RuntimeError):
            site_boogio.set_elb_informer_instances_keyname_environments(
                elb_informer
                )

        # Now fetch EC2 entities.
        self.assertTrue(len(mediator.entities('ec2')) > 0)
        site_boogio.set_elb_informer_instances_keyname_environments(
            elb_informer
            )
        self.assertIn('instance_environments', elb_informer.supplementals)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Define test suite.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# pylint: disable=invalid-name
load_case = unittest.TestLoader().loadTestsFromTestCase
all_suites = {
    # Lowercase these.
    'suite_TestSiteBoogio': load_case(TestSiteBoogio),
    }

master_suite = unittest.TestSuite(all_suites.values())
# pylint: enable=invalid-name

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    unittest.main()
