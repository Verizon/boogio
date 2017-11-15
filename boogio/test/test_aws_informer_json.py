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

'''Test cases for aws_informer JSON import/export.

These are very slow, hence placing in a separate file.
'''

import unittest

import json
# import random

from boogio import aws_informer
from boogio import site_boogio
from boogio.utensils import flatten

# Sharing this will mean reducing fetch time when the same resources are needed
# in multiple test cases.
GLOBAL_MEDIATOR = aws_informer.AWSMediator(
    region_name=site_boogio.test_region_name,
    profile_name=site_boogio.test_profile_name
    )

FLATTEN_COLLAPSES = (flatten.flatten({'a': {'b': {}}, 'c': 1}) == [])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSInformerJSONDumps(unittest.TestCase):
    '''Basic test cases for AWSInformer and subclasses JSON output.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name
    # TODO: Add skiptest based on os.environ['TEST_DURATION_LIMIT']

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        cls.elb_informer_0 = aws_informer.AWSInformer(
            GLOBAL_MEDIATOR.entities('elb')[0],
            mediator=GLOBAL_MEDIATOR
            )

        cls.elb_informer_1 = aws_informer.AWSInformer(
            GLOBAL_MEDIATOR.entities('elb')[-1],
            mediator=GLOBAL_MEDIATOR
            )

        cls.vpc_informer = aws_informer.AWSInformer(
            GLOBAL_MEDIATOR.entities('vpc')[0],
            mediator=GLOBAL_MEDIATOR
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_informer_json_dumps(self):
        '''Test basic json output without specific resource knowledge.'''

        # - - - - - - - - - - - - - - - -

        as_json = self.elb_informer_0.json_dumps()
        from_json = json.loads(as_json)

        self.assertTrue(isinstance(as_json, str))
        self.assertTrue(isinstance(from_json, dict))

        self.elb_informer_0.expand()
        as_json = self.elb_informer_0.json_dumps()
        from_json = json.loads(as_json)

        self.assertTrue(isinstance(as_json, str))
        self.assertTrue(isinstance(from_json, dict))

        # - - - - - - - - - - - - - - - -

        as_json = self.vpc_informer.json_dumps()
        from_json = json.loads(as_json)

        self.assertTrue(isinstance(as_json, str))
        self.assertTrue(isinstance(from_json, dict))

        self.vpc_informer.expand()
        as_json = self.vpc_informer.json_dumps()
        from_json = json.loads(as_json)

        self.assertTrue(isinstance(as_json, str))
        self.assertTrue(isinstance(from_json, dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @unittest.skipIf(
        FLATTEN_COLLAPSES,
        'If a dict contains {} as a value anywhere, flatten() collapses.'
        )
    def test_aws_informer_json_dumps_flat(self):
        '''Test basic json output without specific resource knowledge.'''

        # - - - - - - - - - - - - - - - -

        as_flat_json = self.elb_informer_0.json_dumps(flat=True)
        from_flat_json = json.loads(as_flat_json)

        self.assertTrue(isinstance(as_flat_json, str))
        self.assertTrue(isinstance(from_flat_json, list))
        self.assertTrue(isinstance(from_flat_json[0], dict))

        self.elb_informer_0.expand()
        as_flat_json = self.elb_informer_0.json_dumps(flat=True)
        from_flat_json = json.loads(as_flat_json)

        self.assertTrue(isinstance(as_flat_json, str))
        self.assertTrue(isinstance(from_flat_json, list))
        self.assertTrue(isinstance(from_flat_json[0], dict))

        # - - - - - - - - - - - - - - - -

        as_flat_json = self.vpc_informer.json_dumps(flat=True)
        from_flat_json = json.loads(as_flat_json)

        self.assertTrue(isinstance(as_flat_json, str))
        self.assertTrue(isinstance(from_flat_json, list))
        self.assertTrue(isinstance(from_flat_json[0], dict))

        self.vpc_informer.expand()
        as_flat_json = self.vpc_informer.json_dumps(flat=True)
        from_flat_json = json.loads(as_flat_json)

        self.assertTrue(isinstance(as_flat_json, str))
        self.assertTrue(isinstance(from_flat_json, list))
        self.assertTrue(isinstance(from_flat_json[0], dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_elb_informer_json_dumps(self):
        '''Test elb resource json output.'''

        # - - - - - - - - - - - - - - - - - - - -

        as_json = self.elb_informer_1.json_dumps()
        from_json = json.loads(as_json)

        self.assertTrue(isinstance(as_json, str))
        self.assertTrue(isinstance(from_json, dict))

        self.elb_informer_1.expand()
        as_json = self.elb_informer_1.json_dumps()
        from_json = json.loads(as_json)

        self.assertTrue(isinstance(as_json, str))
        self.assertTrue(isinstance(from_json, dict))

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @unittest.skipIf(
        FLATTEN_COLLAPSES,
        'If a dict contains {} as a value anywhere, flatten() collapses.'
        )
    def test_elb_informer_json_dumps_flat(self):
        '''Test elb resource json output.'''

        # - - - - - - - - - - - - - - - - - - - -

        as_flat_json = self.elb_informer_1.json_dumps(flat=True)
        from_flat_json = json.loads(as_flat_json)

        self.assertTrue(isinstance(as_flat_json, str))
        self.assertTrue(isinstance(from_flat_json, list))
        self.assertTrue(isinstance(from_flat_json[0], dict))

        as_flat_json = self.elb_informer_1.json_dumps(flat=True)
        from_flat_json = json.loads(as_flat_json)

        self.assertTrue(isinstance(as_flat_json, str))
        self.assertTrue(isinstance(from_flat_json, list))
        self.assertTrue(isinstance(from_flat_json[0], dict))


if __name__ == '__main__':
    unittest.main()
