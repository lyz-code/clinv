from setuptools import setup, find_packages

version = '0.7.0'

setup(
    name='Clinv',
    version=version,
    description='DevSecOps command line asset inventory',
    author='Lyz',
    author_email='lyz@riseup.net',
    packages=find_packages(),
    license='GPLv3',
    long_description=open('README.md').read(),
    entry_points={
      'console_scripts': ['clinv = clinv:main']
    }
)
