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

'''Test cases for aws_informer AWSMediator resource and informer caching.'''

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
def cached_type(entity_type):
    '''Return a list of cached entities of the indicated type.'''
    return [
        i for i in GLOBAL_MEDIATOR.informer_cache.values()
        if i.entity_type == entity_type
        ]


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestInformerCaching(unittest.TestCase):
    '''
    Test cases for informer caching and cache flushing.

    1. Load entities and create informers.
    2. Make sure caches are just as long as informers.
    3. Flush various entity types, make sure caches clear.
    4. Reload entity types, make sure caches reload.
    5. Expand entity types, make sure existing type caches don't change.

    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def setUp(self):
        '''Test case common fixture setup.'''

        # Security group and vpc are in mediator._other_entities.
        # EC2 and ELB are in mediator._services.

        GLOBAL_MEDIATOR.flush()
        self.ec2_resources = [
            ec2 for ec2 in GLOBAL_MEDIATOR.entities('ec2')
            ]

        self.elb_resources = [
            elb for elb in GLOBAL_MEDIATOR.entities('elb')
            ]

        self.vpc_resources = [
            vpc for vpc in GLOBAL_MEDIATOR.entities('vpc')
            ]

        self.sg_resources = [
            sg for sg in GLOBAL_MEDIATOR.entities('security_group')
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_elb_informer_caching(self):
        '''Test informer caching.'''

        # pylint: disable=protected-access

        self.assertEqual(GLOBAL_MEDIATOR.informer_cache, {})

        # - - - - - - - - - - - - - - - - - - - -

        ec2_informers = [
            aws_informer.EC2InstanceInformer(
                ec2_resource, mediator=GLOBAL_MEDIATOR
                )
            for ec2_resource in self.ec2_resources
            ]
        ec2_informers_cached = cached_type('ec2')

        # - - - - - - - - - - - - - - - - - - - -

        elb_informers = [
            aws_informer.ELBInformer(
                elb_resource, mediator=GLOBAL_MEDIATOR
                )
            for elb_resource in self.elb_resources
            ]
        elb_informers_cached = cached_type('elb')

        # - - - - - - - - - - - - - - - - - - - -

        vpc_informers = [
            aws_informer.VPCInformer(
                vpc_resource, mediator=GLOBAL_MEDIATOR
                )
            for vpc_resource in self.vpc_resources
            ]
        vpc_informers_cached = cached_type('vpc')

        # - - - - - - - - - - - - - - - - - - - -

        sg_informers = [
            aws_informer.SecurityGroupInformer(
                sg_resource, mediator=GLOBAL_MEDIATOR
                )
            for sg_resource in self.sg_resources
            ]
        sg_informers_cached = cached_type('security_group')

        # - - - - - - - - - - - - - - - - - - - -

        self.assertTrue(len(ec2_informers_cached) > 0)
        self.assertEqual(
            len(ec2_informers), len(ec2_informers_cached)
            )

        self.assertTrue(len(elb_informers_cached) > 0)
        self.assertEqual(
            len(elb_informers), len(elb_informers_cached)
            )

        self.assertTrue(len(vpc_informers_cached) > 0)
        self.assertEqual(
            len(vpc_informers), len(vpc_informers_cached)
            )

        self.assertTrue(len(sg_informers_cached) > 0)
        self.assertEqual(
            len(sg_informers), len(sg_informers_cached)
            )

        # - - - - - - - - - - - - - - - - - - - -

        GLOBAL_MEDIATOR.flush('vpc')

        ec2_informers_cached = cached_type('ec2')
        elb_informers_cached = cached_type('elb')
        vpc_informers_cached = cached_type('vpc')
        sg_informers_cached = cached_type('security_group')

        self.assertTrue(len(vpc_informers_cached) == 0)
        self.assertIsNone(GLOBAL_MEDIATOR._other_entities['vpc'])

        # There may be some unselected entities, so >=, not ==.
        self.assertEqual(len(ec2_informers), len(ec2_informers_cached))
        self.assertTrue(
            len(GLOBAL_MEDIATOR._services['ec2']) >= len(ec2_informers)
            )

        self.assertEqual(len(elb_informers), len(elb_informers_cached))
        self.assertTrue(
            len(GLOBAL_MEDIATOR._services['elb']) >= len(elb_informers)
            )

        self.assertEqual(len(sg_informers), len(sg_informers_cached))
        self.assertTrue(
            len(
                GLOBAL_MEDIATOR._other_entities['security_group']
                ) >= len(sg_informers)
            )

        # - - - - - - - - - - - - - - - - - - - -

        GLOBAL_MEDIATOR.flush('ec2', 'security_group')

        ec2_informers_cached = cached_type('ec2')
        elb_informers_cached = cached_type('elb')
        vpc_informers_cached = cached_type('vpc')
        sg_informers_cached = cached_type('security_group')

        self.assertTrue(len(ec2_informers_cached) == 0)
        self.assertIsNone(GLOBAL_MEDIATOR._services['ec2'])

        self.assertTrue(len(vpc_informers_cached) == 0)
        self.assertIsNone(GLOBAL_MEDIATOR._other_entities['vpc'])

        self.assertTrue(len(sg_informers_cached) == 0)
        self.assertIsNone(GLOBAL_MEDIATOR._other_entities['security_group'])

        # There may be some unselected entities, so >=, not ==.
        self.assertEqual(len(elb_informers), len(elb_informers_cached))
        self.assertTrue(
            len(GLOBAL_MEDIATOR._services['elb']) >= len(elb_informers)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_elb_informer_caching_with_expansion(self):
        '''Test expansion of informers with caching.'''

        # pylint: disable=protected-access

        # - - - - - - - - - - - - - - - - - - - -

        ec2_informers_count = len([
            aws_informer.EC2InstanceInformer(
                ec2_resource, mediator=GLOBAL_MEDIATOR
                )
            for ec2_resource in self.ec2_resources
            ])
        ec2_informers_cached_count = len(cached_type('ec2'))

        # - - - - - - - - - - - - - - - - - - - -

        elb_informers_count = len([
            aws_informer.ELBInformer(
                elb_resource, mediator=GLOBAL_MEDIATOR
                )
            for elb_resource in self.elb_resources
            ])
        elb_informers_cached_count = len(cached_type('elb'))

        # - - - - - - - - - - - - - - - - - - - -

        vpc_informers_count = len([
            aws_informer.VPCInformer(
                vpc_resource, mediator=GLOBAL_MEDIATOR
                )
            for vpc_resource in self.vpc_resources
            ])
        vpc_informers_cached_count = len(cached_type('vpc'))

        # - - - - - - - - - - - - - - - - - - - -

        sg_informers_count = len([
            aws_informer.SecurityGroupInformer(
                sg_resource, mediator=GLOBAL_MEDIATOR
                )
            for sg_resource in self.sg_resources
            ])
        sg_informers_cached_count = len(cached_type('security_group'))

        # - - - - - - - - - - - - - - - - - - - -

        self.assertTrue(ec2_informers_cached_count > 0)
        self.assertEqual(ec2_informers_count, ec2_informers_cached_count)

        self.assertTrue(elb_informers_cached_count > 0)
        self.assertEqual(elb_informers_count, elb_informers_cached_count)

        self.assertTrue(vpc_informers_cached_count > 0)
        self.assertEqual(vpc_informers_count, vpc_informers_cached_count)

        self.assertTrue(sg_informers_cached_count > 0)
        self.assertEqual(sg_informers_count, sg_informers_cached_count)

        # - - - - - - - - - - - - - - - - - - - -

        for informer in GLOBAL_MEDIATOR.informer_cache.values():
            informer.expand()

        new_ec2_informers_cached_count = len(cached_type('ec2'))
        new_elb_informers_cached_count = len(cached_type('elb'))
        new_vpc_informers_cached_count = len(cached_type('vpc'))
        new_sg_informers_cached_count = len(cached_type('security_group'))

        self.assertEqual(
            new_ec2_informers_cached_count,
            ec2_informers_cached_count
            )
        self.assertEqual(
            new_elb_informers_cached_count,
            elb_informers_cached_count
            )
        self.assertEqual(
            new_vpc_informers_cached_count,
            vpc_informers_cached_count
            )
        self.assertEqual(
            new_sg_informers_cached_count,
            sg_informers_cached_count
            )


if __name__ == '__main__':
    unittest.main()
