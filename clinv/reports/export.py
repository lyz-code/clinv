"""
Module to store the ExportReport.

Classes:
  ExportReport: Class to gather methods to export the Clinv resources to ods.

"""

from clinv.reports import ClinvReport
from collections import OrderedDict
from operator import itemgetter
import os
import pyexcel


class ExportReport(ClinvReport):
    """
    Class to gather methods to export the Clinv resources to ods.

    Parameters:
        inventory (Inventory): Clinv inventory object.

    Public methods:
        output: Export the Clinv inventory to ods.

    Private methods:
        _export_aws_resource: Do aggregation of data to return a list with the
            information needed to fill up a spreadsheet for an AWS type of
            resource.
        _export_ec2: Do aggregation of data to return a list with the
            information needed to fill up a spreadsheet for the EC2 resources.
        _export_s3: Do aggregation of data to return a list with the
            information needed to fill up a spreadsheet for the S3 resources.
        _export_rds: Do aggregation of data to return a list with the
            information needed to fill up a spreadsheet for the RDS resources.
        _export_route53: Do aggregation of data to return a list with the
            information needed to fill up a spreadsheet for the Route53
            resources.
        _export_people: Do aggregation of data to return a list with the
            information needed to fill up a spreadsheet for the people
            resources.
        _export_projects: Do aggregation of data to return a list with the
            information needed to fill up a spreadsheet for the project
            resources.
        _export_services: Do aggregation of data to return a list with the
            information needed to fill up a spreadsheet for the service
            resources.
        _export_informations: Do aggregation of data to return a list with the
            information needed to fill up a spreadsheet for the information
            resources.

    Public attributes:
        inv (Inventory): Clinv inventory.
    """

    def __init__(self, inventory):
        super().__init__(inventory)

    def _export_aws_resource(self, resource_type):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for an AWS type of resource.

        Parameters:
            resource_type (str): Type of AWS resource to be processed.
                It must be one of ['ec2', 'rds']

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            "ID",
            "Name",
            "Services",
            "To destroy",
            "Responsible",
            "Region",
            "Comments",
        ]

        # Fill up content
        exported_data = []
        for instance_id, instance in self.inv[resource_type].items():
            related_services = {}
            for service_id, service in self.inv["services"].items():
                try:
                    service.raw["aws"][resource_type]
                except TypeError:
                    continue
                except KeyError:
                    continue
                for service_resource_id in service.raw["aws"][resource_type]:
                    if service_resource_id == instance_id:
                        related_services[service_id] = service

            exported_data.append(
                [
                    instance_id,
                    instance.name,
                    self._get_resource_names("services", related_services),
                    instance._get_field("to_destroy"),
                    ", ".join(
                        set(
                            [
                                service.responsible
                                for service_id, service in related_services.items()
                            ]
                        )
                    ),
                    instance.region,
                    instance.description,
                ]
            )

        # Sort by name
        exported_data = sorted(exported_data, key=itemgetter(1))
        exported_data.insert(0, exported_headers)

        return exported_data

    def _export_ec2(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the EC2 resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        return self._export_aws_resource("ec2")

    def _export_rds(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the RDS resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        return self._export_aws_resource("rds")

    def _export_s3(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the S3 resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            "ID",
            "To destroy",
            "Environment",
            "Read Permissions (desired/real)",
            "Write Permissions (desired/real)",
            "Description",
        ]

        # Fill up content
        exported_data = []
        for instance_id, instance in self.inv["s3"].items():
            related_services = {}
            for service_id, service in self.inv["services"].items():
                try:
                    service.raw["aws"]["s3"]
                except TypeError:
                    continue
                except KeyError:
                    continue
                for service_resource_id in service.raw["aws"]["s3"]:
                    if service_resource_id == instance_id:
                        related_services[service_id] = service

            exported_data.append(
                [
                    instance_id,
                    instance.to_destroy,
                    instance._get_field("environment"),
                    "{}/{}".format(
                        instance.raw["desired_permissions"]["read"],
                        instance.raw["permissions"]["READ"],
                    ),
                    "{}/{}".format(
                        instance.raw["desired_permissions"]["write"],
                        instance.raw["permissions"]["WRITE"],
                    ),
                    instance.description,
                ]
            )

        # Sort by name
        exported_data = sorted(exported_data, key=itemgetter(1))
        exported_data.insert(0, exported_headers)

        return exported_data

    def _export_route53(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the Route53 resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            "ID",
            "Name",
            "Type",
            "Value",
            "Services",
            "To destroy",
            "Access",
            "Description",
        ]

        # Fill up content
        resource_type = "route53"

        exported_data = []
        for instance_id, instance in self.inv[resource_type].items():
            related_services = {}
            for service_id, service in self.inv["services"].items():
                try:
                    service.raw["aws"][resource_type]
                except TypeError:
                    continue
                except KeyError:
                    continue
                for service_resource_id in service.raw["aws"][resource_type]:
                    if service_resource_id == instance_id:
                        related_services[service_id] = service

            exported_data.append(
                [
                    instance.id,
                    instance.name,
                    instance.type,
                    ", ".join(instance.value),
                    self._get_resource_names("services", related_services),
                    instance._get_field("to_destroy"),
                    instance.access,
                    instance.description,
                ]
            )

        # Sort by name
        exported_data = sorted(exported_data, key=itemgetter(1))
        exported_data.insert(0, exported_headers)

        return exported_data

    def _export_projects(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the Project resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            "ID",
            "Name",
            "Services",
            "Informations",
            "State",
            "Description",
        ]

        # Fill up content
        exported_data = []
        for resource_id, resource in self.inv["projects"].items():
            exported_data.append(
                [
                    resource_id,
                    resource.name,
                    self._get_resource_names("services", resource.services),
                    self._get_resource_names("informations", resource.informations),
                    resource.state,
                    resource.description,
                ]
            )

        # Sort by id
        exported_data = sorted(exported_data, key=itemgetter(0))
        exported_data.insert(0, exported_headers)

        return exported_data

    def _export_services(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the Service resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            "ID",
            "Name",
            "Access",
            "State",
            "Informations",
            "Description",
        ]

        # Fill up content
        exported_data = []
        for resource_id, resource in self.inv["services"].items():
            exported_data.append(
                [
                    resource_id,
                    resource.name,
                    resource.access,
                    resource.state,
                    self._get_resource_names("informations", resource.informations),
                    resource.description,
                ]
            )

        # Sort by id
        exported_data = sorted(exported_data, key=itemgetter(0))
        exported_data.insert(0, exported_headers)

        return exported_data

    def _export_informations(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the Information resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            "ID",
            "Name",
            "State",
            "Responsible",
            "Personal Data",
            "Description",
        ]

        # Fill up content
        exported_data = []
        for resource_id, resource in self.inv["informations"].items():
            exported_data.append(
                [
                    resource_id,
                    resource.name,
                    resource.state,
                    resource.responsible,
                    resource.personal_data,
                    resource.description,
                ]
            )

        # Sort by id
        exported_data = sorted(exported_data, key=itemgetter(0))
        exported_data.insert(0, exported_headers)

        return exported_data

    def _export_people(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the People resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            "ID",
            "Name",
            "State",
            "Description",
        ]

        # Fill up content
        exported_data = []
        for resource_id, resource in self.inv["people"].items():
            exported_data.append(
                [resource_id, resource.name, resource.state, resource.description,]
            )

        # Sort by id
        exported_data = sorted(exported_data, key=itemgetter(0))
        exported_data.insert(0, exported_headers)

        return exported_data

    def output(self, export_path):
        """
        Method to export the Clinv inventory to ods.

        It generates the information needed to fill up a spreadsheet for a
        selected resource.

        Parameters:
            export_path (str): Path to export the inventory.
                (Default: ~/.local/share/clinv/inventory.ods)

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        book = OrderedDict()
        book.update({"Projects": self._export_projects()})
        book.update({"Services": self._export_services()})
        book.update({"Informations": self._export_informations()})
        book.update({"EC2": self._export_ec2()})
        book.update({"RDS": self._export_rds()})
        book.update({"Route53": self._export_route53()})
        book.update({"S3": self._export_s3()})
        book.update({"People": self._export_people()})

        pyexcel.save_book_as(
            bookdict=book, dest_file_name=os.path.expanduser(export_path),
        )
