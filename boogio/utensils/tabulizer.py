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

'''Simple tabular text report formatter and excel outputter.'''

import json


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class Tabulizer(object):
    '''
    Manage tabular reports.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(
            self,
            data=None,
            headers=None,
            columns=None
            ):  # pylint: disable=bad-continuation
        '''Create a Tabulizer instance. '''

        super(Tabulizer, self).__init__()

        self._populate_data(data, headers, columns)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _populate_data(
            self,
            data=None,
            headers=None,
            columns=None
            ):  # pylint: disable=bad-continuation
        '''
        Set up the data and headers for this Tabulizer instance.

        Arguments:

            data (list of dicts):
                A list of dicts, each containing definitions of one
                row of data.

            headers (dict):
                A dict containing strings to be used for each column
                header. The keys in ``headers`` should match the keys
                in ``data``. The value for each key will be the
                corresponding column header text.

                If ``headers`` is not provided, the keys in elements of
                ``data`` will be used as headers. If ``headers`` and ``data`` are
                both empty but ``columns`` is provided, ``columns`` will be
                substituted for ``headers``.

            columns (list):
                A list defining the default order for the columns in
                tabular reports. The values in ``columns`` should be
                keys in elements of ``data``. If provided, keys that
                occur in ``data`` but not in ``columns`` won't appear
                in reports, and extra keys in ``columns`` will result
                in a placeholder value in the corresponding column in
                reports.

                If ``columns`` is not provided, the order ``[k for k
                in headers]`` will be used, or ``None`` if ``headers``
                (and hence ``data``) is None.

        '''
        # What to use when a value is needed and no value is available.
        self.placeholder = None

        self.data = list(data)

        # - - - - - - - - - - - - - - - - - - - -
        if headers:
            self.headers = headers

        elif self.data is not None and len(self.data) > 0:
            all_data_keys = set([])
            for datum in self.data:
                all_data_keys = all_data_keys.union(set(datum.keys()))
            # all_data_keys = [d.keys() for d in self.data]

            # if len(all_data_keys) > 0:
            #     all_data_keys = reduce(lambda x, y: x + y, all_data_keys)

            self.headers = {k: k for k in set(all_data_keys)}

        elif columns is not None:
            self.headers = {c: c for c in columns}

        else:
            self.headers = None

        # - - - - - - - - - - - - - - - - - - - -
        if columns is not None:
            self.columns = columns
        else:
            self.columns = [
                k for k in self.headers
                ] if self.headers is not None else None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def json_loads(self, json_string):
        '''
        Load data and construct headers from a json string.
        '''
        data = json.loads(json_string)
        self._populate_data(data, headers=self.headers, columns=self.columns)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def json_load(self, json_filename):
        '''
        Load data and construct headers from a json file.
        '''
        with open(json_filename, 'r') as fptr:
            data = json.load(fptr)
        self._populate_data(data, headers=self.headers, columns=self.columns)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sv_load(self, filename, separator='\t'):
        '''
        Load data and construct headers from a value separated file.
        '''
        keys = None
        data = []
        with open(filename, 'r') as fptr:
            for line in fptr.readlines():
                values = line.rstrip('\n').split(separator)

                # The first line becomes the field keys.
                if keys is None:
                    keys = list(values)
                else:
                    datum = {
                        keys[index]: value
                        for (index, value) in enumerate(values)
                        if len(value) > 0
                        }
                    if len(datum) > 0:
                        data.append(datum)

        self._populate_data(data, columns=keys, headers=self.headers)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def tsv_load(self, filename):
        '''
        Load data and construct headers from a tsv file.
        '''
        self.sv_load(filename, separator='\t')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def csv_load(self, filename):
        '''
        Load data and construct headers from a csv file.
        '''
        self.sv_load(filename, separator=',')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def add_column(
            self,
            col_data=None,
            col_number=0,
            repeat='all'
            ):  # pylint: disable=bad-continuation
        '''Add a column of data at a specified position.

        Arguments:

            col_data (list):
                The values for each row in the new column.

            col_number (int):
                The position at which to add the new column.
                ``col_number`` must be from 0 to ``len(data)``.

            repeat (string):
                How to determine the values to use for the
                new column in rows beyond the length of ``col_data``.
                Possible values include ``all`` and ``last``:

                    ``all``: Repeat the values in ``col_data`` from
                    the beginning.

                    ``last``: Repeat the last value in ``col_data``.

        '''

        # This will replace either None or [] with [None].
        if not col_data:
            col_data = [None]

        col_data_index = 0

        for row in self.data:

            col_data_index += 1

            if col_data_index >= len(col_data):
                col_data_index = 0 if repeat == 'all' else len(col_data) - 1

            row.insert(col_number, col_data[col_data_index])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _header_list(self, columns=None):
        '''
        Return the values for column headers as a list of strings in the
        order defined by the columns parameter or self.columns, adding
        placeholders where required.
        '''
        header_list = []

        # if placeholder is None:
        #     placeholder = self.placeholder

        if columns is None:
            columns = self.columns

        def header_value(col):
            '''
            Provide the value that should be used as a header for this
            column.
            '''
            if self.headers is not None and col in self.headers:
                return self.headers[col]
            else:
                return col

        if columns is not None:
            header_list = [header_value(x) for x in columns]

        return header_list

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _row_list(self, data_row, columns=None, placeholder=None):
        '''
        Return a row of data as a list of strings in the order defined by
        the columns parameter or self.columns, adding placeholders where
        required.
        '''
        row_list = []

        if placeholder is None:
            placeholder = self.placeholder

        if columns is None:
            columns = self.columns

        for k in columns:
            row_list.append(
                str(data_row[k]) if k in data_row
                else str(placeholder)
                )

        return row_list

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sv(
            self,
            include_headers=True,
            columns=None,
            separator=',',
            placeholder=None
            ):  # pylint: disable=bad-continuation, invalid-name
        '''
        Return data in value-separated format.

        Arguments:

            include_headers (boolean):
                Whether or not to include the tabulizer's headers as
                the first row returned.

            columns (list of str):
                A list of columns to include, or None if all columns
                should be included. The consequent selection of
                columns takes place in _row_list().

        Returns:

            (list) A list of ``separator``-separated strings, one for
            each row of the tabulizer's data. If ``include_headers``
            is ``True``, the tabulizer's headers will be prepended as
            the first row.

        '''
        sv = []

        if include_headers:

            sv = self._header_list(columns)
            if len(sv) > 0:
                sv = [separator.join(sv)]

        if self.data is None:
            return sv

        for data_row in self.data:
            sv.append(separator.join(
                self._row_list(data_row, columns, placeholder=placeholder)
                ))

        return sv

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def csv(self, **kwargs):
        '''
        Return data in csv format.

        See sv() for parameter and return value descriptions.
        '''
        kwargs['separator'] = ','
        return self.sv(**kwargs)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def tsv(self, **kwargs):
        '''
        Return data in csv format.

        See sv() for parameter and return value descriptions.
        '''
        kwargs['separator'] = '\t'
        return self.sv(**kwargs)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def json_dumps(self, columns=None, placeholder=None):
        '''
        Create a JSON string representing the tabulizer's data.

        Arguments:

            columns (list of str):
                The columns to include in the JSON output.

            placeholder (various):
                A placeholder value to use if the tabulizer's data is
                missing a value for a particular column. If ``None``,
                this defaults to the placeholder value defined for
                the tabulizer instance.

        Returns:

            (string) A JSON string representing the tabulizer's data
            as a JSON array of JSON objects, where each object
            represents one row of data and the key-value pairs
            in each object are column names and the corresponding
            value in each row.

        '''
        if placeholder is None:
            placeholder = self.placeholder

        if columns is None:
            columns = self.columns

        placeholder_baseline = {c: placeholder for c in columns}

        json_out = [
            {k: d[k] for k in columns}
            for d in [
                dict(placeholder_baseline, **d) for d in self.data
                ]
            ]

        return json.dumps(json_out)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def to_worksheet(
            self,
            worksheet,
            include_headers=True,
            columns=None,
            placeholder=None
            ):  # pylint: disable=bad-continuation
        '''Write data to an excel Worksheet.

        Arguments:

            worksheet (xlsxwriter.Worksheet):
                The worksheet to populate.

            include_headers (boolean):
                Whether or not to include the tabulizer's headers as
                the first row of the spreadsheet.

            columns (list of str):
                A list of columns to include. By default, all columns
                will be included.

        '''

        rows = [
            self._row_list(x, columns, placeholder=placeholder)
            for x in self.data
            ]

        if include_headers:
            rows[0:0] = self._header_list(columns=columns)

        for row_num, _ in enumerate(rows):
            worksheet.write_row(row_num, 0, rows[row_num])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def to_worksheet_table(
            self,
            worksheet,
            include_headers=True,
            columns=None,
            placeholder=None
            ):  # pylint: disable=bad-continuation
        '''
        Write data to a table in an excel Worksheet.

        Arguments:

            worksheet (xlsxwriter.Worksheet):
                The worksheet to populate.

            include_headers (boolean):
                Whether or not to include the tabulizer's headers as
                the first row of the spreadsheet.

            columns (xlsxwriter.Worksheet):
                A list of columns to include. By default, all columns
                will be included.
        '''

        data_rows = [
            self._row_list(x, columns, placeholder=placeholder)
            for x in self.data
            ]

        if include_headers:
            header_row = [
                {'header': x} for x in self._header_list(columns=columns)
                ]
        else:
            header_row = [{} for x in self._header_list(columns=columns)]

        rows = len(data_rows) + (1 if include_headers else 0)
        cols = len(data_rows[0]) if len(data_rows) > 0 else len(header_row)

        worksheet.add_table(
            0, 0, rows - 1, cols - 1,
            {
                'columns': header_row,
                'data': data_rows,
                'style': 'Table Style Medium 2'
                }
            )
