from . import ClinvReportBaseTestClass
from clinv.reports.unused import UnusedReport
from unittest.mock import patch

import unittest


class TestUnusedReport(ClinvReportBaseTestClass, unittest.TestCase):
    """
    Test the UnusedReport implementation.
    """

    def setUp(self):
        super().setUp()
        self.report = UnusedReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    @patch("clinv.reports.unused.UnusedReport.short_print_resources")
    def test_unused_security_groups_doesnt_prints_used_by_ec2(self, printMock):
        self.ec2instance.security_groups.keys.return_value = ["sg-xxxxxxxx"]
        self.rdsinstance.security_groups = []
        self.security_group.id = "sg-xxxxxxxx"
        self.security_group.name = "resource_name"
        self.security_group.is_related.return_value = False

        self.report._unused_security_groups()

        self.assertEqual(
            printMock.assert_called_with([]), None,
        )

    @patch("clinv.reports.unused.UnusedReport.short_print_resources")
    def test_unused_security_groups_doesnt_print_default_security_groups(
        self, printMock
    ):
        # Default security groups can't be deleted so there is no reason to
        # list them.

        self.ec2instance.security_groups.keys.return_value = []
        self.rdsinstance.security_groups = []
        self.security_group.id = "sg-xxxxxxxx"
        self.security_group.name = "default"
        self.security_group.is_related.return_value = False

        self.report._unused_security_groups()

        self.assertEqual(
            printMock.assert_called_with([]), None,
        )

    @patch("clinv.reports.unused.UnusedReport.short_print_resources")
    def test_unused_security_groups_doesnt_prints_used_by_rds(self, printMock):
        self.ec2instance.security_groups.keys.return_value = []
        self.rdsinstance.security_groups = ["sg-xxxxxxxx"]
        self.security_group.id = "sg-xxxxxxxx"
        self.security_group.name = "resource_name"
        self.security_group.is_related.return_value = False

        self.report._unused_security_groups()

        self.assertEqual(
            printMock.assert_called_with([]), None,
        )

    @patch("clinv.reports.unused.UnusedReport.short_print_resources")
    def test_unused_security_groups_doesnt_prints_used_by_security_groups(
        self, printMock
    ):
        self.ec2instance.security_groups.keys.return_value = []
        self.rdsinstance.security_groups = []
        self.security_group.id = "sg-xxxxxxxx"
        self.security_group.name = "resource_name"

        # Here we simulate that it references itself.
        self.security_group.is_related.return_value = True

        self.report._unused_security_groups()

        self.assertEqual(
            printMock.assert_called_with([]), None,
        )

    @patch("clinv.reports.unused.UnusedReport._unused_security_groups")
    def test_output_method(self, security_groupsMock):
        self.report.output()
        self.assertTrue(security_groupsMock.called)
