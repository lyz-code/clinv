from . import ClinvReportBaseTestClass
from clinv.reports.print import PrintReport
import unittest


class TestPrintReport(ClinvReportBaseTestClass, unittest.TestCase):
    """
    Test the PrintReport implementation.
    """

    def setUp(self):
        super().setUp()
        self.report = PrintReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    def test_output_method(self):
        self.report.output("i-023.*")
        self.assertTrue(self.inventory.inv["ec2"]["i-023desldk394995ss"].print.called)
