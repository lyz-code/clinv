import logging
import os

from setuptools import find_packages, setup
from setuptools.command.install import install

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


exec(compile(open("clinv/version.py").read(), "clinv/version.py", "exec"))

setup(
    name="clinv",
    version=__version__,  # noqa: F821
    description="DevSecOps command line asset inventory",
    author="Lyz",
    author_email="lyz@riseup.net",
    license="GNU General Public License v3",
    long_description=open("README.md").read(),
    url="https://github.com/lyz-code/clinv",
    long_description_content_type="text/markdown",
    packages=find_packages("clinv"),
    package_dir={"": "clinv"},
    entry_points={"console_scripts": ["clinv = clinv:main"]},
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
    install_requires=[
        "argcomplete",
        "boto3",
        "pyexcel",
        "PyYAML",
        "requests",
        "tabulate",
    ],
)
