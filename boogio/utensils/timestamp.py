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

'''Timestamp utility class and package methods.

A condensed timestamp is of the format ``YYYYMMDD.HHMMSS.MMMMMM``, where
the three dot-separated elements are the year-month-dom, the hour-
minute-second and the microseconds. The ``.MMMMMM`` microseconds element
is optional.

An rfc3339 timestamp is of the format ``YYYY-MM-DDThh:mm:ss+hh:mm``,
where the ``YYYY-MM-DD`` element is the year-month-dom, the ``hh:mm:ss``
is the hour-minute-second, the ``+hh:mm`` is the offset from UTC, and
the ``T`` is the date-time separator. The UTC offset may also be of the
form ``-hh:mm``.

'''


from datetime import datetime
from datetime import timedelta
from datetime import tzinfo
import re


DEFAULT_SEPARATOR = '.'

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# "YYYYMMDD.HHMMSS.mmmmmm"
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
condensed_timestamp_re_string = r'''
    (?P<timestamp>
        (?P<year>\d{4})
        (?P<mon>\d{2})
        (?P<day>\d{2})\.
        (?P<hour>\d{2})
        (?P<min>\d{2})
        (?P<sec>\d{2})\.
        (?P<msec>\d{6})
        )
    '''
condensed_timestamp_re = re.compile(condensed_timestamp_re_string, re.VERBOSE)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# "YYYY-MM-DDTHH:MM:SS.mmmmmm+/-HH:MM"
# - - - - - - - - - - - - - - - - - - - - - - - - - - - -
rfc3339_timestamp_re_string = r'''
    (?P<timestamp>
        (?P<year>\d{4})-
        (?P<mon>\d{2})-
        (?P<day>\d{2})T
        (?P<hour>\d{2}):
        (?P<min>\d{2}):
        (?P<sec>\d{2})\.
        (?P<msec>\d{6})[+-]
        (?P<hoff>\d{2}):
        (?P<moff>\d{2})
        )
    '''
rfc3339_timestamp_re = re.compile(rfc3339_timestamp_re_string, re.VERBOSE)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# rfc3339 format timestamps require a timezone offset suffix. This will
# provide datetime entities with that capability.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TzUtc(tzinfo):  # pylint: disable=invalid-name
    '''A UTC time zone tzinfo class.

    rfc3339 compliant timestamps require a timezone offset suffix.
    This class defines a tzinfo subclass for the Coordinated Universal
    Time time zone 0.

    '''
    def utcoffset(self, dt):  # pylint: disable=unused-argument
        '''Return offset of local time from UTC.'''
        return timedelta(minutes=0)

    def dst(self, dt):  # pylint: disable=unused-argument
        '''Return the daylight saving time (DST) adjustment.'''
        return timedelta(0)

    def tzname(self, dt):  # pylint: disable=unused-argument
        '''Return the time zone name.'''
        return 'UTC'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TzPacific(tzinfo):  # pylint: disable=invalid-name
    '''A Pacific Time time zone tzinfo class.

    rfc3339 compliant timestamps require a timezone offset suffix.
    This class defines a tzinfo subclass for the US Pacific time zone.

    '''
    def utcoffset(self, dt):  # pylint: disable=unused-argument
        '''Return offset of local time from UTC.'''
        return timedelta(minutes=-480)

    def dst(self, dt):  # pylint: disable=unused-argument
        '''Return the daylight saving time (DST) adjustment.'''
        return timedelta(0)

    def tzname(self, dt):  # pylint: disable=unused-argument
        '''Return the time zone name.'''
        return 'UTC'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Package level versions of timestamp methods.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_condensed_timestamp(ts):  # pylint: disable=invalid-name
    '''Determine if ts is a valid condensed timestamp.'''

    if not isinstance(ts, str):
        return False

    m = condensed_timestamp_re.match(ts)  # pylint: disable=invalid-name
    if m is None or m.group('timestamp') != ts:
        return False
    else:
        return True


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def is_rfc3339_timestamp(ts):  # pylint: disable=invalid-name
    '''Determine if ts is a valid rfc3339 timestamp.'''

    if not isinstance(ts, str):
        return False

    m = rfc3339_timestamp_re.match(ts)  # pylint: disable=invalid-name
    if m is None or m.group('timestamp') != ts:
        return False
    else:
        return True


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def validate_condensed_timestamp(ts):  # pylint: disable=invalid-name
    '''Raise a ValueError if ts is not a valid condensed timestamp.'''

    if ts is None:
        raise ValueError('Expected timestamp, got None')

    if not is_condensed_timestamp(ts):
        raise ValueError('not a valid timestamp string: %s' % ts)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def validate_rfc3339_timestamp(ts):  # pylint: disable=invalid-name
    '''Raise a ValueError if ts is not a valid rfc3339 timestamp.'''

    if ts is None:
        raise ValueError('Expected timestamp, got None')

    if not is_rfc3339_timestamp(ts):
        raise ValueError('not a valid timestamp string: %s' % ts)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def to_condensed(source=None):
    '''Convert source to a condensed timestamp string.

    If the source is None, convert datetime.utcnow() to a timestamp.

    Note that the utc offset is ignored when converting rfc3339
    timestamps to condensed timestamps.

    '''

    if is_condensed_timestamp(source):
        return str(source)

    elif is_rfc3339_timestamp(source):
        fields = rfc3339_timestamp_re.match(source)
        if fields is not None:
            return (
                fields.group('year') +
                fields.group('mon') +
                fields.group('day') + "." +
                fields.group('hour') +
                fields.group('min') +
                fields.group('sec') + "." +
                fields.group('msec')
                )

    elif source is not None and not isinstance(source, datetime):
        raise ValueError(
            'Expected condensed or rfc3339 timestamp, or datetime'
            )

    if source is None:
        source = datetime.utcnow()

    return source.strftime('%Y%m%d.%H%M%S.%f')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def to_rfc3339(source=None, tzinfo=TzUtc()):
    '''Convert source to an rfc3339 timestamp string.

    If the source is None, convert datetime.utcnow() to rfc3339
    format.

    '''

    if is_rfc3339_timestamp(source):
        return str(source)

    elif is_condensed_timestamp(source):
        fields = condensed_timestamp_re.match(source)
        if fields is not None:
            source = datetime(
                year=int(fields.group('year')),
                month=int(fields.group('mon')),
                day=int(fields.group('day')),
                hour=int(fields.group('hour')),
                minute=int(fields.group('min')),
                second=int(fields.group('sec')),
                microsecond=int(fields.group('msec'))
                )

    elif source is not None and not isinstance(source, datetime):
        raise ValueError(
            'Expected condensed or rfc3339 timestamp, or datetime'
            )

    if source is None:
        source = datetime.utcnow()

    if source.tzinfo is None:
        source = source.replace(tzinfo=tzinfo)

    if source.microsecond is 0:
        return source.strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")
    else:
        return source.isoformat()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def to_datetime(source):
    '''Convert source to a datetime object.'''
    if isinstance(source, datetime):
        return source

    if is_condensed_timestamp(source):
        (date, time, microtime) = source.split('.')

    elif is_rfc3339_timestamp(source):

        fields = rfc3339_timestamp_re.match(source)

        date = (
            fields.group('year') + fields.group('mon') + fields.group('day')
            )
        time = (
            fields.group('hour') + fields.group('min') + fields.group('sec')
            )
        microtime = fields.group('msec')

    elif source is not None:
        raise ValueError(
            'Expected condensed or rfc3339 timestamp, or datetime'
            )

    return datetime(
        *[int(x) for x in (
            date[0:4], date[4:6], date[6:8],
            time[0:2], time[2:4], time[4:6],
            microtime
            )]
        )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def add_condensed_timestamp(
        prefix,
        ts=None,
        separator=DEFAULT_SEPARATOR,
        suffix=None
        ):  # pylint: disable=invalid-name, bad-continuation
    '''Add a timestamp to a string.

    Parameters:

        prefix (str)
            The string to which the timestamp is to be appended.

        ts
            The timestamp to add. This can be a string, a Timestamp
            object or a datetime object. If ts is None,
            datetime.utcnow() will be used.

        suffix (str, optional)
            An optional string to add after the timestamp.

        separator (str, optional)
            A string to use as a separator between prefix, timestamp
            and suffix. Default: timestamp.DEFAULT_SEPARATOR

    '''
    try:
        proper_ts = to_condensed(ts)
    except AttributeError:
        raise ValueError('not a valid timestamp: %s' % ts)

    stamped = separator.join([prefix, proper_ts])
    if suffix is not None:
        stamped = separator.join([stamped, suffix])

    return stamped


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def extract_condensed_timestamp(a_string):
    '''Extract a timestamp from a string.

    We assume the timestamp is of the format 'YYYYMMDD.HHMMSS.MMMMMM'.

    It need not be dot-separated from the rest of the string.
    '''
    ts_match = condensed_timestamp_re.search(a_string)

    if ts_match is None:
        return None

    return ts_match.group('timestamp')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def extract_condensed_to_datetime(a_string):
    '''Extract a timestamp from a string and convert it to a datetime.

    We assume the timestamp is of the format 'YYYYMMDD.HHMMSS.MMMMMM'.

    It need not be dot-separated from the rest of the string.
    '''
    ts_match = condensed_timestamp_re.search(a_string)

    if ts_match is None:
        return None

    return to_datetime(ts_match.group('timestamp'))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def except_condensed_timestamp(a_string, separator=DEFAULT_SEPARATOR):
    '''Return the result of removing a timestamp from a string.

    Returns:

        (str) The result of removing the timestamp and collapsing the
        resulting pair of consecutive separators into one.

    '''
    except_condensed_timestamp_re = re.compile(
        r'^(?:(?P<prefix>.*)' + separator + ')?' +
        condensed_timestamp_re_string +
        '(?:' + separator + r'(?P<suffix>.*))?$',
        re.VERBOSE
        )
    except_ts_match = except_condensed_timestamp_re.match(a_string)

    if except_ts_match is None:
        return a_string

    return separator.join([
        s for s in [
            except_ts_match.group('prefix'),
            except_ts_match.group('suffix')
            ]
        if s is not None
        ])
    # return (
    #     except_ts_match.group('prefix')
    #     + separator
    #     + except_ts_match.group('suffix')
    #     )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Timestamp(object):
    '''Construct, extract and manipulate timestamps.'''
    def __init__(self):
        '''Initialize a Timestamp instance.'''

        super(Timestamp, self).__init__()
