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

'''Test cases for the trusted_advisor.py module.'''

import unittest

from boogio import site_boogio
from boogio import trusted_advisor

TEST_PROFILE_NAME = site_boogio.test_profile_name

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
class TestTrustedAdvisorCheckManagerClass(unittest.TestCase):
    '''Tests for TrustedAdvisorCheckManager class definitions.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_trusted_advisor_check_manager_class_constants(self):
        '''Test TrustedAdvisorCheckManager class constant definitions.'''
        self.assertItemsEqual(
            trusted_advisor.TrustedAdvisorCheckManager.categories,
            [
                'cost_optimizing',
                'performance',
                'security',
                'fault_tolerance'
                ]
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTrustedAdvisorCategoryError(unittest.TestCase):
    '''Tests for TrustedAdvisorCheckManager category name errors.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class common fixture setup.'''
        cls.tacm = trusted_advisor.TrustedAdvisorCheckManager(
            profile_name=TEST_PROFILE_NAME
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_trusted_advisor_valid_category(self):
        '''Test TrustedAdvisorCheckManager._valid_category().'''

        for category in self.tacm.categories:
            self.assertTrue(self.tacm._valid_category(category))

        self.assertFalse(self.tacm._valid_category(''))
        self.assertFalse(self.tacm._valid_category('foo'))
        self.assertFalse(self.tacm._valid_category(None))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_trusted_advisor_require_valid_category(self):
        '''Test TrustedAdvisorCheckManager.require_valid_category().'''

        for category in self.tacm.categories:
            self.assertTrue(self.tacm._require_valid_category(category))

        with self.assertRaises(ValueError):
            self.tacm._require_valid_category('')

        with self.assertRaises(ValueError):
            self.tacm._require_valid_category('foo')

        with self.assertRaises(ValueError):
            self.tacm._require_valid_category(None)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_trusted_advisor_method_category_error(self):
        '''Test TrustedAdvisorCheckManager category errors in method calls.'''

        with self.assertRaises(ValueError):
            self.tacm.check_ids('foo')
        with self.assertRaises(ValueError):
            self.tacm.check_ids(self.tacm.categories[0], 'foo')

        with self.assertRaises(ValueError):
            self.tacm.checks('foo')
        with self.assertRaises(ValueError):
            self.tacm.checks(self.tacm.categories[0], 'foo')

        with self.assertRaises(ValueError):
            self.tacm.results('foo')
        with self.assertRaises(ValueError):
            self.tacm.results(self.tacm.categories[0], 'foo')

        with self.assertRaises(ValueError):
            self.tacm.refresh_statuses('foo')
        with self.assertRaises(ValueError):
            self.tacm.refresh_statuses(self.tacm.categories[0], 'foo')

        with self.assertRaises(ValueError):
            self.tacm._raw_summary_data(categories=['foo'])
        with self.assertRaises(ValueError):
            self.tacm._raw_summary_data(
                categories=[self.tacm.categories[0], 'foo']
                )

        with self.assertRaises(ValueError):
            self.tacm.summary_report(categories=['foo'])
        with self.assertRaises(ValueError):
            self.tacm.summary_report(
                categories=[self.tacm.categories[0], 'foo']
                )

        with self.assertRaises(ValueError):
            self.tacm.argus_report(categories=['foo'])
        with self.assertRaises(ValueError):
            self.tacm.argus_report(
                categories=[self.tacm.categories[0], 'foo']
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTrustedAdvisorCheckIdError(unittest.TestCase):
    '''Tests for TrustedAdvisorCheckManager Check ID value errors.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class common fixture setup.'''
        cls.tacm = trusted_advisor.TrustedAdvisorCheckManager(
            profile_name=TEST_PROFILE_NAME
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_trusted_advisor_valid_check_id(self):
        '''Test TrustedAdvisorCheckManager._valid_check_id().'''

        for check_id in self.tacm.check_ids():
            self.assertTrue(self.tacm._valid_check_id(check_id))

        self.assertFalse(self.tacm._valid_check_id(''))
        self.assertFalse(self.tacm._valid_check_id('foo'))
        self.assertFalse(self.tacm._valid_check_id(None))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_trusted_advisor_require_valid_check_id(self):
        '''Test TrustedAdvisorCheckManager.require_valid_check_id().'''

        for check_id in self.tacm.check_ids():
            self.assertTrue(self.tacm._require_valid_check_id(check_id))

        with self.assertRaises(ValueError):
            self.tacm._require_valid_check_id('')

        with self.assertRaises(ValueError):
            self.tacm._require_valid_check_id('foo')

        with self.assertRaises(ValueError):
            self.tacm._require_valid_check_id(None)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_trusted_advisor_method_check_id_error(self):
        '''Test TrustedAdvisorCheckManager Check ID errors in method calls.'''

        with self.assertRaises(ValueError):
            self.tacm._check_field_by_check_id('foo', 'name')

        with self.assertRaises(ValueError):
            self.tacm._refresh_status_field_by_check_id('foo', 'status')

        with self.assertRaises(ValueError):
            self.tacm.name('foo')

        with self.assertRaises(ValueError):
            self.tacm.category('foo')

        with self.assertRaises(ValueError):
            self.tacm.description('foo')

        with self.assertRaises(ValueError):
            self.tacm.metadata('foo')

        with self.assertRaises(ValueError):
            self.tacm.status('foo')

        with self.assertRaises(ValueError):
            self.tacm.refresh_delay_msec('foo')


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTrustedAdvisorCheckManagerInit(unittest.TestCase):
    '''Tests for TrustedAdvisorCheckManager initialization.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class common fixture setup.'''
        cls.tacm = trusted_advisor.TrustedAdvisorCheckManager(
            profile_name=TEST_PROFILE_NAME
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_trusted_advisor_init(self):
        '''Test initialization of a TrustedAdvisorCheckManager instance.'''

        # tacm = trusted_advisor.TrustedAdvisorCheckManager(
        #     profile_name=TEST_PROFILE_NAME
        #     )
        self.assertIsNotNone(self.tacm)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Check content of the checks() and check_index_by_id
        # attributes.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        # print self.tacm.checks()[0].keys()
        # print [x['category'] for x in self.tacm.checks()]

        self.assertIsNotNone(self.tacm.checks())
        self.assertNotEqual(self.tacm.checks(), [])

        for category in self.tacm.categories:
            self.assertIsNotNone(self.tacm.checks(category))
            self.assertNotEqual(self.tacm.checks(category), [])

        self.assertIsNotNone(self.tacm.check_index_by_id)
        self.assertNotEqual(self.tacm.check_index_by_id.keys(), [])

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Check content of the results() and result_index_by_id
        # attributes.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        # print self.tacm.results()[0].keys()

        self.assertIsNotNone(self.tacm.results())
        self.assertNotEqual(self.tacm.results(), [])

        for category in self.tacm.categories:
            self.assertIsNotNone(self.tacm.results(category))
            self.assertNotEqual(self.tacm.results(category), [])

        self.assertIsNotNone(self.tacm.result_index_by_id)
        self.assertNotEqual(self.tacm.result_index_by_id.keys(), [])

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Check content of the refresh_statuses() and
        # refresh_status_index_by_id attributes.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertIsNotNone(self.tacm.refresh_statuses())
        self.assertNotEqual(self.tacm.refresh_statuses(), [])

        for category in self.tacm.categories:
            self.assertIsNotNone(self.tacm.refresh_statuses(category))
            self.assertNotEqual(self.tacm.refresh_statuses(category), [])

        self.assertIsNotNone(self.tacm.refresh_status_index_by_id)
        self.assertNotEqual(self.tacm.refresh_status_index_by_id.keys(), [])

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Test that the indices track the same check ids.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertItemsEqual(
            self.tacm.check_index_by_id.keys(),
            self.tacm.result_index_by_id.keys()
            )
        self.assertItemsEqual(
            self.tacm.check_index_by_id.keys(),
            self.tacm.refresh_status_index_by_id.keys()
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_trusted_advisor_check_ids(self):
        '''Test TrustedAdvisorCheckManager.check_ids().'''

        self.assertEqual(
            len(self.tacm.check_ids()),
            len(self.tacm.check_index_by_id.keys())
            )

        self.assertItemsEqual(
            self.tacm.check_ids(),
            self.tacm.check_index_by_id.keys()
            )

        self.assertItemsEqual(
            self.tacm.check_ids(),
            self.tacm.result_index_by_id.keys()
            )

        category_check_ids = {}
        for category in self.tacm.categories:
            category_check_ids[category] = [
                check_id
                for check_id in self.tacm.check_index_by_id.keys()
                if self.tacm.category(check_id) == category
                ]
            self.assertItemsEqual(
                self.tacm.check_ids(category),
                category_check_ids[category]
                )

        self.assertItemsEqual(
            self.tacm.check_ids(),
            self.tacm.check_ids(*self.tacm.categories)
            )

        self.assertItemsEqual(
            self.tacm.check_ids(*self.tacm.categories[:2]),
            (
                category_check_ids[self.tacm.categories[0]] +
                category_check_ids[self.tacm.categories[1]]
                )
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_trusted_advisor_update_refresh_statuses(self):
        '''Test cases for update_refresh_statuses().'''

        # Harsh, harsh, harsh. :)
        # pylint: disable=protected-access
        self.tacm._refresh_statuses = []
        # pylint: enable=protected-access
        self.tacm.refresh_status_index_by_id = {}

        self.assertEqual(self.tacm.refresh_status_index_by_id, {})
        self.assertEqual(self.tacm.refresh_statuses(), [])

        self.tacm.update_refresh_statuses()

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Check content of the refresh_statuses() and
        # refresh_status_index_by_id attributes.
        # - - - - - - - - - - - - - - - - - - - - - - - -
        self.assertIsNotNone(self.tacm.refresh_statuses())
        self.assertNotEqual(self.tacm.refresh_statuses(), [])

        for category in self.tacm.categories:
            self.assertIsNotNone(self.tacm.refresh_statuses(category))
            self.assertNotEqual(self.tacm.refresh_statuses(category), [])

        self.assertIsNotNone(self.tacm.refresh_status_index_by_id)
        self.assertNotEqual(self.tacm.refresh_status_index_by_id.keys(), [])

        self.assertItemsEqual(
            self.tacm.check_index_by_id.keys(),
            self.tacm.refresh_status_index_by_id.keys()
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTrustedAdvisorCheckManagerAttributeByCheckId(unittest.TestCase):
    '''Tests for attribute-by-check-id methods.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class common fixture setup.'''
        cls.tacm = trusted_advisor.TrustedAdvisorCheckManager(
            profile_name=TEST_PROFILE_NAME
            )

        # We'll use the first check in each category to test that
        # we're getting valid results from these methods.

        cls.sample_category_check_id = {
            cls.tacm.checks(category)[0]['id']: category
            for category in cls.tacm.categories
            }

        cls.sample_name_check_id = {
            cls.tacm.checks(category)[0]['id']:
            cls.tacm.checks(category)[0]['name']
            for category in cls.tacm.categories
            }

        cls.sample_description_check_id = {
            cls.tacm.checks(category)[0]['id']:
            cls.tacm.checks(category)[0]['description']
            for category in cls.tacm.categories
            }

        cls.sample_metadata_check_id = {
            cls.tacm.checks(category)[0]['id']:
            cls.tacm.checks(category)[0]['metadata']
            for category in cls.tacm.categories
            }

        cls.sample_refresh_status_check_id = {
            cls.tacm.refresh_statuses(category)[0]['checkId']:
            cls.tacm.refresh_statuses(category)[0]['status']
            for category in cls.tacm.categories
            }

        cls.sample_refresh_delay_msec_check_id = {
            cls.tacm.refresh_statuses(category)[0]['checkId']:
            cls.tacm.refresh_statuses(category)[0][
                'millisUntilNextRefreshable'
                ]
            for category in cls.tacm.categories
            }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_illegal_attribute(self):
        '''Test TrustedAdvisorCheckManager._check_field_by_check_id() error.'''

        # pylint: disable=protected-access
        with self.assertRaises(ValueError):
            self.tacm._check_field_by_check_id(
                self.tacm.checks()[0]['id'], 'blort'
                )
        # pylint: enable=protected-access

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_check_name(self):
        '''Test TrustedAdvisorCheckManager.name().'''

        for check_id, name in self.sample_name_check_id.items():
            self.assertEqual(self.tacm.name(check_id), name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_check_category(self):
        '''Test TrustedAdvisorCheckManager.category().'''

        for check_id, category in self.sample_category_check_id.items():
            self.assertEqual(self.tacm.category(check_id), category)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_check_description(self):
        '''Test TrustedAdvisorCheckManager.description().'''

        for check_id, description in self.sample_description_check_id.items():
            self.assertEqual(self.tacm.description(check_id), description)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_check_metadata(self):
        '''Test TrustedAdvisorCheckManager.metadata().'''

        for check_id, metadata in self.sample_metadata_check_id.items():
            self.assertEqual(self.tacm.metadata(check_id), metadata)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_refresh_status(self):
        '''Test TrustedAdvisorCheckManager.refresh_status().'''

        for check_id, status in self.sample_refresh_status_check_id.items():
            self.assertEqual(
                self.tacm.status(check_id), status
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_refresh_delay_msec(self):
        '''Test TrustedAdvisorCheckManager.refresh_delay_msec().'''

        for check_id, delay_msec in (
                self.sample_refresh_delay_msec_check_id.items()
                ):  # pylint: disable=bad-continuation
            self.assertEqual(
                self.tacm.refresh_delay_msec(check_id), delay_msec
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTrustedAdvisorCheckManagerReports(unittest.TestCase):
    '''Tests for TrustedAdvisorCheckManager reports.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class common fixture setup.'''

        cls.tacm = trusted_advisor.TrustedAdvisorCheckManager(
            profile_name=TEST_PROFILE_NAME
            )

        # This is used for the check_report() test cases.
        cls.sample_check_id = {
            category: cls.tacm.checks(category)[0]['id']
            for category in cls.tacm.categories
            }

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_summary_report_unknown_format(self):
        '''Test TrustedAdvisorCheckManager.summary_report() format error.'''

        with self.assertRaises(ValueError):
            self.tacm.summary_report(format='blort')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_summary_report_text(self):
        '''Test TrustedAdvisorCheckManager.summary_report() as text.'''

        report = self.tacm.summary_report()
        self.assertTrue(isinstance(report, str))

        report = self.tacm.summary_report(format='text')
        self.assertTrue(isinstance(report, str))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_summary_report_list(self):
        '''Test TrustedAdvisorCheckManager.summary_report() as a list.'''

        report = self.tacm.summary_report(format='list')
        self.assertTrue(isinstance(report, list))
        self.assertEqual(
            list(set(
                [isinstance(x, str) for x in report]
                )),
            [True]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_summary_report_list_one_category(self):
        '''Test TrustedAdvisorCheckManager.summary_report().'''

        report = self.tacm.summary_report(['security'], format='list')
        self.assertTrue(isinstance(report, list))
        self.assertEqual(
            list(set(
                [isinstance(x, str) for x in report]
                )),
            [True]
            )

        report = self.tacm.summary_report(['security'], format='raw')
        self.assertTrue(isinstance(report, list))
        self.assertEqual(
            list(set(
                [isinstance(x, dict) for x in report]
                )),
            [True]
            )
        self.assertEqual(
            list(set([self.tacm.category(x['check_id']) for x in report])),
            ['security']
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_summary_report_list_multi_category(self):
        '''Test TrustedAdvisorCheckManager.summary_report().'''

        report = self.tacm.summary_report(
            ['security', 'fault_tolerance'],
            format='list'
            )
        self.assertTrue(isinstance(report, list))
        self.assertEqual(
            list(set(
                [isinstance(x, str) for x in report]
                )),
            [True]
            )

        report = self.tacm.summary_report(
            ['security', 'fault_tolerance'],
            format='raw'
            )
        self.assertTrue(isinstance(report, list))
        self.assertEqual(
            list(set(
                [isinstance(x, dict) for x in report]
                )),
            [True]
            )
        self.assertItemsEqual(
            list(set(
                [self.tacm.category(x['check_id']) for x in report]
                )),
            ['security', 'fault_tolerance']
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_summary_report_raw(self):
        '''Test TrustedAdvisorCheckManager.summary_report() as raw data.'''

        report = self.tacm.summary_report(format='raw')
        self.assertTrue(isinstance(report, list))
        self.assertEqual(
            list(set(
                [isinstance(x, dict) for x in report]
                )),
            [True]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_summary_report_json(self):
        '''Test TrustedAdvisorCheckManager.summary_report() as JSON.'''

        report = self.tacm.summary_report(format='json')
        self.assertTrue(isinstance(report, str))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTrustedAdvisorCheckManagerArgusReport(unittest.TestCase):
    '''Tests for TrustedAdvisorCheckManager argus report.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class common fixture setup.'''

        cls.tacm = trusted_advisor.TrustedAdvisorCheckManager(
            profile_name=TEST_PROFILE_NAME
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_argus_report_raw(self):
        '''Test TrustedAdvisorCheckManager.argus_report() as raw data.'''

        report = self.tacm.argus_report(['security'], format='raw')

        self.assertIn('name', report)
        self.assertIn('tagline', report)
        self.assertIn('monitors', report)
        self.assertTrue(isinstance(report['monitors'], list))
        self.assertEqual(
            list(set(
                [isinstance(x, dict) for x in report['monitors']]
                )),
            [True]
            )
        self.assertEqual(
            list(set(
                ['name' in x for x in report['monitors']]
                )),
            [True]
            )
        self.assertEqual(
            list(set(
                ['timestamp' in x for x in report['monitors']]
                )),
            [True]
            )
        self.assertEqual(
            list(set(
                ['references' in x for x in report['monitors']]
                )),
            [True]
            )
        self.assertEqual(
            list(set(
                ['statusItems' in x for x in report['monitors']]
                )),
            [True]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_argus_report_json(self):
        '''Test TrustedAdvisorCheckManager.argus_report() as a JSON string.'''

        report = self.tacm.argus_report(['security'], format='json')
        self.assertTrue(isinstance(report, str))

        # This is kind of silly, I guess. If these were in the raw
        # output and we got here by calling json.dumps, of course
        # we'll find these substrings.
        self.assertIn('name', report)
        self.assertIn('tagline', report)
        self.assertIn('monitors', report)
        self.assertIn('timestamp', report)
        self.assertIn('references', report)
        self.assertIn('statusItems', report)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestTrustedAdvisorCheckManagerRefresh(unittest.TestCase):
    '''Tests for TrustedAdvisorCheckManager.refresh().

    Note the delay between allowed refreshes. If we're running this
    test repeatedly or happen to run it when someone just refreshed
    checks, we may not have any refreshable checks. We raise a
    SkipTest exception in that case.

    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class common fixture setup.'''

        cls.tacm = trusted_advisor.TrustedAdvisorCheckManager(
            profile_name=TEST_PROFILE_NAME
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_refresh_category(self):
        '''Test refresh() of one or more categories.'''
        # Check the delay until refresh is possible.

        # - - - - - - - - - - - - - - - - - - - - - - - -
        category = self.tacm.categories[0]

        self.tacm.update_refresh_statuses()
        refreshable_check_ids = [
            check_id for check_id in self.tacm.check_ids(category)
            if (
                self.tacm.refresh_delay_msec(check_id) == 0 and
                self.tacm.status(check_id) == 'none'
                )
            ]
        if not refreshable_check_ids:
            raise unittest.SkipTest(
                'No refreshable Checks found for category %s' % category
                )

        self.tacm.refresh(category)
        self.tacm.update_refresh_statuses()

        now_refreshable_check_ids = [
            check_id for check_id in self.tacm.check_ids(category)
            if (
                self.tacm.refresh_delay_msec(check_id) == 0 and
                self.tacm.status(check_id) == 'none'
                )
            ]
        self.assertEqual(now_refreshable_check_ids, [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_refresh(self):
        '''Test refresh() of all categories.'''

        self.tacm.update_refresh_statuses()
        refreshable_check_ids = [
            check_id for check_id in self.tacm.check_ids()
            if (
                self.tacm.refresh_delay_msec(check_id) == 0 and
                self.tacm.status(check_id) == 'none'
                )
            ]
        if not refreshable_check_ids:
            raise unittest.SkipTest('No refreshable Checks found')

        self.tacm.refresh()
        self.tacm.update_refresh_statuses()

        now_refreshable_check_ids = [
            check_id for check_id in self.tacm.check_ids()
            if (
                self.tacm.refresh_delay_msec(check_id) == 0 and
                self.tacm.status(check_id) == 'none'
                )
            ]

        # We'll call it success if we've at least made something
        # change state.
        self.assertNotEqual(
            now_refreshable_check_ids,
            refreshable_check_ids
            )

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Define test suite.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# pylint: disable=invalid-name
load_case = unittest.TestLoader().loadTestsFromTestCase
all_suites = {
    'suite_TrustedAdvisorCheckManagerClass': load_case(
        TestTrustedAdvisorCheckManagerClass
        ),
    'suite_TrustedAdvisorCheckManagerInit': load_case(
        TestTrustedAdvisorCheckManagerInit
        ),
    'suite_TrustedAdvisorCheckManagerAttributeByCheckId': load_case(
        TestTrustedAdvisorCheckManagerAttributeByCheckId
        ),
    'suite_TrustedAdvisorCheckManagerReports': load_case(
        TestTrustedAdvisorCheckManagerReports
        ),
    }

master_suite = unittest.TestSuite(all_suites.values())
# pylint: enable=invalid-name

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    unittest.main()
