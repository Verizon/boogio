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

'''Report information from collections of ``AWSInformer`` instances.

So you've used ``AWSSurveyor`` to pull records for a few hundred EC2
instances, a handful of VPCs and a few dozen subnets, maybe some ELBs.
What now? With the ``aws_reporter`` package, you can easily define and
re-use report definitions to extract specific fields from a set of
``AWSInformer`` instances and return the results in a variety of
formats:

    *   Text separated value formats such as csv and tsv.
    *   Lists of dicts or lists of structured lists.
    *   Raw or JSON format nested data structures.
    *   Excel worksheets.

Example
-------

A typical work flow proceeds as follows::

    >>> import boogio.aws_surveyor
    >>> import boogio.aws_reporter
    >>> surveyor = aws_surveyor.AWSSurveyor(
    ...     profiles=['default'], regions=['us-east-1', 'us-west-1']
    ...     )
    >>> surveyor.survey('ec2', 'subnet', 'vpc')
    >>> reporter = aws_reporter.AWSReporter()
    >>> from boogio import report_definitions
    >>> reporter.add_packaged_report_definitions([report_definitions])
    >>> report_names = ['EC2Instances', 'EC2Existential', 'Subnets', 'VPCs']
    >>> for name in report_names:
    ...     reporter.write_tsv(
    ...     surveyor=surveyor,
    ...     report_names=[name],
    ...     output_path=name
    ...     )

This will create files :file:`EC2Instances.tsv`,
:file:`EC2Existential.tsv`, :file:`Subnets.tsv` and :file:`VPCs.tsv`
in the current working directory with the records retrieved by the
surveyor.

A few things of which to take note:

    *   The example demonstrates passing AWS entity records by passing
        an ``AWSSurveyor`` instance. You can also pass a list of
        ``AWSInformer`` instances directly with the ``informers``
        argument.
    *   Instances of ``aws_reporter.ReportDefinition`` can be assigned
        to an ``AWSReporter`` instance. The
        ``add_packaged_report_definitions()`` method loads report
        definitions from a python package, by default from the
        ``aws_reporter`` package. The ``add_report_definitions()``
        method adds instances of ``aws_reporter.ReportDefinition``
        directly.
    *   You can use individual reports that are assigned to a reporter
        by specifying their ``name`` attribute when calling reporting
        methods as shown. You can also pass report definitions to
        reporting methods directly using the ``report_definitions``
        argument in place of the ``report_names`` argument.
    *   The appropriate file suffix for the output file format is
        automatically appended.


Report Definitions
------------------

The ``ReportDefinition`` class defines the fields that will be
extracted for an atomic report. Each ``ReportDefinition`` specifies
paths into the ``to_dict()`` representation of an ``AWSInformer``
type as ``prune`` specifications. See the documentation for
``utensils.prune`` for details.

An example report definition::

    elb_report = aws_reporter.ReportDefinition(
        name='LoadBalancers',
        entity_type='elb',
        prune_specs=[
            {'path': 'meta.profile_name', 'path_to_none': False},
            {'path': 'meta.region_name', 'path_to_none': False},
            {'path': 'LoadBalancerName', 'path_to_none': True},
            {'path': 'VPCId.Tags:Name', 'path_to_none': True},
            {'path': 'Scheme', 'path_to_none': True},
            {'path': 'CreatedTime', 'path_to_none': True},
            {'path': 'DNSName', 'path_to_none': True},
            {
                'path': 'AvailabilityZones',
                'path_to_none': True,
                'value_refiner': lambda x: ' '.join([str(y) for y in x])
                },
            {
                'path': 'DNSIpAddress.INET.[]',
                'flatten_leaves': True,
                'path_to_none': True
                },
            {
                'path': 'Instances',
                'value_refiner': len,
                'path_to_none': True
                },
            ],
        default_column_order=[
            'meta.profile_name', 'meta.region_name',
            'VPCId.Tags:Name', 'LoadBalancerName', 'DNSIpAddress.INET',
            'Scheme', 'CreatedTime',
            'DNSName', 'AvailabilityZones', 'Instances',
            ]
        )

The ``ReportDefinition`` instance ``extract_from()`` method is used to
extract the fields from the appropriate ``AWSInformer`` subclass. The
``extract_from()`` method can return results either as nested
structures directly extracted from the Informer's dictionary
representation or as flattened structures: list of dicts, each dict of
which has only scalars among its values. The boolean ``flat`` argument
to ``extract_from()`` selects which structure is returned;
``flat=True`` (the default) for flattened structures, ``flat=False``
for nested.

**Examples**

    *   Extract a flattened report from an
        ``aws_informer.EC2InstanceInformer`` instance::

            >>> surveyor = aws_surveyor.AWSSurveyor(
            ...     profiles=['default'], regions=['us-east-1']
            ...     )
            >>> surveyor.survey('ec2')
            >>> informer = surveyor.informers()[0]
            >>> definition = boogio.report_definitions.ec2_report
            >>> definition.extract_from(informer)


    *   Extract a nested report from the same instance::

            >>> definition.extract_from(informer, flat=False)


'''

import copy
import json
import os

import logging
# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        '''Placeholder handler.'''
        def emit(self, record):
            pass

from utensils import flatten
from utensils import prune
from utensils import tabulizer

logging.getLogger(__name__).addHandler(NullHandler())


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class ReportDefinition(object):
    '''Manage AWSReporter report definitions.

    Arguments:

        name (string):
            The descriptive name for the report.

        entity_type (string):
            The entity type of the AWSInformer subclass the report
            extracts.

        prune_specs (list of dict, optional):
            The specifications for the prune paths the report
            extracts.

        default_column_order (list of str, optional):
            An optional list of the prune paths defining the default
            columns and their order for columnar reports from this
            report definition.

        default_path_to_none (bool, default=True):
            The default value for the ``path_to_none`` item in each of
            the report definition's prune specs. The ``path_to_none``
            value for any prune spec entry that doesn't explicitly
            define it will be set to this value.



    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(
            self,
            name,
            entity_type,
            prune_specs=None,
            default_column_order=None,
            default_path_to_none=True
            ):  # pylint: disable=bad-continuation
        '''
        Initialize a ReportDefinition instance.
        '''

        self.name = name
        self.entity_type = entity_type
        self._prune_specs = (
            [] if prune_specs is None else copy.deepcopy(prune_specs)
            )
        # default_column_order should remain None, not be converted to [].
        self.default_column_order = copy.deepcopy(default_column_order)
        self.default_path_to_none = default_path_to_none

        for pspec in self._prune_specs:
            if 'path_to_none' not in pspec:
                pspec['path_to_none'] = self.default_path_to_none

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @property
    def prune_specs(self):
        '''ReportDefinition prune_specs property.
        '''
        return self._prune_specs

    @prune_specs.setter
    def prune_specs(self, value):
        '''ReportDefinition prune_specs property.

        Ensure that path_to_none is properly set.
        '''
        self._prune_specs = copy.deepcopy(value)

        for pspec in self._prune_specs:
            if 'path_to_none' not in pspec:
                pspec['path_to_none'] = self.default_path_to_none

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def copy(self):
        '''
        Return a copy of a ReportDefinition instance.
        '''

        copied = ReportDefinition(
            name=self.name,
            entity_type=self.entity_type,
            prune_specs=list(self.prune_specs),
            default_column_order=list(self.default_column_order)
            )

        return copied

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def extract_from(self, informers, flat=True):
        '''Extract the fields specified by prune_specs.

        Arguments:

            informers (list of AWSInformer):
                ``AWSInformer`` instances from which to extract
                report data. Any informer whose ``entity_type``
                attribute doesn't match the report definition's
                ``entity_type`` attribute will be skipped.

            flat (bool):
                If ``True``, return a *flat* result; if ``False``,
                return a nested result. See the documentation for
                ``utensils.prune`` and ``utensils.flatten``
                for more information.

        '''
        pruner = prune.Pruner(*self.prune_specs)
        extractable_informers = [
            i for i in informers
            if i.entity_type == self.entity_type
            ]

        if flat:
            records = flatten.flatten([
                pruner.prune_branches(informer.to_dict(), balanced=True)
                for informer in extractable_informers
                ])

        else:
            records = [
                pruner.prune_tree(informer.to_dict())
                for informer in extractable_informers
                ]

        return records


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class AWSReporter(object):
    '''Report information from collections of ``AWSInformer`` instances.

    Arguments:

        packaged_report_definitions (bool, optional):
            Assign reports defined in the
            ``boogio.report_definitions`` module to this
            reporter.
        report_definitions (list of ReportDefinition, optional):
            Assign the specified list of report definitions to this
            reporter.

    Attributes:

        report_definitions (list of ReportDefinition):
            The report definitions, if any, assigned to this instance.

    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(
            self,
            packaged_report_definitions=False,
            report_definitions=None
            ):  # pylint: disable=bad-continuation
        '''Initialize an AWSReporter instance.
        '''

        # This may be superfluous, but it makes the attribute visible.
        self._report_definitions = []

        if report_definitions is None:
            report_definitions = []

        self.add_report_definitions(report_definitions)
        if packaged_report_definitions:
            import boogio.report_definitions
            self.add_packaged_report_definitions(
                [boogio.report_definitions]
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def report_definitions(self, *names):
        '''Get assigned report definitions by name.

        Arguments:

            names (tuple of str):
                The names of the reports to return.

        Returns:

            list: A list of report definitions whose names are those
            in the ``names`` tuple.

        '''
        return [
            d for d in self._report_definitions
            if d.name in names
            or len(names) == 0
            ]

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_report_definitions(self, report_definitions):
        '''Assign additional report definitions to this instance.

        Arguments:

            report_definitions (list of aws_reporter.ReportDefinition):
                The list of report definitions to assign.

        Raises:

            NameError:
                If any item in report_definitions has a ``name``
                attribute that already occurs as the ``name``
                attribute of an assigned report definition.

        '''

        for report_definition in report_definitions:

            if report_definition.name in self.report_names():
                raise NameError(
                    'Report definition named %s is already assigned'
                    '' % report_definition.name
                    )
            self._report_definitions.append(report_definition)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_packaged_report_definitions(self, packages):
        '''Assign additional report definitions to this instance.

        Arguments:

            packages (list of packages):
                The list of packages in which to find report
                definitions.

        Raises:

            NameError:
                If any item in report_definitions has a ``name``
                attribute that already occurs as the ``name``
                attribute of an assigned report definition.

        The ``add_packaged_report_definitions()`` method finds any
        instances of ``aws_reporter.ReportDefinition`` in the
        indicated packages and assigns them to this
        ``aws_reporter.AWSReporter`` instance. The packages must have
        already been imported.

        '''

        for pkg in packages:

            for item in [getattr(pkg, c) for c in dir(pkg)]:

                if type(item).__name__ == 'ReportDefinition':
                    self.add_report_definitions([item])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _combined_report_definitions(
            self,
            report_names=None,
            report_definitions=None
            ):  # pylint: disable=bad-continuation
        '''Combine named and passed report definitions.

        Returns:

            list: All report definitions in the report_definitions
            argument or in the report definitions assigned to this
            reporter, with the latter list filtered by report_names
            if the latter is not None.

        '''
        if report_names is None:
            report_names = []

        if report_definitions is None:
            report_definitions = []

        combined_definitions = [
            r for r in self.report_definitions()
            if r.name in report_names
            or report_names == []
            ]

        combined_definitions.extend(report_definitions)

        return combined_definitions

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def report_names(
            self,
            *report_definitions
            ):  # pylint: disable=bad-continuation
        '''Get names of report definitions.

        Returns:

            list: All names of report definitions in the
            report_definitions tuple or in the report definitions
            assigned to this reporter.

        '''

        if report_definitions is None:
            report_definitions = []

        names = [d.name for d in report_definitions]
        names.extend([d.name for d in self.report_definitions()])

        return names

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def report(
            self,
            informers=None,
            surveyors=None,
            report_name=None,
            report_definition=None,
            flat=True
            ):  # pylint: disable=bad-continuation
        '''Generate a report as plain python.

        Arguments:

            informers (list of AWSInformer, optional):
                A list of informers on which to report.

            surveyors (list of AWSSurveyor, optional):
                A list of surveyors on whose ``informers()`` list to
                report.

            report_name (str, optional):
                The name of aa ``aws_reporter.ReportDefinition``
                instance assigned to this reporter to be generated.

            report_definition (AWSReporter, optional):
                An ``aws_reporter.ReportDefinition`` instance to be
                generated.

            flat (bool, default=True):
                A flag to pass through to the report definition
                ``extract_from()`` method. See the documentation of
                that method for details.

        Raises:

            IndexError: If ``report_names`` contains any values that
                aren't the ``name`` attribute of a member of
                ``self.report_definitions()``.

            TypeError: If no report definitions are assigned to this
                reporter and ``report_definitions`` is not defined.

            TypeError: If neither ``informers`` nor ``surveyors``
                is defined.

        Returns:

            list: The result of the selected ``ReportDefinition``
            extracting from the list of informer targets.

        At least one of ``informers`` and ``surveyors`` is required,
        although the lists may be empty.

        If both ``informers`` an ``surveyors`` are specified, the
        resulting report will include data from all informers in the
        former list and the latter's ``informers()`` method.

        Exactly one of ``report_name`` and ``report_definition`` is
        required.

        **Report Structure**

        The value returned from ``report()`` is the result of calling
        the ``ReportDefinition.extract_from()`` method on lists of
        informers. Thus the result will be a list of flat dicts (if
        the ``flat`` argument had the default ``True`` value) or
        nested dicts (if the ``flat`` argument was explicitly set to
        ``False``).

        E.g., if ``flat`` is ``True``::

            [{<flat record dict>}, {<flat record dict>}, ... ]

        And if ``flat`` is explicitly set to ``False``::

            [{<nested informer dict>}, {<nested informer dict>}, ... ]

        '''
        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Check for any errors in arguments provided.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        # We have something to report on.
        if informers is None and surveyors is None:
            raise TypeError(
                'expected informers and/or surveyors; found None'
                )

        # We have at least one report requested...
        if report_definition is None and report_name is None:
            raise TypeError(
                'no report definition assigned or named'
                )

        # ...and at most one report requested.
        if report_definition is not None and report_name is not None:
            raise TypeError(
                'multiple report definitions (both assigned and named)'
                )

        # If the report was requested as the name of an assigned report,
        # there actually is a report with that name.
        if report_name is not None:
            report_name_is_absent = (report_name not in self.report_names())
            if report_name_is_absent:
                raise IndexError(
                    'no assigned report definition with name'
                    ' %s' % report_name
                    )

        if informers is None:
            informers = []

        if surveyors is None:
            surveyors = []

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Construct the informer list and report definition
        # with which we'll report.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        this_report_informers = informers

        for surveyor in surveyors:
            this_report_informers.extend(surveyor.informers())

        # Either report_definition is the report to use, or report_name
        # holds the name of an assigned report to use.
        if report_definition is None:
            report_definition = self.report_definitions(report_name)[0]

        return report_definition.extract_from(
            this_report_informers,
            flat=flat
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reports(
            self,
            informers=None,
            surveyors=None,
            report_names=None,
            report_definitions=None,
            flat=True
            ):  # pylint: disable=bad-continuation
        '''Generate multiple reports as plain python.

        Arguments:

            report_names (list of str, optional):
                A list of names of ``aws_reporter.ReportDefinition``
                instances assigned to this reporter that define the
                reports to be generated.

            report_definitions (list of AWSReporter, optional):
                A list of ``aws_reporter.ReportDefinition`` instances
                that define the reports to be generated.

        Raises:

            IndexError: If ``report_names`` contains any values that
                aren't the ``name`` attribute of a member of
                ``self.report_definitions()``.

            TypeError: If no report definitions are assigned to this
                reporter and ``report_definitions`` is not defined.

        See the documentation for ``report()`` for additional
        arguments, return values and exceptions raised.

        Returns:

            dict: Each key in the dict is the name of a report, and
            the corresponding value is the result of that named
            ``ReportDefinition`` extracting from the list of informer
            targets.

        This method calls the singular ``report()`` method once for
        each report name and report definition, and returns the
        results as a dict whose keys are the names of each report.

        **Reports Structure**

        The value returned from ``reports()`` is a dict where each
        value represents the result of calling the singular
        ``report()`` method for one of the selected report definitions
        with other arguments unchanged. Thus each value will be a list
        of flat dicts (if the ``flat`` argument had the default
        ``True`` value) or nested dicts (if the ``flat`` argument was
        explicitly set to ``False``).

        E.g., if ``flat`` is ``True``::

            {
                report_name_1: [{<flat dict>}, {<flat dict>}, ... ],
                report_name_2: [{<flat dict>}, {<flat dict>}, ... ],
                ...
                }

        And if ``flat`` is explicitly set to ``False``::

            {
                report_name_1: [{<nested dict>}, {<nested dict>}, ... ],
                report_name_2: [{<nested dict>}, {<nested dict>}, ... ],
                ...
                }

        '''

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Check for errors in report definition arguments provided.
        # - - - - - - - - - - - - - - - - - - - - - - - -

        if report_names is None:
            report_names = []

        else:
            report_names_absent = [
                n for n in report_names
                if n not in self.report_names()
                ]

            if len(report_names_absent) > 0:
                raise IndexError(
                    'no assigned report definitions with names'
                    ' %s' % ', '.join(report_names_absent)
                    )

        # - - - - - - - - - - -

        if report_definitions is None and self.report_definitions() == []:
            raise TypeError(
                'no report definitions assigned or passed as arguments'
                )

        if report_definitions is None:
            report_definitions = []

        # - - - - - - - - - - -

        combined_definitions = self._combined_report_definitions(
            report_names=report_names,
            report_definitions=report_definitions
            )

        results = {}
        for report_definition in combined_definitions:
            results.update({
                report_definition.name: self.report(
                    informers=informers,
                    surveyors=surveyors,
                    report_definition=report_definition,
                    flat=flat
                    )
                })

        return results

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def csv_list(
            self,
            informers=None,
            surveyors=None,
            report_name=None,
            report_definition=None
            ):  # pylint: disable=bad-continuation
        '''Generate a comma separated report as a list of lines.

        See the documentation for ``report()`` for details on
        arguments and exceptions. Note that ``flat`` is not an
        allowed argument for this method, as the reports must be
        flat for this format.

        Returns: A list of comma-separated strings.

        '''
        return self.sv_list(
            informers=informers,
            surveyors=surveyors,
            report_name=report_name,
            report_definition=report_definition,
            separator=','
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def tsv_list(
            self,
            informers=None,
            surveyors=None,
            report_name=None,
            report_definition=None
            ):  # pylint: disable=bad-continuation
        '''Generate a tab separated report as a list of lines.

        See the documentation for ``report()`` for details on
        arguments and exceptions. Note that ``flat`` is not an
        allowed argument for this method, as the reports must be
        flat for this format.

        Returns: A list of tab-separated strings.

        '''
        return self.sv_list(
            informers=informers,
            surveyors=surveyors,
            report_name=report_name,
            report_definition=report_definition,
            separator='\t'
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sv_list(
            self,
            separator=',',
            informers=None,
            surveyors=None,
            report_name=None,
            report_definition=None
            ):  # pylint: disable=bad-continuation
        '''Generate a string separated report as a list of lines.

        Arguments:

            separator (str, default=','): The string with which to
                separate the values in each line.

        See the documentation for ``report()`` for details on other
        arguments and exceptions. Note that ``flat`` is not an
        allowed argument for this method, as the reports must be
        flat for this format.

        Returns: A list of comma-separated strings.

        '''
        tab = self.tabulizer(
            informers=informers,
            surveyors=surveyors,
            report_name=report_name,
            report_definition=report_definition
            )
        return tab.sv(
            include_headers=True,
            separator=separator
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def json_dumps(
            self,
            informers=None,
            surveyors=None,
            report_name=None,
            report_definition=None,
            flat=True
            ):  # pylint: disable=bad-continuation
        '''Generate a report in JSON format.

        See the documentation for ``report()`` for details on
        arguments and exceptions.

        Returns: A JSON string.

        '''
        if flat:
            tab = self.tabulizer(
                informers=informers,
                surveyors=surveyors,
                report_name=report_name,
                report_definition=report_definition
                )
            return tab.json_dumps()

        else:
            return json.dumps(
                self.report(
                    informers=informers,
                    surveyors=surveyors,
                    report_name=report_name,
                    report_definition=report_definition,
                    flat=False
                    )
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def tabulizer(
            self,
            informers=None,
            surveyors=None,
            report_name=None,
            report_definition=None
            ):  # pylint: disable=bad-continuation
        '''Generate a report stored in a ``utensils.tabulizer``.

        See the documentation for ``report()`` for details on
        arguments and exceptions. Note that ``flat`` is not an
        allowed argument for this method, as the reports must be
        flat for this format.

        Returns: A ``utensils.tabulizer.Tabulizer`` instance.

        '''

        report = self.report(
            informers=informers,
            surveyors=surveyors,
            report_name=report_name,
            report_definition=report_definition,
            flat=True
            )

        # report() will have confirmed that exactly one of these is
        # non-None.
        if report_definition:
            report_definition_used = report_definition
        else:
            report_definition_used = self.report_definitions(report_name)[0]

        return tabulizer.Tabulizer(
            data=report,
            columns=report_definition_used.default_column_order
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def tabulizers(
            self,
            informers=None,
            surveyors=None,
            report_names=None,
            report_definitions=None
            ):  # pylint: disable=bad-continuation
        '''Generate multiple reports in ``utensils.tabulizer`` instances.

        See the documentation for ``reports()`` for details on
        arguments and exceptions. Note that ``flat`` is not an
        allowed argument for this method, as the reports must be
        flat for this format.

        Returns:

            dict:  Each key in the dict is the name of a report, and
            the corresponding value is the result of calling
            ``tabulizer`` with that report specified.

        '''

        tabs = {}

        for report_definition in self._combined_report_definitions(
                report_names=report_names,
                report_definitions=report_definitions
                ):  # pylint: disable=bad-continuation

            tabs.update(
                {
                    report_definition.name: self.tabulizer(
                        informers=informers,
                        surveyors=surveyors,
                        report_definition=report_definition
                        )
                    }
                )

        return tabs

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_worksheets(
            self,
            workbook,
            informers=None,
            surveyors=None,
            report_names=None,
            report_definitions=None
            ):  # pylint: disable=bad-continuation
        '''Generate reports and write to an ``xlsxwriter`` workbook.

        Arguments:

            workbook (xlsxwriter.Worksheet):
                The workbook to populate.

        See the documentation for ``report()`` for details on other
        arguments and exceptions. Note that ``flat`` is not an
        allowed argument for this method, as the reports must be
        flat for this format.

        This method writes reports to worksheets in an
        ``xlsxwriter.Workbook`` instance passed as its first
        positional argument. It will set the name of each worksheet
        to the name of the report written to that worksheet.

        Returns: ``None``.

        '''

        tabs = self.tabulizers(
            informers=informers,
            surveyors=surveyors,
            report_names=report_names,
            report_definitions=report_definitions
            )

        for tab_name in tabs:

            worksheet = workbook.add_worksheet()

            tabs[tab_name].to_worksheet_table(worksheet)
            worksheet.name = tab_name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write_workbook(
            self,
            output_path,
            informers=None,
            surveyors=None,
            report_names=None,
            report_definitions=None,
            overwrite=False
            ):  # pylint: disable=bad-continuation
        '''Generate a report written to ``xlsxwriter`` worksheets.

        Arguments:

            output_path (string):
                The path to the resulting workbook.

            overwrite (bool, default=False):
                If ``True``, overwrite any existing file already
                present.

        See the documentation for ``report()`` for details on other
        arguments and exceptions. Note that ``flat`` is not an
        allowed argument for this method, as the reports must be
        flat for this format.

        This method writes reports to worksheets in a
        ``xlsxwriter.Workbook`` instance passed as its first
        positional argument.

        Raises:

            ValueError: If ``overwrite`` is ``False`` and a file
                already exists at the location specified by
                ``output_path``.

        Returns: ``None``.

        '''

        import xlsxwriter

        if overwrite is False and os.path.exists(output_path):
            raise ValueError('%s already exists' % output_path)

        with xlsxwriter.Workbook(output_path) as workbook:

            self.add_worksheets(
                workbook,
                informers=informers,
                surveyors=surveyors,
                report_names=report_names,
                report_definitions=report_definitions
                )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write_sv(
            self,
            output_path,
            separator=',',
            informers=None,
            surveyors=None,
            report_name=None,
            report_definition=None,
            overwrite=False
            ):  # pylint: disable=bad-continuation
        '''Write a string separated report to a specified file.

        Arguments:

            separator (str, default=','): The string with which to
                separate the values in each line.

            output_path (string):
                The path to the resulting workbook.

            overwrite (bool, default=False):
                If ``True``, overwrite any existing file already
                present.

        See the documentation for ``report()`` for details on other
        arguments and exceptions. Note that ``flat`` is not an
        allowed argument for this method, as the reports must be
        flat for this format.

        This method writes reports to a separated value file using
        the specified separator string.

        Raises:

            ValueError: If ``overwrite`` is ``False`` and a file
                already exists at the location specified by
                ``output_path``.

        Returns: ``None``.

        '''

        if overwrite is False and os.path.exists(output_path):
            raise ValueError('%s already exists' % output_path)

        report_lines = self.sv_list(
            separator=separator,
            informers=informers,
            surveyors=surveyors,
            report_name=report_name,
            report_definition=report_definition
            )

        with open(output_path, 'w') as fptr:
            for line in report_lines:
                fptr.write(line)
                fptr.write('\n')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write_csv(
            self,
            output_path,
            informers=None,
            surveyors=None,
            report_name=None,
            report_definition=None,
            overwrite=False
            ):  # pylint: disable=bad-continuation
        '''Write a comma separated report to a specified file.

        This method is a pseudonym for ``write_sv()``
        with ``separator=','``. See the documentation for
        ``write_sv()`` for details on arguments and exceptions.

        '''

        self.write_sv(
            output_path=output_path,
            separator=',',
            informers=informers,
            surveyors=surveyors,
            report_name=report_name,
            report_definition=report_definition,
            overwrite=overwrite
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write_tsv(
            self,
            output_path,
            informers=None,
            surveyors=None,
            report_name=None,
            report_definition=None,
            overwrite=False
            ):  # pylint: disable=bad-continuation
        '''Write a tab separated report to a specified file.

        This method is a pseudonym for ``write_sv()``
        with ``separator='\\t'``. See the documentation for
        ``write_sv()`` for details on arguments and exceptions.

        '''

        self.write_sv(
            output_path=output_path,
            separator='\t',
            informers=informers,
            surveyors=surveyors,
            report_name=report_name,
            report_definition=report_definition,
            overwrite=overwrite
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def write_json(
            self,
            output_path,
            informers=None,
            surveyors=None,
            report_name=None,
            report_definition=None,
            flat=True,
            overwrite=False
            ):  # pylint: disable=bad-continuation
        '''Write a JSON report to a specified file.

        Arguments:

            output_path (string):
                The path to the resulting workbook.

            overwrite (bool, default=False):
                If ``True``, overwrite any existing file already
                present.

        See the documentation for ``write_report()`` for details on
        other arguments and exceptions.
        '''

        if overwrite is False and os.path.exists(output_path):
            raise ValueError('%s already exists' % output_path)

        # TODO: This is inefficient, there needs to be a json_dump
        # method in tabulizer so we don't have to buffer the JSON
        # then write it here.
        if flat:
            tab = self.tabulizer(
                informers=informers,
                surveyors=surveyors,
                report_name=report_name,
                report_definition=report_definition
                )
            report_json = tab.json_dumps()

        else:
            report_json = json.dumps(
                self.report(
                    informers=informers,
                    surveyors=surveyors,
                    report_name=report_name,
                    report_definition=report_definition,
                    flat=False
                    )
                )

        with open(output_path, 'w') as fptr:
            fptr.write(report_json)
