"""
Module to store the ActiveReport.

Classes:
  ActiveReport: Class to gather methods to print the list of active Clinv
    resources.

"""

from clinv.reports import ClinvReport


class ActiveReport(ClinvReport):
    """
    Class to gather methods to print the list of active Clinv resources.

    Parameters:
        inventory (Inventory): Clinv inventory object.

    Public methods:
        output: Print the report to stdout.

    Public attributes:
        inv (Inventory): Clinv inventory.
    """

    def __init__(self, inventory):
        super().__init__(inventory)

    def output(self, desired_resource_type=None):
        """
        Do aggregation of data to print a list of the selected resource entries
        in the inventory.

        Parameters:
            resource_type (str): Type of Clinv resource to be processed.
                It must be one of [
                    'ec2',
                    'rds',
                    'route53',
                    'services',
                    'security_groups',
                    'informations',
                    'projects',
                ]. If not specified it will print all resources.

        Returns:
            stdout: Prints the list of active items of that resource in the
                inventory.
        """

        resources_to_print = []

        for resource_type in sorted(self.inv.keys()):
            if resource_type == desired_resource_type or desired_resource_type is None:
                for resource_id, resource in sorted(self.inv[resource_type].items()):
                    if resource.state == "active":
                        resources_to_print.append(resource)

        self.short_print_resources(resources_to_print)
