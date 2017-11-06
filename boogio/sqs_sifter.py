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

'''Manage retrieval and handling of messages from an AWS SQS queue.
'''
import json

import boto3


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class SQSSifter(object):
    '''
    AWS SQS queue message receiver and handler selector.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(
            self,
            queue_url,
            profile_name=None,
            region_name='us-east-1',
            connect=True,
            filters=None
            ):  # pylint: disable=bad-continuation
        '''Initialize an SQS Sifter instance.

        Arguments:

            queue_url (str)
                The URL of the AWS Queue to sift.

            profile_name (str)
                Session parameter for the AWS connection.

            region_name (str, default='us-east-1')
                Session parameter for the AWS connection.

            connect (bool, default=True)
                If ``True``, a session will be opened and an sqs client
                initialized when the instance is created. If ``False``,
                the session will have to be initialized with a
                separate call to ``connect()``.

            filters (list)
                A list of methods for sifting messages. Each method
                will be applied to each received message, and only
                messages for which some filter returns ``True`` will
                pass the sifting.


        '''

        self.queue_url = queue_url
        self.profile_name = profile_name
        self.region_name = region_name

        self.filters = list(filters) if filters else []
        self.session = None
        self.client = None

        if connect:
            self.connect()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def connect(self, profile_name=None, region_name=None, reconnect=True):
        '''Connect an AWS session and create an SQS client.

        Arguments:


            profile_name (str)
                Session parameter for the AWS connection.

            region_name (str)
                Session parameter for the AWS connection.


            reconnect (bool)
                If ``True``, an existing session and client will be
                replaced with a new pair. If ``False``, a new session
                and client will only be created if none already
                exists.

        '''

        pname = self.profile_name if profile_name is None else profile_name
        rname = self.region_name if region_name is None else region_name

        if pname is None or rname is None:
            raise ValueError(
                "%s: can't connect to region %s with profile %s" % (
                    self.__class__.__name__, rname, pname
                    )
                )

        # We recreate session and client only if they don't exist already,
        # unless reconnect is true.
        if reconnect or (self.session is None):
            self.session = boto3.session.Session(
                profile_name=pname,
                region_name=rname
                )
        if reconnect or (self.client is None):
            self.client = self.session.client('sqs')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sift_for_message(self, delete_scree=False, **kwargs):
        '''Receive and return sifted messages from the Queue.

        Arguments:

            delete_scree (bool)
                If ``True``, messages that don't match the sifter's
                filters will be deleted from the SQS queue.

            kwargs
                Additional parameters to pass through to the sqs
                client ``receive_message()`` call.

        Returns:

            (list): A list of the messages received from the queue
            that passed the sifter's filters.

        '''

        if self.client is None:
            raise RuntimeError(
                "%s: no client connection" % self.__class__.__name__
                )

        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            **kwargs
            )

        # This may be useful, leaving it here for future reference.
        # response_status = response['ResponseMetadata']['HTTPStatusCode']

        assert isinstance(response, dict)

        if 'Messages' not in response:
            return []

        passed_msgs = [
            m for m in response['Messages']
            if self._message_passes_filters(m)
            ]

        # Remove non-passing messages, if required.
        if delete_scree:

            failed_messages = [
                m for m in response['Messages']
                if m not in passed_msgs
                ]

            for msg in failed_messages:
                self._delete_message(msg)

        return passed_msgs

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _message_passes_filters(self, message):
        '''Determine if the indicated message passes the sifter's filters.

        Arguments:

            message
                The message to be checked, as it was received from SQS.

        Returns:

            (bool) True if the sifter has filters defined and any of
            the sifter's filters returns true when run on the message.
            False otherwise.

        '''

        assert isinstance(message, dict)

        # If we have no filters, we'll pass everything.
        if len(self.filters) == 0:
            return True

        # We unpack the Body subordinate JSON before filtering. We'll work
        # with a copy so we aren't altering the original message.
        message = dict(message)
        if 'Body' in message:
            message['Body'] = json.loads(message['Body'])

        # The following was considered, but we only want the first hit so
        # we can return early if we get one.
        # return True in [f(message) for f in self.filters]
        for this_filter in self.filters:
            if this_filter(message):
                return True

        # If no filters passed the message, then the message fails.
        return False

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _delete_message(self, message):
        '''Delete the indicated message from the queue.

        Arguments:

            message
                The message to be deleted, as it was received from
                SQS.

        '''

        if 'ReceiptHandle' not in message:
            raise ValueError(
                (
                    "%s: can't delete message: no ReceiptHandle field."
                    " Message: %s"
                    ) % (self.__class__.__name__, message)
                )

        self.client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=message['ReceiptHandle']
            )
