from setuptools import setup

version = '0.1.0'

setup(
    name='Clinv',
    version=version,
    description='DevSecOps command line asset inventory',
    author='Lyz',
    author_email='lyz@riseup.net',
    packages=['clinv', ],
    license='GPLv3',
    long_description=open('README.md').read(),
    entry_points={
      'console_scripts': ['clinv = clinv:main']
    }
)
