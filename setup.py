""" Setup script for the dxlclient package """

# pylint: disable=no-member, no-name-in-module, import-error, wrong-import-order
# pylint: disable=missing-docstring, no-self-use

from __future__ import absolute_import
import glob
import os
from setuptools import Command, setup
import setuptools.command.sdist
import distutils.command.sdist
import distutils.log
import subprocess
import sys


# Patch setuptools' sdist behaviour with distutils' sdist behaviour
setuptools.command.sdist.sdist.run = distutils.command.sdist.sdist.run

# The name pip records for the distribution. The import package is always ``dxlclient``;
# only this changes. The default keeps the upstream name, which is what makes an install of
# this fork satisfy the plain ``dxlclient`` dependency the downstream OpenDXL projects declare
# (and thereby keeps them off the ``msgpack<1.0.0`` pin of the published package). The upstream
# name on PyPI belongs to the upstream project, so a release of our own is built under a name
# of our own: ``DXLCLIENT_DIST_NAME=opendxlclient python -m build``.
DIST_NAME = os.environ.get("DXLCLIENT_DIST_NAME", "dxlclient")

PRODUCT_PROPS = {}
CWD = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(CWD, "dxlclient", "_product_props.py")) as f:
    exec(f.read(), PRODUCT_PROPS) # pylint: disable=exec-used

class LintCommand(Command):
    """
    Custom setuptools command for running lint
    """
    description = 'run lint against project source files'
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        self.announce("Running pylint for library source files and tests",
                      level=distutils.log.INFO)
        subprocess.check_call(["pylint", "dxlclient"] + glob.glob("*.py"))
        self.announce("Running pylint for examples", level=distutils.log.INFO)
        subprocess.check_call(["pylint"] + glob.glob("examples/*.py") +
                              glob.glob("examples/**/*.py") +
                              ["--rcfile", ".pylintrc.examples"])

class CiCommand(Command):
    """
    Custom setuptools command for running steps that are performed during
    Continuous Integration testing.
    """
    description = 'run CI steps (lint, test, etc.)'
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        self.run_command("lint")
        self.announce("Running tests", level=distutils.log.INFO)
        subprocess.check_call([sys.executable, "-m", "pytest",
                               "dxlclient/test"])

TEST_REQUIREMENTS = [
    'futures; python_version == "3.7"',
    "mock",
    # nose is unmaintained and does not work on Python >= 3.10; pynose is a
    # maintained drop-in fork providing the same ``nose`` package.
    'nose; python_version < "3.10"',
    'pynose; python_version >= "3.10"',
    "parameterized",
    "pytest",
    'astroid<2.3.0; python_version == "3.7"',
    'astroid==2.3.3; python_version > "3.7" and python_version < "3.10"',
    'pylint<=2.3.1; python_version < "3.10"',
    'pylint; python_version >= "3.10"',
    "requests-mock"
]

DEV_REQUIREMENTS = TEST_REQUIREMENTS + ["sphinx"]

setup(
    # Application name:
    name=DIST_NAME,

    # Version number:
    version=PRODUCT_PROPS["__version__"],

    # Application author details:
    author="McAfee, Inc.",

    # License
    license="Apache License 2.0",

    keywords=['opendxl', 'dxl', 'mcafee', 'client'],

    # Custom Paho MQTT Python client with proxy support added as a git submodule
    package_dir={
        'pahoproxy': 'paho_mqtt_dxl/src/paho/mqtt'
    },

    # Packages
    packages=[
        "dxlclient",
        "dxlclient._cli",
        "pahoproxy"
    ],

    # Include additional files into the package
    include_package_data=True,

    install_requires=[
        # cryptography replaces the unmaintained oscrypto/asn1crypto pair the
        # CLI used for key and certificate request generation
        "cryptography>=3.1",
        "configobj",
        "msgpack>=0.5",
        "requests",
        "PySocks"
    ],

    tests_require=TEST_REQUIREMENTS,

    extras_require={
        "dev": DEV_REQUIREMENTS,
        "test": TEST_REQUIREMENTS
    },

    # Details
    url="http://www.mcafee.com/",

    description="McAfee Data Exchange Layer Client",

    long_description=open('README').read(),

    python_requires='>=3.7',

    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],

    cmdclass={
        'ci': CiCommand,
        'lint': LintCommand
    },

    entry_points={
        'console_scripts': [
            'dxlclient = dxlclient._cli:cli_run'
        ],
    }
)
