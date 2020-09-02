"""
Module to store the UnusedReport.

Classes:
  UnusedReport: Report to print the resources that are not being used.

"""

from clinv.reports import ClinvReport


class UnusedReport(ClinvReport):
    """
    Report to print the resources that are not being used.

    Parameters:
        inventory (Inventory): Clinv inventory object.

    Public methods:
        output: Print the report to stdout.

    Private methods:
        _unused_security_groups: Print the security groups that are not being
            used by any resource.

    Public attributes:
        inv (Inventory): Clinv inventory.
    """

    def __init__(self, inventory):
        super().__init__(inventory)

    def _unused_security_groups(self):
        """
        Do aggregation of data to print the security groups that are not being
        used by any resource.

        Returns:
            stdout: Prints the list of unused items.
        """

        used_resources = []
        unused_resources = []

        # Security groups used by EC2 instances.
        for ec2_id, ec2 in self.inv["ec2"].items():
            [
                used_resources.append(security_group)
                for security_group in ec2.security_groups.keys()
            ]

        # Security groups used by RDS instances.
        for rds_id, rds in self.inv["rds"].items():
            [
                used_resources.append(security_group)
                for security_group in rds.security_groups
            ]

        # Security groups used by other security groups.
        def is_security_group_related(security_group_id_to_test):
            if security_group_id_to_test in used_resources:
                return True
            for security_group_id, security_group in self.inv[
                "security_groups"
            ].items():
                if security_group.is_related(security_group_id_to_test):
                    used_resources.append(security_group_id_to_test)
                    return True

            return False

        for security_group_id_to_test, security_group_to_test in self.inv[
            "security_groups"
        ].items():
            # Don't add the VPC/Region default security groups as they can't
            # be removed.
            if security_group_to_test.name == "default":
                continue

            if not is_security_group_related(security_group_id_to_test):
                unused_resources.append(security_group_to_test)

        self.short_print_resources(unused_resources)

    def output(self):
        """
        Method to print the report to stdout.

        Parameters:
            resource_id (str): regular expression of a resource id.

        Returns:
            stdout: Resource information
        """
        self.log.info("Unused Security Groups")
        self._unused_security_groups()
