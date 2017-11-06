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

'''Test cases for the aws_surveyor module package methods.'''

import unittest

import boogio.aws_surveyor as aws_surveyor


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSSurveyorAllRegions(unittest.TestCase):
    '''Basic test cases for the AWSSurveyor.all_regions() method.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):

        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_all_regions(self):
        '''
        Test all_regions() method.

        '''

        all_regions = aws_surveyor.all_regions

        # No filter.
        self.assertIsNotNone(all_regions())
        self.assertTrue(isinstance(all_regions(), list))

        # Empty filter.
        self.assertIsNotNone(all_regions(None, None, ""))
        self.assertTrue(isinstance(all_regions(None, None, ""), list))

        # Nonsense filter.
        self.assertIsNotNone(all_regions(None, None, "xyz123"))
        self.assertTrue(isinstance(all_regions(None, None, "xyz123"), list))
        self.assertEqual(all_regions(None, None, "xyz123"), [])

        # Valid filters.
        self.assertIsNotNone(all_regions(None, None, "us"))
        self.assertTrue(isinstance(all_regions(None, None, "us"), list))
        self.assertEqual(
            len(all_regions(None, None, "us", "us")),
            len(list(set(all_regions(None, None, "us"))))
            )

        self.assertIsNotNone(all_regions(None, None, "us", "us"))
        self.assertTrue(isinstance(all_regions(None, None, "us", "us"), list))
        self.assertEqual(
            len(all_regions(None, None, "us", "us")),
            len(all_regions(None, None, "us"))
            )

        self.assertIsNotNone(all_regions(None, None, "us", "east"))
        self.assertTrue(
            isinstance(all_regions(None, None, "us", "east"), list)
            )

        self.assertIsNotNone(all_regions(None, None, "us-east"))
        self.assertTrue(isinstance(all_regions(None, None, "us-east"), list))

        # Expected region results.
        self.assertIn("us-east-1", all_regions())
        self.assertIn("us-west-1", all_regions())

        self.assertIn("us-east-1", all_regions(None, None, "us"))
        self.assertIn("us-east-2", all_regions(None, None, "us"))
        self.assertIn("us-west-1", all_regions(None, None, "us"))
        self.assertIn("us-west-2", all_regions(None, None, "us"))
        self.assertEqual(len(all_regions(None, None, "us")), 4)

        self.assertIn("us-east-1", all_regions(None, None, "us-east"))
        self.assertEqual(["us-east-1"], all_regions(None, None, "us-east-1"))

        # - - - - - - - - - - - - - - - - - - - -
        # Some checks that filters at least appear to be appropriately strict.
        # - - - - - - - - - - - - - - - - - - - -
        len_us = len(all_regions(None, None, "us"))
        len_east = len(all_regions(None, None, "east"))
        len_us_east = len(all_regions(None, None, "us-east"))
        len_us_east_1 = len(all_regions(None, None, "us-east-1"))

        len_us_and_east = len(all_regions(None, None, "us", "east"))

        self.assertTrue(len_us_east_1 < len_us_east)
        self.assertTrue(len_us_east_1 < len_east)

        self.assertTrue(len_us_east < len_east)
        self.assertTrue(len_us_east < len_us)

        self.assertTrue(len_us < len_us_and_east)
        self.assertTrue(len_east < len_us_and_east)
        self.assertTrue(len_us_east < len_us_and_east)
        self.assertTrue(len_us_east_1 < len_us_and_east)


if __name__ == '__main__':
    unittest.main()
