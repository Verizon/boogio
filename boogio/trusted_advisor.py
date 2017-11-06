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
'''Manage trusted advisor check auditing.'''

import json
import logging

import boto3
import botocore.exceptions

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        '''Placeholder handler.'''
        def emit(self, record):
            '''Pylint compliant docstring.'''
            pass

logging.getLogger(__name__).addHandler(NullHandler())


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TrustedAdvisorCheckManager(object):
    '''Manage trusted advisor check polling and reporting.

    Arguments:

        profile_name (str, optional):
            The AWS profile name to use when establishing a boto3
            session. If not provided, the session will be established
            following the search order described in
            http://boto3.readt hedocs.io/en/latest/guide/configuration.html.

    Upon initialization, a ``TrustedAdvisorCheckManager`` instance
    retrieves the records for all AWS Trusted Advisor checks
    available. These include the Check descriptions and the Check
    Results. Class methods provide access to the Checks and the
    Results by Check Category, summary reporting and reports in the
    Argus Bundle format, and Check refresh.

    '''

    # The categories of checks Trusted Advisor carries out.
    # TODO: This shouldn't require hard coding as it can be obtained
    # from the retrieve checks.
    categories = [
        'performance', 'security', 'fault_tolerance', 'cost_optimizing'
        ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(
            self,
            profile_name=None
            ):  # pylint: disable=bad-continuation
        '''Initialize a TrustedAdvisorCheckManager instance.'''

        # A class-identifying logger for member methods.
        logger_name = '%s.%s' % (__name__, self.__class__.__name__)
        self._logger = logging.getLogger(logger_name)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Create a boto3 support session.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        session_kwargs = {'region_name': 'us-east-1'}
        if profile_name:
            session_kwargs.update({'profile_name': profile_name})
        self._logger.info('initializing AWS session...')
        self._session = boto3.session.Session(**session_kwargs)
        self._client = self._session.client('support')

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Retrieve defined Trusted Advisor checks.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        self._logger.info('retrieving trusted advisor checks...')
        self._checks = self._client.describe_trusted_advisor_checks(
            language='en'
            )['checks']
        self.check_index_by_id = dict([(c['id'], c) for c in self._checks])

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Retrieve current check results.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        self._logger.info('retrieving trusted advisor check results...')
        self.result_index_by_id = dict([
            (
                check_id,
                self._client.describe_trusted_advisor_check_result(
                    checkId=check_id
                    )['result']
                )
            for check_id in self.check_index_by_id
            ])

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Retrieve current check refresh statuses.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        self.update_refresh_statuses()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _valid_category(self, category):
        '''Return True if category is valid, False otherwise.'''
        return category in self.categories

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _require_valid_category(self, category):
        '''Log an error and raise a ValueError if category is not valid.'''
        if not self._valid_category(category):
            err_msg = '%s is not a valid Trusted Advisor check category'
            self._logger.error(err_msg, category)
            raise ValueError(err_msg % category)
        else:
            return True

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _valid_check_id(self, check_id):
        '''Return True if check_id is valid, False otherwise.'''
        return check_id in self.check_index_by_id

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _require_valid_check_id(self, check_id):
        '''Log an error and raise a ValueError if check_id is not valid.'''
        if not self._valid_check_id(check_id):
            err_msg = '%s is not a valid Trusted Advisor Check ID'
            self._logger.error(err_msg, check_id)
            raise ValueError(err_msg % check_id)
        else:
            return True

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _check_field_by_check_id(self, check_id, field):
        '''Return the requested field of a check, identified by id.

        The ``field`` argument must be one of ``name``, ``category``,
        ``description`` or ``metadata``.

        '''
        self._require_valid_check_id(check_id)

        allowed_fields = ['name', 'category', 'description', 'metadata']
        if field not in allowed_fields:
            err_msg = (
                'unknown trusted advisor check field: %s'
                ' (must be one of %s)'
                )
            self._logger.error(err_msg, field, allowed_fields)
            raise ValueError(err_msg % (field, allowed_fields))

        # This is legacy and predates the _require_valid_check_id()
        # check above. I'll leave it in for now to remind me to
        # consider going back to just a warning, but this should be
        # unreachable code.
        if check_id not in self.check_index_by_id:
            err_msg = 'unknown trusted advisor check id: %s'
            self._logger.warn(err_msg, check_id)
            return None
        return self.check_index_by_id[check_id][field]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _refresh_status_field_by_check_id(self, check_id, field):
        '''Return the requested field of a refresh_status, identified by id.

        The ``field`` argument must be one of ``status`` or
        ``millisUntilNextRefreshable``.

        '''
        self._require_valid_check_id(check_id)

        allowed_fields = ['status', 'millisUntilNextRefreshable']
        if field not in allowed_fields:
            err_msg = (
                'unknown trusted advisor refresh status field: %s'
                ' (must be one of %s)'
                )
            self._logger.error(err_msg, field, allowed_fields)
            raise ValueError(err_msg % (field, allowed_fields))

        if check_id not in self.refresh_status_index_by_id:
            err_msg = 'unknown trusted advisor refresh status id: %s'
            self._logger.warn(err_msg, check_id)
            return None
        return self.refresh_status_index_by_id[check_id][field]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def name(self, check_id):
        '''Return the name of a check, identified by id.'''
        self._require_valid_check_id(check_id)
        return self._check_field_by_check_id(check_id, 'name')

    def category(self, check_id):
        '''Return the category of a check, identified by id.'''
        self._require_valid_check_id(check_id)
        return self._check_field_by_check_id(check_id, 'category')

    def description(self, check_id):
        '''Return the description of a check, identified by id.'''
        self._require_valid_check_id(check_id)
        return self._check_field_by_check_id(check_id, 'description')

    def metadata(self, check_id):
        '''Return the metadata of a check, identified by id.'''
        self._require_valid_check_id(check_id)
        return self._check_field_by_check_id(check_id, 'metadata')

    def status(self, check_id):
        '''Return the refresh status of a check, identified by id.'''
        self._require_valid_check_id(check_id)
        return self._refresh_status_field_by_check_id(check_id, 'status')

    def refresh_delay_msec(self, check_id):
        '''Return the refresh delay of a check, identified by id.'''
        self._require_valid_check_id(check_id)
        return self._refresh_status_field_by_check_id(
            check_id, 'millisUntilNextRefreshable'
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def check_ids(self, *categories):
        '''Return a list of the check IDs for a set of categories.'''

        if categories:
            for category in categories:
                self._require_valid_category(category)
            categories = categories
        else:
            categories = self.categories

        return [
            check_id
            for check_id, check in self.check_index_by_id.items()
            if check['category'] in categories
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def checks(self, *categories):
        '''Return the available Trusted Advisor checks.

        Arguments:

            categories (tuple of str, optional):
                The Trusted Advisor categories for which to return the
                check definitions. If not specified, all checks will
                be returned.
        '''

        if categories:
            for category in categories:
                self._require_valid_category(category)
            categories = categories
        else:
            categories = self.categories

        return [
            x for x in self._checks
            if x['category'] in categories
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def results(self, *categories):
        '''Return the available Trusted Advisor check results.

        Arguments:

            categories (tuple of str, optional):
                The Trusted Advisor categories for which to return the
                check definitions. If not specified, all checks will
                be returned.
        '''

        if categories:
            for category in categories:
                self._require_valid_category(category)
            categories = categories
        else:
            categories = self.categories

        return [
            x for x in self.result_index_by_id.values()
            if self.check_index_by_id[x['checkId']]['category'] in categories
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refresh_statuses(self, *categories):
        '''Return the available Trusted Advisor check refresh statuses.

        Arguments:

            categories (tuple of str, optional):
                The Trusted Advisor categories for which to return the
                refresh statuses. If not specified, all checks will be
                returned.
        '''

        if categories:
            for category in categories:
                self._require_valid_category(category)
            categories = categories
        else:
            categories = self.categories

        return [
            x for x in self.refresh_status_index_by_id.values()
            if self.check_index_by_id[x['checkId']]['category'] in categories
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def update_refresh_statuses(self):
        '''Retrieve the current check refresh statuses.'''

        self._logger.info(
            'retrieving trusted advisor check refresh statuses...'
            )

        self._refresh_statuses = (
            self._client.describe_trusted_advisor_check_refresh_statuses(
                checkIds=self.check_index_by_id.keys()
                )
            )['statuses']

        self.refresh_status_index_by_id = dict([
            (s['checkId'], s) for s in self._refresh_statuses
            ])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def refresh(self, *categories):
        '''Refresh Trusted Advisor checks.

        Arguments:

            categories (tuple of str, optional):
                The Trusted Advisor categories for which to refresh
                checks. If not specified, all checks will be
                refreshed.
        '''

        if categories:
            for category in categories:
                self._require_valid_category(category)
            categories = categories
        else:
            categories = self.categories

        log_msg = 'refreshing categories: %s' % ', '.join(categories)
        self._logger.info(log_msg)

        check_ids = self.check_ids(*categories)
        requested_refresh_count = 0
        auto_refresh_only_count = 0

        self._logger.info(
            'requesting refresh of %s trusted advisor checks...',
            len(check_ids)
            )
        for check_id in check_ids:

            try:
                self._client.refresh_trusted_advisor_check(checkId=check_id)
                requested_refresh_count += 1

            except botocore.exceptions.ClientError as err:
                # This indicates a Check that is only auto-refreshable.
                if err.response['Error']['Code'] == (
                        'InvalidParameterValueException'
                        ):  # pylint: disable=bad-continuation
                    auto_refresh_only_count += 1
                    self._logger.info(
                        'manual refresh not allowed: %s (%s: %s)',
                        check_id, self.category(check_id), self.name(check_id)
                        )
                else:
                    self._logger.error(str(err))
                    raise err

        self._logger.info(
            '%s refresh requests (of %s total) were not manually refreshable',
            auto_refresh_only_count, requested_refresh_count
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _raw_summary_data(self, categories, exclude_checks=None):
        '''Return data summarizing the current checks status.'''

        self._logger.info('generating raw summary data...')

        for category in categories:
            self._require_valid_category(category)

        exclude_checks = exclude_checks or []

        report_data = []
        for category in categories:
            self._logger.info('current category: %s', category)
            category_checks = [
                check for check in self.checks(category)
                if check['name'] not in exclude_checks
                ]

            self._logger.info(
                'current category check count: %s', len(category_checks)
                )

            for check in sorted(category_checks, key=lambda x: x['name']):

                check_id = check['id']

                check_result = self.result_index_by_id[check_id]
                timestamp = check_result.get('timestamp')
                resources_summary = check_result['resourcesSummary']

                num_warnings, num_errors = (0, 0)
                if resources_summary['resourcesFlagged']:
                    assert 'flaggedResources' in check_result
                    for resource in check_result['flaggedResources']:
                        if resource['status'] == 'warning':
                            num_warnings += 1
                        elif resource['status'] == 'error':
                            num_errors += 1

                datum = {
                    'check_id': check_id,
                    'category': category,
                    'status': check_result['status'],
                    'processed': resources_summary['resourcesProcessed'],
                    'flagged': resources_summary['resourcesFlagged'],
                    'suppressed': resources_summary['resourcesSuppressed'],
                    'ignored': resources_summary['resourcesIgnored'],
                    'warnings': num_warnings,
                    'errors': num_errors,
                    'timestamp': timestamp,
                    'name': self.name(check_id),
                    }
                self._logger.debug('datum: %s', str(datum))
                report_data.append(datum)

        return report_data

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def summary_report(
            self,
            categories=None,
            exclude_checks=None,
            format='text',
            field_hints=True
            ):  # pylint: disable=bad-continuation
        '''Return a report summarizing the current checks status.

        Arguments:

            categories (list of str, optional):
                The Trusted Advisor categories on which to report. If
                not specified, all checks will be included.

            exclude_checks (list of str, optional):
                A list of check names to exclude. If not specified,
                all checks from the selected categories will be
                included.

            format ('text', list', 'raw' or 'json', optional):
                If 'text' (the default), return the result of joining
                the list with newlines. If 'list', return a list of
                strings representing the lines of a printed report. If
                'raw', return a list of dicts representing the fields
                in each line of the report. If 'json', return the raw
                result as a JSON string.

            field_hints (bool, default True):
                If ``True``, include mnemonic characters in the
                ``text`` or ``line`` output for the numeric fields to
                indicate what they represent. These include the
                "processed", "flagged", "suppressed", "ignored",
                "warnings" and "errors" fields. The mnemonic is the
                first letter of the field name, capitalized.

        '''
        self._logger.info('creating %s summary report...', format)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Note numerous intermediate return points depending
        # on the format requested.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        if categories is None:
            categories = self.categories
        self._logger.info('categories: %s', str(categories))

        if exclude_checks:
            self._logger.info('excluding checks: %s', str(exclude_checks))

        report_data = self._raw_summary_data(categories, exclude_checks)

        if format == 'raw':
            return report_data

        if format == 'json':
            return json.dumps(report_data)

        field_order = [
            'check_id',
            'category',
            'status',
            'processed',
            'flagged',
            'suppressed',
            'ignored',
            'warnings',
            'errors',
            'timestamp',
            'name',
            ]

        if field_hints:
            # Make sure the field order makes the field hint
            # characters align with the right fields!
            line_format = (
                '{}\t{}\t{}\tP: {}\tF: {}\tS: {}\tI: {}\tW: {}\tE: {}\t{}\t{}'
                )
            lines_list = [
                line_format.format(
                    *[line_data[field] for field in field_order]
                    )
                for line_data in report_data
                ]
        else:
            lines_list = [
                '\t'.join(
                    [line_data[field] for field in field_order]
                    )
                for line_data in report_data
                ]

        if format == 'list':
            return lines_list

        if format == 'text':
            return '\n'.join(lines_list)

        # We didn't find a known format to return, so we log and raise
        # an error.
        err_msg = 'unknown report format: %s'
        self._logger.error(err_msg, format)
        raise ValueError(err_msg % format)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def argus_report(
            self,
            categories=None,
            exclude_checks=None,
            format='raw'
            ):  # pylint: disable=bad-continuation
        '''Return an Argus monitoring bundle for the indicated categories.

        Arguments:

            categories (list of str, optional):
                The Trusted Advisor categories on which to report. If
                not specified, all checks will be included.

            exclude_checks (list of str, optional):
                A list of check names to exclude. If not specified,
                all checks from the selected categories will be
                included.

            format ('raw' or 'json', optional):
                If 'raw' (the default), return a list of dicts
                representing the fields in each line of the report. If
                'json', return the raw result as a JSON string.

        '''

        self._logger.info('creating %s argus report...', format)
        if categories is None:
            categories = self.categories
        self._logger.info('categories: %s', str(categories))

        ta_url_template = (
            'https://console.aws.amazon.com/'
            'trustedadvisor/home?#/category/{category}'
            )

        report_data = self._raw_summary_data(categories, exclude_checks)
        argus_bundle_data = {
            'name': 'Trusted Advisor',
            'tagline': 'Trusted Advisor report: {}'.format(
                ', '.join(categories)
                ),
            'refresh': 300,
            'monitors': []
            }

        for check_data in report_data:

            num_inform = check_data['ignored'] + check_data['suppressed']
            num_warn = check_data['warnings']
            num_error = check_data['errors']
            num_ok = (
                check_data['processed'] -
                (num_inform + num_warn + num_error)
                )

            inform_notes = []
            if check_data['ignored']:
                inform_notes.append(
                    'Checks of {} resource{} being ignored.'.format(
                        check_data['ignored'],
                        ' is' if check_data['ignored'] == 1 else 's are'
                        )
                    )
            if check_data['suppressed']:
                inform_notes.append(
                    'Checks of {} resource{} being suppressed.'.format(
                        check_data['suppressed'],
                        ' is' if check_data['suppressed'] == 1 else 's are'
                        )
                    )
            if num_inform + num_warn + num_error + num_ok == 0:
                num_inform = 1
                inform_notes.append(
                    'There were no resources meeting the criteria for'
                    ' this Trusted Advisor check.'
                    )

            monitor_data = {
                'name': '{}: {}'.format(
                    check_data['category'], check_data['name']
                    ),
                # 'tagline': check_data['check_id'],
                'description': check_data['check_id'],
                'timestamp': check_data['timestamp'],
                'references': [
                    {
                        'name': 'Trusted Advisor',
                        'url': ta_url_template.format(
                            category=check_data['category']
                            )
                        }
                    ],
                'statusItems': [
                    {
                        'status': 'ok',
                        'count': num_ok
                        },
                    {
                        'status': 'inform',
                        'count': num_inform,
                        'notes': list(inform_notes)
                        },
                    {
                        'status': 'warn',
                        'count': num_warn
                        },
                    {
                        'status': 'fail',
                        'count': num_error
                        },
                    ]
                }
            argus_bundle_data['monitors'].append(monitor_data)

        if format == 'raw':
            return argus_bundle_data

        if format == 'json':
            return json.dumps(argus_bundle_data)
