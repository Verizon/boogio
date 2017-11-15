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

'''Test cases for the cidr_catalog_helper.py module.'''

import unittest

from boogio.aws_surveyor import AWSSurveyor
from boogio.helpers import cidr_catalog_helper
from boogio import site_boogio
try:
    from carto import cidr_catalog
    CARTO_IMPORTED = True
except ImportError:
    CARTO_IMPORTED = False

from boogio.utensils import prune

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Uncomment to show lower level logging statements.
# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# shandler = logging.StreamHandler()
# shandler.setLevel(logging.INFO)  # Pick one.
# shandler.setLevel(logging.DEBUG)  # Pick one.
# logger.addHandler(shandler)

TEST_CATALOG = 'sample_cidr_catalog.json'


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@unittest.skipIf(not CARTO_IMPORTED, "The carto module is required.")
class TestHelperForSecurityGroupInformer(unittest.TestCase):
    '''Basic test cases for CidrCatalogHelper with a SecurityGroupInformer.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture setup.'''

        cls.catalog = cidr_catalog.CidrCatalog()
        cls.catalog.load(TEST_CATALOG)
        cls.helper = cidr_catalog_helper.CidrCatalogHelper(cls.catalog)

        cls.sg_surv = AWSSurveyor(
            profiles=[site_boogio.test_profile_name],
            regions=site_boogio.default_regions
            )
        cls.sg_surv.survey('security_group')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case level common fixture setup.'''
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_helper_for_securitygroup_informer(self):
        '''Test a CidrCatalogHelper instance with a Security Group Informer.'''

        informers = self.sg_surv.informers()

        # - - - - - - - - - - - - - - - -
        informers_with_cidrip = [
            i for i in informers
            if prune.Pruner().leaf_satisfies(
                i.to_dict(),
                'IpPermissions.[].IpRanges.[]',
                lambda x: 'CidrIp' in x
                )
            ]

        self.assertTrue(len(informers_with_cidrip) > 0)

        self.helper.annotate_group_cidrip(
            informers_with_cidrip[0], 'name'
            )

        self.assertTrue(
            prune.Pruner().leaf_satisfies(
                informers_with_cidrip[0].to_dict(),
                'IpPermissions.[].IpRanges.[]',
                lambda x: 'name' in x
                )
            )

        self.helper.annotate_group_cidrip(
            informers_with_cidrip[0], 'short_name', 'description'
            )

        self.assertTrue(
            prune.Pruner().leaf_satisfies(
                informers_with_cidrip[0].to_dict(),
                'IpPermissions.[].IpRanges.[]',
                lambda x: 'short_name' in x and 'description' in x
                )
            )

        # - - - - - - - - - - - - - - - -

        informers_with_egress_cidrip = [
            i for i in informers
            if prune.Pruner().leaf_satisfies(
                i.to_dict(),
                'IpPermissions.[].IpRanges.[]',
                lambda x: 'CidrIp' in x
                )
            ]

        self.assertTrue(len(informers_with_egress_cidrip) > 0)

        self.helper.annotate_group_cidrip(
            informers_with_egress_cidrip[0], 'name'
            )

        self.assertTrue(
            prune.Pruner().leaf_satisfies(
                informers_with_egress_cidrip[0].to_dict(),
                'IpPermissions.[].IpRanges.[]',
                lambda x: 'name' in x
                )
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Define test suite.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# pylint: disable=invalid-name
load_case = unittest.TestLoader().loadTestsFromTestCase
all_suites = {
    # Lowercase these.
    'suite_HelperForSecurityGroupInformer': load_case(
        TestHelperForSecurityGroupInformer
        ),
    }

master_suite = unittest.TestSuite(all_suites.values())
# pylint: enable=invalid-name

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    unittest.main()
