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

'''Test cases for the timestamp.py module.'''

import unittest

from boogio.utensils import timestamp

from datetime import timedelta
from datetime import datetime


# # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# class TestTimestamp(unittest.TestCase):
#     '''
#     Basic test cases for Timestamp.
#     '''

#     # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     def setUp(self):
#         pass

#     # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#     def test_timestamp_init(self):
#         '''
#         Test initialization of Timestamp instances.
#         '''

#         # ts = timestamp.Timestamp()
#         self.assertIsNotNone(ts)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTimestampPackageMethods(unittest.TestCase):
    '''
    Basic test cases for Timestamp.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_timestamp_is_rfc3339_timestamp(self):
        '''
        Test timestamp validity checking.
        '''
        # Shorter lines so we don't need a linebreak will make it easier
        # to see the relationship between test cases.
        is_rfc3339_ts = timestamp.is_rfc3339_timestamp

        self.assertTrue(is_rfc3339_ts('2010-09-18T12:15:42.941437-08:00'))
        self.assertTrue(is_rfc3339_ts('2010-09-18T12:15:42.849894+00:00'))
        self.assertTrue(is_rfc3339_ts('2010-09-18T23:59:59.999999+00:00'))

        self.assertFalse(is_rfc3339_ts(None))
        self.assertFalse(is_rfc3339_ts(''))
        self.assertFalse(is_rfc3339_ts('2010-09-18T23:59:59.12345+00:00'))
        self.assertFalse(is_rfc3339_ts('2010-09-18T23:59:59.1234567+00:00'))
        self.assertFalse(is_rfc3339_ts('2010-09-18T23:59:59.123456'))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_timestamp_is_condensed_timestamp(self):
        '''
        Test timestamp validity checking.
        '''

        # Shorter lines so we don't need a linebreak will be easier to read.
        is_condensed_timestamp = timestamp.is_condensed_timestamp

        self.assertTrue(is_condensed_timestamp('12345678.123456.123456'))

        with self.assertRaises(TypeError):
            is_condensed_timestamp()

        self.assertFalse(is_condensed_timestamp(None))
        self.assertFalse(is_condensed_timestamp(''))

        self.assertFalse(is_condensed_timestamp('12345678123456.123456'))
        self.assertFalse(is_condensed_timestamp('12345678.123456123456'))
        self.assertFalse(is_condensed_timestamp('12345678123456123456'))

        self.assertFalse(is_condensed_timestamp('1234567.123456.123456'))
        self.assertFalse(is_condensed_timestamp('12345678.12345.123456'))
        self.assertFalse(is_condensed_timestamp('12345678.123456.12345'))

        self.assertFalse(is_condensed_timestamp('123456789.123456.123456'))
        self.assertFalse(is_condensed_timestamp('12345678.1234567.123456'))
        self.assertFalse(is_condensed_timestamp('12345678.123456.1234567'))

        self.assertFalse(is_condensed_timestamp('a2345678.123456.123456'))
        self.assertFalse(is_condensed_timestamp('12345678.a23456.123456'))
        self.assertFalse(is_condensed_timestamp('12345678.123456.a23456'))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_timestamp_validate_rfc3339_timestamp(self):
        '''
        Test invalid timestamp assertion raising.
        '''

        validate_rfc3339_timestamp = timestamp.validate_rfc3339_timestamp

        self.assertIsNone(
            validate_rfc3339_timestamp('2010-09-18T12:15:42.941437-08:00')
            )

        with self.assertRaises(TypeError):
            validate_rfc3339_timestamp()

        with self.assertRaises(ValueError):

            validate_rfc3339_timestamp(None)
            validate_rfc3339_timestamp('')
            validate_rfc3339_timestamp('2010-09-18T23:59:59.12345+00:00')
            validate_rfc3339_timestamp('2010-09-18T23:59:59.1234567+00:00')
            validate_rfc3339_timestamp('2010-09-18T23:59:59.123456')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_timestamp_validate_condensed_timestamp(self):
        '''
        Test invalid timestamp assertion raising.
        '''

        # ts = timestamp.Timestamp()
        # self.assertIsNone(timestamp.validate_condensed_timestamp(ts))

        self.assertIsNone(
            timestamp.validate_condensed_timestamp('12345678.123456.123456')
            )

        with self.assertRaises(TypeError):
            timestamp.validate_condensed_timestamp()

        with self.assertRaises(ValueError):

            timestamp.validate_condensed_timestamp(None)
            timestamp.validate_condensed_timestamp('')

            timestamp.validate_condensed_timestamp('12345678123456.123456')
            timestamp.validate_condensed_timestamp('12345678.123456123456')
            timestamp.validate_condensed_timestamp('12345678123456123456')

            timestamp.validate_condensed_timestamp('1234567.123456.123456')
            timestamp.validate_condensed_timestamp('12345678.12345.123456')
            timestamp.validate_condensed_timestamp('12345678.123456.12345')

            timestamp.validate_condensed_timestamp('123456789.123456.123456')
            timestamp.validate_condensed_timestamp('12345678.1234567.123456')
            timestamp.validate_condensed_timestamp('12345678.123456.1234567')

            timestamp.validate_condensed_timestamp('a2345678.123456.123456')
            timestamp.validate_condensed_timestamp('12345678.a23456.123456')
            timestamp.validate_condensed_timestamp('12345678.123456.a23456')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_timestamp_datetime_conversion(self):
        '''
        Test conversion between datetime and timestamp objects.
        '''

        dt0 = datetime(2010, 9, 18)
        cts0 = '20100918.000000.000000'
        rts0 = '2010-09-18T00:00:00.000000+00:00'

        dt1 = datetime(2010, 9, 18, 11, 20, 5)
        cts1 = '20100918.112005.000000'
        rts1 = '2010-09-18T11:20:05.000000+00:00'

        dt2 = datetime(2010, 9, 18, 11, 20, 5, 206742)
        cts2 = '20100918.112005.206742'
        rts2 = '2010-09-18T11:20:05.206742+00:00'

        dt3 = datetime(2010, 9, 18, 11, 20, 5, 2)
        cts3 = '20100918.112005.000002'
        rts3 = '2010-09-18T11:20:05.000002+00:00'

        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(timestamp.to_condensed(cts3), cts3)
        self.assertEqual(timestamp.to_rfc3339(rts3), rts3)
        self.assertEqual(timestamp.to_datetime(dt3), dt3)

        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(timestamp.to_condensed(dt0), cts0)
        self.assertEqual(timestamp.to_condensed(dt1), cts1)
        self.assertEqual(timestamp.to_condensed(dt2), cts2)
        self.assertEqual(timestamp.to_condensed(dt3), cts3)

        self.assertEqual(timestamp.to_condensed(rts0), cts0)
        self.assertEqual(timestamp.to_condensed(rts1), cts1)
        self.assertEqual(timestamp.to_condensed(rts2), cts2)
        self.assertEqual(timestamp.to_condensed(rts3), cts3)

        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(timestamp.to_rfc3339(dt0), rts0)
        self.assertEqual(timestamp.to_rfc3339(dt1), rts1)
        self.assertEqual(timestamp.to_rfc3339(dt2), rts2)
        self.assertEqual(timestamp.to_rfc3339(dt3), rts3)

        self.assertEqual(timestamp.to_rfc3339(cts0), rts0)
        self.assertEqual(timestamp.to_rfc3339(cts1), rts1)
        self.assertEqual(timestamp.to_rfc3339(cts2), rts2)
        self.assertEqual(timestamp.to_rfc3339(cts3), rts3)

        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(timestamp.to_datetime(cts0), dt0)
        self.assertEqual(timestamp.to_datetime(cts1), dt1)
        self.assertEqual(timestamp.to_datetime(cts2), dt2)
        self.assertEqual(timestamp.to_datetime(cts3), dt3)

        self.assertEqual(timestamp.to_datetime(rts0), dt0)
        self.assertEqual(timestamp.to_datetime(rts1), dt1)
        self.assertEqual(timestamp.to_datetime(rts2), dt2)
        self.assertEqual(timestamp.to_datetime(rts3), dt3)

        # - - - - - - - - - - - - - - - - - - - -
        before = datetime.utcnow()
        cts = timestamp.to_condensed()
        rts = timestamp.to_rfc3339()
        after = datetime.utcnow()

        self.assertTrue(before < timestamp.to_datetime(cts))
        self.assertTrue(before < timestamp.to_datetime(rts))
        self.assertTrue(timestamp.to_datetime(cts) < after)
        self.assertTrue(timestamp.to_datetime(rts) < after)

        # - - - - - - - - - - - - - - - - - - - -
        with self.assertRaises(ValueError):
            timestamp.to_rfc3339('A')

        with self.assertRaises(ValueError):
            timestamp.to_rfc3339('20010609.101112')

        with self.assertRaises(ValueError):
            timestamp.to_condensed('A')

        with self.assertRaises(ValueError):
            timestamp.to_condensed('20010609.101112')

        with self.assertRaises(ValueError):
            timestamp.to_datetime('A')

        with self.assertRaises(ValueError):
            timestamp.to_datetime('20010609.101112')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_timestamp_extract_condensed_timestamp(self):
        '''
        Test extraction of timestamps from strings.
        '''

        ts0 = '20100918.000000.000000'
        ts1 = '20100918.112005.000000'
        ts2 = '20100918.112005.206742'

        s0ps = '.'.join(['prefix', ts0, 'suffix'])
        s1ps = '.'.join(['prefix', ts1, 'suffix'])
        s2ps = '.'.join(['prefix', ts2, 'suffix'])

        s0p = '.'.join(['prefix', ts0])
        s1s = '.'.join([ts1, 'suffix'])

        self.assertEqual(timestamp.extract_condensed_timestamp(s0ps), ts0)
        self.assertEqual(timestamp.extract_condensed_timestamp(s1ps), ts1)
        self.assertEqual(timestamp.extract_condensed_timestamp(s2ps), ts2)
        self.assertEqual(timestamp.extract_condensed_timestamp(s0p), ts0)
        self.assertEqual(timestamp.extract_condensed_timestamp(s1s), ts1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_timestamp_except_condensed_timestamp(self):
        '''
        Test removal of timestamps from strings.
        '''

        ts0 = '20100918.000000.000000'
        ts1 = '20100918.112005.000000'
        ts2 = '20100918.112005.206742'

        ps = '.'.join(['prefix', 'suffix'])

        s0ps = '.'.join(['prefix', ts0, 'suffix'])
        s1ps = '.'.join(['prefix', ts1, 'suffix'])
        s2ps = '.'.join(['prefix', ts2, 'suffix'])

        s0p = '.'.join(['prefix', ts0])
        s1s = '.'.join([ts1, 'suffix'])

        self.assertEqual(timestamp.except_condensed_timestamp(s0ps), ps)
        self.assertEqual(timestamp.except_condensed_timestamp(s1ps), ps)
        self.assertEqual(timestamp.except_condensed_timestamp(s2ps), ps)
        self.assertEqual(timestamp.except_condensed_timestamp(s0p), 'prefix')
        self.assertEqual(timestamp.except_condensed_timestamp(s1s), 'suffix')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_timestamp_extract_condensed_to_datetime(self):
        '''
        Test extraction of timestamps and conversion to datetime objects.
        '''

        dt0 = datetime(2010, 9, 18)
        ts0 = '20100918.000000.000000'

        dt1 = datetime(2010, 9, 18, 11, 20, 5)
        ts1 = '20100918.112005.000000'

        dt2 = datetime(2010, 9, 18, 11, 20, 5, 206742)
        ts2 = '20100918.112005.206742'

        s0ps = '.'.join(['prefix', ts0, 'suffix'])
        s1ps = '.'.join(['prefix', ts1, 'suffix'])
        s2ps = '.'.join(['prefix', ts2, 'suffix'])

        s0p = '.'.join(['prefix', ts0])
        s1s = '.'.join([ts1, 'suffix'])

        self.assertEqual(timestamp.extract_condensed_to_datetime(s0ps), dt0)
        self.assertEqual(timestamp.extract_condensed_to_datetime(s1ps), dt1)
        self.assertEqual(timestamp.extract_condensed_to_datetime(s2ps), dt2)
        self.assertEqual(timestamp.extract_condensed_to_datetime(s0p), dt0)
        self.assertEqual(timestamp.extract_condensed_to_datetime(s1s), dt1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_timestamp_add_condensed_timestamp(self):
        '''
        Test adding timestamps to strings.
        '''

        dt2 = datetime(2010, 9, 18, 11, 20, 5, 206742)
        ts2 = '20100918.112005.206742'

        with self.assertRaises(ValueError):
            timestamp.add_condensed_timestamp('pre', 'x')
            timestamp.add_condensed_timestamp('pre', '12345678')

        # - - - - - - - - - - - - - - - - - - - -
        # Timestamp given as a string.
        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(
            timestamp.add_condensed_timestamp('pre', ts2),
            '.'.join(['pre', ts2])
            )

        self.assertEqual(
            timestamp.add_condensed_timestamp(
                'pre', ts2, separator='XXX'
                ),
            'XXX'.join(['pre', ts2])
            )

        self.assertEqual(
            timestamp.add_condensed_timestamp('pre', ts2, suffix='post'),
            '.'.join(['pre', ts2, 'post'])
            )

        self.assertEqual(
            timestamp.add_condensed_timestamp(
                'pre', ts2, suffix='post', separator='XXX'
                ),
            'XXX'.join(['pre', ts2, 'post'])
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Timestamp given as a datetime.
        # - - - - - - - - - - - - - - - - - - - -
        self.assertEqual(
            timestamp.add_condensed_timestamp('pre', dt2),
            '.'.join(['pre', ts2])
            )

        self.assertEqual(
            timestamp.add_condensed_timestamp(
                'pre', dt2, separator='XXX'
                ),
            'XXX'.join(['pre', ts2])
            )

        self.assertEqual(
            timestamp.add_condensed_timestamp('pre', dt2, suffix='post'),
            '.'.join(['pre', ts2, 'post'])
            )

        self.assertEqual(
            timestamp.add_condensed_timestamp(
                'pre', dt2, suffix='post', separator='XXX'
                ),
            'XXX'.join(['pre', ts2, 'post'])
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Timestamp generated automatically.
        # - - - - - - - - - - - - - - - - - - - -
        before = datetime.utcnow()
        dt_now = timestamp.extract_condensed_to_datetime(
            timestamp.add_condensed_timestamp('pre')
            )
        after = datetime.utcnow()

        self.assertTrue(before < dt_now)
        self.assertTrue(dt_now < after)

        # - - - - - - - - - - - - - - - - - - - -
        before = datetime.utcnow()
        dt_now = timestamp.extract_condensed_to_datetime(
            timestamp.add_condensed_timestamp('pre', suffix='post')
            )
        after = datetime.utcnow()

        self.assertTrue(before < dt_now)
        self.assertTrue(dt_now < after)

if __name__ == '__main__':
    unittest.main()
