"""
Module to store the Print report.

Classes:
    PrintReport: Class to gather methods to print information of Clinv
        resources.
"""

from clinv.reports import ClinvReport
import re


class PrintReport(ClinvReport):
    """
    Class to gather methods to print information of Clinv
    resources.

    Parameters:
        inventory (Inventory): Clinv inventory object.

    Public methods:
        output: Print the report to stdout.

    Public attributes:
        inv (Inventory): Clinv inventory.
    """

    def __init__(self, inventory):
        super().__init__(inventory)

    def output(self, regexp_id):
        """
        Method to print the information of a Clinv resource.

        Parameters:
            resource_id (str): regular expression of a resource id.

        Returns:
            stdout: Resource information
        """

        for resource_type in self.inv:
            for resource_id, resource in self.inv[resource_type].items():
                if re.match(regexp_id, resource_id):
                    resource.print()
