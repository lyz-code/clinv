"""
Module to store the MonitoredReport.

Classes:
  MonitoredReport: {{ class_description }}

"""

from clinv.reports import ClinvReport


class MonitoredReport(ClinvReport):
    """
    Report to print the monitoring status of the inventory resources.

    Parameters:
        inventory (Inventory): Clinv inventory object.

    Public methods:
        output: Print the report to stdout.

    Internal methods:
        _monitored_status: Classify resources based on their monitor status.

    Public attributes:
        inv (Inventory): Clinv inventory.
        monitor_status (dict): Dictionary with the resources classified by
            their monitorization status.
    """

    def __init__(self, inventory):
        super().__init__(inventory)
        self.monitor_status = {
            "monitored": {},
            "unmonitored": {},
            "unknown": {},
        }

    def _get_monitor_status(self):
        """
        Do aggregation of data to classify resources based on their monitor
        status populating the self.monitor_status attribute with the following
        structure:
            {
                'monitored': {
                    'ec2': [
                        EC2()
                    ],
                    ...
                }
                'unmonitored': {
                    'ec2': [
                        EC2()
                    ],
                    ...
                }
                'unknown': {
                    'ec2': [
                        EC2()
                    ],
                    ...
                }
            }

        Returns:
            None
        """

        for resource_type in ["ec2", "route53", "rds"]:
            self.monitor_status["monitored"][resource_type] = []
            self.monitor_status["unmonitored"][resource_type] = []
            self.monitor_status["unknown"][resource_type] = []

            for resource_id, resource in sorted(self.inv[resource_type].items()):
                if resource.state == "terminated":
                    continue
                try:
                    monitor_status = resource.monitored
                except AttributeError:
                    monitor_status = "unknown"

                if monitor_status is True:
                    self.monitor_status["monitored"][resource_type].append(resource)
                elif monitor_status is False:
                    self.monitor_status["unmonitored"][resource_type].append(resource)
                else:
                    self.monitor_status["unknown"][resource_type].append(resource)

    def output(self, monitor_status):
        """
        Method to print the report to stdout.

        Parameters:
            monitor_status (str): Status to print, one of 'true', 'false' or
                'unknown'.

        Returns:
            stdout: Resource information
        """
        if monitor_status == "true":
            status_message = "Monitored {} resources"
            monitor_status = "monitored"
        elif monitor_status == "false":
            status_message = "Unmonitored {} resources"
            monitor_status = "unmonitored"
        else:
            status_message = "Unknown monitor status of {} resources"
            monitor_status = "unknown"

        self._get_monitor_status()
        for resource_type in self.monitor_status[monitor_status]:
            self.log.info(status_message.format(resource_type))
            for resource in self.monitor_status[monitor_status][resource_type]:
                resource.short_print()
