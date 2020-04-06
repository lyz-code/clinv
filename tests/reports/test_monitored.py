from tests.reports import ClinvReportBaseTestClass
from clinv.reports.monitored import MonitoredReport
import unittest
from unittest.mock import patch, MagicMock


class TestMonitoredReport(ClinvReportBaseTestClass, unittest.TestCase):
    '''
    Test the MonitoredReport implementation.
    '''

    def setUp(self):
        super().setUp()
        self.report = MonitoredReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    def test_get_monitored_detects_monitored_resources(self):
        self.ec2instance.monitored = True
        self.rdsinstance.monitored = True
        self.route53instance.monitored = True
        desired_result = {
            'monitored': {
                'ec2': [
                    self.ec2instance,
                ],
                'rds': [
                    self.rdsinstance,
                ],
                'route53': [
                    self.route53instance,
                ],
            },
        }

        self.report._get_monitor_status()
        self.assertEqual(
            self.report.monitor_status['monitored']['ec2'],
            desired_result['monitored']['ec2']
        )
        self.assertEqual(
            self.report.monitor_status['monitored']['rds'],
            desired_result['monitored']['rds']
        )
        self.assertEqual(
            self.report.monitor_status['monitored']['route53'],
            desired_result['monitored']['route53']
        )

    def test_get_monitored_detects_unmonitored_resources(self):
        self.ec2instance.monitored = False
        self.rdsinstance.monitored = False
        self.route53instance.monitored = False
        desired_result = {
            'unmonitored': {
                'ec2': [
                    self.ec2instance,
                ],
                'rds': [
                    self.rdsinstance,
                ],
                'route53': [
                    self.route53instance,
                ],
            },
        }

        self.report._get_monitor_status()
        self.assertEqual(
            self.report.monitor_status['unmonitored']['ec2'],
            desired_result['unmonitored']['ec2']
        )
        self.assertEqual(
            self.report.monitor_status['unmonitored']['rds'],
            desired_result['unmonitored']['rds']
        )
        self.assertEqual(
            self.report.monitor_status['unmonitored']['route53'],
            desired_result['unmonitored']['route53']
        )

    def test_get_monitored_detects_unknown_resources(self):
        self.ec2instance.monitored = 'tbd'
        self.rdsinstance.monitored = 'other'
        self.route53instance.monitored = ''
        desired_result = {
            'unknown': {
                'ec2': [
                    self.ec2instance,
                ],
                'rds': [
                    self.rdsinstance,
                ],
                'route53': [
                    self.route53instance,
                ],
            },
        }

        self.report._get_monitor_status()
        self.assertEqual(
            self.report.monitor_status['unknown']['ec2'],
            desired_result['unknown']['ec2']
        )
        self.assertEqual(
            self.report.monitor_status['unknown']['rds'],
            desired_result['unknown']['rds']
        )
        self.assertEqual(
            self.report.monitor_status['unknown']['route53'],
            desired_result['unknown']['route53']
        )

    def test_get_monitored_doesnt_fail_if_no_monitor_key(self):
        # Used a MagicMock to simulate the AttributeError when calling
        # self.monitored
        self.report.inv['ec2']['i-023desldk394995ss'] = MagicMock(spec=[])
        self.report.inv['ec2']['i-023desldk394995ss'].state = 'active'
        self.report._get_monitor_status()

    def test_get_monitored_doesnt_print_terminated_resources(self):
        self.ec2instance.monitored = True
        self.ec2instance.state = 'terminated'

        self.report._get_monitor_status()
        self.assertEqual(
            self.report.monitor_status['unknown']['ec2'],
            []
        )

    @patch('clinv.reports.monitored.MonitoredReport._get_monitor_status')
    def test_output_method_prints_monitored_resources(self, statusMock):
        # Monitor_status prefilled by the _get_monitor_status method.
        self.report.monitor_status = {
            'monitored': {
                'ec2': [
                    self.ec2instance,
                ],
                'rds': [
                    self.rdsinstance,
                ],
                'route53': [
                    self.route53instance,
                ],
            },
        }

        self.report.output('true')

        self.assertTrue(statusMock.called)
        self.assertTrue(self.ec2instance.short_print.called)
        self.assertTrue(self.route53instance.short_print.called)
        self.assertTrue(self.rdsinstance.short_print.called)

    @patch('clinv.reports.monitored.MonitoredReport._get_monitor_status')
    def test_output_method_prints_unmonitored_resources(self, statusMock):
        # Monitor_status prefilled by the _get_monitor_status method.
        self.report.monitor_status = {
            'unmonitored': {
                'ec2': [
                    self.ec2instance,
                ],
                'rds': [
                    self.rdsinstance,
                ],
                'route53': [
                    self.route53instance,
                ],
            },
        }

        self.report.output('false')

        self.assertTrue(statusMock.called)
        self.assertTrue(self.ec2instance.short_print.called)
        self.assertTrue(self.route53instance.short_print.called)
        self.assertTrue(self.rdsinstance.short_print.called)

    @patch('clinv.reports.monitored.MonitoredReport._get_monitor_status')
    def test_output_method_prints_unknown_monitor_resources(self, statusMock):
        # Monitor_status prefilled by the _get_monitor_status method.
        self.report.monitor_status = {
            'unknown': {
                'ec2': [
                    self.ec2instance,
                ],
                'rds': [
                    self.rdsinstance,
                ],
                'route53': [
                    self.route53instance,
                ],
            },
        }

        self.report.output('unknown')

        self.assertTrue(statusMock.called)
        self.assertTrue(self.ec2instance.short_print.called)
        self.assertTrue(self.route53instance.short_print.called)
        self.assertTrue(self.rdsinstance.short_print.called)
