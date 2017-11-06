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

'''Test cases for the aws_surveyor.py module.'''

import unittest

import json
import os
import tempfile
import time

import botocore.exceptions
import boto3

from boogio import aws_surveyor
from boogio import aws_informer
from boogio.site_boogio import test_profile_name

# Record this now, before any local code has executed.
ORIGINAL_DEFAULT_CONFIG_FILENAME = (
    aws_surveyor.AWSSurveyor.default_config_filename()
    )
ORIGINAL_DEFAULT_CONFIG_DIR = (
    aws_surveyor.AWSSurveyor.default_config_dir()
    )
ORIGINAL_DEFAULT_CONFIG_PATH = (
    aws_surveyor.AWSSurveyor.default_config_path()
    )

TEST_PROFILE_NAME = test_profile_name
POSSIBLE_PROFILES = []
AVAILABLE_PROFILES = [test_profile_name]

for profile_name in POSSIBLE_PROFILES:

    try:
        boto3.session.Session(
            profile_name=profile_name, region_name='us-east-1'
            )
        AVAILABLE_PROFILES.append(profile_name)

    except botocore.exceptions.ProfileNotFound:
        pass


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSSurveyorClassConstants(unittest.TestCase):
    '''Test cases for AWSSurveyor class constants.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def tearDownClass(cls):
        '''Restore any changed defaults.'''

        # Restore any changed default config filename or directory we set.
        aws_surveyor.AWSSurveyor.default_config_filename(
            ORIGINAL_DEFAULT_CONFIG_FILENAME
            )
        aws_surveyor.AWSSurveyor.default_config_dir(
            ORIGINAL_DEFAULT_CONFIG_DIR
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case level common fixture.'''

        # Restore any changed default config filename or directory we set.
        aws_surveyor.AWSSurveyor.default_config_filename(
            ORIGINAL_DEFAULT_CONFIG_FILENAME
            )
        aws_surveyor.AWSSurveyor.default_config_dir(
            ORIGINAL_DEFAULT_CONFIG_DIR
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_default_config_settings(self):
        '''Test defaults for config file location.'''

        self.assertEqual(
            aws_surveyor.AWSSurveyor.default_config_dir(),
            os.path.join(os.path.expanduser('~'), '.aws')
            )

        self.assertEqual(
            aws_surveyor.AWSSurveyor.default_config_filename(),
            'aws_surveyor.cfg'
            )

        self.assertEqual(
            aws_surveyor.AWSSurveyor.default_config_path(),
            os.path.join(os.path.expanduser('~'), '.aws', 'aws_surveyor.cfg')
            )

        # We won't use these in this test class, so we just set them to
        # something different.
        alt_default_config_dir = 'slithy'
        alt_default_config_filename = 'toves'

        self.assertEqual(
            aws_surveyor.AWSSurveyor.default_config_dir(
                alt_default_config_dir
                ),
            alt_default_config_dir
            )

        self.assertEqual(
            aws_surveyor.AWSSurveyor.default_config_filename(
                alt_default_config_filename
                ),
            alt_default_config_filename
            )

        self.assertEqual(
            aws_surveyor.AWSSurveyor.default_config_path(),
            os.path.join(alt_default_config_dir, alt_default_config_filename)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_surveyable_types(self):
        '''Test AWSSurveyor.surveyable_types() class method.'''

        # pylint: disable=protected-access

        types = aws_surveyor.AWSSurveyor._surveyable_types()
        self.assertNotEqual(types, [])

        regional_types = aws_informer.regional_types()
        regionless_types = aws_informer.regionless_types()
        unitary_types = aws_informer.unitary_types()

        self.assertItemsEqual(
            types, regional_types + regionless_types + unitary_types
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSSurveyorInitialization(unittest.TestCase):
    '''Test cases for AWSSurveyor initialization.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        # TODO: We should do one test to confirm that alternate paths
        # for default filename set in AWSSurveyor is used properly,
        # then always set a safe default filename to avoid clobbering.

        # This will be cleaned up in tearDownClass().
        cls.tmpdir = tempfile.mkdtemp()

        cls.all_presets_sample = {
            "profiles": ["some_profile", "another_profile"],
            "regions": ["us-east-1", "us-west-1", "us-west-2"],
            "entity_types": ["ec2", "security_group", "subnet", "vpc"],
            }

        cls.profiles_presets_sample = {
            "profiles": ["this_profile", "that_profile"],
            }

        # Paths into $HOME/.aws and to the default config file.
        cls.home = os.path.expanduser('~')
        cls.aws_dir = os.path.join(cls.home, '.aws')

        # The default configuration file name for AWSSurveyor instances.
        cls.default_config_filename = (
            aws_surveyor.AWSSurveyor.default_config_filename()
            )
        cls.default_config_path = os.path.join(
            cls.aws_dir,
            cls.default_config_filename
            )

        # We will use an alternate default config setting in some cases.
        cls.alt_default_config_filename = '.'.join(
            [cls.default_config_filename, str(time.time())]
            )
        cls.alt_default_config_dir = cls.tmpdir

        # Path to an alternate config file in our working temporary directory.
        cls.tmpdir_config_path = os.path.join(
            cls.tmpdir,
            cls.default_config_filename
            )

        # Add any alternate config files created to this list to
        # ensure cleanup.
        cls.paths_to_clean = set([])

        # Record whether there was a default config file present, so we
        # can check against this in tearDown before removing a temporary
        # version created for testing. We'll just exit with an error if
        # there was a default config file already, rather than risk
        # mucking with it.
        cls.default_config_was_present = os.path.exists(
            ORIGINAL_DEFAULT_CONFIG_PATH
            )

        # Turn off mediator connection, as we use a lot of fake profiles
        # and regions in this test class.
        # pylint: disable=protected-access
        cls.original_hold_sessions = aws_surveyor.AWSSurveyor._hold_sessions
        aws_surveyor.AWSSurveyor._hold_sessions = True

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def tearDownClass(cls):
        '''Remove test files and temp directory, restore changed defaults.'''

        # Remove temp directory.
        for root, dirs, files in os.walk(cls.tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(cls.tmpdir)

        # Restore any changed default config filename or directory we set.
        aws_surveyor.AWSSurveyor.default_config_filename(
            ORIGINAL_DEFAULT_CONFIG_FILENAME
            )
        aws_surveyor.AWSSurveyor.default_config_dir(
            ORIGINAL_DEFAULT_CONFIG_DIR
            )

        # Remove any default config file we created.
        if (
                not cls.default_config_was_present and
                os.path.exists(
                    ORIGINAL_DEFAULT_CONFIG_PATH
                    )
                ):  # pylint: disable=bad-continuation
            os.remove(ORIGINAL_DEFAULT_CONFIG_PATH)

        # Remove any alternate config files we created.
        for clean_path in cls.paths_to_clean:
            if os.path.exists(clean_path):
                os.remove(clean_path)

        # We changed this to True in setUpClass.
        # pylint: disable=protected-access
        aws_surveyor.AWSSurveyor._hold_sessions = cls.original_hold_sessions

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case level common setup.'''

        # Restore any changed default config filename or directory we set.
        aws_surveyor.AWSSurveyor.default_config_filename(
            ORIGINAL_DEFAULT_CONFIG_FILENAME
            )
        aws_surveyor.AWSSurveyor.default_config_dir(
            ORIGINAL_DEFAULT_CONFIG_DIR
            )

        # Remove any default config file we previously created.
        if (
                not self.default_config_was_present and
                os.path.exists(
                    ORIGINAL_DEFAULT_CONFIG_PATH
                    )
                ):  # pylint: disable=bad-continuation
            os.remove(ORIGINAL_DEFAULT_CONFIG_PATH)

        # Remove any alternate config files we created in previous tests.
        for clean_path in self.paths_to_clean:
            if os.path.exists(clean_path):
                os.remove(clean_path)
        self.paths_to_clean = set([])

        # TODO: change class default paths in setup, restore them
        # in teardown, so we don't have to worry about mucking up
        # a pre-existing config file. Create a new tmp dir for this?

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_timestamp(self):
        '''Test initialization of the AWSSurveyor survey timestamp.'''
        self.assertEqual(
            aws_surveyor.AWSSurveyor.timestamp_format,
            "%Y%m%dT%H%M%S"
            )

        surveyor = aws_surveyor.AWSSurveyor()
        self.assertEqual(surveyor.survey_timestamp, None)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_change_default_config_file(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test changing default config file name
        # then initializing from it.
        # - - - - - - - - - - - - - - - - - - - -

        # Record the original default config path, and create a
        # config file there using all_presets_sample.
        default_config_path = (
            aws_surveyor.AWSSurveyor.default_config_path()
            )

        self.assertFalse(os.path.exists(default_config_path))
        with open(default_config_path, 'w') as fptr:
            json.dump(self.all_presets_sample, fptr)

        # Change and record the new default config path, and create a
        # config file there using profiles_presets_sample.
        aws_surveyor.AWSSurveyor.default_config_filename(
            self.alt_default_config_filename
            )
        alt_default_config_path = (
            aws_surveyor.AWSSurveyor.default_config_path()
            )

        self.assertFalse(os.path.exists(alt_default_config_path))
        with open(alt_default_config_path, 'w') as fptr:
            json.dump(self.profiles_presets_sample, fptr)
        self.paths_to_clean.add(alt_default_config_path)

        self.assertNotEqual(default_config_path, alt_default_config_path)

        # With the new config path, this surveyor should be initialized
        # using profiles_presets_sample.
        surveyor = aws_surveyor.AWSSurveyor()

        self.assertItemsEqual(
            surveyor.profiles,
            self.profiles_presets_sample['profiles']
            )
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

        # Clean up our alternate configuration file.
        if os.path.exists(alt_default_config_path):
            os.remove(alt_default_config_path)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_change_default_config_dir(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test changing default config directory
        # then initializing from it.
        # - - - - - - - - - - - - - - - - - - - -

        # Record the original default config path, and create a
        # config file there using all_presets_sample.
        default_config_path = (
            aws_surveyor.AWSSurveyor.default_config_path()
            )

        # Don't clobber a user's default configuration file.
        self.assertFalse(os.path.exists(default_config_path))
        with open(default_config_path, 'w') as fptr:
            json.dump(self.all_presets_sample, fptr)

        # Change and record the new default config path, and create a
        # config file there using profiles_presets_sample.
        aws_surveyor.AWSSurveyor.default_config_dir(
            self.alt_default_config_dir
            )
        alt_default_config_path = (
            aws_surveyor.AWSSurveyor.default_config_path()
            )
        self.paths_to_clean.add(alt_default_config_path)

        self.assertFalse(os.path.exists(alt_default_config_path))
        with open(alt_default_config_path, 'w') as fptr:
            json.dump(self.profiles_presets_sample, fptr)
        self.paths_to_clean.add(alt_default_config_path)

        self.assertNotEqual(default_config_path, alt_default_config_path)

        self.assertEqual(
            alt_default_config_path,
            os.path.join(
                self.alt_default_config_dir,
                aws_surveyor.AWSSurveyor.default_config_filename()
                )
            )

        # With the new config path, this surveyor should be initialized
        # using profiles_presets_sample.
        surveyor = aws_surveyor.AWSSurveyor()

        self.assertItemsEqual(
            surveyor.profiles,
            self.profiles_presets_sample['profiles']
            )
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

        # Clean up our alternate configuration file.
        if os.path.exists(alt_default_config_path):
            os.remove(alt_default_config_path)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_no_config_file(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test initialiation with no config file.
        # - - - - - - - - - - - - - - - - - - - -

        self.assertFalse(os.path.exists(self.default_config_path))

        surveyor = aws_surveyor.AWSSurveyor()

        self.assertEqual(surveyor.profiles, [])
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_full_config_file(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test initialiation with full presets in
        # default config file.
        # - - - - - - - - - - - - - - - - - - - -

        self.assertFalse(os.path.exists(self.default_config_path))
        with open(self.default_config_path, 'w') as fptr:
            json.dump(self.all_presets_sample, fptr)

        # - - - - - - - - - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor()

        self.assertItemsEqual(
            surveyor.profiles,
            self.all_presets_sample['profiles']
            )
        self.assertItemsEqual(
            surveyor.regions,
            self.all_presets_sample['regions']
            )
        self.assertItemsEqual(
            surveyor.entity_types,
            self.all_presets_sample['entity_types']
            )

        # Remove the test config file.
        os.remove(self.default_config_path)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_suppress_config_file(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test initialiation with presets in default
        # config file, but suppressed.
        # - - - - - - - - - - - - - - - - - - - -

        self.assertFalse(os.path.exists(self.default_config_path))
        with open(self.default_config_path, 'w') as fptr:
            json.dump(self.all_presets_sample, fptr)

        # - - - - - - - - - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor(config_path='')

        self.assertEqual(surveyor.profiles, [])
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

        # Remove the test config file.
        os.remove(self.default_config_path)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_partial_config_file(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test initialiation with only some presets
        # in default config file.
        # - - - - - - - - - - - - - - - - - - - -

        self.assertFalse(os.path.exists(self.default_config_path))
        with open(self.default_config_path, 'w') as fptr:
            json.dump(self.profiles_presets_sample, fptr)

        # - - - - - - - - - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor()

        self.assertItemsEqual(
            surveyor.profiles,
            self.profiles_presets_sample['profiles']
            )
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

        # Remove the test config file.
        os.remove(self.default_config_path)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_alternate_config_file(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test initialiation with presets in
        # non-default config file.
        # - - - - - - - - - - - - - - - - - - - -

        # Create a non-default config file.
        with open(self.tmpdir_config_path, 'w') as fptr:
            json.dump(self.profiles_presets_sample, fptr)
        self.paths_to_clean.add(self.tmpdir_config_path)

        # Create a separate default config file to make sure it
        # isn't used.
        self.assertFalse(os.path.exists(self.default_config_path))
        with open(self.default_config_path, 'w') as fptr:
            json.dump(self.all_presets_sample, fptr)

        # - - - - - - - - - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor(
            config_path=self.tmpdir_config_path
            )

        self.assertItemsEqual(
            surveyor.profiles,
            self.profiles_presets_sample['profiles']
            )
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

        # Remove the test config files.
        os.remove(self.default_config_path)
        os.remove(self.tmpdir_config_path)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_override_config_file(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test initialiation with config file presets
        # overridden by initialization arguments.
        # - - - - - - - - - - - - - - - - - - - -

        with open(self.tmpdir_config_path, 'w') as fptr:
            json.dump(self.all_presets_sample, fptr)
        self.paths_to_clean.add(self.tmpdir_config_path)

        self.assertFalse(os.path.exists(self.default_config_path))
        with open(self.default_config_path, 'w') as fptr:
            json.dump(self.profiles_presets_sample, fptr)

        alt_profiles = ['p', 'q']
        alt_regions = ['r', 's']
        alt_entity_types = ['eip', 'elb']

        # - - - - - - - - - - - - - - - - - - - -

        # Using profiles_presets_sample in the default config file.
        surveyor = aws_surveyor.AWSSurveyor(
            regions=alt_regions
            )

        # regions was superceded by alt_regions.
        self.assertItemsEqual(
            surveyor.profiles,
            self.profiles_presets_sample['profiles']
            )
        self.assertItemsEqual(surveyor.regions, alt_regions)
        self.assertEqual(surveyor.entity_types, [])

        # - - - - - - - - - - - - - - - - - - - -

        # Using all_presets_sample in the alternate config file.
        surveyor = aws_surveyor.AWSSurveyor(
            profiles=alt_profiles,
            regions=alt_regions,
            config_path=self.tmpdir_config_path
            )

        # profiles and regions were superceded by alts.
        self.assertItemsEqual(surveyor.profiles, alt_profiles)
        self.assertItemsEqual(surveyor.regions, alt_regions)
        self.assertItemsEqual(
            surveyor.entity_types,
            self.all_presets_sample['entity_types']
            )

        # - - - - - - - - - - - - - - - - - - - -

        # Using all_presets_sample in the alternate config file.
        surveyor = aws_surveyor.AWSSurveyor(
            regions=alt_regions,
            entity_types=alt_entity_types,
            config_path=self.tmpdir_config_path
            )

        # profiles and regions were superceded by alts.
        self.assertItemsEqual(
            surveyor.profiles,
            self.all_presets_sample['profiles']
            )
        self.assertItemsEqual(surveyor.regions, alt_regions)
        self.assertItemsEqual(surveyor.entity_types, alt_entity_types)

        # Remove the test config file.
        os.remove(self.default_config_path)
        os.remove(self.tmpdir_config_path)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_add_to_config_file(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test initialiation with config file presets
        # added to by initialization arguments.
        # - - - - - - - - - - - - - - - - - - - -

        with open(self.tmpdir_config_path, 'w') as fptr:
            json.dump(self.all_presets_sample, fptr)
        self.paths_to_clean.add(self.tmpdir_config_path)

        self.assertFalse(os.path.exists(self.default_config_path))
        with open(self.default_config_path, 'w') as fptr:
            json.dump(self.all_presets_sample, fptr)

        alt_profiles = ['p', 'q']
        alt_regions = ['r', 's']
        alt_entity_types = ['elb', 'eip']

        # - - - - - - - - - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor(
            regions=alt_regions,
            add_to_config=True
            )

        self.assertItemsEqual(
            surveyor.profiles,
            self.all_presets_sample['profiles']
            )
        # alt_regions was added to regions.
        self.assertItemsEqual(
            surveyor.regions,
            self.all_presets_sample['regions'] + alt_regions
            )
        self.assertItemsEqual(
            surveyor.entity_types,
            self.all_presets_sample['entity_types']
            )

        # - - - - - - - - - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor(
            entity_types=alt_entity_types,
            add_to_config=True
            )

        self.assertItemsEqual(
            surveyor.profiles,
            self.all_presets_sample['profiles']
            )
        self.assertItemsEqual(
            surveyor.regions,
            self.all_presets_sample['regions']
            )
        # alt_entity_types was added to entity_types.
        self.assertItemsEqual(
            surveyor.entity_types,
            self.all_presets_sample['entity_types'] + alt_entity_types
            )

        # - - - - - - - - - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor(
            profiles=alt_profiles,
            regions=alt_regions,
            config_path=self.tmpdir_config_path,
            add_to_config=True
            )

        # alt_profiles and alt_regions were added.
        self.assertItemsEqual(
            surveyor.profiles,
            self.all_presets_sample['profiles'] + alt_profiles
            )
        self.assertItemsEqual(
            surveyor.regions,
            self.all_presets_sample['regions'] + alt_regions
            )
        self.assertItemsEqual(
            surveyor.entity_types,
            self.all_presets_sample['entity_types']
            )

        # Remove the test config file.
        os.remove(self.default_config_path)
        os.remove(self.tmpdir_config_path)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_presets_arguments(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test initialiation with presets as
        # arguments at initialization.
        # - - - - - - - - - - - - - - - - - - - -

        self.assertFalse(os.path.exists(self.default_config_path))

        # All presets provided.
        surveyor = aws_surveyor.AWSSurveyor(
            profiles=self.all_presets_sample['profiles'],
            regions=self.all_presets_sample['regions'],
            entity_types=self.all_presets_sample['entity_types']
            )

        self.assertItemsEqual(
            surveyor.profiles,
            self.all_presets_sample['profiles']
            )
        self.assertItemsEqual(
            surveyor.regions,
            self.all_presets_sample['regions']
            )
        self.assertItemsEqual(
            surveyor.entity_types,
            self.all_presets_sample['entity_types']
            )

        # Ony some presets provided.
        surveyor = aws_surveyor.AWSSurveyor(
            entity_types=self.all_presets_sample['entity_types']
            )

        self.assertEqual(surveyor.profiles, [])
        self.assertEqual(surveyor.regions, [])
        self.assertItemsEqual(
            surveyor.entity_types,
            self.all_presets_sample['entity_types']
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_all_regions(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test initialiation with all_regions=True.
        # - - - - - - - - - - - - - - - - - - - -

        surveyor = aws_surveyor.AWSSurveyor(
            config_path='',
            set_all_regions=True
            )

        self.assertEqual(surveyor.profiles, [])
        self.assertEqual(surveyor.entity_types, [])

        self.assertEqual(surveyor.regions, aws_surveyor.all_regions())

        # - - - - - - - - - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(
            config_path='',
            regions=['us-east-1'],
            set_all_regions=True
            )

        self.assertEqual(surveyor.profiles, [])
        self.assertEqual(surveyor.entity_types, [])

        self.assertEqual(surveyor.regions, aws_surveyor.all_regions())

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_init_invalid_entity_type(self):
        '''Test initialization of AWSSurveyor instances.'''

        # - - - - - - - - - - - - - - - - - - - -
        # Test initialiation with an invalid entity type.
        # - - - - - - - - - - - - - - - - - - - -

        # - - - - - - - - - - - - - - - - - - - -
        # First from arguments.

        with self.assertRaises(ValueError):
            aws_surveyor.AWSSurveyor(
                config_path='',
                entity_types=['x']
                )

        # - - - - - - - - - - - - - - - - - - - -
        # Then from file.

        invalid_entity_type_presets = {
            "profiles": ["some_profile", "another_profile"],
            "regions": ["us-east-1", "us-west-1", "us-west-2"],
            "entity_types": ["ec2", "security_group", "subnet", "x"],
            }

        invalid_configuration_path = os.path.join(
            self.tmpdir, 'invalid.awssurveyor.cfg'
            )
        with open(invalid_configuration_path, 'w') as fptr:
            json.dump(invalid_entity_type_presets, fptr)

        with self.assertRaises(ValueError):
            aws_surveyor.AWSSurveyor(
                config_path=invalid_configuration_path
                )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSSurveyorPresets(unittest.TestCase):
    '''Test cases for AWSSurveyor presets manipulation.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def setUpClass(cls):
        '''Test class level common fixture.'''

        # TODO: We should do one test to confirm that alternate paths
        # for default filename set in AWSSurveyor is used properly,
        # then always set a safe default filename to avoid clobbering.

        # This will be cleaned up in tearDownClass().
        cls.tmpdir = tempfile.mkdtemp()

        cls.all_presets_sample = {
            "profiles": ["some_profile", "another_profile"],
            "regions": ["us-east-1", "us-west-1", "us-west-2"],
            "entity_types": ["ec2", "security_group", "subnet", "vpc"],
            }

        cls.profiles_presets_sample = {
            "profiles": ["this_profile", "that_profile"],
            }

        # # Paths into $HOME/.aws and to the default config file.
        # cls.home = os.path.expanduser('~')
        # cls.aws_dir = os.path.join(cls.home, '.aws')

        # # The default configuration file name for AWSSurveyor instances.
        # cls.default_config_filename = (
        #     aws_surveyor.AWSSurveyor.default_config_filename()
        #     )
        # cls.default_config_path = os.path.join(
        #     cls.aws_dir,
        #     cls.default_config_filename
        #     )

        # # We will use an alternate default config setting in some cases.
        # cls.alt_default_config_filename = '.'.join(
        #     [cls.default_config_filename, str(time.time())]
        #     )
        # cls.alt_default_config_dir = cls.tmpdir

        # # Path to alternate config file in our working temporary directory.
        # cls.tmpdir_config_path = os.path.join(
        #     cls.tmpdir,
        #     cls.default_config_filename
        #     )

        # # Add any alternate config files created to this list to
        # # ensure cleanup.
        # cls.paths_to_clean = set([])

        # Record whether there was a default config file present, so we
        # can check against this in tearDown before removing a temporary
        # version created for testing. We'll just exit with an error if
        # there was a default config file already, rather than risk
        # mucking with it.
        cls.default_config_was_present = os.path.exists(
            ORIGINAL_DEFAULT_CONFIG_PATH
            )

        # Turn off mediator connection, as we use a lot of fake profiles
        # and regions in this test class.
        # pylint: disable=protected-access
        cls.original_hold_sessions = aws_surveyor.AWSSurveyor._hold_sessions
        aws_surveyor.AWSSurveyor._hold_sessions = True

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def tearDownClass(cls):
        '''Remove test files and temp directory, restore changed defaults.'''

        # Remove temp directory.
        for root, dirs, files in os.walk(cls.tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(cls.tmpdir)

        # Restore any changed default config filename or directory we set.
        aws_surveyor.AWSSurveyor.default_config_filename(
            ORIGINAL_DEFAULT_CONFIG_FILENAME
            )
        aws_surveyor.AWSSurveyor.default_config_dir(
            ORIGINAL_DEFAULT_CONFIG_DIR
            )

        # Remove any default config file we created.
        if (
                not cls.default_config_was_present and
                os.path.exists(
                    ORIGINAL_DEFAULT_CONFIG_PATH
                    )
                ):  # pylint: disable=bad-continuation
            os.remove(ORIGINAL_DEFAULT_CONFIG_PATH)

        # # Remove any alternate config files we created.
        # for clean_path in cls.paths_to_clean:
        #     if os.path.exists(clean_path):
        #         os.remove(clean_path)

        # We changed this to True in setUpClass.
        # pylint: disable=protected-access
        aws_surveyor.AWSSurveyor._hold_sessions = cls.original_hold_sessions

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case level common fixture.'''

        # # Restore any changed default config filename or directory we set.
        # aws_surveyor.AWSSurveyor.default_config_filename(
        #     ORIGINAL_DEFAULT_CONFIG_FILENAME
        #     )
        # aws_surveyor.AWSSurveyor.default_config_dir(
        #     ORIGINAL_DEFAULT_CONFIG_DIR
        #     )

        # Remove any default config file we previously created.
        if (
                not self.default_config_was_present and
                os.path.exists(
                    ORIGINAL_DEFAULT_CONFIG_PATH
                    )
                ):  # pylint: disable=bad-continuation
            os.remove(ORIGINAL_DEFAULT_CONFIG_PATH)

        # # Remove any alternate config files we created in previous tests.
        # for clean_path in self.paths_to_clean:
        #     if os.path.exists(clean_path):
        #         os.remove(clean_path)
        # self.paths_to_clean = set([])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_presets(self):
        '''Test AWSSurveyor presets() method and individual assignments.'''

        # - - - - - - - - - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(config_path='')

        surveyor.profiles = ['a']
        surveyor.regions = ['b', 'c']
        surveyor.entity_types = ['vpc', 'vpc']

        self.assertEqual(surveyor.profiles, ['a'])
        self.assertItemsEqual(surveyor.regions, ['b', 'c'])
        self.assertItemsEqual(surveyor.entity_types, ['vpc'])
        self.assertEqual(len(surveyor.regions), 2)

        # - - - - - - - - - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(config_path='')

        self.assertEqual(
            surveyor.presets,
            {
                'profiles': [],
                'regions': [],
                'entity_types': []
                }
            )

        surveyor.add_profiles(['a'])
        surveyor.add_regions(['b', 'c'])

        self.assertEqual(surveyor.presets['profiles'], ['a'])
        self.assertItemsEqual(surveyor.presets['regions'], ['b', 'c'])
        self.assertEqual(surveyor.presets['entity_types'], [])

        # - - - - - - - - - - - - - - - - - - - -
        # Presets assign to the appropriate preset attribute.
        surveyor.presets = {
            'profiles': [],
            'regions': ['x'],
            'entity_types': ['elb', 'eip']
            }

        self.assertEqual(surveyor.presets['profiles'], [])
        self.assertItemsEqual(surveyor.presets['regions'], ['x'])
        self.assertEqual(surveyor.presets['entity_types'], ['elb', 'eip'])

        # - - - - - - - - - - - - - - - - - - - -
        # Assigning a dict with only some presets sets others to empty lists.
        surveyor.presets = {
            'entity_types': ['elb', 'eip']
            }

        self.assertEqual(surveyor.presets['profiles'], [])
        self.assertItemsEqual(surveyor.presets['regions'], [])
        self.assertEqual(surveyor.presets['entity_types'], ['elb', 'eip'])

        # - - - - - - - - - - - - - - - - - - - -
        # Assigning a dict with only some presets sets others to empty lists.
        surveyor.presets = {
            'profiles': ['y', 'z']
            }

        self.assertEqual(surveyor.presets['profiles'], ['y', 'z'])
        self.assertItemsEqual(surveyor.presets['regions'], [])
        self.assertEqual(surveyor.presets['entity_types'], [])

        # - - - - - - - - - - - - - - - - - - - -
        # Assigning an empty dict sets all presets to empty lists.
        surveyor.presets = {}

        self.assertEqual(
            surveyor.presets,
            {
                'profiles': [],
                'regions': [],
                'entity_types': []
                }
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_add_presets(self):
        '''Test AWSSurveyor add_* presets methods.'''

        # - - - - - - - - - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(config_path='')

        self.assertEqual(surveyor.profiles, [])
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

        # - - - - - - - - - - - - - - - - - - - -
        # Adding empty lists doesn't change empty lists.
        surveyor.add_profiles([])
        surveyor.add_regions([])
        surveyor.add_entity_types([])

        self.assertEqual(surveyor.profiles, [])
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

        # - - - - - - - - - - - - - - - - - - - -
        # Adding values updates the presets.
        # Adding a value twice has no further effect.
        surveyor.add_profiles(['a'])
        surveyor.add_regions(['b', 'c'])
        surveyor.add_entity_types(['vpc', 'vpc'])

        self.assertEqual(surveyor.profiles, ['a'])
        self.assertItemsEqual(surveyor.regions, ['b', 'c'])
        self.assertItemsEqual(surveyor.entity_types, ['vpc'])
        self.assertEqual(len(surveyor.regions), 2)

        # - - - - - - - - - - - - - - - - - - - -
        # Adding an existing value has no effect.
        surveyor.add_profiles(['a'])
        surveyor.add_regions(['b', 'c'])
        surveyor.add_entity_types(['vpc', 'elb'])

        self.assertEqual(surveyor.profiles, ['a'])
        self.assertItemsEqual(surveyor.regions, ['b', 'c'])
        self.assertItemsEqual(surveyor.entity_types, ['vpc', 'elb'])
        self.assertEqual(len(surveyor.regions), 2)
        self.assertEqual(len(surveyor.entity_types), 2)

        # - - - - - - - - - - - - - - - - - - - -
        # Adding empty lists doesn't change nonempty lists.
        surveyor.add_profiles([])
        surveyor.add_regions([])
        surveyor.add_entity_types([])

        self.assertEqual(surveyor.profiles, ['a'])
        self.assertItemsEqual(surveyor.regions, ['b', 'c'])
        self.assertItemsEqual(surveyor.entity_types, ['vpc', 'elb'])
        self.assertEqual(len(surveyor.regions), 2)
        self.assertEqual(len(surveyor.entity_types), 2)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_remove_presets(self):
        '''Test AWSSurveyor remove_* presets methods.'''

        # - - - - - - - - - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(config_path='')

        self.assertEqual(surveyor.profiles, [])
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

        # - - - - - - - - - - - - - - - - - - - -
        # Removing empty presets doesn't change empty presets.
        surveyor.remove_profiles([])
        surveyor.remove_regions([])
        surveyor.remove_entity_types([])

        self.assertEqual(surveyor.profiles, [])
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

        surveyor.add_profiles(['a'])
        surveyor.add_regions(['b', 'c'])
        surveyor.add_entity_types(['vpc', 'vpc'])

        # - - - - - - - - - - - - - - - - - - - -
        # Removing empty presets doesn't change nonempty presets.
        surveyor.remove_profiles([])
        surveyor.remove_regions([])
        surveyor.remove_entity_types([])

        self.assertEqual(surveyor.profiles, ['a'])
        self.assertItemsEqual(surveyor.regions, ['b', 'c'])
        self.assertEqual(surveyor.entity_types, ['vpc'])

        # - - - - - - - - - - - - - - - - - - - -
        # Removing existing presets empties them.
        surveyor.remove_profiles(['a'])
        surveyor.remove_regions(['b', 'c'])
        surveyor.remove_entity_types(['vpc'])

        self.assertEqual(surveyor.profiles, [])
        self.assertEqual(surveyor.regions, [])
        self.assertEqual(surveyor.entity_types, [])

        surveyor.add_profiles(['a'])
        surveyor.add_regions(['b', 'c'])
        surveyor.add_entity_types(['vpc', 'vpc'])

        # - - - - - - - - - - - - - - - - - - - -
        # Removing non-existent profiles has no effect.
        surveyor.remove_profiles(['x'])
        surveyor.remove_regions(['b', 'y'])
        surveyor.remove_entity_types(['vpc', 'vpc'])

        self.assertEqual(surveyor.profiles, ['a'])
        self.assertEqual(surveyor.regions, ['c'])
        self.assertEqual(surveyor.entity_types, [])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_add_invalid_entity_type(self):
        '''Test AWSSurveyor add_entity_type with an invalid entity type.'''

        surveyor = aws_surveyor.AWSSurveyor(config_path='')
        with self.assertRaises(ValueError):
            surveyor.add_entity_types(['vpc', 'x', 'elb'])


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSSurveyorAccounts(unittest.TestCase):
    '''Test cases for AWSSurveyor AWS account records.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @unittest.skipIf(
        len(AVAILABLE_PROFILES) < 2,
        'requires at least two of {}, found {}'.format(
            POSSIBLE_PROFILES,
            AVAILABLE_PROFILES
            )
        )
    def test_aws_surveyor_accounts(self):
        '''Test AWSSurveyor.mediators().'''

        # - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(
            config_path='', profiles=AVAILABLE_PROFILES[:1]
            )

        self.assertEqual(len(surveyor.accounts), 1)

        self.assertItemsEqual(
            surveyor.accounts[0].keys(),
            ['account_id', 'account_name', 'account_desc', 'region_name']
            )
        # This should be at least 12 digits, so this is pretty mild.
        self.assertTrue(len(surveyor.accounts[0]['account_id']) > 1)

        # - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(
            config_path='', profiles=AVAILABLE_PROFILES[:2]
            )

        self.assertEqual(len(surveyor.accounts), 2)

        self.assertItemsEqual(
            surveyor.accounts[1].keys(),
            ['account_id', 'account_name', 'account_desc', 'region_name']
            )
        # This should be at least 12 digits, so this is pretty mild.
        self.assertTrue(len(surveyor.accounts[1]['account_id']) > 1)

        # - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(config_path='')

        # This will pass if there's a default profile.
        self.assertEqual(len(surveyor.accounts), 1)

        self.assertItemsEqual(
            surveyor.accounts[0].keys(),
            ['account_id', 'account_name', 'account_desc', 'region_name']
            )
        # This should be at least 12 digits, so this is pretty mild.
        self.assertTrue(len(surveyor.accounts[0]['account_id']) > 1)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSSurveyorMediators(unittest.TestCase):
    '''Test cases for AWSSurveyor AWSMediators manipulation.'''

    # Some of the test case function names get pretty long.
    # pylint: disable=invalid-name

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def setUp(self):
        '''Test case level common fixture.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_mediators(self):
        '''Test AWSSurveyor.mediators().'''

        # - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(config_path='')

        # This will pass if there's a default profile.
        self.assertEqual(len(surveyor.mediators()), 1)

        # - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(
            config_path='',
            profiles=[TEST_PROFILE_NAME]
            )

        # This will pass if there's a default profile.
        self.assertEqual(len(surveyor.mediators()), 1)

        # - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(
            config_path='',
            regions=['us-east-1', 'us-west-1']
            )

        # This will pass if there's a default profile.
        self.assertEqual(len(surveyor.mediators()), 2)

        # - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(
            config_path='',
            profiles=[TEST_PROFILE_NAME],
            regions=['us-east-1', 'us-west-1']
            )

        self.assertEqual(
            len(surveyor.mediators()),
            len(surveyor.profiles) * len(surveyor.regions)
            )
        surveyor = aws_surveyor.AWSSurveyor(
            config_path='',
            profiles=[TEST_PROFILE_NAME],
            regions=['us-east-1', 'us-west-1']
            )

        self.assertEqual(
            len(surveyor.mediators()),
            len(surveyor.profiles) * len(surveyor.regions)
            )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_mediator_filters(self):
        '''Test AWSSurveyor mediator filter assignment and removal.'''

        # - - - - - - - - - - - -
        # No errors if mediators() is empty.
        # - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(config_path='')

        # This will pass if there's a default profile.
        self.assertEqual(len(surveyor.mediators()), 1)

        surveyor.add_filters('eip', {'public-ip': ['123.45.67.89']})

        # This will pass if there's a default profile.
        self.assertEqual(len(surveyor.mediators()), 1)

        # - - - - - - - - - - - -
        # Filters are assigned to existing mediators.
        # - - - - - - - - - - - -
        surveyor = aws_surveyor.AWSSurveyor(
            config_path='',
            profiles=[TEST_PROFILE_NAME],
            regions=['us-east-1', 'us-west-1']
            )

        self.assertEqual(
            len(surveyor.mediators()),
            len(surveyor.profiles) * len(surveyor.regions)
            )

        surveyor.add_filters('eip', {'public-ip': ['123.45.67.89']})
        self.assertEqual(
            surveyor.mediators()[0].filters.keys(),
            ['eip']
            )

        surveyor.add_filters('ec2', {'instance-state-name': ['running']})
        self.assertEqual(
            surveyor.mediators()[-1].filters.keys(),
            ['eip', 'ec2']
            )

        surveyor.remove_all_filters('ec2')
        self.assertEqual(
            surveyor.mediators()[0].filters.keys(),
            ['eip']
            )

        surveyor.add_filters('ec2', {'instance-state-name': ['running']})
        surveyor.remove_all_filters()
        self.assertEqual(
            surveyor.mediators()[0].filters.keys(),
            []
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class TestAWSSurveyorSupplementalSetters(unittest.TestCase):
    '''Test cases for AWSSurveyor methods for supplementing AWSInformers.'''

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def test_aws_surveyor_set_ec2_elb_supplementals(self):
        '''Test AWSSurveyor.set_ec2_elb_supplementals().'''

        surveyor = aws_surveyor.AWSSurveyor(
            profiles=[TEST_PROFILE_NAME],
            regions=['us-east-1']
            )

        [m.flush() for m in surveyor.mediators()]

        informer_cache = aws_informer.AWSMediator.informer_cache
        self.assertEqual(informer_cache, {})

        surveyor.survey('ec2', 'elb')
        self.assertNotEqual(informer_cache, {})

        surveyor.set_ec2_elb_supplementals()

        # - - - - - - - - - - - - - - - -
        # Chack that all EC2Informer instances now have load balancer
        # information fields in their supplementals.
        # - - - - - - - - - - - - - - - -
        self.assertEqual(
            [
                i for i in surveyor.informers('ec2')
                if 'load_balancer_names' not in i.supplementals
                ],
            []
            )

        self.assertEqual(
            [
                i for i in surveyor.informers('ec2')
                if 'load_balancer_genuses' not in i.supplementals
                ],
            []
            )

        # - - - - - - - - - - - - - - - -
        # Check that EC2Informer instances load balancer information
        # appears to be correctly populated. We can't be sure some
        # instances weren't being terminated while we're running, and
        # were caught while still appearing in ELB instance lists but
        # no longer appear in EC2 instance records.
        # - - - - - - - - - - - - - - - -
        for elb_informer in surveyor.informers('elb'):

            load_balancer_name = elb_informer.resource['LoadBalancerName']
            load_balancer_genus = (
                elb_informer.supplementals['site-specific']['genus']
                )
            instance_ids = [
                x['InstanceId'] for x in elb_informer.resource['Instances']
                ]

            for instance_id in instance_ids:
                ec2_informer = informer_cache.get(instance_id)

                # ELBs can reference EC2 instances that no longer exist.
                if not ec2_informer:
                    continue
                self.assertIn(
                    load_balancer_name,
                    ec2_informer.supplementals['load_balancer_names']
                    )
                self.assertIn(
                    load_balancer_genus,
                    ec2_informer.supplementals['load_balancer_genuses']
                    )

        # - - - - - - - - - - - - - - - -
        # This is a sanity check to make sure not too many EC2
        # instances appear to have been "in-termination" as
        # mentioned in the comment above.
        # - - - - - - - - - - - - - - - -
        num_elbs_with_instances = len([
            x for x in surveyor.informers('elb')
            if len(x.resource['Instances']) > 0
            ])
        # This is a little seat-of-the-pants, but if it's generally
        # true that instances are only assigned to one ELB, and lots
        # of ELBs have more than one instance, this should hold.
        self.assertTrue(
            len([
                x for x in surveyor.informers('ec2')
                if len(x.supplementals['load_balancer_names']) > 0
                ]) >= num_elbs_with_instances
            )


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    unittest.main()
