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

'''Test cases for the aws_reporter.py module.'''

import json
import os
import tempfile

import unittest
import xlsxwriter

import boogio.aws_reporter as aws_reporter
import boogio.aws_surveyor as aws_surveyor
import boogio.report_definitions
import utensils.tabulizer


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestReportDefinition(unittest.TestCase):
    '''
    Test cases for aws_reporter.ReportDefinition.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        cls.sample_name = 'Sample Reporter'
        cls.sample_entity_type = 'eip'
        cls.sample_prune_specs = [
            {'path': 'meta.profile_name', 'path_to_none': False}
            ]
        cls.sample_prune_specs_no_path_to_none = [
            {'path': 'meta.profile_name'},
            {'path': 'meta.region_name'},
            ]
        cls.sample_prune_specs_varied_path_to_none = [
            {'path': 'meta.profile_name', 'path_to_none': False},
            {'path': 'meta.region_name'},
            ]
        cls.sample_default_column_order = ['meta.profile_name']

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_report_definition_init_minimal(self):
        '''
        Tests of initialization of ReportDefinition instances.
        '''

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type
            )
        self.assertIsNotNone(definition)

        self.assertEqual(definition.name, self.sample_name)
        self.assertEqual(definition.entity_type, self.sample_entity_type)
        self.assertEqual(definition.prune_specs, [])
        self.assertEqual(definition.default_column_order, None)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_report_definition_init_all(self):
        '''
        Tests of initialization of ReportDefinition instances.
        '''

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs,
            default_column_order=self.sample_default_column_order
            )
        self.assertIsNotNone(definition)

        self.assertEqual(definition.name, self.sample_name)
        self.assertEqual(definition.entity_type, self.sample_entity_type)
        self.assertEqual(definition.prune_specs, self.sample_prune_specs)
        self.assertEqual(
            definition.default_column_order,
            self.sample_default_column_order
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_report_definition_init_path_to_none(self):
        '''
        Test handling of path_to_none in ReportDefinition prune_specs.
        '''

        # - - - - - - - - - - - -

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs,
            default_column_order=self.sample_default_column_order
            )

        self.assertTrue(definition.default_path_to_none)

        path_to_none_values = [
            p['path_to_none'] for p in definition.prune_specs
            ]
        self.assertItemsEqual(path_to_none_values, [False])

        # - - - - - - - - - - - -

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs,
            default_column_order=self.sample_default_column_order
            )

        self.assertTrue(definition.default_path_to_none)

        path_to_none_values = [
            p['path_to_none'] for p in definition.prune_specs
            ]
        self.assertItemsEqual(path_to_none_values, [False])

        # - - - - - - - - - - - -

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs,
            default_column_order=self.sample_default_column_order,
            default_path_to_none=True
            )

        self.assertTrue(definition.default_path_to_none)

        path_to_none_values = [
            p['path_to_none'] for p in definition.prune_specs
            ]
        self.assertItemsEqual(path_to_none_values, [False])

        # - - - - - - - - - - - -

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs_no_path_to_none,
            default_column_order=self.sample_default_column_order,
            default_path_to_none=True
            )

        self.assertTrue(definition.default_path_to_none)

        path_to_none_values = [
            p['path_to_none'] for p in definition.prune_specs
            ]
        self.assertItemsEqual(
            list(set(path_to_none_values)),
            [True]
            )

        # - - - - - - - - - - - -

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs_no_path_to_none,
            default_column_order=self.sample_default_column_order,
            default_path_to_none=False
            )

        self.assertFalse(definition.default_path_to_none)

        path_to_none_values = [
            p['path_to_none'] for p in definition.prune_specs
            ]
        self.assertItemsEqual(
            list(set(path_to_none_values)),
            [False]
            )

        # - - - - - - - - - - - -

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs_varied_path_to_none,
            default_column_order=self.sample_default_column_order,
            default_path_to_none=False
            )

        self.assertFalse(definition.default_path_to_none)

        path_to_none_values = [
            p['path_to_none'] for p in definition.prune_specs
            ]
        self.assertItemsEqual(
            list(set(path_to_none_values)),
            [False]
            )

        # - - - - - - - - - - - -

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs_varied_path_to_none,
            default_column_order=self.sample_default_column_order,
            default_path_to_none=True
            )

        self.assertTrue(definition.default_path_to_none)

        path_to_none_values = [
            p['path_to_none'] for p in definition.prune_specs
            ]
        self.assertItemsEqual(
            list(set(path_to_none_values)),
            [True, False]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_report_definition_assign_prune_specs(self):
        '''
        Test assigning ReportDefinition prune_specs.

        In particular, setting the path_to_none.
        '''

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs,
            default_column_order=self.sample_default_column_order,
            default_path_to_none=False
            )

        path_to_none_values = [
            p['path_to_none'] for p in definition.prune_specs
            ]
        self.assertItemsEqual(path_to_none_values, [False])

        definition.prune_specs = []

        self.assertEqual(definition.prune_specs, [])

        definition.prune_specs = (
            self.sample_prune_specs_no_path_to_none
            )

        path_to_none_values = [
            p['path_to_none'] for p in definition.prune_specs
            ]

        self.assertItemsEqual(
            list(set(path_to_none_values)),
            [False]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_report_definition_copy(self):
        '''
        Tests of copying ReportDefinition instances.
        '''

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs,
            default_column_order=self.sample_default_column_order
            )

        definition2 = definition.copy()

        self.assertEqual(
            definition2.name,
            definition.name
            )
        self.assertEqual(
            definition2.entity_type,
            definition.entity_type
            )
        self.assertEqual(
            definition2.prune_specs,
            definition.prune_specs
            )
        self.assertEqual(
            definition2.default_column_order,
            definition.default_column_order
            )

        definition3 = definition2.copy()
        definition3.name = 'Changed name'
        definition3.entity_type = 'foo'
        definition3.prune_specs.append({'path': 'dot.dot.dot'})
        definition3.default_column_order.append('dot.dot')

        self.assertEqual(
            definition2.name,
            definition.name
            )
        self.assertEqual(
            definition2.entity_type,
            definition.entity_type
            )
        self.assertEqual(
            definition2.prune_specs,
            definition.prune_specs
            )
        self.assertEqual(
            definition2.default_column_order,
            definition.default_column_order
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_report_definition_extract_from_flat(self):
        '''
        Tests for ReportDefinition.extract_from().
        '''

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs,
            default_column_order=self.sample_default_column_order
            )

        surveyor = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        surveyor.survey('eip')
        informers = surveyor.informers()

        report = definition.extract_from(
            informers
            )

        self.assertEqual(type(report), list)
        self.assertNotEqual(report, [])
        self.assertEqual(type(report[0]), dict)

        self.assertEqual(
            set([len(r.items()) for r in report]),
            set([1])
            )

        self.assertEqual(
            set([r.items()[0][0] for r in report]),
            set(['meta.profile_name'])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_report_definition_extract_from_nested(self):
        '''
        Tests for ReportDefinition.extract_from().
        '''

        definition = aws_reporter.ReportDefinition(
            name=self.sample_name,
            entity_type=self.sample_entity_type,
            prune_specs=self.sample_prune_specs,
            default_column_order=self.sample_default_column_order
            )

        surveyor = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        surveyor.survey('eip')
        informers = surveyor.informers()

        report = definition.extract_from(
            informers,
            flat=False
            )

        self.assertEqual(type(report), list)
        self.assertNotEqual(report, [])
        self.assertEqual(type(report[0]), dict)

        self.assertEqual(
            set([len(r.items()) for r in report]),
            set([1])
            )

        self.assertEqual(
            set([r.items()[0][0] for r in report]),
            set(['meta'])
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSReporterInit(unittest.TestCase):
    '''
    Test cases for AWSReporter initialization.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):

        cls.sample_name = 'Sample Reporter'
        cls.sample_entity_type = 'eip'
        cls.sample_prune_specs = [
            {'path': 'meta.profile_name', 'path_to_none': False}
            ]
        cls.sample_default_column_order = ['meta.profile_name']

        cls.report_definition = aws_reporter.ReportDefinition(
            name=cls.sample_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs,
            default_column_order=cls.sample_default_column_order
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_init_no_reports(self):
        '''
        Tests of initialization of AWSReporter instances without
        assignment of report definitions.
        '''

        reporter = aws_reporter.AWSReporter()

        self.assertIsNotNone(reporter)
        self.assertEqual(reporter.report_definitions(), [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_init_with_reports(self):
        '''
        Tests of initialization of AWSReporter instances with
        assignment of report definitions.
        '''
        reporter = aws_reporter.AWSReporter(
            packaged_report_definitions=True
            )

        self.assertIsNotNone(reporter)
        self.assertNotEqual(reporter.report_definitions(), [])

        # We'll refer to this in later asserts.
        packaged_report_count = len(reporter.report_definitions())

        # - - - - - - - - - - - -
        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition]
            )

        self.assertIsNotNone(reporter)
        self.assertEqual(len(reporter.report_definitions()), 1)
        self.assertEqual(
            reporter.report_definitions()[0].name,
            self.sample_name
            )

        # - - - - - - - - - - - -
        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition],
            packaged_report_definitions=True
            )

        self.assertIsNotNone(reporter)
        self.assertEqual(
            len(reporter.report_definitions()),
            1 + packaged_report_count
            )
        self.assertTrue(
            self.sample_name in [
                r.name for r in reporter.report_definitions()
                ],
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSReporterGeneralMethods(unittest.TestCase):
    '''
    Test cases for AWSReporter methods.
    '''

    # pylint: disable=invalid-name
    # pylint: disable=protected-access

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):

        cls.sample_entity_type = 'eip'

        # These will be assigned.
        cls.sample_name_a1 = 'Sample Reporter a1'
        cls.report_definition_a1 = aws_reporter.ReportDefinition(
            name=cls.sample_name_a1,
            entity_type=cls.sample_entity_type,
            )

        cls.sample_name_a2 = 'Sample Reporter a2'
        cls.report_definition_a2 = aws_reporter.ReportDefinition(
            name=cls.sample_name_a2,
            entity_type=cls.sample_entity_type,
            )

        # These will be passed.
        cls.sample_name_p1 = 'Sample Reporter p1'
        cls.report_definition_p1 = aws_reporter.ReportDefinition(
            name=cls.sample_name_p1,
            entity_type=cls.sample_entity_type,
            )

        cls.sample_name_p2 = 'Sample Reporter p2'
        cls.report_definition_p2 = aws_reporter.ReportDefinition(
            name=cls.sample_name_p2,
            entity_type=cls.sample_entity_type,
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_combined_report_definitions(self):
        '''
        Test AWSReporter._combined_report_definitions.
        '''

        # - - - - - - - - - - - -

        reporter = aws_reporter.AWSReporter()

        self.assertItemsEqual(
            reporter._combined_report_definitions(),
            []
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_names=[self.sample_name_a1]
                ),
            []
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_definitions=[self.report_definition_p1]
                ),
            [
                self.report_definition_p1
                ]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_names=[self.sample_name_a1],
                report_definitions=[self.report_definition_p1]
                ),
            [
                self.report_definition_p1
                ]
            )

        # - - - - - - - - - - - -

        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition_a1]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(),
            [
                self.report_definition_a1
                ]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_names=[self.sample_name_a1]
                ),
            [
                self.report_definition_a1
                ]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_definitions=[self.report_definition_p1]
                ),
            [
                self.report_definition_a1,
                self.report_definition_p1
                ]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_names=[self.sample_name_a1],
                report_definitions=[self.report_definition_p1]
                ),
            [
                self.report_definition_a1,
                self.report_definition_p1
                ]
            )

        # - - - - - - - - - - - -

        reporter = aws_reporter.AWSReporter(
            report_definitions=[
                self.report_definition_a1,
                self.report_definition_a2
                ]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(),
            [
                self.report_definition_a1,
                self.report_definition_a2
                ]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_names=[self.sample_name_a1]
                ),
            [
                self.report_definition_a1
                ]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_definitions=[self.report_definition_p1]
                ),
            [
                self.report_definition_a1,
                self.report_definition_a2,
                self.report_definition_p1
                ]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_names=[self.sample_name_a1],
                report_definitions=[self.report_definition_p1]
                ),
            [
                self.report_definition_a1,
                self.report_definition_p1
                ]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_names=[self.sample_name_a1],
                report_definitions=[
                    self.report_definition_p1,
                    self.report_definition_p2
                    ]
                ),
            [
                self.report_definition_a1,
                self.report_definition_p1,
                self.report_definition_p2
                ]
            )

        self.assertItemsEqual(
            reporter._combined_report_definitions(
                report_names=[
                    self.sample_name_a1,
                    self.sample_name_a2
                    ],
                report_definitions=[
                    self.report_definition_p1,
                    self.report_definition_p2
                    ]
                ),
            [
                self.report_definition_a1,
                self.report_definition_a2,
                self.report_definition_p1,
                self.report_definition_p2
                ]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_report_definitions(self):
        '''
        Test AWSReporter.report_definitions().
        '''
        reporter = aws_reporter.AWSReporter()

        self.assertItemsEqual(
            reporter.report_definitions(),
            []
            )

        # - - - - - - - - - - - -

        reporter = aws_reporter.AWSReporter(
            report_definitions=[
                self.report_definition_a1,
                self.report_definition_a2,
                ]
            )

        self.assertItemsEqual(
            reporter.report_definitions(),
            [self.report_definition_a1, self.report_definition_a2]
            )

        self.assertItemsEqual(
            reporter.report_definitions(self.sample_name_a1),
            [self.report_definition_a1]
            )

        self.assertItemsEqual(
            reporter.report_definitions(
                self.sample_name_a1,
                self.sample_name_a2
                ),
            [self.report_definition_a1, self.report_definition_a2]
            )

        self.assertEqual(
            len(reporter.report_definitions(
                self.sample_name_a1,
                self.sample_name_a1
                )),
            1
            )

        self.assertItemsEqual(
            reporter.report_definitions(
                self.sample_name_a1,
                self.sample_name_a1
                ),
            [self.report_definition_a1]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_report_names(self):
        '''
        Test AWSReporter.report_names().
        '''
        reporter = aws_reporter.AWSReporter()

        self.assertItemsEqual(
            reporter.report_names(),
            []
            )

        # - - - - - - - - - - - -

        reporter = aws_reporter.AWSReporter()

        self.assertItemsEqual(
            reporter.report_names(self.report_definition_p1),
            [
                self.sample_name_p1,
                ]
            )

        # - - - - - - - - - - - -

        reporter = aws_reporter.AWSReporter(
            report_definitions=[
                self.report_definition_a1,
                self.report_definition_a2,
                ]
            )

        self.assertItemsEqual(
            reporter.report_names(),
            [
                self.sample_name_a1,
                self.sample_name_a2,
                ]
            )

        # - - - - - - - - - - - -

        reporter = aws_reporter.AWSReporter(
            report_definitions=[
                self.report_definition_a1,
                self.report_definition_a2,
                ]
            )

        self.assertItemsEqual(
            reporter.report_names(self.report_definition_p1),
            [
                self.sample_name_a1,
                self.sample_name_a2,
                self.sample_name_p1,
                ]
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSReporterAssignReports(unittest.TestCase):
    '''
    Test cases for AWSReporter report assignment methods.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):

        cls.sample_name = 'Sample Reporter'
        cls.sample_entity_type = 'eip'
        cls.sample_prune_specs = [
            {'path': 'meta.profile_name', 'path_to_none': False}
            ]
        cls.sample_default_column_order = ['meta.profile_name']

        cls.report_definition = aws_reporter.ReportDefinition(
            name=cls.sample_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs,
            default_column_order=cls.sample_default_column_order
            )

        cls.sample_name_2 = 'Sample Reporter 2'

        cls.report_definition_2 = aws_reporter.ReportDefinition(
            name=cls.sample_name_2,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs,
            default_column_order=cls.sample_default_column_order
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_add_report_definitions_single(self):
        '''
        Tests of the AWSReporter add_report_definitions() method,
        adding one definition at a time.
        '''
        reporter = aws_reporter.AWSReporter()

        self.assertEqual(reporter.report_definitions(), [])

        reporter.add_report_definitions([self.report_definition])
        self.assertEqual(len(reporter.report_definitions()), 1)
        self.assertEqual(
            reporter.report_definitions()[0].name,
            self.sample_name
            )

        with self.assertRaises(NameError):
            reporter.add_report_definitions([self.report_definition])

        reporter.add_report_definitions([self.report_definition_2])
        self.assertEqual(len(reporter.report_definitions()), 2)
        self.assertEqual(
            set([r.name for r in reporter.report_definitions()]),
            set([self.sample_name, self.sample_name_2])
            )

        with self.assertRaises(NameError):
            reporter.add_report_definitions([self.report_definition])

        with self.assertRaises(NameError):
            reporter.add_report_definitions([self.report_definition_2])

        with self.assertRaises(NameError):
            reporter.add_report_definitions(
                [self.report_definition, self.report_definition_2]
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_add_report_definitions_multiple(self):
        '''
        Tests of the AWSReporter add_report_definitions() method,
        adding multiple definitions at a time.
        '''
        reporter = aws_reporter.AWSReporter()

        self.assertEqual(reporter.report_definitions(), [])

        reporter.add_report_definitions(
            [self.report_definition, self.report_definition_2]
            )

        self.assertEqual(len(reporter.report_definitions()), 2)
        self.assertEqual(
            set([r.name for r in reporter.report_definitions()]),
            set([self.sample_name, self.sample_name_2])
            )

        with self.assertRaises(NameError):
            reporter.add_report_definitions([self.report_definition])

        with self.assertRaises(NameError):
            reporter.add_report_definitions([self.report_definition_2])

        with self.assertRaises(NameError):
            reporter.add_report_definitions(
                [self.report_definition, self.report_definition_2]
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_add_packaged_report_definitions(self):
        '''
        Tests of the AWSReporter add_packaged_report_definitions()
        method.
        '''
        reporter = aws_reporter.AWSReporter()

        self.assertEqual(reporter.report_definitions(), [])

        reporter.add_packaged_report_definitions(
            [boogio.report_definitions]
            )

        self.assertNotEqual(reporter.report_definitions(), [])
        self.assertIn(
            'EC2Instances',
            [r.name for r in reporter.report_definitions()]
            )

        with self.assertRaises(NameError):
            reporter.add_packaged_report_definitions(
                [boogio.report_definitions]
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_add_multiple_report_definitions(self):
        '''
        Tests of adding AWSReporter report definitions from both
        packages and individually.
        '''
        reporter = aws_reporter.AWSReporter()

        self.assertEqual(reporter.report_definitions(), [])

        reporter.add_packaged_report_definitions(
            [boogio.report_definitions]
            )

        packaged_report_count = len(reporter.report_definitions())

        reporter.add_report_definitions(
            [self.report_definition, self.report_definition_2]
            )

        self.assertEqual(
            len(reporter.report_definitions()),
            packaged_report_count + 2
            )

        with self.assertRaises(NameError):
            reporter.add_report_definitions([self.report_definition])

        with self.assertRaises(NameError):
            reporter.add_report_definitions([self.report_definition_2])

        with self.assertRaises(NameError):
            reporter.add_report_definitions(
                [self.report_definition, self.report_definition_2]
                )

        with self.assertRaises(NameError):
            reporter.add_packaged_report_definitions(
                [boogio.report_definitions]
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSReporterReportErrors(unittest.TestCase):
    '''
    Test cases for AWSReporter.report() method exceptions.

    This is the "singular" method for one report definition.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):

        # Define a reporter to use in cases.
        cls.sample_name = 'Sample Reporter'
        cls.sample_entity_type = 'eip'
        cls.sample_prune_specs = [
            {'path': 'meta.profile_name', 'path_to_none': False}
            ]
        cls.sample_default_column_order = ['meta.profile_name']

        cls.report_definition = aws_reporter.ReportDefinition(
            name=cls.sample_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs,
            default_column_order=cls.sample_default_column_order
            )

        # Define a surveyor and informers to use in cases.
        cls.surveyor = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        cls.surveyor.survey('eip')
        cls.informer = cls.surveyor.informers()[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_report_errors(self):
        '''
        Tests of the AWSReporter.report() method with improper
        signature, raising exceptions.
        '''

        # - - - - - - - - - - - -

        reporter = aws_reporter.AWSReporter()

        with self.assertRaises(TypeError):
            reporter.report()

        # - - - - - - - - - - - -
        # No informer or surveyor; reports assigned.
        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition]
            )

        with self.assertRaises(TypeError):
            reporter.report()

        # - - - - - - - - - - - -
        # No informer or surveyor; reports passed to report().
        reporter = aws_reporter.AWSReporter()

        with self.assertRaises(TypeError):
            reporter.report(
                report_definition=self.report_definition
                )

        # - - - - - - - - - - - -
        # Surveyor used; no reports assigned or selected.
        reporter = aws_reporter.AWSReporter()

        with self.assertRaises(TypeError):
            reporter.report(surveyors=[self.surveyor])

        # - - - - - - - - - - - -
        # Informer used; no reports assigned or selected.
        reporter = aws_reporter.AWSReporter()

        with self.assertRaises(TypeError):
            reporter.report(informers=[self.informer])

        # - - - - - - - - - - - -
        # No reports assigned; report name is missing.
        reporter = aws_reporter.AWSReporter()

        with self.assertRaises(IndexError):
            reporter.report(
                informers=[self.informer],
                report_name='ceci_nest_pas_une_nome'
                )

        # - - - - - - - - - - - -
        # Reports assigned; report name is missing.
        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition]
            )

        with self.assertRaises(IndexError):
            reporter.report(
                informers=[self.informer],
                report_name='ceci_nest_pas_une_nome'
                )

        # - - - - - - - - - - - -
        # Both report name and report definition provided.
        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition]
            )

        with self.assertRaises(TypeError):
            reporter.report(
                informers=[self.informer],
                report_definition=self.report_definition,
                report_name=self.report_definition.name
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSReporterReportsErrors(unittest.TestCase):
    '''
    Test cases for AWSReporter.reports() method exceptions.

    This is the "plural" method that calls AWSReporter.report()
    multiple times.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):

        # Define a reporter to use in cases.
        cls.sample_name = 'Sample Reporter'
        cls.sample_entity_type = 'eip'
        cls.sample_prune_specs = [
            {'path': 'meta.profile_name', 'path_to_none': False}
            ]
        cls.sample_default_column_order = ['meta.profile_name']

        cls.report_definition = aws_reporter.ReportDefinition(
            name=cls.sample_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs,
            default_column_order=cls.sample_default_column_order
            )

        # Define a surveyor and informers to use in cases.
        cls.surveyor = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        cls.surveyor.survey('eip')
        cls.informer = cls.surveyor.informers()[0]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_reports_errors(self):
        '''
        Tests of the AWSReporter.reports() method with improper
        signature, raising exceptions.
        '''

        # - - - - - - - - - - - -

        reporter = aws_reporter.AWSReporter()

        with self.assertRaises(TypeError):
            reporter.reports()

        # - - - - - - - - - - - -
        # No informer or surveyor; reports assigned.
        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition]
            )

        with self.assertRaises(TypeError):
            reporter.reports()

        # - - - - - - - - - - - -
        # No informer or surveyor; reports passed to report().
        reporter = aws_reporter.AWSReporter()

        with self.assertRaises(TypeError):
            reporter.reports(
                report_definitions=[self.report_definition]
                )

        # - - - - - - - - - - - -
        # Surveyor used; no reports assigned or selected.
        reporter = aws_reporter.AWSReporter()

        with self.assertRaises(TypeError):
            reporter.reports(surveyors=[self.surveyor])

        # - - - - - - - - - - - -
        # Informer used; no reports assigned or selected.
        reporter = aws_reporter.AWSReporter()

        with self.assertRaises(TypeError):
            reporter.reports(informers=[self.informer])

        # - - - - - - - - - - - -
        # No reports assigned; report name is missing.
        reporter = aws_reporter.AWSReporter()

        with self.assertRaises(IndexError):
            reporter.reports(
                informers=[self.informer],
                report_definitions=[self.report_definition],
                report_names=['ceci_nest_pas_une_nome']
                )

        # - - - - - - - - - - - -
        # Reports assigned; report name is missing.
        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition]
            )

        with self.assertRaises(IndexError):
            reporter.reports(
                informers=[self.informer],
                report_names=['ceci_nest_pas_une_nome']
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSReporterReport(unittest.TestCase):
    '''
    Test cases for the AWSReporter.report() method.

    This is the "singular" method for one report definition.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):

        # Define reporters to use in cases.

        cls.sample_entity_type = 'eip'

        # - - - - - - - - - - - -

        cls.sample_name_profile_name = 'Sample Reporter profile_name'
        cls.sample_prune_specs_profile_name = [
            {'path': 'meta.profile_name', 'path_to_none': False}
            ]

        cls.report_definition_profile_name = aws_reporter.ReportDefinition(
            name=cls.sample_name_profile_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_profile_name,
            )

        # - - - - - - - - - - - -

        cls.sample_name_region_name = 'Sample Reporter region_name'
        cls.sample_prune_specs_region_name = [
            {'path': 'meta.region_name', 'path_to_none': False}
            ]

        cls.report_definition_region_name = aws_reporter.ReportDefinition(
            name=cls.sample_name_region_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_region_name,
            )

        # - - - - - - - - - - - -

        cls.sample_entity_type_2 = 'vpc'

        cls.sample_name_profile_name_2 = 'Sample Reporter profile_name 2'
        cls.sample_prune_specs_profile_name_2 = [
            {'path': 'meta.profile_name', 'path_to_none': False}
            ]

        cls.report_definition_profile_name_2 = aws_reporter.ReportDefinition(
            name=cls.sample_name_profile_name_2,
            entity_type=cls.sample_entity_type_2,
            prune_specs=cls.sample_prune_specs_profile_name_2,
            )

        # - - - - - - - - - - - -

        # Define a surveyor and informers to use in cases.
        cls.surveyor_eip = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        cls.surveyor_eip.survey('eip')
        cls.informers = cls.surveyor_eip.informers()
        # An alias for consistency & clarity when needed.
        cls.eip_informers = cls.informers

        # - - - - - - - - - - - -

        # Define additional surveyors and informers to use in cases.
        cls.surveyor_vpc = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        cls.surveyor_vpc.survey('vpc')
        cls.vpc_informers = cls.surveyor_vpc.informers()

        # - - - - - - - - - - - -

        cls.surveyor_eip_vpc = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        cls.surveyor_eip_vpc.survey('eip', 'vpc')
        cls.eip_vpc_informers = cls.surveyor_eip_vpc.informers()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_report_no_informers(self):
        '''

        Tests of the AWSReporter.report() method when the list
        of informers to be checked is empty. Check both with ``flat``
        set to ``True`` and to ``False``.

        '''
        reporter = aws_reporter.AWSReporter()

        report = reporter.report(
            informers=[],
            report_definition=self.report_definition_profile_name,
            flat=True
            )

        # List is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertEqual(report, [])

        report = reporter.report(
            informers=[],
            report_definition=self.report_definition_profile_name,
            flat=False
            )

        # List is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertEqual(report, [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_report_flat_named_with_surveyors(self):
        '''

        Tests of the AWSReporter.report() method when report() is
        passed report names and surveyors. Here we set flat to True.

        '''
        reporter = aws_reporter.AWSReporter(
            report_definitions=[
                self.report_definition_profile_name,
                self.report_definition_region_name
                ]
            )

        report = reporter.report(
            surveyors=[self.surveyor_eip],
            report_name=self.sample_name_region_name,
            flat=True
            )

        # List is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertNotEqual(report, [])
        self.assertTrue(isinstance(report[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_report_nested_passed_with_informers(self):
        '''

        Tests of the AWSReporter.report() method when report() is
        passed report definitions and informers. Here we set flat to
        False.

        '''
        reporter = aws_reporter.AWSReporter()

        report = reporter.report(
            informers=self.informers,
            report_definition=self.report_definition_profile_name,
            flat=False
            )

        # List is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertNotEqual(report, [])
        self.assertTrue(isinstance(report[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_report_passed_with_surveyors(self):
        '''

        Tests of the AWSReporter.report() method when report() is
        passed report definitions and surveyors. Here we set flat to
        True.

        '''
        reporter = aws_reporter.AWSReporter()

        report = reporter.report(
            surveyors=[self.surveyor_eip],
            report_definition=self.report_definition_profile_name,
            flat=True
            )

        # List is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertNotEqual(report, [])
        self.assertTrue(isinstance(report[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_report_multiple_informer_types(self):
        '''

        Tests of the AWSReporter.report() method when report() is
        passed multiple informer types.

        '''
        reporter = aws_reporter.AWSReporter()

        # report_definition_region_name should extract region name
        # from eip resources only.

        report_eip_vpc_informers_eip_region_name = reporter.report(
            informers=self.eip_vpc_informers,
            report_definition=self.report_definition_region_name,
            flat=True
            )

        report_eip_informers_eip_region_name = reporter.report(
            informers=self.eip_informers,
            report_definition=self.report_definition_region_name,
            flat=True
            )

        # print "eip informers: {}".format(len(self.eip_informers))
        # print "vpc informers: {}".format(len(self.vpc_informers))
        # print "eip & vpc informers: {}".format(len(self.eip_vpc_informers))

        self.assertEqual(
            len(report_eip_vpc_informers_eip_region_name),
            len(report_eip_informers_eip_region_name)
            )

        # - - - - - - - - - - - -

        # report_definition_profile_name should extract profile name
        # from eip resources only.

        report_eip_vpc_informers_eip_profile_name = reporter.report(
            informers=self.eip_vpc_informers,
            report_definition=self.report_definition_profile_name,
            flat=True
            )

        report_eip_informers_eip_profile_name = reporter.report(
            informers=self.eip_informers,
            report_definition=self.report_definition_profile_name,
            flat=True
            )

        self.assertEqual(
            len(report_eip_vpc_informers_eip_profile_name),
            len(report_eip_informers_eip_profile_name)
            )

        # - - - - - - - - - - - -

        # report_definition_profile_name_2 should extract profile name
        # from vpc resources only.

        report_eip_vpc_informers_vpc_profile_name = reporter.report(
            informers=self.eip_vpc_informers,
            report_definition=self.report_definition_profile_name_2,
            flat=True
            )

        report_vpc_informers_vpc_profile_name = reporter.report(
            informers=self.vpc_informers,
            report_definition=self.report_definition_profile_name_2,
            flat=True
            )

        self.assertEqual(
            len(report_eip_vpc_informers_vpc_profile_name),
            len(report_vpc_informers_vpc_profile_name)
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSReporterReports(unittest.TestCase):
    '''
    Test cases for the AWSReporter.reports() method.

    This is the "plural" method that calls AWSReporter.report()
    multiple times.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):

        # Define reporters to use in cases.

        cls.sample_entity_type = 'eip'

        cls.sample_name_profile_name = 'Sample Reporter profile_name'
        cls.sample_prune_specs_profile_name = [
            {'path': 'meta.profile_name', 'path_to_none': False}
            ]

        cls.report_definition_profile_name = aws_reporter.ReportDefinition(
            name=cls.sample_name_profile_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_profile_name,
            )

        cls.sample_name_region_name = 'Sample Reporter region_name'
        cls.sample_prune_specs_region_name = [
            {'path': 'meta.region_name', 'path_to_none': False}
            ]

        cls.report_definition_region_name = aws_reporter.ReportDefinition(
            name=cls.sample_name_region_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_region_name,
            )

        # Define a surveyor and informers to use in cases.
        cls.surveyor_eip = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        cls.surveyor_eip.survey('eip')
        cls.informers = cls.surveyor_eip.informers()

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_reports_no_informers(self):
        '''

        Tests of the AWSReporter.report() method when the list
        of informers to be checked is empty. Check both with ``flat``
        set to ``True`` and to ``False``.

        '''
        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition_profile_name]
            )

        reports = reporter.reports(
            informers=[],
            flat=True
            )

        # Dict items are the result of each report definition.
        self.assertIsNotNone(reports)
        self.assertTrue(isinstance(reports, dict))
        self.assertEqual(len(reports), 1)
        self.assertItemsEqual(
            reports.keys(), [self.report_definition_profile_name.name]
            )

        report = reports.values()[0]

        # The report is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertEqual(report, [])

        reports = reporter.reports(
            informers=[],
            flat=False
            )

        # Dict items are the result of each report definition.
        self.assertIsNotNone(reports)
        self.assertTrue(isinstance(reports, dict))
        self.assertEqual(len(reports), 1)
        self.assertItemsEqual(
            reports.keys(), [self.report_definition_profile_name.name]
            )

        report = reports.values()[0]

        # The report is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertEqual(report, [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_reports_all_assigned_with_informers(self):
        '''

        Tests of the AWSReporter.report() method when report
        definitions are assigned at instantiation and report() is
        passed informers. Here we set flat to True.

        '''
        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition_profile_name]
            )

        self.assertNotEqual(self.informers, [])

        reports = reporter.reports(
            informers=self.informers,
            flat=True
            )

        # Dict items are the result of each report definition.
        self.assertIsNotNone(reports)
        self.assertTrue(isinstance(reports, dict))
        self.assertNotEqual(reports, {})
        self.assertEqual(len(reports), 1)
        self.assertItemsEqual(
            reports.keys(), [self.report_definition_profile_name.name]
            )

        report = reports.values()[0]

        # The report is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertNotEqual(report, [])
        self.assertTrue(isinstance(report[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_reports_all_assigned_with_surveyors(self):
        '''

        Tests of the AWSReporter.report() method when report
        definitions are assigned at instantiation and report() is
        passed surveyors. Here we set flat to False.

        '''
        reporter = aws_reporter.AWSReporter(
            report_definitions=[self.report_definition_profile_name]
            )

        reports = reporter.reports(
            surveyors=[self.surveyor_eip],
            flat=False
            )

        # Dict items are the result of each report definition.
        self.assertIsNotNone(reports)
        self.assertTrue(isinstance(reports, dict))
        self.assertEqual(len(reports), 1)
        self.assertItemsEqual(
            reports.keys(), [self.report_definition_profile_name.name]
            )

        report = reports.values()[0]

        # The report is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertNotEqual(report, [])
        self.assertTrue(isinstance(report[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_reports_named_with_surveyors(self):
        '''

        Tests of the AWSReporter.report() method when report() is
        passed report names and informers. Here we set flat to True.

        '''
        reporter = aws_reporter.AWSReporter(
            report_definitions=[
                self.report_definition_profile_name,
                self.report_definition_region_name
                ]
            )

        reports = reporter.reports(
            informers=self.informers,
            report_names=[self.sample_name_region_name],
            flat=True
            )

        # Dict items are the result of each report definition.
        self.assertIsNotNone(reports)
        self.assertTrue(isinstance(reports, dict))
        self.assertEqual(len(reports), 1)
        self.assertItemsEqual(
            reports.keys(), [self.report_definition_region_name.name]
            )

        report = reports.values()[0]

        # The report is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertNotEqual(report, [])
        self.assertTrue(isinstance(report[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_reports_named_and_passed_with_surveyors(self):
        '''

        Tests of the AWSReporter.report() method when report
        definitions are both assigned/named and passed in and report()
        is passed surveyors. Here we set flat to True.

        '''

        sample_name_public_ip = 'Sample Reporter PublicIP'
        sample_prune_specs_public_ip = [
            {'path': 'PublicIp', 'path_to_none': True}
            ]

        report_definition_public_ip = aws_reporter.ReportDefinition(
            name=sample_name_public_ip,
            entity_type=self.sample_entity_type,
            prune_specs=sample_prune_specs_public_ip,
            )

        reporter = aws_reporter.AWSReporter(
            report_definitions=[
                self.report_definition_profile_name,
                report_definition_public_ip
                ]
            )

        reports = reporter.reports(
            surveyors=[self.surveyor_eip],
            report_names=[
                self.sample_name_profile_name,
                ],
            report_definitions=[self.report_definition_region_name],
            flat=True
            )

        # Dict items are the result of each report definition.
        self.assertIsNotNone(reports)
        self.assertTrue(isinstance(reports, dict))
        self.assertEqual(len(reports), 2)
        self.assertItemsEqual(
            reports.keys(), [
                self.sample_name_profile_name,
                self.report_definition_region_name.name
                ]
            )

        report = reports.values()[0]

        # The report is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertNotEqual(report, [])
        self.assertTrue(isinstance(report[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_reports_passed_with_informers(self):
        '''

        Tests of the AWSReporter.report() method when report() is
        passed report definitions and informers. Here we set flat to
        False.

        '''
        reporter = aws_reporter.AWSReporter()

        reports = reporter.reports(
            informers=self.informers,
            report_definitions=[self.report_definition_profile_name],
            flat=False
            )

        # Dict items are the result of each report definition.
        self.assertIsNotNone(reports)
        self.assertTrue(isinstance(reports, dict))
        self.assertEqual(len(reports), 1)
        self.assertItemsEqual(
            reports.keys(), [self.report_definition_profile_name.name]
            )

        report = reports.values()[0]

        # The report is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertNotEqual(report, [])
        self.assertTrue(isinstance(report[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_reports_passed_with_surveyors(self):
        '''

        Tests of the AWSReporter.report() method when report() is
        passed report definitions and surveyors. Here we set flat to
        True.

        '''
        reporter = aws_reporter.AWSReporter()

        reports = reporter.reports(
            surveyors=[self.surveyor_eip],
            report_definitions=[self.report_definition_profile_name],
            flat=True
            )

        # Dict items are the result of each report definition.
        self.assertIsNotNone(reports)
        self.assertTrue(isinstance(reports, dict))
        self.assertEqual(len(reports), 1)
        self.assertItemsEqual(
            reports.keys(), [self.report_definition_profile_name.name]
            )

        report = reports.values()[0]

        # The report is the result of calling extract_from().
        self.assertTrue(isinstance(report, list))
        self.assertNotEqual(report, [])
        self.assertTrue(isinstance(report[0], dict))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSReporterReportFormats(unittest.TestCase):
    '''
    Test cases for AWSReporter report methods.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):

        # - - - - - - - - - - - - - - - - - - - -
        # Define reporters to use in cases.
        # - - - - - - - - - - - - - - - - - - - -

        cls.sample_entity_type = 'eip'

        # - - - - - - - - - - - - - - - - - - - -
        cls.sample_name_profile_name = 'Sample Reporter profile_name'
        cls.sample_prune_specs_profile_name = [
            {'path': 'meta.profile_name', 'path_to_none': False}
            ]

        cls.report_definition_profile_name = aws_reporter.ReportDefinition(
            name=cls.sample_name_profile_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_profile_name,
            )

        # - - - - - - - - - - - - - - - - - - - -
        cls.sample_name_region_name = 'Sample Reporter region_name'
        cls.sample_prune_specs_region_name = [
            {'path': 'meta.region_name', 'path_to_none': False}
            ]

        cls.report_definition_region_name = aws_reporter.ReportDefinition(
            name=cls.sample_name_region_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_region_name,
            )

        # - - - - - - - - - - - - - - - - - - - -
        cls.sample_name_public_ip = 'Sample Reporter PublicIp'
        cls.sample_prune_specs_public_ip = [
            {'path': 'PublicIp', 'path_to_none': False}
            ]

        cls.report_definition_public_ip = aws_reporter.ReportDefinition(
            name=cls.sample_name_public_ip,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_public_ip,
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Define a surveyor and informers to use in cases.
        # - - - - - - - - - - - - - - - - - - - -

        cls.surveyor_eip = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        cls.surveyor_eip.survey('eip')
        cls.informers = cls.surveyor_eip.informers()

        # - - - - - - - - - - - - - - - - - - - -
        # Define reporters to use in cases.
        # - - - - - - - - - - - - - - - - - - - -

        cls.single_definition_reporter = aws_reporter.AWSReporter(
            report_definitions=[
                cls.report_definition_profile_name,
                ]
            )

        cls.single_definition_report_name = (
            cls.report_definition_profile_name.name
            )

        cls.triple_definition_reporter = aws_reporter.AWSReporter(
            report_definitions=[
                cls.report_definition_profile_name,
                cls.report_definition_region_name,
                cls.report_definition_public_ip
                ]
            )

        cls.triple_definition_report_names = [
            d.name
            for d in cls.triple_definition_reporter.report_definitions()
            ]

        # - - - - - - - - - - - - - - - - - - - -
        # Run their basic reports so we can compare to formatted
        # report results.
        # - - - - - - - - - - - - - - - - - - - -

        cls.single_definition_report_flat = (
            cls.single_definition_reporter.reports(
                informers=cls.informers,
                flat=True
                )
            )

        cls.single_definition_report_nested = (
            cls.single_definition_reporter.reports(
                informers=cls.informers,
                flat=False
                )
            )

        # - - - - - - - - - - - -

        cls.triple_definition_report_flat = (
            cls.triple_definition_reporter.reports(
                informers=cls.informers,
                flat=True
                )
            )

        cls.triple_definition_report_nested = (
            cls.triple_definition_reporter.reports(
                informers=cls.informers,
                flat=False
                )
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_csv_list(self):
        '''Tests for the aws_reporter csv_list() method. '''

        report_name = self.single_definition_report_name
        report = (
            self.single_definition_reporter.csv_list(
                informers=self.informers,
                report_name=report_name
                )
            )

        self.assertTrue(isinstance(report, list))
        self.assertEqual(
            len(report),
            1 + len(self.single_definition_report_flat[report_name])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_tsv_list(self):
        '''Tests for the aws_reporter tsv_list() method. '''

        report_name = self.single_definition_report_name
        report = (
            self.single_definition_reporter.tsv_list(
                informers=self.informers,
                report_name=report_name
                )
            )

        self.assertTrue(isinstance(report, list))
        self.assertEqual(
            len(report),
            1 + len(self.single_definition_report_flat[report_name])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_sv_list(self):
        '''Tests for the aws_reporter sv_list() method. '''

        # TODO: Document, add include_headers, columns and
        # placeholder arguments to pass to tabulizer.

        # - - - - - - - - - - - -
        report_name = self.single_definition_report_name
        report = (
            self.single_definition_reporter.sv_list(
                informers=self.informers,
                report_name=report_name,
                separator='XXX',
                # include_headers=True
                )
            )

        self.assertTrue(isinstance(report, list))
        # This adds a header list.
        self.assertEqual(
            len(report),
            1 + len(self.single_definition_report_flat[report_name])
            )

        # TODO: Move to plural version, if it gets created.
        # # - - - - - - - - - - - -
        # report = (
        #     self.triple_definition_reporter.sv_list(
        #         informers=self.informers,
        #         separator='XXX',
        #         # include_headers=True
        #         )
        #     )

        # self.assertTrue(isinstance(report, list))
        # # This adds a header list.
        # self.assertEqual(
        #     len(report),
        #     3 + reduce(
        #         lambda x, y: x + y,
        #         [len(d) for d in self.triple_definition_report_flat]
        #         )
        #     )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_json_dumps(self):
        '''Tests for the aws_reporter json_dumps() method. '''

        # - - - - - - - - - - - -
        # Flat.
        # - - - - - - - - - - - -
        report_name = self.single_definition_report_name
        report_json = (
            self.single_definition_reporter.json_dumps(
                informers=self.informers,
                report_name=report_name,
                flat=True
                )
            )

        report = json.loads(report_json)

        self.assertTrue(isinstance(report, list))
        self.assertEqual(
            len(report),
            len(self.single_definition_report_flat[report_name])
            )

        # - - - - - - - - - - - -
        # Not flat.
        # - - - - - - - - - - - -
        report_name = self.single_definition_report_name
        report_json = (
            self.single_definition_reporter.json_dumps(
                informers=self.informers,
                report_name=report_name,
                flat=False
                )
            )

        report = json.loads(report_json)

        self.assertTrue(isinstance(report, list))
        self.assertNotEqual(report, [])
        self.assertTrue(isinstance(report[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_tabulizer(self):
        '''Tests for the aws_reporter tabulizer() method. '''

        # TODO: Add support for headers, columns arguments.
        report_name = self.single_definition_report_name
        report = self.single_definition_reporter.tabulizer(
            informers=self.informers,
            report_name=report_name
            )

        self.assertTrue(
            isinstance(report, utensils.tabulizer.Tabulizer)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_tabulizers(self):
        '''Tests for the aws_reporter tabulizers() method.

        This is the plural method, which calls the singular tabulizer
        method for multiple report definitions.

        '''

        report_names = self.triple_definition_report_names
        reports = self.triple_definition_reporter.tabulizers(
            informers=self.informers,
            )

        self.assertItemsEqual(
            reports.keys(),
            report_names
            )

        for report_name in report_names:

            self.assertTrue(
                isinstance(
                    reports[report_name],
                    utensils.tabulizer.Tabulizer
                    )
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSReporterReportExcelMethods(unittest.TestCase):
    '''
    Test cases for AWSReporter report excel interaction methods.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Class setup. Doh.
        '''

        # Get a temp directory for output.
        cls.tmpdir = tempfile.mkdtemp()

        # - - - - - - - - - - - - - - - - - - - -
        # Define reporters to use in cases.
        # - - - - - - - - - - - - - - - - - - - -

        cls.sample_entity_type = 'eip'

        # - - - - - - - - - - - - - - - - - - - -
        cls.sample_name_profile_name = 'Sample Reporter profile_name'
        cls.sample_prune_specs_profile_name = [
            {'path': 'meta.profile_name', 'path_to_none': False}
            ]

        cls.report_definition_profile_name = aws_reporter.ReportDefinition(
            name=cls.sample_name_profile_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_profile_name,
            )

        # - - - - - - - - - - - - - - - - - - - -
        cls.sample_name_region_name = 'Sample Reporter region_name'
        cls.sample_prune_specs_region_name = [
            {'path': 'meta.region_name', 'path_to_none': False}
            ]

        cls.report_definition_region_name = aws_reporter.ReportDefinition(
            name=cls.sample_name_region_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_region_name,
            )

        # - - - - - - - - - - - - - - - - - - - -
        cls.sample_name_public_ip = 'Sample Reporter PublicIp'
        cls.sample_prune_specs_public_ip = [
            {'path': 'PublicIp', 'path_to_none': False}
            ]

        cls.report_definition_public_ip = aws_reporter.ReportDefinition(
            name=cls.sample_name_public_ip,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_public_ip,
            )

        # - - - - - - - - - - - - - - - - - - - -
        # Define a surveyor and informers to use in cases.
        # - - - - - - - - - - - - - - - - - - - -

        cls.surveyor_eip = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        cls.surveyor_eip.survey('eip')
        cls.informers = cls.surveyor_eip.informers()

        # - - - - - - - - - - - - - - - - - - - -
        # Define reporters to use in cases.
        # - - - - - - - - - - - - - - - - - - - -

        cls.single_definition_reporter = aws_reporter.AWSReporter(
            report_definitions=[
                cls.report_definition_profile_name,
                ]
            )

        cls.single_definition_report_name = (
            cls.report_definition_profile_name.name
            )

        cls.triple_definition_reporter = aws_reporter.AWSReporter(
            report_definitions=[
                cls.report_definition_profile_name,
                cls.report_definition_region_name,
                cls.report_definition_public_ip
                ]
            )

        cls.triple_definition_report_names = [
            d.name
            for d in cls.triple_definition_reporter.report_definitions()
            ]

        # - - - - - - - - - - - - - - - - - - - -
        # Run their basic reports so we can compare to formatted
        # report results.
        # - - - - - - - - - - - - - - - - - - - -

        cls.single_definition_report_flat = (
            cls.single_definition_reporter.reports(
                informers=cls.informers,
                flat=True
                )
            )

        cls.triple_definition_report_flat = (
            cls.triple_definition_reporter.reports(
                informers=cls.informers,
                flat=True
                )
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def tearDownClass(cls):
        '''
        Remove test files and temp directory.
        '''
        for root, dirs, files in os.walk(cls.tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(cls.tmpdir)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_add_worksheets_single(self):
        '''Tests for the aws_reporter add_worksheets() method. '''

        workbook_path = os.path.join(self.tmpdir, 'test_add_worksheets.xls')

        workbook = xlsxwriter.Workbook(
            workbook_path,
            {'strings_to_numbers': True}
            )
        # worksheet_1 = workbook.add_worksheet()
        # worksheet_2 = workbook.add_worksheet()

        report_name = self.single_definition_report_name

        # - - - - - - - - - - - - - - - - - - - -
        # Error case testing.
        # - - - - - - - - - - - - - - - - - - - -

        # with self.assertRaises(ValueError):
        #     self.triple_definition_reporter.add_worksheets(
        #         worksheets=[worksheet_1],
        #         informers=self.informers,
        #         report_names=self.triple_definition_report_names
        #         )

        # with self.assertRaises(ValueError):
        #     self.single_definition_reporter.add_worksheets(
        #         worksheets=[worksheet_1, worksheet_2],
        #         informers=self.informers,
        #         report_names=[report_name]
        #         )

        # - - - - - - - - - - - - - - - - - - - -
        # Test populating worksheets.
        # - - - - - - - - - - - - - - - - - - - -

        self.single_definition_reporter.add_worksheets(
            workbook=workbook,
            informers=self.informers,
            report_names=[report_name]
            )

        self.assertEqual(len(workbook.worksheets()), 1)

        worksheet = workbook.worksheets()[0]

        # The worksheet has one extra row, for the headers, while the
        # report list's length is one more than the last index, so
        # these are equal.
        self.assertEqual(
            worksheet.dim_rowmax,
            len(self.single_definition_report_flat[report_name])
            )

        # This doesn't add a column, the way headers add a row, so the
        # dim_colmax value is one less than the length.
        self.assertEqual(
            worksheet.dim_colmax,
            len(self.single_definition_report_flat[report_name][0]) - 1
            )

        self.assertEqual(worksheet.name, report_name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_add_worksheets_triple(self):
        '''Tests for the aws_reporter add_worksheets() method. '''

        workbook_path = os.path.join(self.tmpdir, 'test_add_worksheets.xls')

        workbook = xlsxwriter.Workbook(
            workbook_path,
            {'strings_to_numbers': True}
            )
        worksheet_1 = workbook.add_worksheet()
        worksheet_2 = workbook.add_worksheet()

        report_names = self.triple_definition_report_names

        self.triple_definition_reporter.add_worksheets(
            workbook=workbook,
            informers=self.informers,
            report_names=report_names
            )

        self.assertEqual(len(workbook.worksheets()), 5)

        worksheets = workbook.worksheets()
        worksheet_names = [s.name for s in worksheets]

        self.assertItemsEqual(
            worksheet_names,
            report_names + [worksheet_1.name, worksheet_2.name]
            )

        for report_name in report_names:

            worksheet = [w for w in worksheets if w.name == report_name][0]
            # report_definition = [
            #     d for d in
            #     self.triple_definition_reporter.report_definitions()
            #     if d.name == report_name
            #     ][0]

            # The worksheet has one extra row, for the headers, while the
            # report list's length is one more than the last index, so
            # these are equal.
            self.assertEqual(
                worksheet.dim_rowmax,
                len(self.triple_definition_report_flat[report_name])
                )

            # This doesn't add a column, the way headers add a row, so the
            # dim_colmax value is one less than the length.
            self.assertEqual(
                worksheet.dim_colmax,
                len(self.triple_definition_report_flat[report_name][0]) - 1
                )

            self.assertEqual(worksheet.name, report_name)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_write_workbook(self):
        '''Tests for the aws_reporter write_workbook() method. '''

        workbook_path = os.path.join(self.tmpdir, 'test_write_workbook.xls')
        report_name = self.single_definition_report_name

        self.single_definition_reporter.write_workbook(
            output_path=workbook_path,
            informers=self.informers,
            report_names=[report_name]
            )

        # This is a pretty minimal test, since xlsxwriter doesn't
        # provide a "read in workbook" method.
        self.assertTrue(os.path.exists(workbook_path))

        statinfo = os.stat(workbook_path)
        self.assertTrue(statinfo.st_size > 0)

        # Replace the workbook with an empty file.
        os.remove(workbook_path)
        self.assertFalse(os.path.exists(workbook_path))
        with open(workbook_path, 'w') as _:
            pass
        self.assertTrue(os.path.exists(workbook_path))

        statinfo = os.stat(workbook_path)
        self.assertTrue(statinfo.st_size == 0)

        with self.assertRaises(ValueError):
            self.single_definition_reporter.write_workbook(
                output_path=workbook_path,
                informers=self.informers,
                report_names=[report_name]
                )

        self.single_definition_reporter.write_workbook(
            output_path=workbook_path,
            informers=self.informers,
            report_names=[report_name],
            overwrite=True
            )

        # Make sure we updated the file.
        statinfo = os.stat(workbook_path)
        self.assertTrue(statinfo.st_size > 0)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSReporterReportWriteToFile(unittest.TestCase):
    '''
    Test cases for AWSReporter report file output methods.
    '''

    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Class setup. Doh.
        '''

        # Get a temp directory for output.
        cls.tmpdir = tempfile.mkdtemp()

        # - - - - - - - - - - - - - - - - - - - -
        # Define reporters to use in cases.
        # - - - - - - - - - - - - - - - - - - - -

        cls.sample_entity_type = 'eip'

        # - - - - - - - - - - - - - - - - - - - -
        cls.sample_name_profile_name = 'Sample Reporter profile_name'
        cls.sample_prune_specs_profile_name = [
            {'path': 'meta.profile_name', 'path_to_none': False},
            {'path': 'meta.region_name', 'path_to_none': False},
            {'path': 'PublicIp', 'path_to_none': False}
            ]

        cls.report_definition_profile_name = aws_reporter.ReportDefinition(
            name=cls.sample_name_profile_name,
            entity_type=cls.sample_entity_type,
            prune_specs=cls.sample_prune_specs_profile_name,
            )

        # # - - - - - - - - - - - - - - - - - - - -
        # cls.sample_name_region_name = 'Sample Reporter region_name'
        # cls.sample_prune_specs_region_name = [
        #     {'path': 'meta.region_name', 'path_to_none': False}
        #     ]

        # cls.report_definition_region_name = aws_reporter.ReportDefinition(
        #     name=cls.sample_name_region_name,
        #     entity_type=cls.sample_entity_type,
        #     prune_specs=cls.sample_prune_specs_region_name,
        #     )

        # # - - - - - - - - - - - - - - - - - - - -
        # cls.sample_name_public_ip = 'Sample Reporter PublicIp'
        # cls.sample_prune_specs_public_ip = [
        #     {'path': 'PublicIp', 'path_to_none': False}
        #     ]

        # cls.report_definition_public_ip = aws_reporter.ReportDefinition(
        #     name=cls.sample_name_public_ip,
        #     entity_type=cls.sample_entity_type,
        #     prune_specs=cls.sample_prune_specs_public_ip,
        #     )

        # - - - - - - - - - - - - - - - - - - - -
        # Define a surveyor and informers to use in cases.
        # - - - - - - - - - - - - - - - - - - - -

        cls.surveyor_eip = aws_surveyor.AWSSurveyor(
            profiles=['default'], regions=['us-east-1']
            )
        cls.surveyor_eip.survey('eip')
        cls.informers = cls.surveyor_eip.informers()

        # - - - - - - - - - - - - - - - - - - - -
        # Define reporters to use in cases.
        # - - - - - - - - - - - - - - - - - - - -

        cls.single_definition_reporter = aws_reporter.AWSReporter(
            report_definitions=[
                cls.report_definition_profile_name,
                ]
            )

        cls.single_definition_report_name = (
            cls.report_definition_profile_name.name
            )

        # cls.triple_definition_reporter = aws_reporter.AWSReporter(
        #     report_definitions=[
        #         cls.report_definition_profile_name,
        #         cls.report_definition_region_name,
        #         cls.report_definition_public_ip
        #         ]
        #     )

        # cls.triple_definition_report_names = [
        #     d.name
        #     for d in cls.triple_definition_reporter.report_definitions()
        #     ]

        # - - - - - - - - - - - - - - - - - - - -
        # Run their basic reports so we can compare to formatted
        # report results.
        # - - - - - - - - - - - - - - - - - - - -

        cls.single_definition_report_flat = (
            cls.single_definition_reporter.reports(
                informers=cls.informers,
                flat=True
                )
            )

        cls.single_definition_report_nested = (
            cls.single_definition_reporter.reports(
                informers=cls.informers,
                flat=False
                )
            )

        # cls.triple_definition_report_flat = (
        #     cls.triple_definition_reporter.reports(
        #         informers=cls.informers,
        #         flat=True
        #         )
        #     )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def tearDownClass(cls):
        '''
        Remove test files and temp directory.
        '''
        for root, dirs, files in os.walk(cls.tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(cls.tmpdir)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_write_sv(self):
        '''Tests for the aws_reporter write_sv() method. '''

        sv_file_base = 'test_write_sv'
        sv_file_name = '.'.join([sv_file_base, '.sv'])
        sv_path = os.path.join(self.tmpdir, sv_file_name)

        current_separator = 'XXX'

        report_name = self.single_definition_report_name

        self.single_definition_reporter.write_sv(
            separator=current_separator,
            output_path=sv_path,
            informers=self.informers,
            report_name=report_name
            )

        self.assertTrue(os.path.exists(sv_path))

        statinfo = os.stat(sv_path)
        self.assertTrue(statinfo.st_size > 0)

        lines = []
        for line in open(sv_path, 'r'):
            lines.append(line)

        # There's a header row.
        self.assertEqual(
            len(lines),
            1 + len(self.single_definition_report_flat[report_name])
            )
        self.assertEqual(
            len(lines[0].split(current_separator)),
            len(self.sample_prune_specs_profile_name)
            )
        self.assertEqual(
            len(lines[-1].split(current_separator)),
            len(self.sample_prune_specs_profile_name)
            )

        # Replace the file with an empty file.
        os.remove(sv_path)
        self.assertFalse(os.path.exists(sv_path))
        with open(sv_path, 'w') as _:
            pass
        self.assertTrue(os.path.exists(sv_path))

        statinfo = os.stat(sv_path)
        self.assertTrue(statinfo.st_size == 0)

        with self.assertRaises(ValueError):
            self.single_definition_reporter.write_sv(
                separator=current_separator,
                output_path=sv_path,
                informers=self.informers,
                report_name=report_name
                )

        self.single_definition_reporter.write_sv(
            separator=current_separator,
            output_path=sv_path,
            informers=self.informers,
            report_name=report_name,
            overwrite=True
            )

        # Make sure we updated the file.
        statinfo = os.stat(sv_path)
        self.assertTrue(statinfo.st_size > 0)

        lines = []
        for line in open(sv_path, 'r'):
            lines.append(line)

        # There's a header row.
        self.assertEqual(
            len(lines),
            1 + len(self.single_definition_report_flat[report_name])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_write_csv(self):
        '''Tests for the aws_reporter write_csv() method. '''

        csv_file_base = 'test_write_csv'
        csv_file_name = '.'.join([csv_file_base, '.csv'])
        csv_path = os.path.join(self.tmpdir, csv_file_name)

        current_separator = ','

        report_name = self.single_definition_report_name

        self.single_definition_reporter.write_csv(
            output_path=csv_path,
            informers=self.informers,
            report_name=report_name
            )

        self.assertTrue(os.path.exists(csv_path))

        statinfo = os.stat(csv_path)
        self.assertTrue(statinfo.st_size > 0)

        lines = []
        for line in open(csv_path, 'r'):
            lines.append(line)

        # There's a header row.
        self.assertEqual(
            len(lines),
            1 + len(self.single_definition_report_flat[report_name])
            )
        self.assertEqual(
            len(lines[0].split(current_separator)),
            len(self.sample_prune_specs_profile_name)
            )
        self.assertEqual(
            len(lines[-1].split(current_separator)),
            len(self.sample_prune_specs_profile_name)
            )

        # Replace the file with an empty file.
        os.remove(csv_path)
        self.assertFalse(os.path.exists(csv_path))
        with open(csv_path, 'w') as _:
            pass
        self.assertTrue(os.path.exists(csv_path))

        statinfo = os.stat(csv_path)
        self.assertTrue(statinfo.st_size == 0)

        with self.assertRaises(ValueError):
            self.single_definition_reporter.write_csv(
                output_path=csv_path,
                informers=self.informers,
                report_name=report_name
                )

        self.single_definition_reporter.write_csv(
            output_path=csv_path,
            informers=self.informers,
            report_name=report_name,
            overwrite=True
            )

        # Make sure we updated the file.
        statinfo = os.stat(csv_path)
        self.assertTrue(statinfo.st_size > 0)

        lines = []
        for line in open(csv_path, 'r'):
            lines.append(line)

        # There's a header row.
        self.assertEqual(
            len(lines),
            1 + len(self.single_definition_report_flat[report_name])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_write_tsv(self):
        '''Tests for the aws_reporter write_tsv() method. '''

        tsv_file_base = 'test_write_tsv'
        tsv_file_name = '.'.join([tsv_file_base, '.tsv'])
        tsv_path = os.path.join(self.tmpdir, tsv_file_name)

        current_separator = '\t'

        report_name = self.single_definition_report_name

        self.single_definition_reporter.write_tsv(
            output_path=tsv_path,
            informers=self.informers,
            report_name=report_name
            )

        self.assertTrue(os.path.exists(tsv_path))

        statinfo = os.stat(tsv_path)
        self.assertTrue(statinfo.st_size > 0)

        lines = []
        for line in open(tsv_path, 'r'):
            lines.append(line)

        # There's a header row.
        self.assertEqual(
            len(lines),
            1 + len(self.single_definition_report_flat[report_name])
            )
        self.assertEqual(
            len(lines[0].split(current_separator)),
            len(self.sample_prune_specs_profile_name)
            )
        self.assertEqual(
            len(lines[-1].split(current_separator)),
            len(self.sample_prune_specs_profile_name)
            )

        # Replace the file with an empty file.
        os.remove(tsv_path)
        self.assertFalse(os.path.exists(tsv_path))
        with open(tsv_path, 'w') as _:
            pass
        self.assertTrue(os.path.exists(tsv_path))

        statinfo = os.stat(tsv_path)
        self.assertTrue(statinfo.st_size == 0)

        with self.assertRaises(ValueError):
            self.single_definition_reporter.write_tsv(
                output_path=tsv_path,
                informers=self.informers,
                report_name=report_name
                )

        self.single_definition_reporter.write_tsv(
            output_path=tsv_path,
            informers=self.informers,
            report_name=report_name,
            overwrite=True
            )

        # Make sure we updated the file.
        statinfo = os.stat(tsv_path)
        self.assertTrue(statinfo.st_size > 0)

        lines = []
        for line in open(tsv_path, 'r'):
            lines.append(line)

        # There's a header row.
        self.assertEqual(
            len(lines),
            1 + len(self.single_definition_report_flat[report_name])
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_reporter_write_json(self):
        '''Tests for the aws_reporter write_json() method. '''

        json_file_base = 'test_write_json'
        json_file_name = '.'.join([json_file_base, '.json'])
        json_path = os.path.join(self.tmpdir, json_file_name)

        report_name = self.single_definition_report_name
        report_data = self.single_definition_report_flat[
            self.single_definition_report_name
            ]

        self.single_definition_reporter.write_json(
            output_path=json_path,
            informers=self.informers,
            report_name=report_name
            )

        self.assertTrue(os.path.exists(json_path))

        statinfo = os.stat(json_path)
        self.assertTrue(statinfo.st_size > 0)

        # lines = []
        # for line in open(json_path, 'r'):
        #     lines.append(line)
        with open(json_path, 'r') as fptr:
            reloaded_1 = json.load(fptr)

        # # There's a header row.
        # self.assertEqual(
        #     len(lines),
        #     1 + len(self.single_definition_report_flat[report_name])
        #     )
        # self.assertEqual(
        #     len(lines[0].split(current_separator)),
        #     len(self.sample_prune_specs_profile_name)
        #     )
        # self.assertEqual(
        #     len(lines[-1].split(current_separator)),
        #     len(self.sample_prune_specs_profile_name)
        #     )

        # Replace the file with an empty file.
        os.remove(json_path)
        self.assertFalse(os.path.exists(json_path))
        with open(json_path, 'w') as _:
            pass
        self.assertTrue(os.path.exists(json_path))

        statinfo = os.stat(json_path)
        self.assertTrue(statinfo.st_size == 0)

        with self.assertRaises(ValueError):
            self.single_definition_reporter.write_json(
                output_path=json_path,
                informers=self.informers,
                report_name=report_name
                )

        self.single_definition_reporter.write_json(
            output_path=json_path,
            informers=self.informers,
            report_name=report_name,
            overwrite=True
            )

        # Make sure we updated the file.
        statinfo = os.stat(json_path)
        self.assertTrue(statinfo.st_size > 0)

        # lines = []
        # for line in open(json_path, 'r'):
        #     lines.append(line)
        with open(json_path, 'r') as fptr:
            reloaded_2 = json.load(fptr)

        self.assertEqual(
            type(reloaded_1),
            type(report_data)
            )
        self.assertEqual(reloaded_1, report_data)
        self.assertEqual(reloaded_1, reloaded_2)


        # # There's a header row.
        # self.assertEqual(
        #     len(lines),
        #     1 + len(self.single_definition_report_flat[report_name])
        #     )

if __name__ == '__main__':
    unittest.main()
