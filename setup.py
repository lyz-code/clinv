"""Python package building configuration."""

import logging
import os
import re
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup
from setuptools.command.install import install

log = logging.getLogger(__name__)


# ignore: Install has class Any, and can't be subclassed. It's how I used it in the
#   past and don't have time to fix it right now.
class PostInstallCommand(install):  # type: ignore
    """Post-installation for installation mode."""

    def run(self) -> None:
        """Create data directory after installation."""
        install.run(self)
        try:
            data_directory = os.path.expanduser("~/.local/share/clinv")
            os.makedirs(data_directory)
            log.info("Data directory created")
        except FileExistsError:
            log.info("Data directory already exits")


# Avoid loading the package to extract the version
with open("src/clinv/version.py") as fp:
    version_match = re.search(r'__version__ = "(?P<version>.*)"', fp.read())
    if version_match is None:
        raise ValueError("The version is not specified in the version.py file.")
    version = version_match["version"]


with open("README.md", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="clinv",
    version=version,
    description="DevSecOps command line asset inventory",
    author="Lyz",
    author_email="lyz-code-security-advisories@riseup.net",
    license="GNU General Public License v3",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/lyz-code/clinv",
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={"clinv": ["py.typed"]},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
        "Natural Language :: English",
    ],
    entry_points="""
        [console_scripts]
        clinv=clinv.entrypoints.cli:cli
    """,
    install_requires=[
        "boto3",
        "pydantic",
        "ruyaml",
        "requests",
        "repository_orm",
        "rich",
        "tabulate",
        "Click",
    ],
)
