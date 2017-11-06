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

'''Test cases for the sqs_sifter.py module.'''

import unittest

import os
import json

from boogio import site_boogio
import boogio.sqs_sifter as sqs_sifter

TEST_QUEUE_NAME = os.environ.get('SQS_SIFTER_TEST_QUEUE_NAME') or ''
TEST_QUEUE_URL = (
    'https://sqs.us-east-1.amazonaws.com/999999999999/' + TEST_QUEUE_NAME
    )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@unittest.skipUnless(
    TEST_QUEUE_NAME, (
        'To enable SQSSifter test cases, define environment variable'
        ' SQS_SIFTER_TEST_QUEUE_NAME.'
        )
    )
class TestSQSSifter(unittest.TestCase):
    '''Basic test cases for SQSSifter.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case common fixture setup.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_sqs_sifter_init(self):
        '''Test basic initialization of sqs sifter instances.'''

        # Most basic initialization without connection.
        sifter = sqs_sifter.SQSSifter('', connect=False)
        self.assertIsNotNone(sifter)
        self.assertIsNone(sifter.session)
        self.assertIsNone(sifter.client)

        sifter = sqs_sifter.SQSSifter(TEST_QUEUE_URL, connect=False)
        self.assertIsNotNone(sifter)

        # Initialization with connection parameter errors.
        with self.assertRaises(ValueError):
            sifter = sqs_sifter.SQSSifter('')

        with self.assertRaises(ValueError):
            sifter = sqs_sifter.SQSSifter('', profile_name='default')

        with self.assertRaises(ValueError):
            sifter = sqs_sifter.SQSSifter('', region_name='us-east-1')

        # Connection with legal connection parameters.
        sifter = sqs_sifter.SQSSifter(
            TEST_QUEUE_URL,
            profile_name='default', region_name='us-east-1'
            )
        self.assertIsNotNone(sifter)
        self.assertIsNotNone(sifter.session)
        self.assertIsNotNone(sifter.client)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_sqs_sifter_connect(self):
        '''Test sqs sifter instance AWS session and SQS client creation.'''

        sifter = sqs_sifter.SQSSifter(
            '',
            connect=False, profile_name='default', region_name='us-east-1'
            )

        self.assertIsNotNone(sifter)
        self.assertIsNone(sifter.session)
        self.assertIsNone(sifter.client)

        sifter.connect()
        self.assertIsNotNone(sifter.session)
        self.assertIsNotNone(sifter.client)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Record the original session and client for comparing to check
        # if the reconnect parameter controlled the right behavior.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        old_session = sifter.session
        old_client = sifter.client

        self.assertEqual(old_session, sifter.session)
        self.assertEqual(old_client, sifter.client)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        sifter.connect(reconnect=False)
        self.assertIsNotNone(sifter.session)
        self.assertIsNotNone(sifter.client)

        self.assertEqual(old_session, sifter.session)
        self.assertEqual(old_client, sifter.client)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        sifter.connect()
        self.assertIsNotNone(sifter.session)
        self.assertIsNotNone(sifter.client)

        self.assertNotEqual(old_session, sifter.session)
        self.assertNotEqual(old_client, sifter.client)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        old_session = sifter.session
        old_client = sifter.client

        sifter.connect(reconnect=True)
        self.assertIsNotNone(sifter.session)
        self.assertIsNotNone(sifter.client)

        self.assertNotEqual(old_session, sifter.session)
        self.assertNotEqual(old_client, sifter.client)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_message_passes_filters(self):
        '''Test sqs sifter message filter checking.'''

        sifter = sqs_sifter.SQSSifter(
            TEST_QUEUE_URL,
            region_name=site_boogio.test_region_name,
            profile_name=site_boogio.test_profile_name
            )
        msgs = sifter.sift_for_message()
        self.assertTrue(len(msgs) > 0)
        msg = msgs[0]
        msg_md5 = msg['MD5OfBody']
        msg_id = msg['MessageId']

        body = json.loads(msg['Body'])
        body_timestamp = body['Timestamp']

        # Emtpy filters.
        self.assertTrue(sifter._message_passes_filters(msg))

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Filtering on message header fields
        # - - - - - - - - - - - - - - - - - - - - - - - -

        # One failing filter.
        sifter.filters = [lambda x: x['MD5OfBody'] == '']
        self.assertFalse(sifter._message_passes_filters(msg))

        # Two failing filters.
        sifter.filters += [lambda x: x['MD5OfBody'] == '42']
        self.assertFalse(sifter._message_passes_filters(msg))

        # One passing filter.
        sifter.filters = [lambda x: x['MD5OfBody'] == msg_md5]
        self.assertTrue(sifter._message_passes_filters(msg))

        # Two passing filters.
        sifter.filters += [lambda x: x['MessageId'] == msg_id]
        self.assertTrue(sifter._message_passes_filters(msg))

        # One passing, one failing filter.
        sifter.filters = [
            lambda x: x['MD5OfBody'] == '',
            lambda x: x['MD5OfBody'] == msg_md5
            ]
        self.assertTrue(sifter._message_passes_filters(msg))

        # Two passing, two failing filters.
        sifter.filters = [
            lambda x: x['MD5OfBody'] == '',
            lambda x: x['MD5OfBody'] == '42',
            lambda x: x['MD5OfBody'] == msg_md5,
            lambda x: x['MessageId'] == msg_id
            ]
        self.assertTrue(sifter._message_passes_filters(msg))

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Filtering on message body elements.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        # One failing filter.
        sifter.filters = [lambda x: x['Body']['Timestamp'] == '']
        self.assertFalse(sifter._message_passes_filters(msg))

        # One passing filter.
        sifter.filters = [lambda x: x['Body']['Timestamp'] == body_timestamp]
        self.assertTrue(sifter._message_passes_filters(msg))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_delete_message(self):
        '''Test sqs sifter queue message deletion.'''
        # - - - - - - - - - - - - - - - - - - - - - - - -
        # We need to hook up a test topic/queue pair so we have full
        # control over messages in the queue before this can be
        # properly implemented.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_sqs_sifter_sift_for_message(self):
        '''Test sqs sifter queue message retrieval and filtering.'''
        # - - - - - - - - - - - - - - - - - - - - - - - -
        # We need to hook up a test topic/queue pair so we have full
        # control over messages in the queue before this can be
        # properly implemented.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        sifter = sqs_sifter.SQSSifter(
            TEST_QUEUE_URL,
            region_name=site_boogio.test_region_name,
            profile_name=site_boogio.test_profile_name
            )

        def dump_receivedmessage(rmsg):
            '''Dump content of one received message.'''
            try:
                rmsg_body_json = rmsg['Body']
                rmsg_body = json.loads(rmsg_body_json)
            except TypeError:  # Wasn't JSON.
                rmsg_body = rmsg['Body']

            msg_json = rmsg_body['Message']
            msg = json.loads(msg_json)

            # print (
            #     '\n--------------------------------------------\n'
            #     'Received Message:\n------------------'
            #     )
            # print type(rmsg)
            # print rmsg.keys()
            # print '--------'
            # for (k, v) in rmsg.items():
            #     if k != 'Body':
            #         print '%s:\t%s' % (k, v)

            # print (
            #     '\n--------------------------------------------\n'
            #     'Body:\n------------------'
            #     )
            # print type(rmsg_body)
            # print rmsg_body.keys()
            # print '--------'
            # for (k, v) in rmsg_body.items():
            #     if k != 'Message':
            #         print '%s:\t%s' % (k, v)

            # print (
            #     '\n--------------------------------------------\n'
            #     'Message:\n------------------'
            #     )
            # # print type(msg)
            # print msg.keys()
            # print '--------'
            # for (k, v) in msg.items():
            #     if k not in ['configurationItem', 'configurationItemDiff']:
            #         print '%s:\t%s' % (k, v)
            # # print msg['messageType']

            print (
                '\n--------------------------------------------\n'
                'configurationItem:\n------------------'
                )
            configuration_item = msg['configurationItem']
            print type(configuration_item)
            print configuration_item.keys()
            print '--------'
            for (k, v) in configuration_item.items():
                # if k not in ['configurationItem', 'configurationItemDiff']:
                print '%s:\t%s' % (k, v)

            print (
                '\n--------------------------------------------\n'
                'configurationItemDiff:\n------------------'
                )
            configuration_item_diff = msg['configurationItemDiff']
            print type(configuration_item_diff)
            print configuration_item_diff.keys()
            print '--------'
            for (k, v) in configuration_item_diff.items():
                # if k not in ['configurationItem', 'configurationItemDiff']:
                print '%s:\t%s' % (k, v)

            if 'configuration' in configuration_item:
                print (
                    '\n--------------------------------------------\n'
                    'configuration:\n------------------'
                    )
                configuration = configuration_item['configuration']
                print type(configuration)
                print configuration.keys()
                print '--------'
                for (k, v) in configuration.items():
                    # if k not in ['configurationItem', 'configuration']:
                    print '%s:\t%s' % (k, v)

        def filter_existential_instance_messages(rmsg):
            '''Return True for instance Create and Delete messages.'''
            rmsg_body = rmsg['Body']

            msg_json = rmsg_body['Message']
            try:
                msg = json.loads(msg_json)
            except ValueError:
                print rmsg_body

            subject = (
                rmsg_body['Subject']
                if 'Subject' in rmsg_body
                else None
                )

            message_type = (
                msg['messageType']
                if 'messageType' in msg
                else None
                )

            configuration_item = (
                msg['configurationItem']
                if 'configurationItem' in msg
                else None
                )

            configuration_item_diff = (
                msg['configurationItemDiff']
                if 'configurationItemDiff' in msg
                else None

                )

            change_type = (
                configuration_item_diff['changeType']
                if (
                    configuration_item_diff is not None and
                    'changeType' in configuration_item_diff
                    )
                else None
                )

            event_timestamp = (
                configuration_item['resourceCreationTime']
                if configuration_item is not None and
                'resourceCreationTime' in configuration_item
                else None
                )

            capture_timestamp = (
                configuration_item['configurationItemCaptureTime']
                if configuration_item is not None and
                'configurationItemCaptureTime' in configuration_item
                else None
                )

            if subject is not None:
                # print
                # print subject
                # print subject.split(None, 4)
                try:
                    (
                        _, service, entity_type, entity_id, action, info
                        ) = subject.split(None, 5)
                except ValueError:
                    (
                        service, entity_type, entity_id, action, info
                        ) = [None] * 5

            # print "%s\t%s\t%s" % (message_type, change_type, subject)
            if entity_type == 'AWS::EC2::Instance':
                print (
                    "{:<32}  {:<8}  {:<22}  {:<12}  {:<8}  {:<24}  {:<24}"
                    ).format(
                    message_type, change_type, entity_type, entity_id,
                    action, event_timestamp, capture_timestamp
                    )
                # if change_type == 'CREATE':
                #     dump_receivedmessage(rmsg)
                return True

            return False

        # sifter.filters = [lambda _: False]
        sifter.filters = [filter_existential_instance_messages]

        msgs = sifter.sift_for_message(
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20,
            delete_scree=True
            )

        print "\nMessages in test_sqs_sifter_sift_for_message: %s" % len(msgs)
        if len(msgs) == 0:
            return

        self.assertTrue(isinstance(msgs, list))
        self.assertTrue(len(msgs) > 0)
        # for m in msgs:
        #     dump_receivedmessage(m)

if __name__ == '__main__':
    unittest.main()
