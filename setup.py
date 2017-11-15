
'''Boogio package setup.'''

# pylint: disable=invalid-name

import os

from setuptools import find_packages
from setuptools import setup


# Construct a list of all scripts to be installed.
script_files = os.listdir(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'bin'
        )
    )

script_package_paths = [os.path.join('bin', s) for s in script_files]

setup(
    name="boogio",
    version="1.1.5",
    description="AWS records retrieval tools",
    author="Scott Brown",
    author_email='scott.brown@one.verizon.com',
    url="https://github.oncue.verizon.net/oss/boogio",
    packages=find_packages(exclude=['test_*']),
    package_data={
        '': [
            'elastic_stools/schema/*',
            'sheetspecs/*',
            ]
        },
    # scripts reside in bin dirs.
    scripts=script_package_paths,
    install_requires=[
        "boto3",
        "botocore",
        "jsonschema",
        "PyYAML",
        "xlsxwriter",
        ]
    )
