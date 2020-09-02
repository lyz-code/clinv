from . import ClinvReportBaseTestClass
from clinv.reports.active import ActiveReport
import unittest


class TestActiveReport(ClinvReportBaseTestClass, unittest.TestCase):
    """
    Test the ActiveReport implementation.
    """

    def setUp(self):
        super().setUp()
        self.report = ActiveReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    def test_output_method_if_no_arguments_are_given_all_is_printed(self):
        self.inventory.inv["ec2"]["i-023desldk394995ss"].state = "active"
        self.inventory.inv["projects"]["pro_01"].state = "active"

        self.report.output()
        self.assertTrue(
            self.inventory.inv["ec2"]["i-023desldk394995ss"].short_print.called
        )
        self.assertTrue(self.inventory.inv["projects"]["pro_01"].short_print.called)

    def test_output_method(self):
        self.inventory.inv["ec2"]["i-023desldk394995ss"].state = "active"

        self.report.output("ec2")

        self.assertTrue(
            self.inventory.inv["ec2"]["i-023desldk394995ss"].short_print.called
        )
        self.assertFalse(self.inventory.inv["projects"]["pro_01"].short_print.called)

    def test_output_method_doesnt_print_terminated_items(self):
        self.inventory.inv["ec2"]["i-023desldk394995ss"].state = "terminated"

        self.report.output("ec2")

        self.assertFalse(
            self.inventory.inv["ec2"]["i-023desldk394995ss"].short_print.called
        )
