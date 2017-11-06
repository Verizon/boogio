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

'''Test cases for aws_informer.py parallel AWS information retrieval.'''

import os
import time
import unittest

from boogio import aws_informer


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@unittest.skipIf(
    not os.environ.get('RUN_SLOW_IAM_TESTS'),
    (
        'Enable IAM tests by setting environment variable'
        ' RUN_SLOW_IAM_TESTS to a truthy value.'
        )
    )
class TestGetAWSInfoInParallel(unittest.TestCase):
    '''Basic test cases for AWSMediator.get_aws_info_in_parallel.'''

    # pylint: disable=invalid-name
    # TODO: Add skiptest based on os.environ['TEST_DURATION_LIMIT']

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case common fixture setup.'''
        self.mediator = aws_informer.AWSMediator()
        self.iam_informer = aws_informer.IAMInformer(
            mediator=self.mediator,
            record_types=['Users']
            )

        mediator = self.mediator
        informer = self.iam_informer

        self.assertIn('Users', informer.supplementals)
        # print informer.supplementals['Users'][0]
        # - - - - - - - - - - - - - - - - - -
        # user = informer.supplementals['Users'][0]

        def request(user):
            '''Helper for creating a request structure.'''
            return {
                'origin': user,
                'session_kwargs': {
                    'profile_name': mediator.session.profile_name
                    },
                'client_type': 'iam',
                'client_method': 'list_access_keys',
                'method_args': [],
                'method_kwargs': {'UserName': user['UserName']},
                'response_data_keys': {'AccessKeyMetadata': 'AccessKeys'}
                }

        # - - - - - - - - - - - - - - - - - -
        # This establishes the baseline for request duration.
        # - - - - - - - - - - - - - - - - - -
        baseline_sample_size = 12
        durations = []

        for user_index in range(baseline_sample_size):
            start = time.time()
            mediator.get_aws_info_in_parallel(
                [request(informer.supplementals['Users'][user_index])]
                )
            durations.append(time.time() - start)

        # self.duration_baseline = duration / baseline_sample_size
        self.max_duration_baseline = max(durations)
        self.min_duration_baseline = min(durations)
        # We'll allow requests "too slow" up to this limit without failing.
        self.duration_leeway_factor = 2.2

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_aws_info_in_parallel_1(self):
        '''Test get_aws_info_in_parallel.'''

        mediator = self.mediator
        informer = self.iam_informer

        requests = [
            {
                'origin': user,
                'session_kwargs': {
                    'profile_name': mediator.session.profile_name
                    },
                'client_type': 'iam',
                'client_method': 'list_access_keys',
                'method_args': [],
                'method_kwargs': {'UserName': user['UserName']},
                'response_data_keys': {'AccessKeyMetadata': 'AccessKeys'}
                }
            for user in informer.supplementals['Users'][:1]
            ]

        start = time.time()
        responses = mediator.get_aws_info_in_parallel(requests)
        time.time() - start

        self.assertTrue(isinstance(responses, list))
        self.assertEqual(len(responses), 1)
        self.assertTrue(isinstance(responses[0], list))
        self.assertEqual(len(responses[0]), 3)
        self.assertEqual(responses[0][0], requests[0])
        self.assertIn('AccessKeyMetadata', responses[0][1])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_aws_info_in_parallel_2(self):
        '''Test get_aws_info_in_parallel.'''

        mediator = self.mediator
        informer = self.iam_informer

        requests = [
            {
                'origin': user,
                'session_kwargs': {
                    'profile_name': mediator.session.profile_name
                    },
                'client_type': 'iam',
                'client_method': 'list_access_keys',
                'method_args': [],
                'method_kwargs': {'UserName': user['UserName']},
                'response_data_keys': {'AccessKeyMetadata': 'AccessKeys'}
                }
            for user in informer.supplementals['Users'][:2]
            ]

        start = time.time()
        responses = mediator.get_aws_info_in_parallel(requests)
        duration = time.time() - start

        self.assertTrue(isinstance(responses, list))
        self.assertEqual(len(responses), len(requests))
        self.assertTrue(isinstance(responses[0], list))
        self.assertEqual(len(responses[0]), 3)
        self.assertEqual(responses[0][0], requests[0])
        self.assertIn('AccessKeyMetadata', responses[0][1])

        max_expected_duration = (
            self.duration_leeway_factor * self.max_duration_baseline
            )

        self.assertTrue(
            duration < (max_expected_duration),
            msg='duration: %s (baseline %s)' % (
                duration, max_expected_duration
                )
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_aws_info_in_parallel_single_batch(self):
        '''Test get_aws_info_in_parallel.'''

        mediator = self.mediator
        informer = self.iam_informer

        requests = [
            {
                'origin': user,
                'session_kwargs': {
                    'profile_name': mediator.session.profile_name
                    },
                'client_type': 'iam',
                'client_method': 'list_access_keys',
                'method_args': [],
                'method_kwargs': {'UserName': user['UserName']},
                'response_data_keys': {'AccessKeyMetadata': 'AccessKeys'}
                }
            for user in informer.supplementals['Users'][
                :mediator.PARALLEL_FETCH_PROCESS_COUNT - 1
                ]
            ]

        start = time.time()
        responses = mediator.get_aws_info_in_parallel(requests)
        duration = time.time() - start

        self.assertTrue(isinstance(responses, list))
        self.assertEqual(len(responses), len(requests))
        self.assertTrue(isinstance(responses[0], list))
        self.assertEqual(len(responses[0]), 3)
        self.assertEqual(responses[0][0], requests[0])
        self.assertIn('AccessKeyMetadata', responses[0][1])

        max_expected_duration = (
            1.5 * self.duration_leeway_factor * self.max_duration_baseline
            )

        self.assertTrue(
            duration < (max_expected_duration),
            msg='duration: %s (at most expected: %s)' % (
                duration, max_expected_duration
                )
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_aws_info_in_parallel_batch_plus_1(self):
        '''Test get_aws_info_in_parallel.'''

        mediator = self.mediator
        informer = self.iam_informer

        requests = [
            {
                'origin': user,
                'session_kwargs': {
                    'profile_name': mediator.session.profile_name
                    },
                'client_type': 'iam',
                'client_method': 'list_access_keys',
                'method_args': [],
                'method_kwargs': {'UserName': user['UserName']},
                'response_data_keys': {'AccessKeyMetadata': 'AccessKeys'}
                }
            for user in informer.supplementals['Users'][
                :mediator.PARALLEL_FETCH_PROCESS_COUNT + 1
                ]
            ]

        start = time.time()
        responses = mediator.get_aws_info_in_parallel(requests)
        duration = time.time() - start

        self.assertTrue(isinstance(responses, list))
        self.assertEqual(len(responses), len(requests))
        self.assertTrue(isinstance(responses[0], list))
        self.assertEqual(len(responses[0]), 3)
        self.assertEqual(responses[0][0], requests[0])
        self.assertIn('AccessKeyMetadata', responses[0][1])

        # We're doing one more request than can be done in one parallel pass.
        # It wouldn't really be wrong for it to happen this fast, but it's
        # very unlikely and if it's repeatable might be worth checking.
        # Or, remove this assert.
        self.assertTrue(
            duration > (
                self.min_duration_baseline
                ),
            msg='duration: %s (at least expected: %s)' % (
                duration, self.min_duration_baseline
                )
            )

        max_expected_duration = (
            2 * self.duration_leeway_factor * self.max_duration_baseline
            )

        self.assertTrue(
            duration < (max_expected_duration),
            msg='duration: %s (at most expected: %s)' % (
                duration,
                max_expected_duration
                )
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_get_aws_info_in_parallel_double_batch(self):
        '''Test get_aws_info_in_parallel.'''

        mediator = self.mediator
        informer = self.iam_informer

        requests = [
            {
                'origin': user,
                'session_kwargs': {
                    'profile_name': mediator.session.profile_name
                    },
                'client_type': 'iam',
                'client_method': 'list_access_keys',
                'method_args': [],
                'method_kwargs': {'UserName': user['UserName']},
                'response_data_keys': {'AccessKeyMetadata': 'AccessKeys'}
                }
            for user in informer.supplementals['Users'][
                :(2 * mediator.PARALLEL_FETCH_PROCESS_COUNT - 1)
                ]
            ]

        start = time.time()
        responses = mediator.get_aws_info_in_parallel(requests)
        duration = time.time() - start

        self.assertTrue(isinstance(responses, list))
        self.assertEqual(len(responses), len(requests))
        self.assertTrue(isinstance(responses[0], list))
        self.assertEqual(len(responses[0]), 3)
        self.assertEqual(responses[0][0], requests[0])
        self.assertIn('AccessKeyMetadata', responses[0][1])

        max_expected_duration = (
            3 * self.duration_leeway_factor * self.max_duration_baseline
            )

        self.assertTrue(
            duration < (max_expected_duration),
            msg='duration: %s (at most expected: %s)' % (
                duration,
                max_expected_duration
                )
            )


if __name__ == '__main__':
    unittest.main()
