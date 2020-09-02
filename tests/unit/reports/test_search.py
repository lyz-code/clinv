from . import ClinvReportBaseTestClass
from clinv.reports.search import SearchReport
from unittest.mock import patch, call
import unittest


class TestSearchReport(ClinvReportBaseTestClass, unittest.TestCase):
    """
    Test the SearchReport implementation.
    """

    def setUp(self):
        super().setUp()
        self.report = SearchReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    @patch("clinv.reports.search.print")
    def test_output_method_returns_an_inventory_resource_if_match(
        self, printMock,
    ):
        self.ec2instance.search.return_value = True

        self.report.output("ec2")

        self.assertEqual(printMock.mock_calls, [call("\nType: ec2")])
        self.assertTrue(self.ec2instance.short_print.called)
