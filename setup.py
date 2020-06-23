from setuptools import setup, find_packages
from setuptools.command.install import install

import logging
import os

log = logging.getLogger(__name__)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        try:
            data_directory = os.path.expanduser("~/.local/share/clinv")
            os.makedirs(data_directory)
            log.info("Data directory created")
        except FileExistsError:
            log.info("Data directory already exits")


exec(compile(open('clinv/version.py').read(), 'clinv/version.py', 'exec'))

setup(
    name='Clinv',
    version=__version__, # noqa: F821
    description='DevSecOps command line asset inventory',
    author='Lyz',
    author_email='lyz@riseup.net',
    license='GPLv3',
    long_description=open('README.md').read(),
    packages=find_packages(exclude=('tests',)),
    entry_points={
      'console_scripts': ['clinv = clinv:main']
    },
    install_requires=[
        "argcomplete>=1.11.1",
        "boto3>=1.14.8",
        "pyexcel>=0.6.2",
        "PyYAML>=5.3.1",
        "requests>=2.24.0",
        "tabulate>=0.8.7",
    ]
)
