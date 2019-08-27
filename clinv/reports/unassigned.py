"""
Module to store the UnassignedReport.

Classes:
  UnassignedReport: Class to gather methods to print the list of unassigned
    Clinv resources.

"""

from clinv.reports import ClinvReport


class UnassignedReport(ClinvReport):
    """
    Class to gather methods to print the list of unassigned Clinv resources.

    Parameters:
        inventory (Inventory): Clinv inventory object.

    Public methods:
        output: Print the report to stdout.

    Private methods:
        _unassigned_aws_resource: Do aggregation of data to print the
            AWS resources that are not associated to any service.
        _unassigned_ec2: Do aggregation of data to print the EC2 resources
            that are not associated to any service.
        _unassigned_rds: Do aggregation of data to print the RDS resources
            that are not associated to any service.
        _unassigned_route53: Do aggregation of data to print the Route53
            resources that are not associated to any service.
        _unassigned_services: Do aggregation of data to print the services
            resources that are not associated to any project.
        _unassigned_informations: Do aggregation of data to print the
            informations resources that are not associated to any project.

    Public attributes:
        inv (Inventory): Clinv inventory.
    """

    def __init__(self, inventory):
        super().__init__(inventory)

    def _unassigned_aws_resource(self, resource_type):
        """
        Do aggregation of data to print the resource_type resources that are
        not associated to any service.

        Parameters:
            resource_type (str): Type of clinv resource to be processed.
                It must be one of [
                    'ec2',
                    'rds',
                ]

        Returns:
            stdout: Prints the list of unassigned items.
        """

        all_assigned_instances = []
        for service_id, service in sorted(self.inv['services'].items()):
            try:
                for instance in service.raw['aws'][resource_type]:
                    all_assigned_instances.append(instance)
            except TypeError:
                pass
            except KeyError:
                pass

        for instance_id, instance in sorted(self.inv[resource_type].items()):
            if instance_id not in all_assigned_instances:
                if instance.state != 'terminated':
                    instance.print()

    def _unassigned_ec2(self):
        """
        Do aggregation of data to print the EC2 resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_aws_resource('ec2')

    def _unassigned_rds(self):
        """
        Do aggregation of data to print the RDS resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_aws_resource('rds')

    def _unassigned_route53(self):
        """
        Do aggregation of data to print the Route53 resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        resource_type = 'route53'
        all_assigned_instances = []
        for service_id, service in sorted(self.inv['services'].items()):
            try:
                for instance in service.raw['aws'][resource_type]:
                    all_assigned_instances.append(instance)
            except TypeError:
                pass
            except KeyError:
                pass

        for instance_id, instance in sorted(self.inv[resource_type].items()):
            if instance_id not in all_assigned_instances:
                if instance.type != 'SOA' and instance.type != 'NS':
                    instance.print()

    def _unassigned_services(self):
        """
        Do aggregation of data to print the services resources that are not
        associated to any project.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        all_assigned_services = []
        for project_id, project in sorted(self.inv['projects'].items()):
            if project.services is None:
                continue
            else:
                for service in project.services:
                    all_assigned_services.append(service)

        unassigned_services = []
        for service_id, service in sorted(self.inv['services'].items()):
            if service_id not in all_assigned_services:
                unassigned_services.append(service)
        self.short_print_resources(unassigned_services)

    def _unassigned_informations(self):
        """
        Do aggregation of data to print the informations resources that are not
        associated to any project.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        all_assigned_informations = []
        for project_id, project in self.inv['projects'].items():
            if project.informations is None:
                continue
            else:
                for information in project.informations:
                    all_assigned_informations.append(information)

        unassigned_informations = []
        for information_id, information in \
                sorted(self.inv['informations'].items()):
            if information_id not in all_assigned_informations:
                unassigned_informations.append(information)
        self.short_print_resources(unassigned_informations)

    def output(self, resource_type):
        """
        Method to print the list of unassigned Clinv resources

        Parameters:
            resource_type (str): Type of clinv resource to be processed.
                It must be one of [
                    'all',
                    'ec2',
                    'rds',
                    'route53',
                    'services',
                    'informations',
                    'projects',
                ], if it's set to 'all' it will test all kind of resources

        Returns:
            stdout: Unassigned Resource ids.
        """

        if resource_type == 'all':
            self.log.info('Unassigned EC2')
            self._unassigned_ec2()
            self.log.info('Unassigned RDS')
            self._unassigned_rds()
            self.log.info('Unassigned Route53')
            self._unassigned_route53()
            self.log.info('Unassigned Services')
            self._unassigned_services()
            self.log.info('Unassigned Informations')
            self._unassigned_informations()
        elif resource_type == 'ec2':
            self._unassigned_ec2()
        elif resource_type == 'rds':
            self._unassigned_rds()
        elif resource_type == 'route53':
            self._unassigned_route53()
        elif resource_type == 'services':
            self._unassigned_services()
        elif resource_type == 'informations':
            self._unassigned_informations()
