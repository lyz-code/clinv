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
        _unassigned_s3: Do aggregation of data to print the S3 resources
            that are not associated to any service.
        _unassigned_services: Do aggregation of data to print the services
            resources that are not associated to any project.
        _unassigned_informations: Do aggregation of data to print the
            informations resources that are not associated to any project.
        _unassigned_security_groups: Do aggregation of data to print the
            security_groups resources that are not associated to any instance.

    Public attributes:
        inv (Inventory): Clinv inventory.
    """

    def __init__(self, inventory):
        super().__init__(inventory)

    def _unassigned_aws_resource(self, resource_type, exclude_ids=[]):
        """
        Do aggregation of data to print the resource_type resources that are
        not associated to any service.

        Parameters:
            resource_type (str): Type of clinv resource to be processed.
                It must be one of [
                    'ec2',
                    'rds',
                    's3',
                    'iam_groups',
                    'vpc',
                ]
            exclude_ids (list): List of IDs to exclude from the report

        Returns:
            stdout: Prints the list of unassigned items.
        """

        all_assigned_instances = []
        for service_id, service in sorted(self.inv["services"].items()):
            try:
                for instance in service.raw["aws"][resource_type]:
                    all_assigned_instances.append(instance)
            except TypeError:
                pass
            except KeyError:
                pass

        for instance_id, instance in sorted(self.inv[resource_type].items()):
            if instance_id in exclude_ids:
                continue
            if instance_id not in all_assigned_instances:
                if instance.state != "terminated":
                    instance.short_print()

    def _unassigned_asg(self):
        """
        Do aggregation of data to print the ASG resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_aws_resource("asg")

    def _unassigned_ec2(self):
        """
        Do aggregation of data to print the EC2 resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """
        for asg_id, asg in self.inv["asg"].items():
            for instance_id in asg.instances:
                instance_id

        asg_instances = [
            instance_id
            for asg_id, asg in self.inv["asg"].items()
            for instance_id in asg.instances
        ]
        self._unassigned_aws_resource("ec2", asg_instances)

    def _unassigned_rds(self):
        """
        Do aggregation of data to print the RDS resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_aws_resource("rds")

    def _unassigned_route53(self):
        """
        Do aggregation of data to print the Route53 resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        resource_type = "route53"
        all_assigned_instances = []
        for service_id, service in sorted(self.inv["services"].items()):
            try:
                for instance in service.raw["aws"][resource_type]:
                    all_assigned_instances.append(instance)
            except TypeError:
                pass
            except KeyError:
                pass

        for instance_id, instance in sorted(self.inv[resource_type].items()):
            if instance_id not in all_assigned_instances:
                if instance.type != "SOA" and instance.type != "NS":
                    instance.print()

    def _unassigned_s3(self):
        """
        Do aggregation of data to print the S3 resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_aws_resource("s3")

    def _unassigned_risk_management_resource(self, resource_type):
        """
        Do aggregation of data to print the services resources that are not
        associated to any project.

        Parameters:
            resource_type (str): Type of clinv resource to be processed.
                It must be one of [
                    'services',
                    'informations',
                    'people',
                ]
        Returns:
            stdout: Prints the list of unassigned items.
        """

        all_assigned_resources = []
        for project_id, project in sorted(self.inv["projects"].items()):
            resource_method = getattr(project, resource_type)
            if resource_method is None:
                continue
            else:
                for resource_id in resource_method:
                    all_assigned_resources.append(resource_id)

        unassigned_resources = []
        for resource_id, resource in sorted(self.inv[resource_type].items()):
            if (
                resource_id not in all_assigned_resources
                and resource.state != "terminated"
            ):
                unassigned_resources.append(resource)
        self.short_print_resources(unassigned_resources)

    def _unassigned_services(self):
        """
        Do aggregation of data to print the services resources that are not
        associated to any project.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_risk_management_resource("services")

    def _unassigned_informations(self):
        """
        Do aggregation of data to print the informations resources that are not
        associated to any project.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_risk_management_resource("informations")

    def _unassigned_people(self):
        """
        Do aggregation of data to print the people resources that are not
        associated to any project.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_risk_management_resource("people")

    def _unassigned_iam_users(self):
        """
        Do aggregation of data to print the iam user resources that are not
        associated to any person.

        Returns:
            stdout: Prints the list of unassigned items.
        """
        all_assigned_resources = []
        for person_id, person in sorted(self.inv["people"].items()):
            if person.iam_user is None:
                continue
            else:
                all_assigned_resources.append(person.iam_user)

        unassigned_resources = []
        for resource_id, resource in sorted(self.inv["iam_users"].items()):
            if resource_id not in all_assigned_resources:
                unassigned_resources.append(resource)
        self.short_print_resources(unassigned_resources)

    def _unassigned_iam_groups(self):
        """
        Do aggregation of data to print the iam group resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_aws_resource("iam_groups")

    def _unassigned_security_groups(self):
        """
        Do aggregation of data to print the security_group resources that are
        not being imported to the inventory.

        This method tests if the `state` property is different than active or
        terminated. That's the default value of the property, so it means that
        the resource has not been verified by a human.

        I've thought of adding a `security_groups` key under the `aws` one of
        the services, but I feel it would add a lot of work when adding new
        services without giving too much value.

        The policy enforcement of the security groups should be done through
        the `is_synchronized` methods.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        unassigned_resources = []

        for security_group_id, security_group in self.inv["security_groups"].items():
            if security_group.state not in ["active", "terminated"]:
                unassigned_resources.append(security_group)

        self.short_print_resources(unassigned_resources)

    def _unassigned_vpc(self):
        """
        Do aggregation of data to print the vpc resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_aws_resource("vpc")

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
                    'iam_users',
                    'informations',
                    'people',
                    'projects',
                    'security_groups',
                ], if it's set to 'all' it will test all kind of resources

        Returns:
            stdout: Unassigned Resource ids.
        """

        if resource_type == "all":
            self.log.info("Unassigned ASG")
            self._unassigned_asg()
            self.log.info("Unassigned EC2")
            self._unassigned_ec2()
            self.log.info("Unassigned RDS")
            self._unassigned_rds()
            self.log.info("Unassigned Route53")
            self._unassigned_route53()
            self.log.info("Unassigned S3")
            self._unassigned_s3()
            self.log.info("Unassigned Services")
            self._unassigned_services()
            self.log.info("Unassigned People")
            self._unassigned_people()
            self.log.info("Unassigned IAM Users")
            self._unassigned_iam_users()
            self.log.info("Unassigned IAM Groups")
            self._unassigned_iam_groups()
            self.log.info("Unassigned Informations")
            self._unassigned_informations()
            self.log.info("Unassigned Security Groups")
            self._unassigned_security_groups()
            self.log.info("Unassigned VPC")
            self._unassigned_vpc()
        else:
            self.__getattribute__("_unassigned_{}".format(resource_type))()
