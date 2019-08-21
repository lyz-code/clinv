"""
Module to store the Clinv sources abstract class.

Classes:
    ClinvSourcesrc: Class to gather the common methods for the Clinv sources.
"""

import logging


class ClinvSourcesrc():
    """
    Class to gather the common methods for the Clinv sources.

    Public attributes:
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        self.source_data = source_data
        self.user_data = user_data
        self.log = logging.getLogger('main')
