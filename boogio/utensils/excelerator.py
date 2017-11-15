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

'''Create Excel workbooks from python data.

**Example**

    Create a workbook with sheets "Employees" and "Sites"::

        excelerate(
            'sample_workbook.xls',
            {
                'data': [
                    {'name': 'Alice', 'age': 32, 'sex': 'F'},
                    {'name': 'Bob', 'age': 31, 'sex': 'M'},
                    {'name': 'Carol', 'age': 42, 'sex': 'F'},
                    {'name': 'Dan', 'age': 36, 'sex': 'M'},
                    ],
                'sheetname': 'Employees',
                'headers': {'name': 'Name', 'age': 'Age', 'sex': 'Gender'},
                'columns': ['name', 'sex', 'age']
                },
            {
                'data': [
                    {'city': 'state': 'CA', 'Los Gatos', 'country': 'US' },
                    {'city': 'Paris', 'country': 'FR' },
                    {'city': 'London', 'country': 'GB' },
                    ],
                'sheetname': 'Sites',
                'columns': ['city', 'country', 'state']
                'placeholder': ''
                }
            )

'''

import json
import xlsxwriter

from boogio.utensils import tabulizer


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TODO: Rename sheetdata -> sheetspecs
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def excelerate(filename, *sheetdata, **kwargs):
    '''Create an Excel workbook with specified data and simple layout.

    Arguments:

        filename (string):
            The name of the resulting Excel workbook output file.

        sheetdata (list of dicts):
            Data for each worksheet in the resulting Excel file, and
            optional additional specification (see below).

        placeholder (str, in kwargs):
            The value to use for missing fields in a row of data.
            Individual sheet data can override this per sheet. If not
            provided, a placeholder of 'None' will be used.

        sheetspecs (list, in kwargs):

            A list of dicts, or of names of files each containing a
            JSON encoding of a dict, whose keys are sheet name
            strings and whose values define layout control items for
            the sheet with the matching name.

    Each dict in ``sheetdata`` is used to construct one sheet of the
    resulting Excel workbook.

    **Worksheet Data Definition**

    The data for the cells of the sheet is taken from a list of dicts
    passed directly as a python list, as a JSON string or as the
    contents of a JSON file, the first of the following that is found:

        ``data``: A python dictionary to be used for the sheet data.

        ``json``: A JSON string encoding of the data dictionary.

        ``jsonfile``: A file containing the JSON encoded data
        dictionary.

    **Worksheet Layout Control**

    The following simple "layout control" items in a sheet's dict are
    recognized:

        ``sheetname``: The name to use for the worksheet.

        ``headers``: A dict mapping data keys to strings to be used
        for each worksheet column header.

        ``columns``: An array defining the default order for the
        columns of the resulting worksheet.

        ``placeholder``: The value to use for missing fields in a row
        of data in the worksheet.

    Sheet layout control items can also be passed in the optional
    ``sheetspecs`` parameter. If a layout control item appears both in
    a ``sheetdata`` entry and a corresponding ``sheetspecs`` entry,
    the values in the sheet data will take precedence.

    **Sheet Naming**

    The default name for a sheet is "Sheet <N>", where <N> is the
    index of the sheet in the ``sheetdata`` list. If a ``sheetname``
    is specified for the sheet, that will be used instead.

    **Column Headers and Order**

    By default, the column headers in each worksheet will be the
    cumulative set of keys in all the data dicts in the entry.

    This can be changed with a ``headers`` layout control item, a
    dict whose keys are sheet data keys and whose values will be
    used as the name for the corresponding column in place of the
    data key.

    Column order is normally unspecified. This can be controlled by the
    ``columns`` layout control item, defined as a list with elements
    taken from the keys in the worksheet's row data dictionaries.

    Note that the ``headers`` keys and the ``columns`` entries should
    both be sets of strings that occur as keys in the worksheet's row
    data dictionaries. These parameters are used as initialization
    parameters for a ``utensils.tabulizer.Tabulizer`` instance;
    see the documentation there for further details.

    **Cell Values and Placeholders**

    As noted above, the spreadsheet created for a given element of the
    ``sheetdata`` list will have one column for each key that occurs
    in any of the dictionaries that define its rows of data. If the
    items in the entry for a row only include a subset of these keys,
    the value specified by ``placeholder`` will be used as the value
    in the column for any missing keys.

    See tabulizer.py for more details on these fields.

    '''
    workbook = xlsxwriter.Workbook(filename)

    sheet_count = 0

    # We pass all the fields to _populate_worksheet, but there's no
    # reason to re-read the files every time.
    sheetspecs = {}
    if 'sheetspecs' in kwargs:
        for sheetspec in kwargs['sheetspecs']:

            if isinstance(sheetspec, str) or isinstance(sheetspec, unicode):
                with open(sheetspec, 'r') as fptr:
                    sheetspecs.update(json.load(fptr))

            else:
                sheetspecs.update(sheetspec)

    for sheetdatum in [] if sheetdata is None else sheetdata:
        sheet_count += 1
        if 'sheetname' in sheetdatum:
            sheetname = sheetdatum['sheetname']
        else:
            sheetname = "Sheet %s" % sheet_count

        if sheetname in sheetspecs:
            # Take values for columns, etc., from sheetspecs and update
            # them with the specific values in sheetdatum.
            sheetdatum = dict(sheetspecs[sheetname], **sheetdatum)

        worksheet = workbook.add_worksheet(sheetname)

        _populate_worksheet(worksheet, **dict(kwargs, **sheetdatum))

    workbook.close()


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _populate_worksheet(worksheet, **kwargs):
    '''
    Parse the indicated data and use tabularize to create a worksheet.
    '''
    if 'data' in kwargs:
        sheet_data = kwargs['data']

    elif 'json' in kwargs:
        sheet_data = json.loads(kwargs['json'])

    elif 'jsonfile' in kwargs:
        with open(kwargs['jsonfile'], 'r') as fptr:
            sheet_data = json.load(fptr)

    sheet_headers = kwargs['headers'] if 'headers' in kwargs else None
    sheet_columns = kwargs['columns'] if 'columns' in kwargs else None
    placeholder = kwargs['placeholder'] if 'placeholder' in kwargs else None

    data_tabulizer = tabulizer.Tabulizer(
        data=sheet_data,
        columns=sheet_columns,
        headers=sheet_headers
        )

    data_tabulizer.to_worksheet_table(worksheet, placeholder=placeholder)
