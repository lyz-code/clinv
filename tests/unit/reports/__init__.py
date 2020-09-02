from unittest.mock import Mock, PropertyMock


class ClinvReportBaseTestClass(object):
    """
    Abstract Base class to ensure that all the clinv reports have the same
    interface.

    Public attributes:
        inventory (Inventory): Clinv inventory Mock.
        ec2instance: Clinv EC2 resource Mock.
        rdsinstance: Clinv RDS resource Mock.
        route53instance: Clinv Route53 resource Mock.
        information: Clinv Information resource Mock.
        service: Clinv Service resource Mock.
        project: Clinv Project resource Mock.
    """

    def setUp(self):
        self.inventory = Mock()
        self.inventory.inv = {
            "asg": {"asg-resource_name": PropertyMock()},
            "ec2": {"i-023desldk394995ss": Mock()},
            "rds": {"db-YDFL2": Mock()},
            "route53": {"hosted_zone_id-record1.clinv.org-cname": Mock()},
            "s3": {"s3_bucket_name": Mock()},
            "people": {"peo_01": Mock()},
            "iam_groups": {"arn:aws:iam::XXXXXXXXXXXX:group/Administrator": Mock()},
            "iam_users": {"arn:aws:iam::XXXXXXXXXXXX:user/user_1": Mock()},
            "security_groups": {"sg-xxxxxxxx": Mock()},
            "projects": {"pro_01": Mock()},
            "services": {"ser_01": Mock()},
            "informations": {"inf_01": Mock()},
            "vpc": {"vpc-xxxxxxxx": Mock()},
        }
        self.asg = self.inventory.inv["asg"]["asg-resource_name"]
        self.ec2instance = self.inventory.inv["ec2"]["i-023desldk394995ss"]
        self.s3instance = self.inventory.inv["s3"]["s3_bucket_name"]
        self.iamuser = self.inventory.inv["iam_users"][
            "arn:aws:iam::XXXXXXXXXXXX:user/user_1"
        ]
        self.iamgroup = self.inventory.inv["iam_groups"][
            "arn:aws:iam::XXXXXXXXXXXX:group/Administrator"
        ]
        self.information = self.inventory.inv["informations"]["inf_01"]
        self.person = self.inventory.inv["people"]["peo_01"]
        self.project = self.inventory.inv["projects"]["pro_01"]
        self.rdsinstance = self.inventory.inv["rds"]["db-YDFL2"]
        self.route53instance = self.inventory.inv["route53"][
            "hosted_zone_id-record1.clinv.org-cname"
        ]
        self.service = self.inventory.inv["services"]["ser_01"]
        self.security_group = self.inventory.inv["security_groups"]["sg-xxxxxxxx"]
        self.vpc = self.inventory.inv["vpc"]["vpc-xxxxxxxx"]

    def tearDown(self):
        pass

    def test_inventory_is_set(self):
        self.assertEqual(self.report.inv, self.inventory.inv)
