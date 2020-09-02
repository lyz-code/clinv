from . import ClinvReportBaseTestClass
from clinv.reports.export import ExportReport
from collections import OrderedDict
from unittest.mock import patch
import unittest


class TestExportReport(ClinvReportBaseTestClass, unittest.TestCase):
    """
    Test the ExportReport implementation.
    """

    def setUp(self):
        super().setUp()
        self.report = ExportReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    def test_export_ec2_generates_expected_dictionary(self):
        exported_data = [
            [
                "ID",
                "Name",
                "Services",
                "To destroy",
                "Responsible",
                "Region",
                "Comments",
            ],
            [
                "i-023desldk394995ss",
                "resource_name",
                "Service 1",
                False,
                "Person 1",
                "us-east-1",
                "Test instance",
            ],
        ]

        self.ec2instance.name = "resource_name"
        self.ec2instance.id = "i-023desldk394995ss"
        self.ec2instance._get_field.return_value = False
        self.ec2instance.description = "Test instance"
        self.ec2instance.region = "us-east-1"

        self.service.name = "Service 1"
        self.service.responsible = "Person 1"
        self.service.raw = {"aws": {"ec2": ["i-023desldk394995ss"]}}

        self.assertEqual(
            self.report._export_ec2(), exported_data,
        )

    def test_export_rds_generates_expected_dictionary(self):
        exported_data = [
            [
                "ID",
                "Name",
                "Services",
                "To destroy",
                "Responsible",
                "Region",
                "Comments",
            ],
            [
                "db-YDFL2",
                "resource_name",
                "Service 1",
                False,
                "Person 1",
                "us-east-1",
                "Test instance",
            ],
        ]

        self.rdsinstance.id = "db-YDFL2"
        self.rdsinstance.name = "resource_name"
        self.rdsinstance._get_field.return_value = False
        self.rdsinstance.description = "Test instance"
        self.rdsinstance.region = "us-east-1"

        self.service.name = "Service 1"
        self.service.responsible = "Person 1"
        self.service.raw = {"aws": {"rds": ["db-YDFL2"]}}

        self.assertEqual(
            self.report._export_rds(), exported_data,
        )

    def test_export_projects_generates_expected_dictionary(self):
        exported_data = [
            ["ID", "Name", "Services", "Informations", "State", "Description",],
            [
                "pro_01",
                "Project 1",
                "Service 1",
                "Information 1",
                "active",
                "Project 1 description",
            ],
        ]

        self.project.id = "pro_01"
        self.project.name = "Project 1"
        self.project.services = ["ser_01"]
        self.project.informations = ["inf_01"]
        self.project.state = "active"
        self.project.description = "Project 1 description"

        self.service.name = "Service 1"
        self.information.name = "Information 1"

        self.assertEqual(
            self.report._export_projects(), exported_data,
        )

    def test_export_services_generates_expected_dictionary(self):
        exported_data = [
            ["ID", "Name", "Access", "State", "Informations", "Description",],
            [
                "ser_01",
                "Service 1",
                "internal",
                "active",
                "Information 1",
                "Service 1 description",
            ],
        ]

        self.service.id = "ser_01"
        self.service.name = "Service 1"
        self.service.access = "internal"
        self.service.informations = ["inf_01"]
        self.service.state = "active"
        self.service.description = "Service 1 description"

        self.information.name = "Information 1"

        self.assertEqual(
            self.report._export_services(), exported_data,
        )

    def test_export_route53_generates_expected_dictionary(self):
        exported_data = [
            [
                "ID",
                "Name",
                "Type",
                "Value",
                "Services",
                "To destroy",
                "Access",
                "Description",
            ],
            [
                "hosted_zone_id-record1.clinv.org-cname",
                "record1.clinv.org",
                "CNAME",
                "127.0.0.1, localhost",
                "Service 01",
                "tbd",
                "public",
                "record description",
            ],
        ]

        self.route53instance.id = "hosted_zone_id-record1.clinv.org-cname"
        self.route53instance.name = "record1.clinv.org"
        self.route53instance.type = "CNAME"
        self.route53instance.value = ["127.0.0.1", "localhost"]
        self.route53instance._get_field.return_value = "tbd"
        self.route53instance.access = "public"
        self.route53instance.description = "record description"
        self.service.raw = {
            "aws": {"route53": ["hosted_zone_id-record1.clinv.org-cname",],}
        }
        self.service.name = "Service 01"

        self.assertEqual(
            self.report._export_route53(), exported_data,
        )

    def test_export_informations_generates_expected_dictionary(self):
        exported_data = [
            ["ID", "Name", "State", "Responsible", "Personal Data", "Description",],
            [
                "inf_01",
                "Information 1",
                "active",
                "Person 1",
                True,
                "Information 1 description",
            ],
        ]

        self.information.id = "inf_01"
        self.information.name = "Information 1"
        self.information.state = "active"
        self.information.responsible = "Person 1"
        self.information.personal_data = True
        self.information.description = "Information 1 description"

        self.assertEqual(
            self.report._export_informations(), exported_data,
        )

    def test_export_s3_generates_expected_dictionary(self):
        exported_data = [
            [
                "ID",
                "To destroy",
                "Environment",
                "Read Permissions (desired/real)",
                "Write Permissions (desired/real)",
                "Description",
            ],
            [
                "s3_bucket_name",
                "tbd",
                "pro",
                "tbd/public",
                "tbd/private",
                "This is the description",
            ],
        ]

        self.s3instance.id = "s3_bucket_name"
        self.s3instance._get_field.return_value = "pro"
        self.s3instance.to_destroy = "tbd"
        self.s3instance.raw = {
            "permissions": {"READ": "public", "WRITE": "private",},
            "desired_permissions": {"read": "tbd", "write": "tbd",},
        }
        self.s3instance.description = "This is the description"

        self.assertEqual(
            self.report._export_s3(), exported_data,
        )

    def test_export_people_generates_expected_dictionary(self):
        exported_data = [
            ["ID", "Name", "State", "Description",],
            ["peo_01", "User 1", "active", "User 1 description",],
        ]

        self.person.id = "peo_01"
        self.person.name = "User 1"
        self.person.state = "active"
        self.person.description = "User 1 description"

        self.assertEqual(
            self.report._export_people(), exported_data,
        )

    @patch("clinv.reports.export.ExportReport._export_s3")
    @patch("clinv.reports.export.ExportReport._export_route53")
    @patch("clinv.reports.export.ExportReport._export_rds")
    @patch("clinv.reports.export.ExportReport._export_ec2")
    @patch("clinv.reports.export.ExportReport._export_informations")
    @patch("clinv.reports.export.ExportReport._export_services")
    @patch("clinv.reports.export.ExportReport._export_people")
    @patch("clinv.reports.export.ExportReport._export_projects")
    @patch("clinv.reports.export.pyexcel")
    def test_export_generates_expected_book(
        self,
        pyexcelMock,
        projectsMock,
        peopleMock,
        servicesMock,
        informationsMock,
        ec2Mock,
        rdsMock,
        route53Mock,
        s3Mock,
    ):
        expected_book = OrderedDict()
        expected_book.update({"Projects": projectsMock.return_value})
        expected_book.update({"Services": servicesMock.return_value})
        expected_book.update({"Informations": informationsMock.return_value})
        expected_book.update({"EC2": ec2Mock.return_value})
        expected_book.update({"RDS": rdsMock.return_value})
        expected_book.update({"Route53": route53Mock.return_value})
        expected_book.update({"S3": s3Mock.return_value})
        expected_book.update({"People": peopleMock.return_value})

        self.report.output("file.ods")
        self.assertEqual(
            pyexcelMock.save_book_as.assert_called_with(
                bookdict=expected_book, dest_file_name="file.ods",
            ),
            None,
        )
