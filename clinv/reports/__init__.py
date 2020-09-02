"""
Module to store the Clinv report abstract class.

Classes:
    ClinvReport: Class to gather the common methods for the Clinv reports.
"""

import logging


class ClinvReport:
    """
    Class to gather the common methods for the Clinv reports.

    Parameters:
        inventory (Inventory): Clinv inventory object.

    Public methods:
        short_print_resources: Executes the short_print method for a list
            of clinv resources.

    Private methods:
        _get_resource_names: Return list of resource names.

    Public attributes:
        inv (Inventory): Clinv inventory.
        log (logging object):
    """

    def __init__(self, inventory):
        self.inv = inventory.inv
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

    def short_print_resources(self, resource_list):
        """
        Executes the short_print method for a list of Clinv resources.

        Parameters:
            resource_list (list): List of ClinvGenericResource derived classes.

        Returns:
            stdout: Short print of the selected resources.
        """
        for resource in resource_list:
            resource.short_print()

    def _get_resource_names(self, resource_type, resource_ids):
        """
        Do aggregation of data to return a list with the names of the
        selected resources.

        Parameters:
            resource_type (str): Type of resource, one of [
                'services',
                'informations',
                ].
            resource_ids (list): List of resource ids.

        Return:
            str: With the resource names separated by commas.
        """

        resource_names = []

        for resource_id in resource_ids:
            try:
                resource_names.append(self.inv[resource_type][resource_id].name)
            except KeyError:
                pass

        if len(resource_names) == 0:
            return None
        elif len(resource_names) == 1:
            return resource_names[0]
        else:
            return ", ".join(resource_names)
