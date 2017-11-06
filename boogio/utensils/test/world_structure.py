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

nation_1 = {
    'Name': 'England',
    'Language': 'English (UK)',
    'Continent': 'Europe',
    'HistoricDates': [1066, 1605, 1859],
    'Cities': [
        {
            'Name': 'London',
            'Population': 96,
            'Royalty': [
                {'Palace': 'Buckingham', 'Title': 'King', 'Age': 47},
                {'Palace': 'Buckingham', 'Title': 'Queen', 'Age': 44},
                {'Palace': 'Buckingham', 'Title': 'Princess'},
                # {'Title': 'Princess'},
                # {'Title': 'Princess'},
                # {'Palace': 'Kensington', 'Title': 'Duke'},
                # {'Palace': 'Kensington', 'Title': 'Duchess'},
                # {'Palace': 'Kensington', 'Title': 'Prince'}
                ]
            },
        {
            'Name': 'Balmoral',
            'Population': 42,
            'Royalty': [
                {'Palace': 'Delnadamph Lodge', 'Title': 'Duke', 'Age': 63},
                # {'Palace': 'Delnadamph Lodge', 'Title': 'Duchess'},
                # {'Palace': 'Craigowan Lodge', 'Title': 'Duke'}
                ]
            }
        ]
    }

nation_2 = {
    'Name': 'France',
    'Language': 'French',
    'Continent': 'Europe',
    'HistoricDates': [1789, 1917],
    'Cities': [
        {
            'Name': 'Paris',
            'Population': 17,
            'Royalty': [
                {'Palace': 'Versailles', 'Title': 'Dauphin'},
                {'Palace': 'Versailles', 'Title': 'Marquis'},
                {'Palace': 'Versailles', 'Title': 'Duchess'},
                {'Title': 'Chevalier'},
                {'Title': 'Chevalier'},
                {'Title': 'Chevalier'}
                ]
            },
        {'Name': 'Marseille', 'Population': 91},
        {'Name': 'Lyon'},
        ]
    }

nation_3 = {
    'Name': 'Spain',
    'Language': 'Spanish',
    'Continent': 'Europe',
    'HistoricDates': [1492],
    'Cities': [
        {'Name': 'Madrid', 'Population': 55},
        {'Name': 'Toledo', 'Population': 8}
        ]
    }

world = {'nations': [nation_1, nation_2, nation_3]}
