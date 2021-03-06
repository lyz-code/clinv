from . import ClinvReportBaseTestClass
from clinv.reports.list import ListReport
import unittest


class TestListReport(ClinvReportBaseTestClass, unittest.TestCase):
    """
    Test the ListReport implementation.
    """

    def setUp(self):
        super().setUp()
        self.report = ListReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    def test_output_method_if_no_arguments_are_given_all_is_printed(self):
        self.report.output()
        self.assertTrue(
            self.inventory.inv["ec2"]["i-023desldk394995ss"].short_print.called
        )
        self.assertTrue(self.inventory.inv["projects"]["pro_01"].short_print.called)

    def test_output_method(self):
        self.report.output("ec2")
        self.assertTrue(
            self.inventory.inv["ec2"]["i-023desldk394995ss"].short_print.called
        )
        self.assertFalse(self.inventory.inv["projects"]["pro_01"].short_print.called)
