from . import ClinvReportBaseTestClass
from clinv.reports import ClinvReport
import unittest


class TestClinvReport(ClinvReportBaseTestClass, unittest.TestCase):
    """
    Test the ClinvReport implementation.
    """

    def setUp(self):
        super().setUp()
        self.report = ClinvReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    def test_short_print_resources(self):
        self.report.short_print_resources(
            [
                self.inventory.inv["projects"]["pro_01"],
                self.inventory.inv["services"]["ser_01"],
            ]
        )

        self.assertTrue(self.inventory.inv["projects"]["pro_01"].short_print.called)
        self.assertTrue(self.inventory.inv["services"]["ser_01"].short_print.called)

    def test_get_resource_names(self):
        name = self.report._get_resource_names("informations", ["inf_01"])
        self.assertEqual(name, self.inventory.inv["informations"]["inf_01"].name)
