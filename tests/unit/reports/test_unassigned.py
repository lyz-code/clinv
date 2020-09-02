from . import ClinvReportBaseTestClass
from clinv.reports.unassigned import UnassignedReport
from unittest.mock import patch, PropertyMock
import unittest


class TestUnassignedReport(ClinvReportBaseTestClass, unittest.TestCase):
    """
    Test the UnassignedReport implementation.
    """

    def setUp(self):
        super().setUp()
        self.report = UnassignedReport(self.inventory)

    def tearDown(self):
        super().tearDown()

    def test_unassigned_ec2_prints_instances(self):
        self.report._unassigned_ec2()

        self.assertTrue(self.ec2instance.short_print.called)

    def test_unassigned_ec2_doesnt_print_asg_instances(self):
        type(self.report.inv["asg"]["asg-resource_name"]).instances = PropertyMock(
            return_value={"i-023desldk394995ss": {}}
        )
        self.report._unassigned_ec2()

        self.assertFalse(self.ec2instance.short_print.called)

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_ec2")
    def test_general_unassigned_can_use_ec2_resource(self, unassignMock):
        self.report.output("ec2")
        self.assertTrue(unassignMock.called)

    def test_unassigned_rds_prints_instances(self):
        self.rdsinstance.id = "db-YDFL2"
        self.rdsinstance.name = "resource_name"

        self.report._unassigned_rds()

        self.assertTrue(self.rdsinstance.short_print.called)

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_services_prints_instances(self, printMock):
        self.project.services = []
        self.project.informations = ["ser_02"]
        self.report._unassigned_services()
        self.assertEqual(
            printMock.assert_called_with([self.report.inv["services"]["ser_01"]]), None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_services_does_not_fail_on_empty_project_services(
        self, printMock,
    ):
        self.project.services = None
        self.report._unassigned_services()
        self.assertEqual(
            printMock.assert_called_with([self.report.inv["services"]["ser_01"]]), None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_people_prints_instances(self, printMock):
        self.project.people = []
        self.report._unassigned_people()
        self.assertEqual(
            printMock.assert_called_with([self.report.inv["people"]["peo_01"]]), None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_people_does_not_fail_on_empty_project_people(
        self, printMock,
    ):
        self.project.people = None
        self.report._unassigned_people()
        self.assertEqual(
            printMock.assert_called_with([self.report.inv["people"]["peo_01"]]), None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_people_does_not_print_terminated(self, printMock):
        self.inventory.inv["people"]["peo_01"].state = "terminated"
        self.project.people = []
        self.report._unassigned_people()
        self.assertEqual(printMock.assert_called_with([]), None)

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_informations_prints_instances(self, printMock):
        self.project.informations = ["inf_02"]
        self.report._unassigned_informations()
        self.assertEqual(
            printMock.assert_called_with([self.report.inv["informations"]["inf_01"]]),
            None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_informations_does_not_fail_on_empty_project(
        self, printMock,
    ):
        self.project.informations = None
        self.report._unassigned_informations()
        self.assertEqual(
            printMock.assert_called_with([self.report.inv["informations"]["inf_01"]]),
            None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_rds")
    def test_general_unassigned_can_use_rds_resource(self, unassignMock):
        self.report.output("rds")
        self.assertTrue(unassignMock.called)

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_services")
    def test_general_unassigned_can_use_service_resource(self, unassignMock):
        self.report.output("services")
        self.assertTrue(unassignMock.called)

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_people")
    def test_general_unassigned_can_use_people_resource(self, unassignMock):
        self.report.output("people")
        self.assertTrue(unassignMock.called)

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_informations")
    def test_general_unassigned_can_use_informations_resource(
        self, unassignMock,
    ):
        self.report.output("informations")
        self.assertTrue(unassignMock.called)

    def test_unassigned_route53_prints_instances(self):
        self.route53instance.name = "record1.clinv.org"
        self.route53instance.type = "CNAME"

        self.report._unassigned_route53()
        self.assertTrue(self.route53instance.print.called)

    def test_unassigned_route53_doesnt_prints_soa(self):
        self.route53instance.name = "record1.clinv.org"
        self.route53instance.type = "SOA"

        self.report._unassigned_route53()
        self.assertFalse(self.route53instance.print.called)

    def test_unassigned_route53_doesnt_prints_ns(self):
        self.route53instance.name = "record1.clinv.org"
        self.route53instance.type = "NS"

        self.report._unassigned_route53()
        self.assertFalse(self.route53instance.print.called)

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_route53")
    def test_general_unassigned_can_use_route53_resource(self, unassignMock):
        self.report.output("route53")
        self.assertTrue(unassignMock.called)

    def test_unassigned_s3_prints_instances(self):
        self.report._unassigned_s3()
        self.assertTrue(self.s3instance.short_print.called)

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_iam_users_prints_instances(self, printMock):
        self.report._unassigned_iam_users()
        self.assertEqual(
            printMock.assert_called_with(
                [self.report.inv["iam_users"]["arn:aws:iam::XXXXXXXXXXXX:user/user_1"]]
            ),
            None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_iam_users_does_not_fail_on_empty_people_iam_user(
        self, printMock,
    ):
        self.person.iam_user = None
        self.report._unassigned_iam_users()
        self.assertEqual(
            printMock.assert_called_with(
                [self.report.inv["iam_users"]["arn:aws:iam::XXXXXXXXXXXX:user/user_1"]]
            ),
            None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_iam_users")
    def test_general_unassigned_can_use_iam_users_resource(self, unassignMock):
        self.report.output("iam_users")
        self.assertTrue(unassignMock.called)

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_iam_groups_prints_instances(self, printMock):
        self.iamgroup.id = "arn:aws:iam::XXXXXXXXXXXX:group/Administrator"
        self.iamgroup.name = "resource_name"

        self.report._unassigned_iam_groups()

        self.assertTrue(self.iamgroup.short_print.called)

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_iam_groups")
    def test_general_unassigned_can_use_iam_groups_resource(self, unassignMock):
        self.report.output("iam_groups")
        self.assertTrue(unassignMock.called)

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_security_groups_prints_instances_if_tbd(self, printMock):
        self.security_group.id = "sg-xxxxxxxx"
        self.security_group.name = "resource_name"
        self.security_group.state = "tbd"

        self.report._unassigned_security_groups()

        self.assertEqual(
            printMock.assert_called_with(
                [self.report.inv["security_groups"]["sg-xxxxxxxx"]]
            ),
            None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_security_groups_doesnt_prints_instances_if_active(
        self, printMock
    ):
        self.security_group.id = "sg-xxxxxxxx"
        self.security_group.name = "resource_name"
        self.security_group.state = "active"

        self.report._unassigned_security_groups()

        self.assertEqual(
            printMock.assert_called_with([]), None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_security_groups_doesnt_prints_instances_if_terminated(
        self, printMock
    ):
        self.security_group.id = "sg-xxxxxxxx"
        self.security_group.name = "resource_name"
        self.security_group.state = "terminated"

        self.report._unassigned_security_groups()

        self.assertEqual(
            printMock.assert_called_with([]), None,
        )

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_vpc_prints_instances(self, printMock):
        self.report._unassigned_vpc()
        self.assertTrue(self.vpc.short_print.called)

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_vpc")
    def test_general_unassigned_can_use_vpc_resource(self, unassignMock):
        self.report.output("vpc")
        self.assertTrue(unassignMock.called)

    @patch("clinv.reports.unassigned.UnassignedReport.short_print_resources")
    def test_unassigned_asg_prints_instances(self, printMock):
        self.report._unassigned_asg()
        self.assertTrue(self.asg.short_print.called)

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_asg")
    def test_general_unassigned_can_use_asg_resource(self, unassignMock):
        self.report.output("asg")
        self.assertTrue(unassignMock.called)

    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_s3")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_route53")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_rds")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_ec2")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_services")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_people")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_iam_users")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_iam_groups")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_asg")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_vpc")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_informations")
    @patch("clinv.reports.unassigned.UnassignedReport._unassigned_security_groups")
    def test_output_can_test_all(
        self,
        informationsMock,
        iamgroupsMock,
        iamusersMock,
        peopleMock,
        servicesMock,
        ec2Mock,
        rdsMock,
        route53Mock,
        s3Mock,
        security_groupMock,
        asgMock,
        vpcMock,
    ):
        self.report.output("all")
        self.assertTrue(informationsMock.called)
        self.assertTrue(servicesMock.called)
        self.assertTrue(peopleMock.called)
        self.assertTrue(iamusersMock.called)
        self.assertTrue(iamgroupsMock.called)
        self.assertTrue(ec2Mock.called)
        self.assertTrue(rdsMock.called)
        self.assertTrue(route53Mock.called)
        self.assertTrue(s3Mock.called)
        self.assertTrue(security_groupMock.called)
        self.assertTrue(vpcMock.called)
        self.assertTrue(asgMock.called)
