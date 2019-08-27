from tests.reports import ClinvReportBaseTestClass
from clinv.reports.unassigned import UnassignedReport
from unittest.mock import patch
import unittest


class TestUnassignedReport(ClinvReportBaseTestClass, unittest.TestCase):
    '''
    Test the UnassignedReport implementation.
    '''

    def setUp(self):
        super().setUp()
        self.report = UnassignedReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    def test_unassigned_ec2_prints_instances(self):
        self.report._unassigned_ec2()

        self.assertTrue(self.ec2instance.print.called)

    def test_unassigned_rds_prints_instances(self):
        self.rdsinstance.id = 'db-YDFL2'
        self.rdsinstance.name = 'resource_name'

        self.report._unassigned_rds()

        self.assertTrue(self.rdsinstance.print.called)

    @patch('clinv.reports.unassigned.UnassignedReport.short_print_resources')
    def test_unassigned_services_prints_instances(self, printMock):
        self.project.services = []
        self.project.informations = ['ser_02']
        self.report._unassigned_services()
        self.assertEqual(
            printMock.assert_called_with(
                [self.report.inv['services']['ser_01']]
            ),
            None,
        )

    @patch('clinv.reports.unassigned.UnassignedReport.short_print_resources')
    def test_unassigned_services_does_not_fail_on_empty_project_services(
        self,
        printMock,
    ):
        self.project.services = None
        self.report._unassigned_services()
        self.assertEqual(
            printMock.assert_called_with(
                [self.report.inv['services']['ser_01']]
            ),
            None,
        )

    @patch('clinv.reports.unassigned.UnassignedReport.short_print_resources')
    def test_unassigned_informations_prints_instances(self, printMock):
        self.project.informations = ['inf_02']
        self.report._unassigned_informations()
        self.assertEqual(
            printMock.assert_called_with(
                [self.report.inv['informations']['inf_01']]
            ),
            None,
        )

    @patch('clinv.reports.unassigned.UnassignedReport.short_print_resources')
    def test_unassigned_informations_does_not_fail_on_empty_project(
        self,
        printMock,
    ):
        self.project.informations = None
        self.report._unassigned_informations()
        self.assertEqual(
            printMock.assert_called_with(
                [self.report.inv['informations']['inf_01']]
            ),
            None,
        )

    @patch('clinv.reports.unassigned.UnassignedReport._unassigned_ec2')
    def test_general_unassigned_can_use_ec2_resource(self, unassignMock):
        self.report.output('ec2')
        self.assertTrue(unassignMock.called)

    @patch('clinv.reports.unassigned.UnassignedReport._unassigned_rds')
    def test_general_unassigned_can_use_rds_resource(self, unassignMock):
        self.report.output('rds')
        self.assertTrue(unassignMock.called)

    @patch('clinv.reports.unassigned.UnassignedReport._unassigned_services')
    def test_general_unassigned_can_use_service_resource(self, unassignMock):
        self.report.output('services')
        self.assertTrue(unassignMock.called)

    @patch(
        'clinv.reports.unassigned.UnassignedReport._unassigned_informations'
    )
    def test_general_unassigned_can_use_informations_resource(
        self,
        unassignMock,
    ):
        self.report.output('informations')
        self.assertTrue(unassignMock.called)

    def test_unassigned_route53_prints_instances(self):
        self.route53instance.name = 'record1.clinv.org'
        self.route53instance.type = 'CNAME'

        self.report._unassigned_route53()
        self.assertTrue(self.route53instance.print.called)

    def test_unassigned_route53_doesnt_prints_soa(self):
        self.route53instance.name = 'record1.clinv.org'
        self.route53instance.type = 'SOA'

        self.report._unassigned_route53()
        self.assertFalse(self.route53instance.print.called)

    def test_unassigned_route53_doesnt_prints_ns(self):
        self.route53instance.name = 'record1.clinv.org'
        self.route53instance.type = 'NS'

        self.report._unassigned_route53()
        self.assertFalse(self.route53instance.print.called)

    @patch('clinv.reports.unassigned.UnassignedReport._unassigned_route53')
    def test_general_unassigned_can_use_route53_resource(self, unassignMock):
        self.report.output('route53')
        self.assertTrue(unassignMock.called)

    @patch('clinv.reports.unassigned.UnassignedReport._unassigned_route53')
    @patch('clinv.reports.unassigned.UnassignedReport._unassigned_rds')
    @patch('clinv.reports.unassigned.UnassignedReport._unassigned_ec2')
    @patch('clinv.reports.unassigned.UnassignedReport._unassigned_services')
    @patch(
        'clinv.reports.unassigned.UnassignedReport._unassigned_informations'
    )
    def test_output_can_test_all(
        self,
        informationsMock,
        servicesMock,
        ec2Mock,
        rdsMock,
        route53Mock,
    ):
        self.report.output('all')
        self.assertTrue(informationsMock.called)
        self.assertTrue(servicesMock.called)
        self.assertTrue(ec2Mock.called)
        self.assertTrue(rdsMock.called)
        self.assertTrue(route53Mock.called)
