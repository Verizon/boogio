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

'''Test cases for the aws_informer.py AWSSession classes.'''

import unittest

import boto3

from boogio import aws_informer
from boogio import site_boogio


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSSession(unittest.TestCase):
    '''Basic test cases for AWSSession.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case common fixture setup.'''
        self.boto3_session = boto3.session.Session()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_session_init(self):
        '''Test initialization of aws connectors.'''

        # - - - - - - - - - - - - - - - - - -
        session = aws_informer.AWSSession(
            region_name=site_boogio.test_region_name
            )
        self.assertIsNotNone(session)

        # - - - - - - - - - - - - - - - - - -
        session = aws_informer.AWSSession(
            profile_name=site_boogio.test_profile_name
            )
        self.assertIsNotNone(session)

        # - - - - - - - - - - - - - - - - - -
        session = aws_informer.AWSSession(
            region_name=site_boogio.test_region_name,
            profile_name=site_boogio.test_profile_name
            )
        self.assertIsNotNone(session)

        # - - - - - - - - - - - - - - - - - -
        session = aws_informer.AWSSession(
            session=self.boto3_session
            )
        self.assertIsNotNone(session)

        # - - - - - - - - - - - - - - - - - -
        with self.assertRaises(ValueError):
            session = aws_informer.AWSSession(
                region_name=site_boogio.test_region_name,
                session=self.boto3_session
                )
            session = aws_informer.AWSSession(
                profile_name=site_boogio.test_profile_name,
                session=self.boto3_session
                )
            session = aws_informer.AWSSession(
                region_name=site_boogio.test_region_name,
                profile_name=site_boogio.test_profile_name,
                session=self.boto3_session
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSMediator(unittest.TestCase):
    '''Basic test cases for AWSMediator.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case common fixture setup.'''
        self.boto3_session = boto3.session.Session()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_init(self):
        '''Test initialization of aws mediators.'''

        # - - - - - - - - - - - - - - - - - -
        mediator = aws_informer.AWSMediator(
            region_name=site_boogio.test_region_name
            )
        self.assertIsNotNone(mediator)
        self.assertIsNotNone(mediator.account_id)

        # - - - - - - - - - - - - - - - - - -
        mediator = aws_informer.AWSMediator(
            profile_name=site_boogio.test_profile_name
            )
        self.assertIsNotNone(mediator)
        self.assertIsNotNone(mediator.account_id)

        # - - - - - - - - - - - - - - - - - -
        mediator = aws_informer.AWSMediator(
            region_name=site_boogio.test_region_name,
            profile_name=site_boogio.test_profile_name
            )
        self.assertIsNotNone(mediator)
        self.assertIsNotNone(mediator.account_id)

        # - - - - - - - - - - - - - - - - - -
        mediator = aws_informer.AWSMediator(
            session=self.boto3_session
            )
        self.assertIsNotNone(mediator)
        self.assertIsNotNone(mediator.account_id)

        # - - - - - - - - - - - - - - - - - -
        # Errors due to assigning region/profile/session incompatibly.
        with self.assertRaises(ValueError):
            mediator = aws_informer.AWSMediator(
                region_name=site_boogio.test_region_name,
                session=self.boto3_session
                )
        with self.assertRaises(ValueError):
            mediator = aws_informer.AWSMediator(
                profile_name=site_boogio.test_profile_name,
                session=self.boto3_session
                )
        with self.assertRaises(ValueError):
            mediator = aws_informer.AWSMediator(
                region_name=site_boogio.test_region_name,
                profile_name=site_boogio.test_profile_name,
                session=self.boto3_session
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSMediatorFlush(unittest.TestCase):
    '''Basic test cases for AWSMediator flush().'''

    # pylint: disable=protected-access, invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # This can be a class method, as we'll make sure we have it in the
    # right state in each test case.
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.mediator = aws_informer.AWSMediator(
            region_name=site_boogio.test_region_name,
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case common fixture setup.'''

        self.assertIsNotNone(self.mediator.services('ec2'))
        self.assertIsNotNone(self.mediator.entities('eip'))
        self.assertIsNotNone(self.mediator.entities('subnet'))

        self.assertEqual(self.mediator.informer_cache, {})

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_flush_1(self):
        '''Test flushing a single informer entity type.'''

        # Make sure the "raw" internal list has been populated.
        self.assertIsNotNone(self.mediator._services['ec2'])
        self.assertIsNotNone(self.mediator._other_entities['eip'])
        self.assertIsNotNone(self.mediator._other_entities['subnet'])

        # Flush 'em.
        self.mediator.flush('eip')

        # This was flushed.
        self.assertIsNone(self.mediator._other_entities['eip'])

        # These weren't flushed.
        self.assertIsNotNone(self.mediator._services['ec2'])
        self.assertIsNotNone(self.mediator._other_entities['subnet'])
        self.assertEqual(self.mediator.informer_cache, {})

        # Reload.
        self.assertIsNotNone(self.mediator.entities('eip'))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_flush_2(self):
        '''Test flushing multiple informer entity types.'''

        # Make sure the "raw" internal list has been populated.
        self.assertIsNotNone(self.mediator._services['ec2'])
        self.assertIsNotNone(self.mediator._other_entities['eip'])
        self.assertIsNotNone(self.mediator._other_entities['subnet'])

        # Flush 'em.
        self.mediator.flush('eip', 'subnet')

        # These were flushed.
        self.assertIsNone(self.mediator._other_entities['eip'])
        self.assertIsNone(self.mediator._other_entities['subnet'])

        # This wasn't flushed.
        self.assertIsNotNone(self.mediator._services['ec2'])
        self.assertEqual(self.mediator.informer_cache, {})

        # Reload.
        self.assertIsNotNone(self.mediator.entities('eip'))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_flush_all(self):
        '''Test flushing all informer entity types.'''

        # Make sure the "raw" internal list has been populated.
        self.assertIsNotNone(self.mediator._services['ec2'])
        self.assertIsNotNone(self.mediator._other_entities['eip'])
        self.assertIsNotNone(self.mediator._other_entities['subnet'])

        # Flush 'em.
        self.mediator.flush()

        # These were flushed.
        self.assertIsNone(self.mediator._services['ec2'])
        self.assertIsNone(self.mediator._other_entities['eip'])
        self.assertIsNone(self.mediator._other_entities['subnet'])

        # WE DIDN"T RELOAD, SO IF YOU EXTEND THIS CASE MAKE SURE YOU DO SO.


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSMediatorFilters(unittest.TestCase):
    '''Basic test cases for AWSMediator filter setting.'''

    # pylint: disable=invalid-name, protected-access

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_add_filters(self):
        '''Test aws_mediator.add_filters().'''

        mediator = aws_informer.AWSMediator(
            region_name=site_boogio.test_region_name,
            profile_name=site_boogio.test_profile_name
            )

        self.assertEqual(mediator.filters, {})

        # - - - - - - - - - - - -
        # Adding a single filter value to one entity type.
        # - - - - - - - - - - - -
        mediator.add_filters(
            'eip',
            {'public-ip': ['123.45.67.89']}
            )
        expected_values = ['123.45.67.89']

        self.assertItemsEqual(mediator.filters.keys(), ['eip'])

        self.assertItemsEqual(
            mediator.filters['eip'].keys(),
            ['public-ip']
            )

        self.assertItemsEqual(
            mediator.filters['eip']['public-ip'],
            expected_values
            )

        self.assertEqual(
            mediator._filters_kwarg('eip')['Filters'],
            [{'Name': 'public-ip', 'Values': expected_values}]
            )

        # - - - - - - - - - - - -
        # Adding a second filter value.
        # - - - - - - - - - - - -
        mediator.add_filters(
            'eip',
            {'public-ip': ['56.78.91.234']}
            )
        expected_values = ['123.45.67.89', '56.78.91.234']

        self.assertItemsEqual(mediator.filters.keys(), ['eip'])

        self.assertItemsEqual(
            mediator.filters['eip'].keys(),
            ['public-ip']
            )

        self.assertItemsEqual(
            mediator.filters['eip']['public-ip'],
            expected_values
            )

        # - - - - - - - - - - - -
        # Adding a duplicate filter value.
        # - - - - - - - - - - - -
        mediator.add_filters(
            'eip',
            {'public-ip': ['56.78.91.234']}
            )

        self.assertItemsEqual(mediator.filters.keys(), ['eip'])

        self.assertItemsEqual(
            mediator.filters['eip'].keys(),
            ['public-ip']
            )

        self.assertItemsEqual(
            mediator.filters['eip']['public-ip'],
            ['123.45.67.89', '56.78.91.234']
            )
        self.assertEqual(
            len(mediator.filters['eip']['public-ip']),
            len(['123.45.67.89', '56.78.91.234'])
            )

        # - - - - - - - - - - - -
        # Adding a second entity type.
        # - - - - - - - - - - - -
        mediator.add_filters(
            'ec2',
            {'instance-state-name': ['running']}
            )

        self.assertItemsEqual(mediator.filters.keys(), ['eip', 'ec2'])

        # eip filters
        self.assertItemsEqual(
            mediator.filters['eip'].keys(),
            ['public-ip']
            )

        self.assertItemsEqual(
            mediator.filters['eip']['public-ip'],
            ['123.45.67.89', '56.78.91.234']
            )

        # ec2 filters
        self.assertItemsEqual(
            mediator.filters['ec2'].keys(),
            ['instance-state-name']
            )

        self.assertItemsEqual(
            mediator.filters['ec2']['instance-state-name'],
            ['running']
            )

        # - - - - - - - - - - - -
        # Adding a second filter field name.
        # - - - - - - - - - - - -
        mediator.add_filters(
            'eip',
            {'domain': ['vpc']}
            )

        self.assertItemsEqual(mediator.filters.keys(), ['eip', 'ec2'])

        # eip filters
        self.assertItemsEqual(
            mediator.filters['eip'].keys(),
            ['public-ip', 'domain']
            )

        self.assertItemsEqual(
            mediator.filters['eip']['public-ip'],
            ['123.45.67.89', '56.78.91.234']
            )

        self.assertItemsEqual(
            mediator.filters['eip']['domain'],
            ['vpc']
            )

        # ec2 filters
        self.assertItemsEqual(
            mediator.filters['ec2']['instance-state-name'],
            ['running']
            )

        # Check _filters_kwarg()
        eip_filters_kwarg = mediator._filters_kwarg('eip')['Filters']

        self.assertEqual(
            len(eip_filters_kwarg),
            2
            )

        self.assertItemsEqual(
            [f['Name'] for f in eip_filters_kwarg],
            ['public-ip', 'domain']
            )

        eip_public_ip_filter = [
            f for f in eip_filters_kwarg if f['Name'] == 'public-ip'
            ][0]

        self.assertItemsEqual(
            eip_public_ip_filter['Values'],
            ['123.45.67.89', '56.78.91.234']
            )

        eip_domain_filter = [
            f for f in eip_filters_kwarg if f['Name'] == 'domain'
            ][0]

        self.assertItemsEqual(
            eip_domain_filter['Values'],
            ['vpc']
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_filters_kwarg(self):
        '''Test aws_mediator._filters_kwarg().'''

        mediator = aws_informer.AWSMediator(
            region_name=site_boogio.test_region_name,
            profile_name=site_boogio.test_profile_name
            )

        # - - - - - - - - - - - -
        # No filters defined for entity type.
        # - - - - - - - - - - - -
        self.assertEqual(
            mediator._filters_kwarg('eip'),
            {'Filters': []}
            )

        # - - - - - - - - - - - -
        # Single filter key for entity type.
        # - - - - - - - - - - - -
        mediator.add_filters('eip', {'public-ip': ['123.45.67.89']})
        mediator.add_filters('eip', {'public-ip': ['56.78.91.234']})
        eip_expected_values = ['123.45.67.89', '56.78.91.234']

        self.assertEqual(
            mediator._filters_kwarg('eip', use_filters=False),
            {'Filters': []}
            )

        self.assertEqual(len(mediator._filters_kwarg('eip')['Filters']), 1)

        self.assertEqual(
            mediator._filters_kwarg('eip')['Filters'][0]['Name'],
            'public-ip'
            )

        self.assertItemsEqual(
            mediator._filters_kwarg('eip')['Filters'][0]['Values'],
            eip_expected_values
            )

        # - - - - - - - - - - - -
        # Multiple filter keys for entity type.
        # - - - - - - - - - - - -
        mediator.add_filters('eip', {'domain': ['vpc']})
        domain_expected_values = ['vpc']

        self.assertEqual(
            mediator._filters_kwarg('eip', use_filters=False),
            {'Filters': []}
            )

        eip_filters_kwarg = mediator._filters_kwarg('eip')['Filters']

        self.assertEqual(len(eip_filters_kwarg), 2)

        self.assertItemsEqual(
            [f['Name'] for f in eip_filters_kwarg],
            ['public-ip', 'domain']
            )

        eip_public_ip_filter = [
            f for f in eip_filters_kwarg if f['Name'] == 'public-ip'
            ][0]

        self.assertItemsEqual(
            eip_public_ip_filter['Values'],
            eip_expected_values
            )

        eip_domain_filter = [
            f for f in eip_filters_kwarg if f['Name'] == 'domain'
            ][0]

        self.assertItemsEqual(
            eip_domain_filter['Values'],
            domain_expected_values
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_remove_all_filters(self):
        '''Test aws_mediator_remove_all_filters().'''

        mediator = aws_informer.AWSMediator(
            region_name=site_boogio.test_region_name,
            profile_name=site_boogio.test_profile_name
            )

        self.assertEqual(mediator.filters, {})

        # - - - - - - - - - - - -
        # Remove all filters.
        # - - - - - - - - - - - -

        mediator.add_filters('eip', {'public-ip': ['123.45.67.89']})

        self.assertEqual(
            mediator.filters,
            {'eip': {'public-ip': ['123.45.67.89']}}
            )

        mediator.remove_all_filters()

        self.assertEqual(mediator.filters, {})

        # - - - - - - - - - - - -
        # Remove all entity type filters.
        # - - - - - - - - - - - -

        mediator.add_filters('ec2', {'instance-state-name': ['running']})
        mediator.add_filters('eip', {'domain': ['vpc']})
        mediator.add_filters('eip', {'public-ip': ['123.45.67.89']})
        self.assertItemsEqual(mediator.filters.keys(), ['eip', 'ec2'])

        mediator.remove_all_filters('ec2')

        self.assertItemsEqual(mediator.filters.keys(), ['eip'])

        # - - - - - - - - - - - -

        mediator.add_filters('ec2', {'instance-state-name': ['running']})
        self.assertItemsEqual(mediator.filters.keys(), ['eip', 'ec2'])

        mediator.remove_all_filters('eip')

        self.assertItemsEqual(mediator.filters.keys(), ['ec2'])

        # - - - - - - - - - - - -

        mediator.add_filters('eip', {'domain': ['vpc']})
        mediator.add_filters('eip', {'public-ip': ['123.45.67.89']})
        self.assertItemsEqual(mediator.filters.keys(), ['eip', 'ec2'])

        mediator.remove_all_filters('eip', 'ec2')

        self.assertEqual(mediator.filters, {})

        # - - - - - - - - - - - -
        # Remove non-existent entity type filters.
        # - - - - - - - - - - - -

        mediator.add_filters('ec2', {'instance-state-name': ['running']})
        mediator.add_filters('eip', {'domain': ['vpc']})
        mediator.add_filters('eip', {'public-ip': ['123.45.67.89']})
        self.assertItemsEqual(mediator.filters.keys(), ['eip', 'ec2'])

        mediator.remove_all_filters('s3')

        self.assertItemsEqual(mediator.filters.keys(), ['eip', 'ec2'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_use_filters(self):
        '''Test aws_mediator_entity filtered entity retrieval.'''

        mediator = aws_informer.AWSMediator(
            region_name=site_boogio.test_region_name,
            profile_name=site_boogio.test_profile_name
            )

        # Pull a set of elastic IPs and get a couple of values.
        entities = mediator.entities('eip')

        all_ips = [e['PublicIp'] for e in entities]

        # If this isn't true we won't really be testing what this
        # case is intended to test.
        self.assertTrue(len(all_ips) > 3)

        mediator.flush()

        selected_ips = all_ips[:3]

        mediator.add_filters(
            'eip', {'public-ip': selected_ips})

        some_entities = mediator.entities('eip')

        self.assertEqual(len(some_entities), len(selected_ips))

        # We have to flush so we force a re-fetch.
        mediator.flush()
        all_entities = mediator.entities('eip', use_filters=False)

        self.assertEqual(len(all_entities), len(all_ips))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSMediatorProfile(unittest.TestCase):
    '''Basic test cases for AWSMediator profile setting().'''

    # pylint: disable=protected-access, invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    # This can be a class method, as we'll make sure we have it in the
    # right state in each test case.
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.mediator = aws_informer.AWSMediator(
            region_name=site_boogio.test_region_name,
            profile_name=site_boogio.test_profile_name
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case common fixture setup.'''

        self.assertIsNotNone(self.mediator.services('elb'))
        self.assertIsNotNone(self.mediator.entities('eip'))
        self.assertIsNotNone(self.mediator.entities('subnet'))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_set_profile_unchanged(self):
        '''Test that setting profile to the same value doesn't flush.'''

        # Make sure the "raw" internal list has been populated.
        self.assertIsNotNone(self.mediator._services['elb'])
        self.assertIsNotNone(self.mediator._other_entities['eip'])
        self.assertIsNotNone(self.mediator._other_entities['subnet'])

        sample_elb = self.mediator._services['elb'][0]

        # Set the profile to the same value it had initially.
        old_profile_name = self.mediator.profile_name
        self.mediator.profile_name = old_profile_name

        # Make sure the "raw" internal list WAS NOT flushed.
        self.assertIsNotNone(self.mediator._services['elb'])
        self.assertIsNotNone(self.mediator._other_entities['eip'])
        self.assertIsNotNone(self.mediator._other_entities['subnet'])

        # There's a slight chance this could spuriously fail if we
        # happen to be running in the middle of a rev.
        self.assertIn(sample_elb, self.mediator._services['elb'])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_mediator_set_profile_changed(self):
        '''Test that setting profile to a new value does flush.'''

        # Make sure the "raw" internal list has been populated.
        self.assertIsNotNone(self.mediator._services['elb'])
        self.assertIsNotNone(self.mediator._other_entities['eip'])
        self.assertIsNotNone(self.mediator._other_entities['subnet'])

        # Set the profile to a new value.
        old_profile_name = self.mediator.profile_name
        self.assertNotEqual(old_profile_name, 'default')
        self.mediator.profile_name = 'default'

        # Make sure the "raw" internal list WAS flushed.
        self.assertIsNone(self.mediator._services['elb'])
        self.assertIsNone(self.mediator._other_entities['eip'])
        self.assertIsNone(self.mediator._other_entities['subnet'])


if __name__ == '__main__':
    unittest.main()
