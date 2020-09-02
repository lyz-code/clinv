"""
Module to store the SearchReport.

Classes:
  SearchReport: Class to gather methods to search Clinv resources into the
  inventory.

"""

from clinv.reports import ClinvReport


class SearchReport(ClinvReport):
    """
    Class to gather methods to search Clinv resources into the inventory.

    Parameters:
        inventory (Inventory): Clinv inventory object.

    Public methods:
        output: Print the report to stdout.

    Public attributes:
        inv (Inventory): Clinv inventory.
    """

    def __init__(self, inventory):
        super().__init__(inventory)

    def output(self, search_string):
        """
        Method to print the report to stdout.

        Parameters:
            resource_id (str): regular expression of a resource id.

        Returns:
            stdout: Resource information
        """

        for resource_type in self.inv.keys():
            result = []
            for resource_id, resource in self.inv[resource_type].items():
                if resource.search(search_string) is True:
                    result.append(resource)

            if result != []:
                print("\nType: {}".format(resource_type))
                self.short_print_resources(result)
