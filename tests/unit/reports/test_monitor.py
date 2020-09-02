import unittest
from unittest.mock import MagicMock, patch

from clinv.reports.monitor import MonitorReport

from . import ClinvReportBaseTestClass


class TestMonitorReport(ClinvReportBaseTestClass, unittest.TestCase):
    """
    Test the MonitorReport implementation.
    """

    def setUp(self):
        super().setUp()
        self.report = MonitorReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    def test_get_monitor_detects_monitor_resources(self):
        self.ec2instance.monitor = True
        self.rdsinstance.monitor = True
        self.route53instance.monitor = True
        desired_result = {
            "monitor": {
                "ec2": [self.ec2instance],
                "rds": [self.rdsinstance],
                "route53": [self.route53instance],
            },
        }

        self.report._get_monitor_status()
        self.assertEqual(
            self.report.monitor_status["monitor"]["ec2"],
            desired_result["monitor"]["ec2"],
        )
        self.assertEqual(
            self.report.monitor_status["monitor"]["rds"],
            desired_result["monitor"]["rds"],
        )
        self.assertEqual(
            self.report.monitor_status["monitor"]["route53"],
            desired_result["monitor"]["route53"],
        )

    def test_get_monitor_detects_unmonitor_resources(self):
        self.ec2instance.monitor = False
        self.rdsinstance.monitor = False
        self.route53instance.monitor = False
        desired_result = {
            "unmonitor": {
                "ec2": [self.ec2instance],
                "rds": [self.rdsinstance],
                "route53": [self.route53instance],
            },
        }

        self.report._get_monitor_status()
        self.assertEqual(
            self.report.monitor_status["unmonitor"]["ec2"],
            desired_result["unmonitor"]["ec2"],
        )
        self.assertEqual(
            self.report.monitor_status["unmonitor"]["rds"],
            desired_result["unmonitor"]["rds"],
        )
        self.assertEqual(
            self.report.monitor_status["unmonitor"]["route53"],
            desired_result["unmonitor"]["route53"],
        )

    def test_get_monitor_detects_unknown_resources(self):
        self.ec2instance.monitor = "tbd"
        self.rdsinstance.monitor = "other"
        self.route53instance.monitor = ""
        desired_result = {
            "unknown": {
                "ec2": [self.ec2instance],
                "rds": [self.rdsinstance],
                "route53": [self.route53instance],
            },
        }

        self.report._get_monitor_status()
        self.assertEqual(
            self.report.monitor_status["unknown"]["ec2"],
            desired_result["unknown"]["ec2"],
        )
        self.assertEqual(
            self.report.monitor_status["unknown"]["rds"],
            desired_result["unknown"]["rds"],
        )
        self.assertEqual(
            self.report.monitor_status["unknown"]["route53"],
            desired_result["unknown"]["route53"],
        )

    def test_get_monitor_doesnt_fail_if_no_monitor_key(self):
        # Used a MagicMock to simulate the AttributeError when calling
        # self.monitor
        self.report.inv["ec2"]["i-023desldk394995ss"] = MagicMock(spec=[])
        self.report.inv["ec2"]["i-023desldk394995ss"].state = "active"
        self.report._get_monitor_status()

    def test_get_monitor_doesnt_print_terminated_resources(self):
        self.ec2instance.monitor = True
        self.ec2instance.state = "terminated"

        self.report._get_monitor_status()
        self.assertEqual(self.report.monitor_status["unknown"]["ec2"], [])

    @patch("clinv.reports.monitor.MonitorReport._get_monitor_status")
    def test_output_method_prints_monitor_resources(self, statusMock):
        # Monitor_status prefilled by the _get_monitor_status method.
        self.report.monitor_status = {
            "monitor": {
                "ec2": [self.ec2instance],
                "rds": [self.rdsinstance],
                "route53": [self.route53instance],
            },
        }

        self.report.output("true")

        self.assertTrue(statusMock.called)
        self.assertTrue(self.ec2instance.short_print.called)
        self.assertTrue(self.route53instance.short_print.called)
        self.assertTrue(self.rdsinstance.short_print.called)

    @patch("clinv.reports.monitor.MonitorReport._get_monitor_status")
    def test_output_method_prints_unmonitor_resources(self, statusMock):
        # Monitor_status prefilled by the _get_monitor_status method.
        self.report.monitor_status = {
            "unmonitor": {
                "ec2": [self.ec2instance],
                "rds": [self.rdsinstance],
                "route53": [self.route53instance],
            },
        }

        self.report.output("false")

        self.assertTrue(statusMock.called)
        self.assertTrue(self.ec2instance.short_print.called)
        self.assertTrue(self.route53instance.short_print.called)
        self.assertTrue(self.rdsinstance.short_print.called)

    @patch("clinv.reports.monitor.MonitorReport._get_monitor_status")
    def test_output_method_prints_unknown_monitor_resources(self, statusMock):
        # Monitor_status prefilled by the _get_monitor_status method.
        self.report.monitor_status = {
            "unknown": {
                "ec2": [self.ec2instance],
                "rds": [self.rdsinstance],
                "route53": [self.route53instance],
            },
        }

        self.report.output("unknown")

        self.assertTrue(statusMock.called)
        self.assertTrue(self.ec2instance.short_print.called)
        self.assertTrue(self.route53instance.short_print.called)
        self.assertTrue(self.rdsinstance.short_print.called)
