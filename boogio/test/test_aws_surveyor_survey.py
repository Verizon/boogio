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


'''Test cases for the aws_surveyor.AWSSurveyor.survey() method.

This also covers other methods that work with populated informer
records.
'''

from datetime import datetime
import unittest

import boogio.aws_surveyor as aws_surveyor
import boogio.aws_informer as aws_informer


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSSurveyorSurvey(unittest.TestCase):
    '''Test cases for the AWSSurveyor.survey() and .informers() functions.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case level common fixture setup.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_survey_empty(self):
        '''Test AWSSurveyor.survey().'''

        # - - - - - - - - - - - -
        # No profiles, regions or entity_types are defined.
        surveyor = aws_surveyor.AWSSurveyor(config_path='')

        before = datetime.utcnow().replace(microsecond=0)
        surveyor.survey()
        after = datetime.utcnow().replace(microsecond=0)

        self.assertEqual(surveyor.informers(), [])

        self.assertIsNotNone(surveyor.survey_timestamp)
        survey_time = datetime.strptime(
            surveyor.survey_timestamp,
            aws_surveyor.AWSSurveyor.timestamp_format
            )
        self.assertTrue(before <= survey_time)
        self.assertTrue(survey_time <= after)

        # # - - - - - - - - - - - -
        # # No profiles are defined.
        # (Now covered in test_aws_surveyor_survey_unassigned_profile())
        # surveyor = aws_surveyor.AWSSurveyor(
        #     config_path='',
        #     regions=['us-east-1']
        #     )

        # surveyor.survey('ec2')
        # self.assertEqual(surveyor.informers(), [])

        # - - - - - - - - - - - -
        # No regions are defined.
        surveyor = aws_surveyor.AWSSurveyor(
            config_path='',
            profiles=['default']
            )

        surveyor.survey('ec2')
        self.assertEqual(surveyor.informers(), [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_survey_errors(self):
        '''Test AWSSurveyor.survey() errors.'''

        # - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(
            profiles=['default'],
            regions=['us-east-1'],
            config_path=''
            )

        with self.assertRaises(ValueError):
            surveyor.survey('plugh')

        with self.assertRaises(ValueError):
            surveyor.survey('ec2', profiles='foo')

        with self.assertRaises(ValueError):
            surveyor.survey('ec2', regions='us-west-1')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_survey(self):
        '''Test AWSSurveyor.survey() basic interface.'''

        # - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor(
            profiles=['default'],
            regions=['us-east-1'],
            config_path=''
            )

        # - - - - - - - - - - - -

        surveyor.survey('ec2')
        informers = surveyor.informers()
        self.assertNotEqual(informers, [])

        # Surveyed instances are not expanded yet.
        self.assertEqual(
            set([i.is_expanded for i in surveyor.informers()]),
            set([False])
            )

        # Expanding a different entity type has no effect.
        surveyor.expand_informers('elb')
        self.assertEqual(
            set([i.is_expanded for i in surveyor.informers()]),
            set([False])
            )

        # Expanding the correct entity type expands informers.
        surveyor.expand_informers('ec2')
        self.assertEqual(
            set([i.is_expanded for i in surveyor.informers()]),
            set([True])
            )

        informer_types = list(set([type(i) for i in informers]))

        # Only the expected type of informer was created.
        self.assertEqual(
            informer_types,
            [aws_informer.EC2InstanceInformer]
            )

        # - - - - - - - - - - - -

        surveyor.survey('eip', 'sqs', 'elb')
        informers = surveyor.informers()
        self.assertNotEqual(informers, [])

        # Surveyed instances are not expanded yet.
        self.assertEqual(
            set([i.is_expanded for i in surveyor.informers()]),
            set([False])
            )

        # Expanding specific entity types expands only those informers.
        surveyor.expand_informers('eip')
        self.assertEqual(
            set([i.is_expanded for i in surveyor.informers('eip')]),
            set([True])
            )
        self.assertEqual(
            set(
                [
                    i.is_expanded
                    for i in surveyor.informers('sqs', 'elb')
                    ]
                ),
            set([False])
            )

        # Only the expected types of informers were created.
        informer_types = list(set([type(i) for i in informers]))
        self.assertItemsEqual(
            informer_types,
            [
                aws_informer.EIPInformer,
                aws_informer.SQSInformer,
                aws_informer.ELBInformer
                ]
            )

        # AWSSurveyor.informers() entity type arguments are handled
        # properly: Single arguments.
        self.assertItemsEqual(
            list(set([type(i) for i in surveyor.informers('eip')])),
            [aws_informer.EIPInformer]
            )
        # The same, with multiple arguments.
        self.assertItemsEqual(
            list(set([type(i) for i in surveyor.informers('sqs', 'elb')])),
            [aws_informer.SQSInformer, aws_informer.ELBInformer]
            )
        # Now with a type that isn't present.
        self.assertItemsEqual(
            list(set([type(i) for i in surveyor.informers('ec2')])),
            []
            )

        # - - - - - - - - - - - -

        surveyor.survey('eip', 'sqs', 'elb')
        informers = surveyor.informers()
        self.assertNotEqual(informers, [])

        # Some surveyed instances are not expanded yet.
        self.assertIn(
            False,
            [i.is_expanded for i in surveyor.informers()],
            )

        # Expanding all entity types expands all informers.
        surveyor.expand_informers()
        self.assertEqual(
            set([i.is_expanded for i in surveyor.informers()]),
            set([True])
            )

        # # - - - - - - - - - - - - - - - - - - - - - - - -
        # all_ec2 = aws_surveyor.informers('ec2', profile_names=['roqa'])

        # self.assertIsNotNone(all_ec2)
        # self.assertNotEqual(all_ec2, [])
        # self.assertTrue(len(all_ec2) > 0)

        # # - - - - - - - - - - - - - - - - - - - - - - - -
        # us_east_1_ec2 = aws_surveyor.informers(
        #     'ec2', profile_names=['roqa'], region_names=['us-east-1']
        #     )

        # self.assertIsNotNone(us_east_1_ec2)
        # self.assertNotEqual(us_east_1_ec2, [])

        # # - - - - - - - - - - - - - - - - - - - - - - - -
        # us_ec2 = aws_surveyor.informers(
        #     'ec2',
        #     profile_names=['roqa'],
        #     region_names=['us-east-1', 'us-west']
        #     )
        # self.assertIsNotNone(us_ec2)
        # self.assertNotEqual(us_ec2, [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_survey_no_refresh(self):
        '''Test AWSSurveyor.survey() with refresh: False.'''

        # We're going to muck with the internal _informers list.
        # pylint: disable=protected-access

        surveyor = aws_surveyor.AWSSurveyor(
            profiles=['default'],
            regions=['us-east-1'],
            config_path=''
            )
        surveyor.survey('eip')
        informer_count = len(surveyor.informers())

        # - - - - - - - - - - - -
        # Force a "fake" extra informer.

        surveyor._informers.append(surveyor._informers[0])
        self.assertEqual(len(surveyor.informers()), informer_count + 1)

        surveyor.survey('eip', refresh=False)
        self.assertEqual(len(surveyor.informers()), informer_count + 1)

        surveyor.survey('eip')
        self.assertEqual(len(surveyor.informers()), informer_count)

        # - - - - - - - - - - - -
        # Add our "fake" in again.

        surveyor._informers.append(surveyor._informers[0])
        self.assertEqual(len(surveyor.informers()), informer_count + 1)

        surveyor.survey('vpc', refresh=False)
        self.assertEqual(len(surveyor.informers('eip')), informer_count + 1)

        surveyor.survey('vpc', 'eip')
        self.assertEqual(len(surveyor.informers('eip')), informer_count)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_survey_unassigned_profile(self):
        '''Test AWSSurveyor.survey() with no profile assigned.'''

        # - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor(
            regions=['us-east-1'],
            config_path=''
            )

        # - - - - - - - - - - - -

        surveyor.survey('ec2')
        informers = surveyor.informers()
        self.assertNotEqual(informers, [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_survey_filtered(self):
        '''Test AWSSurveyor.survey() with filters defined.

        This is a light test, basically just making sure filters get
        used.
        '''

        # - - - - - - - - - - - -
        # Preliminary fetch to get a set of filterable IPs.
        # - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor(
            profiles=['default'],
            regions=['us-east-1', 'us-west-1'],
            config_path=''
            )
        surveyor.survey('eip')
        all_ips = [
            i.to_dict()['PublicIp']
            for i in surveyor.informers()
            ]
        # If this isn't true we're not testing what this case is
        # intended to test.
        self.assertTrue(len(all_ips) > 3)

        # - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor(
            profiles=['default'],
            regions=['us-east-1', 'us-west-1'],
            config_path=''
            )

        selected_ips = all_ips[:3]
        surveyor.add_filters('eip', {'public-ip': selected_ips})

        surveyor.survey('eip')

        some_ips = [
            i.to_dict()['PublicIp']
            for i in surveyor.informers()
            ]

        self.assertItemsEqual(some_ips, selected_ips)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSSurveyorAllPaths(unittest.TestCase):
    '''Test cases for the AWSSurveyor.all_paths() method.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_all_paths(self):
        '''Test AWSSurveyor.mediators().'''

        surveyor = aws_surveyor.AWSSurveyor(
            profiles=['default'],
            regions=['us-east-1'],
            config_path=''
            )

        surveyor.survey('ec2')

        # - - - - - - - - - - - -

        ec2_paths = surveyor.all_paths('ec2')

        self.assertNotEqual(ec2_paths, [])
        self.assertIn('[].Tags:Name', ec2_paths)

        # - - - - - - - - - - - -

        elb_paths = surveyor.all_paths('elb')

        self.assertEqual(elb_paths, [])

        # - - - - - - - - - - - -

        surveyor.survey('ec2', 'elb')

        new_ec2_paths = surveyor.all_paths('ec2')
        self.assertItemsEqual(ec2_paths, new_ec2_paths)

        new_elb_paths = surveyor.all_paths('elb')
        self.assertNotEqual(new_elb_paths, [])
        self.assertIn('[].LoadBalancerName', new_elb_paths)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    unittest.main()
