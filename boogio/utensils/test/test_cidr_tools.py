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

'''Test cases for the cidr_tools.py module.'''

import unittest

from boogio.utensils import cidr_tools
UNIVERSAL_CIDR = cidr_tools.UNIVERSAL_CIDR


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestCidrModuleFunctions(unittest.TestCase):
    '''
    Basic test cases for cidr_tools module level functions.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_sort_cidrs(self):
        '''Test cidr_tools.sort_cidrs()
        '''

        # - - - - - - - - - - - - - - - -
        cidrs = ["1.0.0.0", "2.0.0.0"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["1.0.0.0", "2.0.0.0"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["2.0.0.0", "1.0.0.0"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["1.0.0.0", "2.0.0.0"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["2.0.0.0", "1.0.0.0/32"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["1.0.0.0/32", "2.0.0.0"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["2.0.0.0/32", "1.0.0.0"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["1.0.0.0", "2.0.0.0/32"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["2.0.0.0/32", "1.0.0.0/32"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["1.0.0.0/32", "2.0.0.0/32"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["10.0.0.0/8", "10.0.0.0/12"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["10.0.0.0/8", "10.0.0.0/12"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["10.0.0.0/12", "10.0.0.0/8"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["10.0.0.0/8", "10.0.0.0/12"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["32.32.32.32", "32.32.32.32"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["32.32.32.32", "32.32.32.32"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["32.32.32.32", "32.32.32.1"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["32.32.32.1", "32.32.32.32"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["32.32.32.32", "32.32.1.32"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["32.32.1.32", "32.32.32.32"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["32.32.32.32", "32.1.32.32"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["32.1.32.32", "32.32.32.32"]
            )

        # - - - - - - - - - - - - - - - -
        cidrs = ["32.32.1.32", "32.1.32.32"]
        self.assertEqual(
            sorted(cidrs, cmp=cidr_tools.sort_cidrs),
            ["32.1.32.32", "32.32.1.32"]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_to_cidr(self):
        '''Test cidr_tools.to_cidr()
        '''
        self.assertEqual(cidr_tools.to_cidr('1.0.0.0'), '1.0.0.0/32')
        self.assertEqual(cidr_tools.to_cidr('1.0.0.0/1'), '1.0.0.0/1')
        self.assertEqual(cidr_tools.to_cidr('1.0.0.0/32'), '1.0.0.0/32')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_cidr_address(self):
        '''Test cidr_tools.cidr_address()
        '''
        self.assertEqual(cidr_tools.cidr_address('1.0.0.0'), '1.0.0.0')
        self.assertEqual(cidr_tools.cidr_address('1.0.0.0/1'), '1.0.0.0')
        self.assertEqual(cidr_tools.cidr_address('1.0.0.0/32'), '1.0.0.0')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_cidr_netmask_size(self):
        '''Test cidr_tools.cidr_netmask_size()
        '''

        self.assertEqual(cidr_tools.cidr_netmask_size('1.0.0.0'), 32)
        self.assertEqual(cidr_tools.cidr_netmask_size('1.0.0.0/1'), 1)
        self.assertEqual(cidr_tools.cidr_netmask_size('1.0.0.0/16'), 16)
        self.assertEqual(cidr_tools.cidr_netmask_size('1.0.0.0/32'), 32)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_bitmask_octet(self):
        '''Test cidr_tools.bitmask_octet()
        '''

        self.assertEqual(cidr_tools.bitmask_octet(8), 255)
        self.assertEqual(cidr_tools.bitmask_octet(2), 192)
        self.assertEqual(cidr_tools.bitmask_octet(1), 128)
        self.assertEqual(cidr_tools.bitmask_octet(0), 0)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_netmask_octets(self):
        '''Test cidr_tools.netmask_octets()
        '''

        self.assertEqual(cidr_tools.netmask_octets(16), (255, 255, 0, 0))
        self.assertEqual(cidr_tools.netmask_octets(32), (255, 255, 255, 255))
        self.assertEqual(cidr_tools.netmask_octets(11), (255, 224, 0, 0))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_cidr_netmask_octets(self):
        '''Test cidr_tools.cidr_netmask_octets()
        '''

        self.assertEqual(
            cidr_tools.cidr_netmask_octets('10.23.0.0/16'),
            (255, 255, 0, 0)
            )
        self.assertEqual(
            cidr_tools.cidr_netmask_octets('10.23.0.0/32'),
            (255, 255, 255, 255)
            )
        self.assertEqual(
            cidr_tools.cidr_netmask_octets('10.23.0.0/22'),
            (255, 255, 252, 0)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_masked_address_octets(self):
        '''Test cidr_tools.masked_address_octets()
        '''

        self.assertEqual(
            cidr_tools.masked_address_octets(
                '10.23.71.93', cidr_tools.cidr_netmask_octets('10.23.0.0/16')
                ),
            [10, 23, 0, 0]
            )
        self.assertEqual(
            cidr_tools.masked_address_octets(
                '10.23.71.93', cidr_tools.cidr_netmask_octets('10.23.0.0/20')
                ),
            [10, 23, 64, 0]
            )
        self.assertEqual(
            cidr_tools.masked_address_octets(
                '10.23.71.93', cidr_tools.cidr_netmask_octets('10.23.0.0/28')
                ),
            [10, 23, 71, 80]
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_masked_address(self):
        '''Test cidr_tools.masked_address()
        '''

        self.assertEqual(
            cidr_tools.masked_address(
                '10.23.71.93', cidr_tools.cidr_netmask_octets('10.23.0.0/16')
                ),
            '10.23.0.0'
            )
        self.assertEqual(
            cidr_tools.masked_address(
                '10.23.71.93', cidr_tools.cidr_netmask_octets('10.23.0.0/20')
                ),
            '10.23.64.0'
            )
        self.assertEqual(
            cidr_tools.masked_address(
                '10.23.71.93', cidr_tools.cidr_netmask_octets('10.23.0.0/24')
                ),
            '10.23.71.0'
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_is_subcidr(self):
        '''Test cidr_tools.is_subcidr()
        '''

        self.assertTrue(
            cidr_tools.is_subcidr('128.56.0.0/16', '128.0.0.0/8')
            )
        self.assertTrue(
            cidr_tools.is_subcidr('128.56.0.0/16', '0.0.0.0/0')
            )
        self.assertTrue(
            cidr_tools.is_subcidr('128.56.0.0/16', '128.56.1.0/16')
            )
        self.assertFalse(
            cidr_tools.is_subcidr('128.56.0.0/16', '128.78.0.0/16')
            )
        self.assertFalse(
            cidr_tools.is_subcidr('128.56.0.0/16', '128.58.0.0/17')
            )
        self.assertFalse(
            cidr_tools.is_subcidr('128.56.0.0/16', '128.56.0.0/32')
            )
        self.assertFalse(
            cidr_tools.is_subcidr('128.56.0.0/16', '128.56.0.0')
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_is_universal_cidr(self):
        '''Test cidr_tools.is_universal_cidr()
        '''
        self.assertTrue(cidr_tools.is_universal_cidr(UNIVERSAL_CIDR))
        self.assertFalse(cidr_tools.is_universal_cidr('0.0.0.0'))
        self.assertFalse(cidr_tools.is_universal_cidr('128.56.28.14'))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_is_valid_address(self):
        '''Test cidr_tools.is_valid_address()
        '''
        self.assertTrue(cidr_tools.is_valid_address('0.0.0.0'))
        self.assertTrue(cidr_tools.is_valid_address('1.1.1.1'))
        self.assertTrue(cidr_tools.is_valid_address('255.255.255.255'))
        self.assertTrue(cidr_tools.is_valid_address('128.56.28.14'))

        self.assertFalse(cidr_tools.is_valid_address('255.255.256.255'))
        self.assertFalse(cidr_tools.is_valid_address('128.56.28.14.'))
        self.assertFalse(cidr_tools.is_valid_address('.128.56.28.14'))
        self.assertFalse(cidr_tools.is_valid_address('128..56.28.14'))
        self.assertFalse(cidr_tools.is_valid_address('128.56.28'))
        self.assertFalse(cidr_tools.is_valid_address('128.56.28.14.7'))
        self.assertFalse(cidr_tools.is_valid_address('128.56.28/16'))
        self.assertFalse(cidr_tools.is_valid_address('bob'))
        self.assertFalse(cidr_tools.is_valid_address(''))
        self.assertFalse(cidr_tools.is_valid_address(0))
        self.assertFalse(cidr_tools.is_valid_address(None))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_is_valid_cidr(self):
        '''Test cidr_tools.is_valid_cidr()
        '''
        self.assertTrue(cidr_tools.is_valid_cidr(UNIVERSAL_CIDR))
        self.assertTrue(cidr_tools.is_valid_cidr('128.56.28.14/1'))
        self.assertTrue(cidr_tools.is_valid_cidr('128.56.28.14/16'))
        self.assertTrue(cidr_tools.is_valid_cidr('128.56.28.14/32'))

        self.assertFalse(cidr_tools.is_valid_cidr('128.56.28.14'))
        self.assertFalse(cidr_tools.is_valid_cidr('128.56.28.14/33'))
        self.assertFalse(cidr_tools.is_valid_cidr('128.56.28/16'))
        self.assertFalse(cidr_tools.is_valid_cidr('128.56.28.14.7/16'))
        self.assertFalse(cidr_tools.is_valid_cidr('128.56.28.256/16'))
        self.assertFalse(cidr_tools.is_valid_cidr('128.56.28.14/16.'))
        self.assertFalse(cidr_tools.is_valid_cidr('128.56.28.14/16.1'))
        self.assertFalse(cidr_tools.is_valid_cidr('128.56.28.14/.1'))
        self.assertFalse(cidr_tools.is_valid_cidr('128.56.28.14/x'))
        self.assertFalse(cidr_tools.is_valid_cidr('128.56.28.14/-22'))
        self.assertFalse(cidr_tools.is_valid_cidr('bob'))
        self.assertFalse(cidr_tools.is_valid_cidr('bob/22'))
        self.assertFalse(cidr_tools.is_valid_cidr('bob/x'))
        self.assertFalse(cidr_tools.is_valid_cidr(''))
        self.assertFalse(cidr_tools.is_valid_cidr(0))
        self.assertFalse(cidr_tools.is_valid_cidr(None))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_is_valid_address_or_cidr(self):
        '''Test cidr_tools.is_valid_address_or_cidr()
        '''
        self.assertTrue(cidr_tools.is_valid_address_or_cidr('0.0.0.0'))
        self.assertTrue(cidr_tools.is_valid_address_or_cidr('1.1.1.1'))
        self.assertTrue(cidr_tools.is_valid_address_or_cidr('255.255.255.255'))
        self.assertTrue(cidr_tools.is_valid_address_or_cidr('128.56.28.14'))

        self.assertTrue(cidr_tools.is_valid_address_or_cidr(UNIVERSAL_CIDR))
        self.assertTrue(cidr_tools.is_valid_address_or_cidr('128.56.28.14/1'))
        self.assertTrue(cidr_tools.is_valid_address_or_cidr('128.56.28.14/16'))
        self.assertTrue(cidr_tools.is_valid_address_or_cidr('128.56.28.14/32'))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestCidr(unittest.TestCase):
    '''
    Basic test cases for Cidr.
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        pass

    # # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # def test_cidr_tools_init(self):
    #     '''Test initialization of a Cidr instance.
    #     '''

    #     thing = cidr_tools.Cidr()
    #     self.assertIsNotNone(thing)

    #     self.assertTrue(True)
    #     self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
