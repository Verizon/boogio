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

'''Test cases for importing the boogio package contents.'''

import unittest


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestImports(unittest.TestCase):
    '''
    Basic test cases for importing boogio package contents
    '''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        pass

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_import_boogio(self):
        '''Test that "import boogio" creates the desired namespaces.
        '''

        # pylint: disable=redefined-variable-type

        exc = None

        try:
            import boogio
        except ImportError as exc:
            pass

        self.assertIsNone(exc)

        # Some general checks that namespaces are correctly defined.
        self.assertIn('aws_informer', dir(boogio))
        self.assertIn('aws_reporter', dir(boogio))
        self.assertIn('aws_surveyor', dir(boogio))
        self.assertIn('sqs_sifter', dir(boogio))
        self.assertIn('AWSInformer', dir(boogio.aws_informer))
        self.assertIn('AWSSurveyor', dir(boogio.aws_surveyor))
        self.assertIn('AWSReporter', dir(boogio.aws_reporter))

        try:
            _ = boogio.aws_informer.AWSMediator()
        except NameError as exc:
            pass

        self.assertIsNone(exc)

        try:
            _ = boogio.aws_surveyor.AWSSurveyor()
        except NameError as exc:
            pass

        self.assertIsNone(exc)

        try:
            _ = boogio.aws_reporter.AWSReporter()
        except NameError as exc:
            pass

        self.assertIsNone(exc)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_import_boogio_aws_informer(self):
        '''Test "import boogio.aws_informer".
        '''

        exc = None

        try:
            import boogio.aws_informer
        except ImportError as exc:
            pass

        self.assertIsNone(exc)

        # Some general checks that namespaces are correctly defined.
        self.assertIn('AWSInformer', dir(boogio.aws_informer))

        try:
            _ = boogio.aws_informer.AWSMediator()
        except NameError as exc:
            pass

        self.assertIsNone(exc)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_import_boogio_aws_surveyor(self):
        '''Test "import boogio.aws_surveyor".
        '''

        exc = None

        try:
            import boogio.aws_surveyor
        except ImportError as exc:
            pass

        self.assertIsNone(exc)

        # Some general checks that namespaces are correctly defined.
        self.assertIn('AWSSurveyor', dir(boogio.aws_surveyor))

        try:
            _ = boogio.aws_surveyor.AWSSurveyor()
        except NameError as exc:
            pass

        self.assertIsNone(exc)
        # print
        # print
        # print
        # print dir(boogio.aws_surveyor)
        # print
        # print
        # print

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_import_boogio_aws_reporter(self):
        '''Test "import boogio.aws_reporter".
        '''

        exc = None

        try:
            import boogio.aws_reporter
        except ImportError as exc:
            pass

        self.assertIsNone(exc)

        # Some general checks that namespaces are correctly defined.
        self.assertIn('AWSReporter', dir(boogio.aws_reporter))

        try:
            _ = boogio.aws_reporter.AWSReporter()
        except NameError as exc:
            pass

        self.assertIsNone(exc)
        # print
        # print
        # print
        # print dir(boogio.aws_reporter)
        # print
        # print
        # print


if __name__ == '__main__':
    unittest.main()
