import datetime
import unittest
from unittest.mock import PropertyMock, call, patch

from clinv.sources import aws
from dateutil.tz import tzutc

from . import ClinvGenericResourceTests, ClinvSourceBaseTestClass


class AWSSourceBaseTestClass(ClinvSourceBaseTestClass):
    """
    Abstract Base class to ensure that all the AWS sources have the same
    interface.

    Must be combined with a unittest.TestCase that defines:
        * self.source_obj the name of the source class to test
        * self.module_name: the name of the module file
    """

    def setUp(self):
        self.module_name = "aws"
        super().setUp()
        self.boto_patch = patch("clinv.sources.aws.boto3", autospect=True)
        self.boto = self.boto_patch.start()

    def tearDown(self):
        super().tearDown()
        self.boto_patch.stop()

    def test_get_regions(self):
        self.boto.client.return_value.describe_regions.return_value = {
            "Regions": [{"RegionName": "us-east-1"}, {"RegionName": "eu-west-1"}]
        }
        self.assertEqual(self.src.regions, ["us-east-1", "eu-west-1"])


class TestASGSource(AWSSourceBaseTestClass, unittest.TestCase):
    """
    Test the ASG implementation in the inventory.
    """

    def setUp(self):
        super().setUp()
        self.source_obj = aws.ASGsrc

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # What data we want to aggregate to our inventory
        self.desired_source_data = {
            "asg-autoscaler_name": {
                "AutoScalingGroupARN": "arn:aws:autoscaler_arn",
                "AutoScalingGroupName": "autoscaler_name",
                "AvailabilityZones": ["us-east-1a"],
                "CreatedTime": datetime.datetime(
                    2015, 10, 10, 10, 36, 41, 398000, tzinfo=tzutc()
                ),
                "DesiredCapacity": 2,
                "HealthCheckGracePeriod": 300,
                "HealthCheckType": "EC2",
                "Instances": [
                    {
                        "AvailabilityZone": "eu-east-1a",
                        "HealthStatus": "Healthy",
                        "InstanceId": "i-xxxxxxxxxxxxxxxx1",
                        "LaunchConfigurationName": "lc_name",
                        "LifecycleState": "InService",
                        "ProtectedFromScaleIn": False,
                    },
                    {
                        "AvailabilityZone": "eu-east-1a",
                        "HealthStatus": "Healthy",
                        "InstanceId": "i-xxxxxxxxxxxxxxxx2",
                        "LaunchConfigurationName": "lc_name",
                        "LifecycleState": "InService",
                        "ProtectedFromScaleIn": False,
                    },
                ],
                "LaunchConfigurationName": "lc_name",
                "LoadBalancerNames": [],
                "MaxSize": 10,
                "MinSize": 2,
                "ServiceLinkedRoleARN": "service_role_arn",
                "TargetGroupARNs": ["target_group_arn"],
                "VPCZoneIdentifier": "subnet-xxxxxxxx",
                "region": "us-east-1",
            },
        }
        self.desired_user_data = {
            "asg-autoscaler_name": {
                "state": "tbd",
                "to_destroy": "tbd",
                "description": "tbd",
            }
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        # Mock here the call to your provider
        boto_mock = self.boto.client.return_value

        # Simulate only one region
        boto_mock.describe_regions.return_value = {
            "Regions": [{"RegionName": "us-east-1"}]
        }
        boto_mock.describe_auto_scaling_groups.return_value = {
            "AutoScalingGroups": [
                {
                    "AutoScalingGroupARN": "arn:aws:autoscaler_arn",
                    "AutoScalingGroupName": "autoscaler_name",
                    "AvailabilityZones": ["us-east-1a"],
                    "CreatedTime": datetime.datetime(
                        2015, 10, 10, 10, 36, 41, 398000, tzinfo=tzutc()
                    ),
                    "DefaultCooldown": 300,
                    "DesiredCapacity": 2,
                    "EnabledMetrics": [
                        {"Granularity": "1Minute", "Metric": "GroupInServiceInstances"},
                        {"Granularity": "1Minute", "Metric": "GroupDesiredCapacity"},
                        {"Granularity": "1Minute", "Metric": "GroupPendingInstances"},
                        {
                            "Granularity": "1Minute",
                            "Metric": "GroupTerminatingInstances",
                        },
                        {"Granularity": "1Minute", "Metric": "GroupTotalInstances"},
                        {"Granularity": "1Minute", "Metric": "GroupMinSize"},
                        {"Granularity": "1Minute", "Metric": "GroupMaxSize"},
                        {"Granularity": "1Minute", "Metric": "GroupStandbyInstances"},
                    ],
                    "HealthCheckGracePeriod": 300,
                    "HealthCheckType": "EC2",
                    "Instances": [
                        {
                            "AvailabilityZone": "eu-east-1a",
                            "HealthStatus": "Healthy",
                            "InstanceId": "i-xxxxxxxxxxxxxxxx1",
                            "LaunchConfigurationName": "lc_name",
                            "LifecycleState": "InService",
                            "ProtectedFromScaleIn": False,
                        },
                        {
                            "AvailabilityZone": "eu-east-1a",
                            "HealthStatus": "Healthy",
                            "InstanceId": "i-xxxxxxxxxxxxxxxx2",
                            "LaunchConfigurationName": "lc_name",
                            "LifecycleState": "InService",
                            "ProtectedFromScaleIn": False,
                        },
                    ],
                    "LaunchConfigurationName": "lc_name",
                    "LoadBalancerNames": [],
                    "MaxSize": 10,
                    "MinSize": 2,
                    "NewInstancesProtectedFromScaleIn": False,
                    "ServiceLinkedRoleARN": "service_role_arn",
                    "SuspendedProcesses": [],
                    "Tags": [
                        {
                            "Key": "Name",
                            "PropagateAtLaunch": True,
                            "ResourceId": "austoscaler_name",
                            "ResourceType": "auto-scaling-group",
                            "Value": "autoscaler_name",
                        },
                    ],
                    "TargetGroupARNs": ["target_group_arn"],
                    "TerminationPolicies": ["Default"],
                    "VPCZoneIdentifier": "subnet-xxxxxxxx",
                },
            ],
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "11839",
                    "content-type": "text/xml",
                    "date": "Tue, 03 Dec 2019 13:36:12 GMT",
                    "vary": "Accept-Encoding",
                    "x-amzn-requestid": "df092cb4-15d1-11ea-8543-9febaca0a9c9",
                },
                "HTTPStatusCode": 200,
                "RequestId": "df092cb4-15d1-11ea-8543-9febaca0a9c9",
                "RetryAttempts": 0,
            },
        }

        self.src.source_data = {}

        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data, self.desired_source_data,
        )
        self.assertEqual(
            generated_source_data, self.desired_source_data,
        )

    def test_generate_user_data_creates_expected_user_data_attrib(self):
        generated_user_data = self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, self.desired_user_data,
        )
        self.assertEqual(
            generated_user_data, self.desired_user_data,
        )

    def test_generate_user_data_doesnt_loose_existing_data(self):
        user_key = [key for key in self.desired_user_data.keys()][0]
        desired_user_data = {user_key: {}}
        self.src.user_data = desired_user_data

        self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, desired_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {}
        self.assertEqual(self.src.generate_inventory(), {})

    @patch("clinv.sources.aws.ASG")
    def test_generate_inventory_creates_expected_dictionary(self, resource_mock):
        resource_id = "asg-autoscaler_name"
        self.src.user_data = self.desired_user_data

        desired_mock_input = {
            **self.src.user_data[resource_id],
            **self.src.source_data[resource_id],
        }

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with({resource_id: desired_mock_input},), None,
        )

        self.assertEqual(
            desired_inventory, {resource_id: resource_mock.return_value},
        )


class TestEC2Source(AWSSourceBaseTestClass, unittest.TestCase):
    """
    Test the EC2 implementation in the inventory.
    """

    def setUp(self):
        super().setUp()
        self.source_obj = aws.EC2src

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # Expected source_data dictionary generated by generate_source_data
        self.desired_source_data = {
            "us-east-1": [
                {
                    "Groups": [],
                    "Instances": [
                        {
                            "ImageId": "ami-ffcsssss",
                            "InstanceId": "i-023desldk394995ss",
                            "InstanceType": "c4.4xlarge",
                            "LaunchTime": datetime.datetime(
                                2018, 5, 10, 7, 13, 17, tzinfo=tzutc()
                            ),
                            "NetworkInterfaces": [
                                {
                                    "PrivateIpAddresses": [
                                        {
                                            "Association": {
                                                "IpOwnerId": "585394460090",
                                                "PublicDnsName": "ec2.com",
                                                "PublicIp": "32.312.444.22",
                                            },
                                            "Primary": True,
                                            "PrivateDnsName": "ec2.nternal",
                                            "PrivateIpAddress": "1.1.1.1",
                                        }
                                    ],
                                }
                            ],
                            "SecurityGroups": [
                                {"GroupId": "sg-f2234gf6", "GroupName": "sg-1"},
                                {"GroupId": "sg-cwfccs17", "GroupName": "sg-2"},
                            ],
                            "State": {"Code": 16, "Name": "running"},
                            "StateTransitionReason": "",
                            "Tags": [{"Key": "Name", "Value": "name"}],
                            "VpcId": "vpc-31084921",
                        }
                    ],
                    "OwnerId": "585394460090",
                    "ReservationId": "r-039ed99cad2bb3da5",
                },
            ],
        }
        self.desired_user_data = {
            "i-023desldk394995ss": {
                "description": "",
                "to_destroy": "tbd",
                "environment": "tbd",
                "monitor": "tbd",
                "region": "us-east-1",
            },
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    @patch("clinv.sources.aws.EC2src.regions", new_callable=PropertyMock)
    def test_generate_source_data_creates_expected_source_data_attrib(
        self, regionsMock
    ):
        regionsMock.return_value = ["us-east-1"]
        self.boto.client.return_value.describe_instances.return_value = {
            "Reservations": [
                {
                    "Groups": [],
                    "Instances": [
                        {
                            "AmiLaunchIndex": 0,
                            "Architecture": "x86_64",
                            "BlockDeviceMappings": [
                                {
                                    "DeviceName": "/dev/sda1",
                                    "Ebs": {
                                        "AttachTime": datetime.datetime(
                                            2018, 5, 10, 2, 58, 4, tzinfo=tzutc()
                                        ),
                                        "DeleteOnTermination": True,
                                        "Status": "attached",
                                        "VolumeId": "vol-02257f9299430042f",
                                    },
                                }
                            ],
                            "CapacityReservationSpecification": {
                                "CapacityReservationPreference": "open"
                            },
                            "ClientToken": "",
                            "CpuOptions": {"CoreCount": 8, "ThreadsPerCore": 2},
                            "EbsOptimized": True,
                            "HibernationOptions": {"Configured": False},
                            "Hypervisor": "xen",
                            "ImageId": "ami-ffcsssss",
                            "InstanceId": "i-023desldk394995ss",
                            "InstanceType": "c4.4xlarge",
                            "KeyName": "ssh_keypair",
                            "LaunchTime": datetime.datetime(
                                2018, 5, 10, 7, 13, 17, tzinfo=tzutc()
                            ),
                            "Monitoring": {"State": "enabled"},
                            "NetworkInterfaces": [
                                {
                                    "Association": {
                                        "IpOwnerId": "585394229490",
                                        "PublicDnsName": "ec21.amazonaws.com",
                                        "PublicIp": "32.312.444.22",
                                    },
                                    "Attachment": {
                                        "AttachTime": datetime.datetime(
                                            2018, 5, 10, 2, 58, 3, tzinfo=tzutc()
                                        ),
                                        "AttachmentId": "eni-attach-032346",
                                        "DeleteOnTermination": True,
                                        "DeviceIndex": 0,
                                        "Status": "attached",
                                    },
                                    "Description": "Primary ni",
                                    "Groups": [
                                        {"GroupId": "sg-f2234gf6", "GroupName": "sg-1"},
                                        {"GroupId": "sg-cwfccs17", "GroupName": "sg-2"},
                                    ],
                                    "InterfaceType": "interface",
                                    "Ipv6Addresses": [],
                                    "MacAddress": "0a:ff:ff:ff:ff:aa",
                                    "NetworkInterfaceId": "eni-3fssaw0a",
                                    "OwnerId": "583949112399",
                                    "PrivateDnsName": "ip-112.ec2.internal",
                                    "PrivateIpAddress": "142.33.2.113",
                                    "PrivateIpAddresses": [
                                        {
                                            "Association": {
                                                "IpOwnerId": "585394460090",
                                                "PublicDnsName": "ec2.com",
                                                "PublicIp": "32.312.444.22",
                                            },
                                            "Primary": True,
                                            "PrivateDnsName": "ec2.nternal",
                                            "PrivateIpAddress": "1.1.1.1",
                                        }
                                    ],
                                    "SourceDestCheck": True,
                                    "Status": "in-use",
                                    "SubnetId": "subnet-3ssaafs1",
                                    "VpcId": "vpc-fs12f872",
                                }
                            ],
                            "Placement": {
                                "AvailabilityZone": "eu-east-1a",
                                "GroupName": "",
                                "Tenancy": "default",
                            },
                            "PrivateDnsName": "ip-112.ec2.internal",
                            "PrivateIpAddress": "142.33.2.113",
                            "ProductCodes": [],
                            "PublicDnsName": "ec2.com",
                            "PublicIpAddress": "32.312.444.22",
                            "RootDeviceName": "/dev/sda1",
                            "RootDeviceType": "ebs",
                            "SecurityGroups": [
                                {"GroupId": "sg-f2234gf6", "GroupName": "sg-1"},
                                {"GroupId": "sg-cwfccs17", "GroupName": "sg-2"},
                            ],
                            "SourceDestCheck": True,
                            "State": {"Code": 16, "Name": "running"},
                            "StateTransitionReason": "",
                            "SubnetId": "subnet-sfsdwf12",
                            "Tags": [{"Key": "Name", "Value": "name"}],
                            "VirtualizationType": "hvm",
                            "VpcId": "vpc-31084921",
                        }
                    ],
                    "OwnerId": "585394460090",
                    "ReservationId": "r-039ed99cad2bb3da5",
                }
            ]
        }

        self.src.source_data = {}

        generated_source_data = self.src.generate_source_data()
        self.assertEqual(
            self.src.source_data, self.desired_source_data,
        )
        self.assertEqual(
            generated_source_data, self.desired_source_data,
        )

    def test_generate_user_data_creates_empty_user_data_if_no_src_data(self):
        self.src.source_data = {"us-east-1": {}}
        self.src.generate_user_data()
        self.assertEqual(self.src.user_data, {})

    def test_generate_user_data_adds_desired_default_user_data(self):
        self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, self.desired_user_data,
        )

    def test_generate_user_data_doesnt_loose_existing_data(self):
        desired_user_data = {
            "i-023desldk394995ss": {
                "description": "filled description",
                "to_destroy": False,
                "environment": "production",
                "region": "us-east-1",
            },
        }

        self.src.user_data = desired_user_data

        self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, desired_user_data,
        )

    def test_generate_user_data_adds_monitor_value_from_instance_tags_if_empty(self):
        self.src.source_data["us-east-1"][0]["Instances"][0]["Tags"].append(
            {"Key": "monitor", "Value": "True"}
        )

        self.src.generate_user_data()

        assert self.src.user_data["i-023desldk394995ss"]["monitor"] is True

    def test_generate_user_data_doesnt_modify_monitor_value_if_empty(self):
        self.src.source_data["us-east-1"][0]["Instances"][0]["Tags"].append(
            {"Key": "monitor", "Value": "False"}
        )
        self.src.user_data = self.desired_user_data
        self.src.user_data["i-023desldk394995ss"]["monitor"] = True

        self.src.generate_user_data()

        self.assertTrue(self.desired_user_data["i-023desldk394995ss"]["monitor"])

    def test_generate_user_data_creates_expected_user_data_attrib(self):
        expected_user_data = {}

        generated_user_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.user_data, expected_user_data,
        )
        self.assertEqual(
            generated_user_data, expected_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {"hosted_zones": {}}
        self.assertEqual(self.src.generate_inventory(), {})

    @patch("clinv.sources.aws.EC2")
    def test_generate_inventory_creates_expected_dictionary(self, resource_mock):
        resource_id = "i-023desldk394995ss"
        self.src.user_data = {
            "i-023desldk394995ss": {
                "description": "tbd",
                "to_destroy": "tbd",
                "environment": "tbd",
                "region": "us-east-1",
            },
        }

        desired_mock_input = {
            **self.src.user_data["i-023desldk394995ss"],
            **self.src.source_data["us-east-1"][0]["Instances"][0],
        }

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with({resource_id: desired_mock_input},), None,
        )

        self.assertEqual(
            desired_inventory, {resource_id: resource_mock.return_value},
        )


class TestIAMUserSource(AWSSourceBaseTestClass, unittest.TestCase):
    """
    Test the IAMUser source implementation in the inventory.
    """

    def setUp(self):
        super().setUp()
        self.source_obj = aws.IAMUsersrc

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # What data we want to aggregate to our inventory
        self.desired_source_data = {
            "arn:aws:iam::XXXXXXXXXXXX:user/user_1": {
                "Path": "/",
                "CreateDate": datetime.datetime(2019, 2, 7, 12, 15, 57, tzinfo=tzutc()),
                "UserId": "XXXXXXXXXXXXXXXXXXXXX",
                "UserName": "User 1",
            },
        }
        self.desired_user_data = {
            "arn:aws:iam::XXXXXXXXXXXX:user/user_1": {
                "name": "User 1",
                "description": "tbd",
                "to_destroy": "tbd",
                "state": "tbd",
            },
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        self.boto.client.return_value.list_users.return_value = {
            "Users": [
                {
                    "UserName": "User 1",
                    "Path": "/",
                    "CreateDate": datetime.datetime(
                        2019, 2, 7, 12, 15, 57, tzinfo=tzutc()
                    ),
                    "PasswordLastUsed": datetime.datetime(
                        2019, 11, 5, 9, 10, 59, tzinfo=tzutc()
                    ),
                    "UserId": "XXXXXXXXXXXXXXXXXXXXX",
                    "Arn": "arn:aws:iam::XXXXXXXXXXXX:user/user_1",
                },
            ]
        }

        self.src.source_data = {}
        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data, self.desired_source_data,
        )
        self.assertEqual(
            generated_source_data, self.desired_source_data,
        )

    def test_generate_user_data_creates_expected_user_data_attrib(self):
        generated_user_data = self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, self.desired_user_data,
        )
        self.assertEqual(
            generated_user_data, self.desired_user_data,
        )

    def test_generate_user_data_doesnt_loose_existing_data(self):
        desired_user_data = {
            "arn:aws:iam::XXXXXXXXXXXX:user/user_1": {
                "name": "User 1",
                "description": "User 1 description",
                "to_destroy": False,
            },
        }

        self.src.user_data = desired_user_data

        self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, desired_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {}
        self.assertEqual(self.src.generate_inventory(), {})

    @patch("clinv.sources.aws.IAMUser")
    def test_generate_inventory_creates_expected_dictionary(self, resource_mock):
        resource_id = "arn:aws:iam::XXXXXXXXXXXX:user/user_1"
        self.src.user_data = self.desired_user_data

        desired_mock_input = {
            **self.src.user_data[resource_id],
            **self.src.source_data[resource_id],
        }

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with({resource_id: desired_mock_input},), None,
        )

        self.assertEqual(
            desired_inventory, {resource_id: resource_mock.return_value},
        )


class TestIAMGroupSource(AWSSourceBaseTestClass, unittest.TestCase):
    """
    Test the IAMGroup implementation in the inventory.
    """

    def setUp(self):
        super().setUp()
        self.source_obj = aws.IAMGroupsrc

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # What data we want to aggregate to our inventory
        self.desired_source_data = {
            "arn:aws:iam::XXXXXXXXXXXX:group/Administrator": {
                "CreateDate": datetime.datetime(
                    2019, 11, 4, 12, 41, 24, tzinfo=tzutc()
                ),
                "GroupId": "XXXXXXXXXXXXXXXXXXXXX",
                "GroupName": "Administrator",
                "Path": "/",
                "Users": ["arn:aws:iam::XXXXXXXXXXXX:user/user_1"],
                "InlinePolicies": ["Inlinepolicy"],
                "AttachedPolicies": ["arn:aws:iam::aws:policy/Attachedpolicy"],
            },
        }
        self.desired_user_data = {
            "arn:aws:iam::XXXXXXXXXXXX:group/Administrator": {
                "name": "Administrator",
                "description": "tbd",
                "to_destroy": "tbd",
                "state": "tbd",
                "desired_users": ["arn:aws:iam::XXXXXXXXXXXX:user/user_1"],
            },
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        boto_mock = self.boto.client.return_value
        boto_mock.list_groups.return_value = {
            "Groups": [
                {
                    "Arn": "arn:aws:iam::XXXXXXXXXXXX:group/Administrator",
                    "CreateDate": datetime.datetime(
                        2019, 11, 4, 12, 41, 24, tzinfo=tzutc()
                    ),
                    "GroupId": "XXXXXXXXXXXXXXXXXXXXX",
                    "GroupName": "Administrator",
                    "Path": "/",
                }
            ],
            "IsTruncated": False,
            "ResponseMetadata": {},
        }

        boto_mock.get_group.return_value = {
            "Group": {
                "Arn": "arn:aws:iam::XXXXXXXXXXXX:group/Administrator",
                "CreateDate": datetime.datetime(
                    2019, 11, 4, 12, 41, 24, tzinfo=tzutc()
                ),
                "GroupId": "XXXXXXXXXXXXXXXXXXXXX",
                "GroupName": "Administrator",
                "Path": "/",
            },
            "IsTruncated": False,
            "ResponseMetadata": {},
            "Users": [
                {
                    "UserName": "User 1",
                    "Path": "/",
                    "CreateDate": datetime.datetime(
                        2019, 2, 7, 12, 15, 57, tzinfo=tzutc()
                    ),
                    "PasswordLastUsed": datetime.datetime(
                        2019, 11, 5, 9, 10, 59, tzinfo=tzutc()
                    ),
                    "UserId": "XXXXXXXXXXXXXXXXXXXXX",
                    "Arn": "arn:aws:iam::XXXXXXXXXXXX:user/user_1",
                }
            ],
        }
        boto_mock.list_group_policies.return_value = {
            "PolicyNames": ["Inlinepolicy"],
            "IsTruncated": False,
            "ResponseMetadata": {},
        }
        boto_mock.list_attached_group_policies.return_value = {
            "AttachedPolicies": [
                {
                    "PolicyArn": "arn:aws:iam::aws:policy/Attachedpolicy",
                    "PolicyName": "AttachedPolicy",
                },
            ],
            "IsTruncated": False,
            "ResponseMetadata": {},
        }

        self.src.source_data = {}

        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data, self.desired_source_data,
        )
        self.assertEqual(
            generated_source_data, self.desired_source_data,
        )

    def test_generate_user_data_creates_expected_user_data_attrib(self):
        generated_user_data = self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, self.desired_user_data,
        )
        self.assertEqual(
            generated_user_data, self.desired_user_data,
        )

    def test_generate_user_data_doesnt_loose_existing_data(self):
        user_key = [key for key in self.desired_user_data.keys()][0]
        desired_user_data = {user_key: {}}
        self.src.user_data = desired_user_data

        self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, desired_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {}
        self.assertEqual(self.src.generate_inventory(), {})

    @patch("clinv.sources.aws.IAMGroup")
    def test_generate_inventory_creates_expected_dictionary(self, resource_mock):
        resource_id = "arn:aws:iam::XXXXXXXXXXXX:group/Administrator"
        self.src.user_data = self.desired_user_data

        desired_mock_input = {
            **self.src.user_data[resource_id],
            **self.src.source_data[resource_id],
        }

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with({resource_id: desired_mock_input},), None,
        )

        self.assertEqual(
            desired_inventory, {resource_id: resource_mock.return_value},
        )


class TestRDSSource(AWSSourceBaseTestClass, unittest.TestCase):
    """
    Test the RDS implementation in the inventory.
    """

    def setUp(self):
        super().setUp()
        self.source_obj = aws.RDSsrc

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # Expected source_data dictionary generated by generate_source_data
        self.desired_source_data = {
            "us-east-1": [
                {
                    "AllocatedStorage": 100,
                    "AssociatedRoles": [],
                    "AutoMinorVersionUpgrade": True,
                    "AvailabilityZone": "us-east-1a",
                    "BackupRetentionPeriod": 7,
                    "CACertificateIdentifier": "rds-ca-2015",
                    "DBInstanceArn": "arn:aws:rds:us-east-1:224119285:db:db",
                    "DBInstanceClass": "db.t2.micro",
                    "DBInstanceIdentifier": "rds-name",
                    "DBInstanceStatus": "available",
                    "DBSecurityGroups": [],
                    "DBSubnetGroup": {
                        "DBSubnetGroupDescription": (
                            "Created from the RDS Management Console"
                        ),
                        "DBSubnetGroupName": "default-vpc-v2dcp2jh",
                        "SubnetGroupStatus": "Complete",
                        "Subnets": [
                            {
                                "SubnetAvailabilityZone": {"Name": "us-east-1a"},
                                "SubnetIdentifier": "subnet-42sfl222",
                                "SubnetStatus": "Active",
                            },
                            {
                                "SubnetAvailabilityZone": {"Name": "us-east-1e"},
                                "SubnetIdentifier": "subnet-42sfl221",
                                "SubnetStatus": "Active",
                            },
                        ],
                        "VpcId": "vpc-v2dcp2jh",
                    },
                    "DbiResourceId": "db-YDFL2",
                    "DeletionProtection": True,
                    "Endpoint": {
                        "Address": "rds-name.us-east-1.rds.amazonaws.com",
                        "HostedZoneId": "202FGHSL2JKCFW",
                        "Port": 5521,
                    },
                    "Engine": "mariadb",
                    "EngineVersion": "1.2",
                    "InstanceCreateTime": datetime.datetime(
                        2019, 6, 17, 15, 15, 8, 461000, tzinfo=tzutc()
                    ),
                    "Iops": 1000,
                    "MasterUsername": "root",
                    "MultiAZ": True,
                    "PreferredBackupWindow": "03:00-04:00",
                    "PreferredMaintenanceWindow": "fri:04:00-fri:05:00",
                    "PubliclyAccessible": False,
                    "StorageEncrypted": True,
                    "VpcSecurityGroups": [
                        {"Status": "active", "VpcSecurityGroupId": "sg-f23le20g"}
                    ],
                },
            ],
        }
        self.desired_user_data = {
            "db-YDFL2": {
                "description": "",
                "to_destroy": "tbd",
                "environment": "tbd",
                "monitor": "tbd",
                "region": "us-east-1",
            },
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    @patch("clinv.sources.aws.RDSsrc.regions", new_callable=PropertyMock)
    def test_generate_source_data_creates_expected_source_data_attrib(
        self, regionsMock
    ):
        regionsMock.return_value = ["us-east-1"]
        self.boto.client.return_value.describe_db_instances.return_value = {
            "DBInstances": [
                {
                    "AllocatedStorage": 100,
                    "AssociatedRoles": [],
                    "AutoMinorVersionUpgrade": True,
                    "AvailabilityZone": "us-east-1a",
                    "BackupRetentionPeriod": 7,
                    "CACertificateIdentifier": "rds-ca-2015",
                    "CopyTagsToSnapshot": True,
                    "DBInstanceArn": "arn:aws:rds:us-east-1:224119285:db:db",
                    "DBInstanceClass": "db.t2.micro",
                    "DBInstanceIdentifier": "rds-name",
                    "DBInstanceStatus": "available",
                    "DBParameterGroups": [
                        {
                            "DBParameterGroupName": "default.postgres11",
                            "ParameterApplyStatus": "in-sync",
                        }
                    ],
                    "DBSecurityGroups": [],
                    "DBSubnetGroup": {
                        "DBSubnetGroupDescription": (
                            "Created from the RDS Management Console"
                        ),
                        "DBSubnetGroupName": "default-vpc-v2dcp2jh",
                        "SubnetGroupStatus": "Complete",
                        "Subnets": [
                            {
                                "SubnetAvailabilityZone": {"Name": "us-east-1a"},
                                "SubnetIdentifier": "subnet-42sfl222",
                                "SubnetStatus": "Active",
                            },
                            {
                                "SubnetAvailabilityZone": {"Name": "us-east-1e"},
                                "SubnetIdentifier": "subnet-42sfl221",
                                "SubnetStatus": "Active",
                            },
                        ],
                        "VpcId": "vpc-v2dcp2jh",
                    },
                    "DbInstancePort": 0,
                    "DbiResourceId": "db-YDFL2",
                    "DeletionProtection": True,
                    "DomainMemberships": [],
                    "Endpoint": {
                        "Address": "rds-name.us-east-1.rds.amazonaws.com",
                        "HostedZoneId": "202FGHSL2JKCFW",
                        "Port": 5521,
                    },
                    "Engine": "mariadb",
                    "EngineVersion": "1.2",
                    "EnhancedMonitoringResourceArn": "logs-arn",
                    "IAMDatabaseAuthenticationEnabled": False,
                    "InstanceCreateTime": datetime.datetime(
                        2019, 6, 17, 15, 15, 8, 461000, tzinfo=tzutc()
                    ),
                    "Iops": 1000,
                    "LatestRestorableTime": datetime.datetime(
                        2019, 7, 8, 6, 23, 55, tzinfo=tzutc()
                    ),
                    "LicenseModel": "mariadb-license",
                    "MasterUsername": "root",
                    "MonitoringInterval": 60,
                    "MonitoringRoleArn": "monitoring-arn",
                    "MultiAZ": True,
                    "OptionGroupMemberships": [
                        {"OptionGroupName": "default:mariadb-1", "Status": "in-sync"}
                    ],
                    "PendingModifiedValues": {},
                    "PerformanceInsightsEnabled": True,
                    "PerformanceInsightsKMSKeyId": "performance-arn",
                    "PerformanceInsightsRetentionPeriod": 7,
                    "PreferredBackupWindow": "03:00-04:00",
                    "PreferredMaintenanceWindow": "fri:04:00-fri:05:00",
                    "PubliclyAccessible": False,
                    "ReadReplicaDBInstanceIdentifiers": [],
                    "StorageEncrypted": True,
                    "StorageType": "io1",
                    "VpcSecurityGroups": [
                        {"Status": "active", "VpcSecurityGroupId": "sg-f23le20g"},
                    ],
                },
            ],
        }

        self.src.source_data = {}
        generated_source_data = self.src.generate_source_data()
        self.assertEqual(
            self.src.source_data, self.desired_source_data,
        )
        self.assertEqual(
            generated_source_data, self.desired_source_data,
        )

    def test_generate_user_data_creates_empty_user_data_if_no_src_data(self):
        self.src.source_data = {"us-east-1": {}}
        self.src.generate_user_data()
        self.assertEqual(self.src.user_data, {})

    def test_generate_user_data_adds_desired_default_user_data(self):
        generated_user_data = self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, self.desired_user_data,
        )
        self.assertEqual(
            generated_user_data, self.desired_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {"hosted_zones": {}}
        self.assertEqual(self.src.generate_inventory(), {})

    @patch("clinv.sources.aws.RDS")
    def test_generate_inventory_creates_expected_dictionary(self, resource_mock):
        resource_id = "db-YDFL2"
        self.src.user_data = {
            "db-YDFL2": {
                "description": "tbd",
                "to_destroy": "tbd",
                "environment": "tbd",
                "region": "us-east-1",
            },
        }

        desired_mock_input = {
            **self.src.user_data["db-YDFL2"],
            **self.src.source_data["us-east-1"][0],
        }

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with({resource_id: desired_mock_input},), None,
        )

        self.assertEqual(
            desired_inventory, {resource_id: resource_mock.return_value},
        )


class TestRoute53Source(AWSSourceBaseTestClass, unittest.TestCase):
    """
    Test the Route53 implementation in the inventory.
    """

    def setUp(self):
        super().setUp()
        self.source_obj = aws.Route53src

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # What data we want to aggregate to our inventory
        self.desired_source_data = {
            "hosted_zones": [
                {
                    "Config": {
                        "Comment": "This is the description",
                        "PrivateZone": False,
                    },
                    "Id": "/hostedzone/hosted_zone_id",
                    "Name": "hostedzone.org",
                    "ResourceRecordSetCount": 1,
                    "records": [
                        {
                            "Name": "record1.clinv.org",
                            "ResourceRecords": [
                                {"Value": "127.0.0.1"},
                                {"Value": "localhost"},
                            ],
                            "TTL": 172800,
                            "Type": "CNAME",
                        },
                    ],
                },
            ],
        }
        self.desired_user_data = {
            "hosted_zone_id-record1.clinv.org-cname": {
                "description": "tbd",
                "to_destroy": "tbd",
                "monitor": "tbd",
                "state": "active",
            },
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    def test_generate_user_data_creates_empty_user_data_if_no_src_data(self):
        self.src.source_data = {"hosted_zones": {}}
        self.src.generate_user_data()
        self.assertEqual(self.src.user_data, {})

    def test_generate_user_data_adds_desired_default_user_data(self):
        generated_user_data = self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, self.desired_user_data,
        )
        self.assertEqual(
            generated_user_data, self.desired_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {"hosted_zones": {}}
        self.assertEqual(self.src.generate_inventory(), {})

    @patch("clinv.sources.aws.Route53")
    def test_generate_inventory_creates_expected_dictionary(self, resource_mock):
        resource_id = "hosted_zone_id-record1.clinv.org-cname"
        desired_mock_input = {
            "Name": "record1.clinv.org",
            "ResourceRecords": [{"Value": "127.0.0.1"}, {"Value": "localhost"}],
            "TTL": 172800,
            "Type": "CNAME",
            "description": "tbd",
            "to_destroy": "tbd",
            "hosted_zone": {
                "id": "/hostedzone/hosted_zone_id",
                "private": False,
                "name": "hostedzone.org",
            },
            "state": "active",
        }
        self.src.user_data = {
            "hosted_zone_id-record1.clinv.org-cname": {
                "description": "tbd",
                "to_destroy": "tbd",
                "state": "active",
            },
        }
        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with({resource_id: desired_mock_input},), None,
        )

        self.assertEqual(
            desired_inventory, {resource_id: resource_mock.return_value},
        )


class TestRoute53SourceFetch(AWSSourceBaseTestClass, unittest.TestCase):
    """
    Extend AWSBaseTewstClass to test the Route53 fetch implementation in the
    inventory.
    """

    def setUp(self):
        super().setUp()
        self.source_obj = aws.Route53src

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = aws.Route53src(source_data, user_data)

        self.boto_client = self.boto.client.return_value

        # Expected boto call to get the hosted zones
        self.boto_client.list_hosted_zones.return_value = {
            "HostedZones": [
                {
                    "CallerReference": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
                    "Config": {
                        "Comment": "This is the description",
                        "PrivateZone": False,
                    },
                    "Id": "/hostedzone/hosted_zone_id",
                    "Name": "hostedzone.org",
                    "ResourceRecordSetCount": 1,
                },
            ],
            "IsTruncated": False,
            "MaxItems": "100",
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "4211",
                    "content-type": "text/xml",
                    "date": "Mon, 15 Jul 2019 13:13:51 GMT",
                    "vary": "accept-encoding",
                    "x-amzn-requestid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                },
                "HTTPStatusCode": 200,
                "RequestId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "RetryAttempts": 0,
            },
        }

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        # Expected boto call to get the resources of a hosted zone
        self.boto_client.list_resource_record_sets.return_value = {
            "IsTruncated": False,
            "MaxItems": "100",
            "ResourceRecordSets": [
                {
                    "Name": "record1.clinv.org.",
                    "ResourceRecords": [
                        {"Value": "127.0.0.1"},
                        {"Value": "localhost"},
                    ],
                    "TTL": 172800,
                    "Type": "CNAME",
                },
            ],
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "20952",
                    "content-type": "text/xml",
                    "date": "Mon, 15 Jul 2019 13:20:58 GMT",
                    "vary": "accept-encoding",
                    "x-amzn-requestid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                },
                "HTTPStatusCode": 200,
                "RequestId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "RetryAttempts": 0,
            },
        }

        expected_source_data = {
            "hosted_zones": [
                {
                    "Config": {
                        "Comment": "This is the description",
                        "PrivateZone": False,
                    },
                    "Id": "/hostedzone/hosted_zone_id",
                    "Name": "hostedzone.org",
                    "ResourceRecordSetCount": 1,
                    "records": [
                        {
                            "Name": "record1.clinv.org.",
                            "ResourceRecords": [
                                {"Value": "127.0.0.1"},
                                {"Value": "localhost"},
                            ],
                            "TTL": 172800,
                            "Type": "CNAME",
                        },
                    ],
                },
            ],
        }

        generated_source_data = self.src.generate_source_data()
        self.assertEqual(
            self.src.source_data, expected_source_data,
        )
        self.assertEqual(
            generated_source_data, expected_source_data,
        )

    def test_generate_source_data_supports_pagination_on_resources(self):
        self.src.source_data = {"route53": {}}

        expected_first_list_resource_record_sets = {
            "IsTruncated": True,
            "NextRecordName": "record2.clinv.org",
            "NextRecordType": "CNAME",
            "MaxItems": "100",
            "ResourceRecordSets": [
                {
                    "Name": "record1.clinv.org",
                    "ResourceRecords": [
                        {"Value": "127.0.0.1"},
                        {"Value": "localhost"},
                    ],
                    "TTL": 172800,
                    "Type": "CNAME",
                },
            ],
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "20952",
                    "content-type": "text/xml",
                    "date": "Mon, 15 Jul 2019 13:20:58 GMT",
                    "vary": "accept-encoding",
                    "x-amzn-requestid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                },
                "HTTPStatusCode": 200,
                "RequestId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "RetryAttempts": 0,
            },
        }
        expected_second_list_resource_record_sets = {
            "IsTruncated": False,
            "MaxItems": "100",
            "ResourceRecordSets": [
                {
                    "Name": "record2.clinv.org",
                    "ResourceRecords": [
                        {"Value": "127.0.0.1"},
                        {"Value": "localhost"},
                    ],
                    "TTL": 172800,
                    "Type": "CNAME",
                },
            ],
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "content-length": "20952",
                    "content-type": "text/xml",
                    "date": "Mon, 15 Jul 2019 13:20:58 GMT",
                    "vary": "accept-encoding",
                    "x-amzn-requestid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                },
                "HTTPStatusCode": 200,
                "RequestId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "RetryAttempts": 0,
            },
        }

        self.boto.client.return_value.list_resource_record_sets.side_effect = [
            expected_first_list_resource_record_sets,
            expected_second_list_resource_record_sets,
        ]

        expected_source_data = {
            "hosted_zones": [
                {
                    "Config": {
                        "Comment": "This is the description",
                        "PrivateZone": False,
                    },
                    "Id": "/hostedzone/hosted_zone_id",
                    "Name": "hostedzone.org",
                    "ResourceRecordSetCount": 1,
                    "records": [
                        {
                            "Name": "record1.clinv.org",
                            "ResourceRecords": [
                                {"Value": "127.0.0.1"},
                                {"Value": "localhost"},
                            ],
                            "TTL": 172800,
                            "Type": "CNAME",
                        },
                        {
                            "Name": "record2.clinv.org",
                            "ResourceRecords": [
                                {"Value": "127.0.0.1"},
                                {"Value": "localhost"},
                            ],
                            "TTL": 172800,
                            "Type": "CNAME",
                        },
                    ],
                },
            ],
        }

        self.src.generate_source_data()
        self.assertEqual(
            self.src.source_data, expected_source_data,
        )

        self.assertEqual(
            self.boto.client.return_value.list_resource_record_sets.mock_calls,
            [
                call(HostedZoneId="/hostedzone/hosted_zone_id"),
                call(
                    HostedZoneId="/hostedzone/hosted_zone_id",
                    StartRecordName="record2.clinv.org",
                    StartRecordType="CNAME",
                ),
            ],
        )


class TestS3Source(AWSSourceBaseTestClass, unittest.TestCase):
    """
    Test the S3 implementation in the inventory.
    """

    def setUp(self):
        super().setUp()
        self.source_obj = aws.S3src

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # What data we want to aggregate to our inventory
        self.desired_source_data = {
            "s3_bucket_name": {
                "CreationDate": datetime.datetime(
                    2012, 12, 12, 0, 7, 46, tzinfo=tzutc()
                ),
                "Name": "s3_bucket_name",
                "permissions": {"READ": "public", "WRITE": "private"},
                "Grants": [
                    {
                        "Grantee": {
                            "DisplayName": "admin",
                            "ID": "admin_id",
                            "Type": "CanonicalUser",
                        },
                        "Permission": "READ",
                    },
                    {
                        "Grantee": {
                            "DisplayName": "admin",
                            "ID": "admin_id",
                            "Type": "CanonicalUser",
                        },
                        "Permission": "WRITE",
                    },
                    {
                        "Grantee": {
                            "Type": "Group",
                            "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                        },
                        "Permission": "READ",
                    },
                ],
            },
        }
        self.desired_user_data = {
            "s3_bucket_name": {
                "description": "",
                "to_destroy": "tbd",
                "environment": "tbd",
                "desired_permissions": {"read": "tbd", "write": "tbd"},
                "state": "active",
            },
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        self.boto.client.return_value.list_buckets.return_value = {
            "Buckets": [
                {
                    "CreationDate": datetime.datetime(
                        2012, 12, 12, 0, 7, 46, tzinfo=tzutc()
                    ),
                    "Name": "s3_bucket_name",
                },
            ],
            "Owner": {"DisplayName": "owner_name", "ID": "owner_id"},
            "ResponseMetadata": {
                "HTTPHeaders": {"content-type": "application/xml"},
                "HTTPStatusCode": 200,
                "HostId": "Host_id",
                "RequestId": "Request_id",
                "RetryAttempts": 0,
            },
        }

        self.boto.client.return_value.get_bucket_acl.return_value = {
            "Grants": [
                {
                    "Grantee": {
                        "DisplayName": "admin",
                        "ID": "admin_id",
                        "Type": "CanonicalUser",
                    },
                    "Permission": "READ",
                },
                {
                    "Grantee": {
                        "DisplayName": "admin",
                        "ID": "admin_id",
                        "Type": "CanonicalUser",
                    },
                    "Permission": "WRITE",
                },
                {
                    "Grantee": {
                        "Type": "Group",
                        "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                    },
                    "Permission": "READ",
                },
            ],
            "Owner": {"DisplayName": "owner_name", "ID": "owner_id"},
            "ResponseMetadata": {
                "HTTPHeaders": {"content-type": "application/xml"},
                "HTTPStatusCode": 200,
                "HostId": "Host_id",
                "RequestId": "Request_id",
                "RetryAttempts": 0,
            },
        }

        self.src.source_data = {}

        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data, self.desired_source_data,
        )
        self.assertEqual(
            generated_source_data, self.desired_source_data,
        )

    def test_generate_user_data_creates_expected_user_data_attrib(self):
        generated_user_data = self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, self.desired_user_data,
        )
        self.assertEqual(
            generated_user_data, self.desired_user_data,
        )

    def test_generate_user_data_doesnt_loose_existing_data(self):
        user_key = [key for key in self.desired_user_data.keys()][0]
        desired_user_data = {user_key: {}}
        self.src.user_data = desired_user_data

        self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, desired_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {}
        self.assertEqual(self.src.generate_inventory(), {})

    @patch("clinv.sources.aws.S3")
    def test_generate_inventory_creates_expected_dictionary(self, resource_mock):
        resource_id = "s3_bucket_name"
        self.src.user_data = self.desired_user_data

        desired_mock_input = {
            **self.src.user_data[resource_id],
            **self.src.source_data[resource_id],
        }

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with({resource_id: desired_mock_input},), None,
        )

        self.assertEqual(
            desired_inventory, {resource_id: resource_mock.return_value},
        )


class TestSecurityGroupSource(AWSSourceBaseTestClass, unittest.TestCase):
    """
    Test the SecurityGroup implementation in the inventory.
    """

    def setUp(self):
        self.module_name = "aws"
        self.source_obj = aws.SecurityGroupsrc
        super().setUp()

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # What data we want to aggregate to our inventory
        self.desired_source_data = {
            "sg-xxxxxxxx": {
                "description": "default group",
                "GroupName": "default",
                "region": "us-east-1",
                "IpPermissions": [
                    {
                        "FromPort": 0,
                        "IpProtocol": "udp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": 65535,
                        "UserIdGroupPairs": [],
                    },
                    {
                        "FromPort": -1,
                        "IpProtocol": "icmp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": -1,
                        "UserIdGroupPairs": [],
                    },
                    {
                        "FromPort": 0,
                        "IpProtocol": "tcp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": 65535,
                        "UserIdGroupPairs": [],
                    },
                ],
                "IpPermissionsEgress": [],
                "VpcId": "vpc-xxxxxxxxxxx",
            },
        }

        self.desired_user_data = {
            "sg-xxxxxxxx": {
                "state": "tbd",
                "to_destroy": "tbd",
                "ingress": [
                    {
                        "FromPort": 0,
                        "IpProtocol": "udp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": 65535,
                        "UserIdGroupPairs": [],
                    },
                    {
                        "FromPort": -1,
                        "IpProtocol": "icmp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": -1,
                        "UserIdGroupPairs": [],
                    },
                    {
                        "FromPort": 0,
                        "IpProtocol": "tcp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": 65535,
                        "UserIdGroupPairs": [],
                    },
                ],
                "egress": [],
            },
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        # Mock here the call to your provider
        boto_mock = self.boto.client.return_value

        # Simulate only one region
        boto_mock.describe_regions.return_value = {
            "Regions": [{"RegionName": "us-east-1"}]
        }
        boto_mock.describe_security_groups.return_value = {
            "SecurityGroups": [
                {
                    "Description": "default group",
                    "GroupId": "sg-xxxxxxxx",
                    "GroupName": "default",
                    "IpPermissions": [
                        {
                            "FromPort": 0,
                            "IpProtocol": "udp",
                            "IpRanges": [],
                            "Ipv6Ranges": [],
                            "PrefixListIds": [],
                            "ToPort": 65535,
                            "UserIdGroupPairs": [],
                        },
                        {
                            "FromPort": -1,
                            "IpProtocol": "icmp",
                            "IpRanges": [],
                            "Ipv6Ranges": [],
                            "PrefixListIds": [],
                            "ToPort": -1,
                            "UserIdGroupPairs": [],
                        },
                        {
                            "FromPort": 0,
                            "IpProtocol": "tcp",
                            "IpRanges": [],
                            "Ipv6Ranges": [],
                            "PrefixListIds": [],
                            "ToPort": 65535,
                            "UserIdGroupPairs": [],
                        },
                    ],
                    "IpPermissionsEgress": [],
                    "OwnerId": "yyyyyyyyyyyy",
                    "VpcId": "vpc-xxxxxxxxxxx",
                }
            ]
        }

        self.src.source_data = {}

        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data, self.desired_source_data,
        )
        self.assertEqual(
            generated_source_data, self.desired_source_data,
        )

    def test_generate_user_data_creates_expected_user_data_attrib(self):
        generated_user_data = self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, self.desired_user_data,
        )
        self.assertEqual(
            generated_user_data, self.desired_user_data,
        )

    def test_generate_user_data_doesnt_loose_existing_data(self):
        user_key = [key for key in self.desired_user_data.keys()][0]
        desired_user_data = {user_key: {}}
        self.src.user_data = desired_user_data

        self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, desired_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {}
        self.assertEqual(self.src.generate_inventory(), {})

    @patch("clinv.sources.aws.SecurityGroup")
    def test_generate_inventory_creates_expected_dictionary(self, resource_mock):
        resource_id = "sg-xxxxxxxx"
        self.src.user_data = self.desired_user_data

        desired_mock_input = {
            **self.src.user_data[resource_id],
            **self.src.source_data[resource_id],
        }

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with({resource_id: desired_mock_input},), None,
        )

        self.assertEqual(
            desired_inventory, {resource_id: resource_mock.return_value},
        )


class TestVPCSource(AWSSourceBaseTestClass, unittest.TestCase):
    """
    Test the VPC implementation in the inventory.
    """

    def setUp(self):
        self.module_name = "aws"
        super().setUp()
        self.source_obj = aws.VPCsrc

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # What data we want to aggregate to our inventory
        self.desired_source_data = {
            "vpc-xxxxxxxxxxxx": {
                "CidrBlock": "172.16.0.0/16",
                "DhcpOptionsId": "dopt-xxxxxxxx",
                "InstanceTenancy": "default",
                "IsDefault": False,
                "region": "us-east-1",
                "State": "available",
                "Tags": [{"Key": "Name", "Value": "vpc name"}],
            }
        }
        self.desired_user_data = {
            "vpc-xxxxxxxxxxxx": {
                "state": "tbd",
                "to_destroy": "tbd",
                "description": "tbd",
            }
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        # Mock here the call to your provider
        boto_mock = self.boto.client.return_value

        # Simulate only one region
        boto_mock.describe_regions.return_value = {
            "Regions": [{"RegionName": "us-east-1"}]
        }
        boto_mock.describe_vpcs.return_value = {
            "Vpcs": [
                {
                    "CidrBlock": "172.16.0.0/16",
                    "CidrBlockAssociationSet": [
                        {
                            "AssociationId": "vpc-cidr-assoc-xxxxxxxxx",
                            "CidrBlock": "172.16.0.0/16",
                            "CidrBlockState": {"State": "associated"},
                        }
                    ],
                    "DhcpOptionsId": "dopt-xxxxxxxx",
                    "InstanceTenancy": "default",
                    "IsDefault": False,
                    "OwnerId": "xxxxxxxxxxxx",
                    "State": "available",
                    "Tags": [{"Key": "Name", "Value": "vpc name"}],
                    "VpcId": "vpc-xxxxxxxxxxxx",
                }
            ],
        }

        self.src.source_data = {}

        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data, self.desired_source_data,
        )
        self.assertEqual(
            generated_source_data, self.desired_source_data,
        )

    def test_generate_user_data_creates_expected_user_data_attrib(self):
        generated_user_data = self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, self.desired_user_data,
        )
        self.assertEqual(
            generated_user_data, self.desired_user_data,
        )

    def test_generate_user_data_doesnt_loose_existing_data(self):
        user_key = [key for key in self.desired_user_data.keys()][0]
        desired_user_data = {user_key: {}}
        self.src.user_data = desired_user_data

        self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data, desired_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {}
        self.assertEqual(self.src.generate_inventory(), {})

    @patch("clinv.sources.aws.VPC")
    def test_generate_inventory_creates_expected_dictionary(self, resource_mock):
        resource_id = "vpc-xxxxxxxxxxxx"
        self.src.user_data = self.desired_user_data

        desired_mock_input = {
            **self.src.user_data[resource_id],
            **self.src.source_data[resource_id],
        }

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with({resource_id: desired_mock_input},), None,
        )

        self.assertEqual(
            desired_inventory, {resource_id: resource_mock.return_value},
        )


class ClinvAWSResourceTests(ClinvGenericResourceTests):
    """Must be combined with a unittest.TestCase that defines:
        * self.resource as a ClinvAWSResource subclass instance
        * self.raw as a dictionary with the data of the resource
        * self.id as a string with the resource id

    And the following properties must be set:
        * resource name: resource_name
        * type: 'c4.4xlarge'
        * region: 'us-east-1'
    """

    def setUp(self):
        self.module_name = "aws"
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_type(self):
        self.assertEqual(self.resource.type, "c4.4xlarge")

    def test_get_region(self):
        self.assertEqual(
            self.resource.region, "us-east-1",
        )

    def test_search_by_security_group(self):
        self.assertTrue(self.resource.search("sg-f2234gf6"))

    def test_search_by_region(self):
        self.assertTrue(self.resource.search("us-east-1"))

    def test_search_by_type(self):
        self.assertTrue(self.resource.search("c4.4xlarge"))

    def test_monitor_property_works_as_expected_if_unset(self):
        self.resource.raw.pop("monitor")
        self.assertEqual(self.resource.monitor, "unknown")

    def test_monitor_property_works_as_expected_if_non_known_value(self):
        self.resource.raw["monitor"] = "tbd"
        self.assertEqual(self.resource.monitor, "unknown")

    def test_monitor_property_works_as_expected_if_set_to_bool_true(self):
        self.resource.raw["monitor"] = True
        self.assertEqual(self.resource.monitor, True)

    def test_monitor_property_works_as_expected_if_set_to_bool_false(self):
        self.resource.raw["monitor"] = False
        self.assertEqual(self.resource.monitor, False)


class TestASG(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        self.module_name = "aws"
        self.id = "asg-resource_name"

        super().setUp()

        self.raw = {
            "asg-resource_name": {
                "AutoScalingGroupARN": "arn:aws:autoscaler_arn",
                "AutoScalingGroupName": "resource_name",
                "AvailabilityZones": ["us-east-1a", "us-east-1b"],
                "CreatedTime": datetime.datetime(
                    2015, 10, 10, 10, 36, 41, 398000, tzinfo=tzutc()
                ),
                "DesiredCapacity": 2,
                "HealthCheckGracePeriod": 300,
                "HealthCheckType": "EC2",
                "Instances": [
                    {
                        "AvailabilityZone": "eu-east-1a",
                        "HealthStatus": "Healthy",
                        "InstanceId": "i-xxxxxxxxxxxxxxxx1",
                        "LaunchConfigurationName": "lc_name",
                        "LifecycleState": "InService",
                        "ProtectedFromScaleIn": False,
                    },
                    {
                        "AvailabilityZone": "eu-east-1a",
                        "HealthStatus": "Healthy",
                        "InstanceId": "i-xxxxxxxxxxxxxxxx2",
                        "LaunchConfigurationName": "lc_name",
                        "LifecycleState": "InService",
                        "ProtectedFromScaleIn": False,
                    },
                ],
                "LaunchConfigurationName": "lc_name",
                "LoadBalancerNames": [],
                "MaxSize": 10,
                "MinSize": 2,
                "ServiceLinkedRoleARN": "service_role_arn",
                "TargetGroupARNs": ["target_group_arn"],
                "VPCZoneIdentifier": "subnet-xxxxxxxx",
                "region": "us-east-1",
                "state": "active",
                "to_destroy": "tbd",
                "description": "This is the description",
            }
        }
        self.resource = aws.ASG(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_instances_returns_expected_dictionary(self):
        self.assertEqual(
            self.resource.instances,
            {
                "i-xxxxxxxxxxxxxxxx1": {
                    "AvailabilityZone": "eu-east-1a",
                    "HealthStatus": "Healthy",
                    "LaunchConfigurationName": "lc_name",
                    "LifecycleState": "InService",
                    "ProtectedFromScaleIn": False,
                },
                "i-xxxxxxxxxxxxxxxx2": {
                    "AvailabilityZone": "eu-east-1a",
                    "HealthStatus": "Healthy",
                    "LaunchConfigurationName": "lc_name",
                    "LifecycleState": "InService",
                    "ProtectedFromScaleIn": False,
                },
            },
        )

    def test_print_instances_prints_expected_information(self):
        with patch("clinv.sources.aws.tabulate") as tabulateMock:
            self.resource.print_instances()

        # Status formats the data in a table
        expected_headers = [
            "Instance",
            "Status",
            "Zones",
            "LaunchConfiguration",
        ]
        expected_data = [
            ["i-xxxxxxxxxxxxxxxx1", "Healthy/InService", "eu-east-1a", "lc_name"],
            ["i-xxxxxxxxxxxxxxxx2", "Healthy/InService", "eu-east-1a", "lc_name"],
        ]
        tabulateMock.assert_called_once_with(
            expected_data, headers=expected_headers, tablefmt="simple",
        )

        self.assertEqual(
            self.print.assert_called_once_with(tabulateMock.return_value), None,
        )

    @patch("clinv.sources.aws.ASG.print_instances")
    def test_print_resource_information(self, printinstancesMock):
        self.resource.print()
        print_calls = (
            call("asg-resource_name"),
            call("  Description: This is the description"),
            call("  State: active"),
            call("  Destroy: tbd"),
            call("  Zones: us-east-1a, us-east-1b"),
            call("  Launch Configuration: lc_name"),
            call("  Healthcheck: EC2"),
            call("  Capacity: 2"),
            call("    Desired: 2"),
            call("    Max: 10"),
            call("    Min: 2"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(12, len(self.print.mock_calls))
        self.assertTrue(printinstancesMock.called)


class TestEC2(ClinvAWSResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = "i-01"
        self.raw = {
            "i-01": {
                "AmiLaunchIndex": 0,
                "Architecture": "x86_64",
                "BlockDeviceMappings": [
                    {
                        "DeviceName": "/dev/sda1",
                        "Ebs": {
                            "AttachTime": datetime.datetime(
                                2018, 5, 10, 2, 58, 4, tzinfo=tzutc()
                            ),
                            "DeleteOnTermination": True,
                            "Status": "attached",
                            "VolumeId": "vol-02257f9299430042f",
                        },
                    }
                ],
                "CapacityReservationSpecification": {
                    "CapacityReservationPreference": "open"
                },
                "ClientToken": "",
                "CpuOptions": {"CoreCount": 8, "ThreadsPerCore": 2},
                "EbsOptimized": True,
                "HibernationOptions": {"Configured": False},
                "Hypervisor": "xen",
                "ImageId": "ami-ffcsssss",
                "InstanceId": "i-01",
                "InstanceType": "c4.4xlarge",
                "KeyName": "ssh_keypair",
                "LaunchTime": datetime.datetime(2018, 5, 10, 7, 13, 17, tzinfo=tzutc()),
                "Monitoring": {"State": "enabled"},
                "NetworkInterfaces": [
                    {
                        "Association": {
                            "IpOwnerId": "585394229490",
                            "PublicDnsName": "ec2.aws.com",
                            "PublicIp": "32.312.444.22",
                        },
                        "Attachment": {
                            "AttachTime": datetime.datetime(
                                2018, 5, 10, 2, 58, 3, tzinfo=tzutc()
                            ),
                            "AttachmentId": "eni-032346",
                            "DeleteOnTermination": True,
                            "DeviceIndex": 0,
                            "Status": "attached",
                        },
                        "Description": "Primary ni",
                        "Groups": [
                            {"GroupId": "sg-f2234gf6", "GroupName": "sg-1"},
                            {"GroupId": "sg-cwfccs17", "GroupName": "sg-2"},
                        ],
                        "InterfaceType": "interface",
                        "Ipv6Addresses": [],
                        "MacAddress": "0a:ff:ff:ff:ff:aa",
                        "NetworkInterfaceId": "eni-3fssaw0a",
                        "OwnerId": "583949112399",
                        "PrivateDnsName": "ipec2.internal",
                        "PrivateIpAddress": "142.33.2.113",
                        "PrivateIpAddresses": [
                            {
                                "Association": {
                                    "IpOwnerId": "584460090",
                                    "PublicDnsName": "ec2.com",
                                    "PublicIp": "32.312.444.22",
                                },
                                "Primary": True,
                                "PrivateDnsName": "ecernal",
                                "PrivateIpAddress": "142.33.2.113",
                            }
                        ],
                        "SourceDestCheck": True,
                        "Status": "in-use",
                        "SubnetId": "subnet-3ssaafs1",
                        "VpcId": "vpc-fs12f872",
                    }
                ],
                "Placement": {
                    "AvailabilityZone": "eu-east-1a",
                    "GroupName": "",
                    "Tenancy": "default",
                },
                "PrivateDnsName": "ip-112.ec2.internal",
                "PrivateIpAddress": "142.33.2.113",
                "ProductCodes": [],
                "PublicDnsName": "ec2.com",
                "PublicIpAddress": "32.312.444.22",
                "RootDeviceName": "/dev/sda1",
                "RootDeviceType": "ebs",
                "SecurityGroups": [
                    {"GroupId": "sg-f2234gf6", "GroupName": "sg-1"},
                    {"GroupId": "sg-cwfccs17", "GroupName": "sg-2"},
                ],
                "SourceDestCheck": True,
                "State": {"Code": 16, "Name": "active"},
                "StateTransitionReason": "reason",
                "SubnetId": "subnet-sfsdwf12",
                "Tags": [{"Key": "Name", "Value": "resource_name"}],
                "VirtualizationType": "hvm",
                "VpcId": "vpc-31084921",
                "description": "This is in the description of the instance",
                "region": "us-east-1",
                "to_destroy": "tbd",
                "monitor": "tbd",
                "environment": "tbd",
            }
        }
        self.resource = aws.EC2(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_instance_name_return_null_if_empty(self):
        self.raw["i-01"].pop("Tags", None)
        self.assertEqual(self.resource.name, "none")

    def test_get_private_ip(self):
        self.assertEqual(self.resource.private_ips, ["142.33.2.113"])

    def test_get_multiple_private_ips(self):
        self.resource.raw["NetworkInterfaces"][0]["PrivateIpAddresses"].append(
            {"PrivateIpAddress": "142.33.2.114"}
        )
        self.assertEqual(self.resource.private_ips, ["142.33.2.113", "142.33.2.114"])

    def test_get_public_ip(self):
        self.assertEqual(self.resource.public_ips, ["32.312.444.22"])

    def test_get_multiple_public_ips(self):
        self.resource.raw["NetworkInterfaces"][0]["PrivateIpAddresses"].append(
            {"Association": {"PublicIp": "32.312.444.23"}}
        )
        self.assertEqual(self.resource.public_ips, ["32.312.444.22", "32.312.444.23"])

    def test_get_state_transition_reason(self):
        self.assertEqual(self.resource.state_transition, "reason")

    def test_print_resource_information(self):
        self.resource.raw["State"]["Name"] = "running"

        self.resource.print()
        print_calls = (
            call("i-01"),
            call("  Name: resource_name"),
            call("  State: running"),
            call("  Type: c4.4xlarge"),
            call("  SecurityGroups: "),
            call("    - sg-f2234gf6: sg-1"),
            call("    - sg-cwfccs17: sg-2"),
            call("  PrivateIP: ['142.33.2.113']"),
            call("  PublicIP: ['32.312.444.22']"),
            call("  Region: us-east-1"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(10, len(self.print.mock_calls))

    def test_print_ec2_reason_if_stopped(self):
        self.raw["i-01"]["State"]["Name"] = "stopped"
        self.resource.print()
        print_calls = (
            call("i-01"),
            call("  Name: resource_name"),
            call("  State: stopped"),
            call("  State Reason: reason"),
            call("  Type: c4.4xlarge"),
            call("  SecurityGroups: "),
            call("    - sg-f2234gf6: sg-1"),
            call("    - sg-cwfccs17: sg-2"),
            call("  PrivateIP: ['142.33.2.113']"),
            call("  PublicIP: ['32.312.444.22']"),
            call("  Region: us-east-1"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(11, len(self.print.mock_calls))

    def test_search_ec2_by_public_ip(self):
        self.assertTrue(self.resource.search("32.312.444.22"))

    def test_search_ec2_by_private_ip(self):
        self.assertTrue(self.resource.search("142.33.2.113"))

    def test_get_security_groups(self):
        self.assertEqual(
            self.resource.security_groups,
            {"sg-f2234gf6": "sg-1", "sg-cwfccs17": "sg-2"},
        )

    def test_search_ec2_by_security_group_id(self):
        self.assertTrue(self.resource.search("sg-cw.*"))

    def test_get_vpc(self):
        self.assertEqual(self.resource.vpc, "vpc-31084921")

    def test_get_vpc_doesnt_fail_if_it_doesnt_exist(self):
        self.resource.raw.pop("VpcId")
        self.assertEqual(self.resource.vpc, None)

    def test_search_uses_vpc(self):
        self.assertTrue(self.resource.search("vpc-310.*"))

    def test_search_by_vpc_doesnt_fail_if_none(self):
        self.resource.raw.pop("VpcId")
        self.assertFalse(self.resource.search("vpc-310.*"))

    def test_monitor_property_works_as_expected_if_unset(self):
        self.resource.raw.pop("monitor")
        self.assertEqual(self.resource.monitor, "unknown")

    def test_monitor_property_works_as_expected_if_non_known_value(self):
        self.resource.raw["monitor"] = "tbd"
        self.assertEqual(self.resource.monitor, "unknown")

    def test_monitor_property_works_as_expected_if_set_to_true(self):
        self.resource.raw["monitor"] = True
        self.assertEqual(self.resource.monitor, True)

    def test_monitor_property_works_as_expected_if_set_to_false(self):
        self.resource.raw["monitor"] = False
        self.assertEqual(self.resource.monitor, False)


class TestRDS(ClinvAWSResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = "db-YDFL2"
        self.raw = {
            "db-YDFL2": {
                "AllocatedStorage": 100,
                "AssociatedRoles": [],
                "AutoMinorVersionUpgrade": True,
                "AvailabilityZone": "us-east-1a",
                "BackupRetentionPeriod": 7,
                "CACertificateIdentifier": "rds-ca-2015",
                "DBInstanceArn": "arn:aws:rds:us-east-1:224119285:db:db",
                "DBInstanceClass": "c4.4xlarge",
                "DBInstanceIdentifier": "resource_name",
                "DBInstanceStatus": "active",
                "DBSecurityGroups": ["sg-f2234gf6"],
                "DBSubnetGroup": {
                    "DBSubnetGroupDescription": (
                        "Created from the RDS Management Console"
                    ),
                    "DBSubnetGroupName": "default-vpc-v2dcp2jh",
                    "SubnetGroupStatus": "Complete",
                    "Subnets": [
                        {
                            "SubnetAvailabilityZone": {"Name": "us-east-1a"},
                            "SubnetIdentifier": "subnet-42sfl222",
                            "SubnetStatus": "Active",
                        },
                        {
                            "SubnetAvailabilityZone": {"Name": "us-east-1e"},
                            "SubnetIdentifier": "subnet-42sfl221",
                            "SubnetStatus": "Active",
                        },
                    ],
                    "VpcId": "vpc-v2dcp2jh",
                },
                "DbiResourceId": "db-YDFL2",
                "DeletionProtection": True,
                "Endpoint": {
                    "Address": "rds-name.us-east-1.rds.amazonaws.com",
                    "HostedZoneId": "202FGHSL2JKCFW",
                    "Port": 5521,
                },
                "Engine": "mariadb",
                "EngineVersion": "1.2",
                "InstanceCreateTime": datetime.datetime(
                    2019, 6, 17, 15, 15, 8, 461000, tzinfo=tzutc()
                ),
                "Iops": 1000,
                "MasterUsername": "root",
                "MultiAZ": True,
                "PreferredBackupWindow": "03:00-04:00",
                "PreferredMaintenanceWindow": "fri:04:00-fri:05:00",
                "PubliclyAccessible": False,
                "StorageEncrypted": True,
                "description": "This is in the description of the instance",
                "region": "us-east-1",
                "to_destroy": "tbd",
                "monitor": "true",
                "environment": "production",
                "VpcSecurityGroups": [
                    {"Status": "active", "VpcSecurityGroupId": "sg-f23le20g"}
                ],
            }
        }
        self.resource = aws.RDS(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_endpoint_property_works_as_expected(self):
        self.assertEqual(
            self.resource.endpoint, "rds-name.us-east-1.rds.amazonaws.com:5521",
        )

    def test_vpc_property_works_as_expected(self):
        self.assertEqual(self.resource.vpc, "vpc-v2dcp2jh")

    def test_engine_property_works_as_expected(self):
        self.assertEqual(self.resource.engine, "mariadb 1.2")

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("db-YDFL2"),
            call("  Name: resource_name"),
            call("  Endpoint: rds-name.us-east-1.rds.amazonaws.com:5521"),
            call("  Type: c4.4xlarge"),
            call("  Engine: mariadb 1.2"),
            call("  Description: This is in the description of the instance"),
            call("  SecurityGroups:"),
            call("    - sg-f2234gf6"),
            call("    - sg-f23le20g"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(9, len(self.print.mock_calls))

    def test_security_groups_property_gets_dbsecurity_groups(self):
        self.resource.raw["DBSecurityGroups"] = ["sg-yyyyyyyy"]
        self.resource.raw["VpcSecurityGroups"] = {}

        self.assertEqual(self.resource.security_groups, ["sg-yyyyyyyy"])

    def test_security_groups_property_gets_vpc_security_groups(self):
        self.resource.raw["DBSecurityGroups"] = []

        self.assertEqual(self.resource.security_groups, ["sg-f23le20g"])

    def test_search_uses_vpc(self):
        self.assertTrue(self.resource.search("vpc-v2d.*"))


class TestRoute53(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        self.module_name = "aws"
        super().setUp()

        self.id = "hosted_zone_id-record1.clinv.org-cname"
        self.raw = {
            "hosted_zone_id-record1.clinv.org-cname": {
                "Name": "record1.clinv.org",
                "ResourceRecords": [{"Value": "127.0.0.1"}, {"Value": "localhost"}],
                "TTL": 172800,
                "Type": "CNAME",
                "description": "This is the description",
                "to_destroy": "tbd",
                "state": "active",
                "monitor": "true",
                "hosted_zone": {
                    "id": "/hostedzone/hosted_zone_id",
                    "private": False,
                    "name": "hostedzone.org",
                },
            },
        }
        self.resource = aws.Route53(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_name_property_works_as_expected(self):
        """
        Override the parent test, as the name == id
        """

        self.assertEqual(self.resource.name, "record1.clinv.org")

    def test_search_resource_by_regexp_on_name(self):
        """
        Override the parent test, as the name == id
        """

        self.assertTrue(self.resource.search(".*record1"))

    def test_short_print_resource_information(self):
        """
        Override the parent test, as the name == id
        """

        self.resource.short_print()

        self.assertEqual(
            self.print.assert_called_with(self.resource.id), None,
        )

    def test_value_property_works_as_expected(self):
        self.assertEqual(self.resource.value, ["127.0.0.1", "localhost"])

    def test_value_property_supports_aliases(self):
        self.raw = {
            "record1.clinv.org": {
                "Name": "record1.clinv.org",
                "AliasTarget": {
                    "DNSName": "aliasdns.org",
                    "EvaluateTargetHealth": False,
                    "HostedZoneId": "XXXXXXXXXXXXXX",
                },
                "TTL": 172800,
                "Type": "A",
                "description": "This is the description",
                "to_destroy": "tbd",
                "state": "active",
                "hosted_zone": {
                    "id": "/hostedzone/hosted_zone_id",
                    "private": False,
                    "name": "hostedzone.org",
                },
            },
        }
        self.resource = aws.Route53(self.raw)
        self.assertEqual(self.resource.value, ["aliasdns.org"])

    def test_type_property_works_as_expected(self):
        self.assertEqual(self.resource.type, "CNAME")

    def test_to_destroy_property_works_as_expected(self):
        self.assertEqual(self.resource.to_destroy, "tbd")

    def test_hosted_zone_property_works_as_expected(self):
        self.assertEqual(self.resource.hosted_zone, "hostedzone.org")

    def test_hosted_zone_id_property_works_as_expected(self):
        self.assertEqual(
            self.resource.hosted_zone_id, "/hostedzone/hosted_zone_id",
        )

    def test_access_property_works_as_expected_if_public(self):
        self.assertEqual(self.resource.access, "public")

    def test_access_property_works_as_expected_if_private(self):
        self.resource.raw["hosted_zone"]["private"] = True
        self.assertEqual(self.resource.access, "private")

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("hosted_zone_id-record1.clinv.org-cname"),
            call("  Name: record1.clinv.org"),
            call("  Value:"),
            call("    127.0.0.1"),
            call("    localhost"),
            call("  Type: CNAME"),
            call("  Zone: /hostedzone/hosted_zone_id"),
            call("  Access: public"),
            call("  Description: This is the description"),
            call("  Destroy: tbd"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(10, len(self.print.mock_calls))

    def test_search_resource_by_regexp_on_value(self):
        self.assertTrue(self.resource.search(".*alhost"))

    def test_search_resource_by_type(self):
        self.assertTrue(self.resource.search("CNAME"))

    def test_search_resource_by_type_insensitive(self):
        self.assertTrue(self.resource.search("cname"))

    def test_monitor_property_works_as_expected_if_unset(self):
        self.resource.raw.pop("monitor")
        self.assertEqual(self.resource.monitor, "unknown")

    def test_monitor_property_works_as_expected_if_non_known_value(self):
        self.resource.raw["monitor"] = "tbd"
        self.assertEqual(self.resource.monitor, "unknown")

    def test_monitor_property_works_as_expected_if_set_to_true(self):
        self.resource.raw["monitor"] = True
        self.assertEqual(self.resource.monitor, True)

    def test_monitor_property_works_as_expected_if_set_to_false(self):
        self.resource.raw["monitor"] = False
        self.assertEqual(self.resource.monitor, False)


class TestS3(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        self.module_name = "aws"
        super().setUp()

        self.id = "s3_bucket_name"
        self.raw = {
            "s3_bucket_name": {
                "CreationDate": datetime.datetime(
                    2012, 12, 12, 0, 7, 46, tzinfo=tzutc()
                ),
                "Name": "resource_name",
                "permissions": {"READ": "public", "WRITE": "private"},
                "Grants": [
                    {
                        "Grantee": {
                            "DisplayName": "admin",
                            "ID": "admin_id",
                            "Type": "CanonicalUser",
                        },
                        "Permission": "READ",
                    },
                    {
                        "Grantee": {
                            "DisplayName": "admin",
                            "ID": "admin_id",
                            "Type": "CanonicalUser",
                        },
                        "Permission": "WRITE",
                    },
                    {
                        "Grantee": {
                            "Type": "Group",
                            "URI": "http://acs.amazonaws.com/groups/global/AllUsers",
                        },
                        "Permission": "READ",
                    },
                ],
                "description": "This is the description",
                "to_destroy": "tbd",
                "environment": "tbd",
                "desired_permissions": {"read": "tbd", "write": "tbd"},
                "state": "active",
            },
        }
        self.resource = aws.S3(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_to_destroy_property_works_as_expected(self):
        self.assertEqual(self.resource.to_destroy, "tbd")

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("s3_bucket_name"),
            call("  Description: This is the description"),
            call("  Permissions: desired/real"),
            call("      READ: tbd/public"),
            call("      WRITE: tbd/private"),
            call("  Environment: tbd"),
            call("  State: active"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(8, len(self.print.mock_calls))


class TestIAMGroup(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        self.module_name = "aws"
        super().setUp()

        self.id = "arn:aws:iam::XXXXXXXXXXXX:group/Administrator"
        self.raw = {
            "arn:aws:iam::XXXXXXXXXXXX:group/Administrator": {
                "CreateDate": datetime.datetime(
                    2019, 11, 4, 12, 41, 24, tzinfo=tzutc()
                ),
                "GroupId": "XXXXXXXXXXXXXXXXXXXXX",
                "GroupName": "resource_name",
                "Path": "/",
                "Users": ["arn:aws:iam::XXXXXXXXXXXX:user/user_1"],
                "InlinePolicies": ["Inlinepolicy"],
                "AttachedPolicies": ["arn:aws:iam::aws:policy/Attachedpolicy"],
                "description": "This is the description",
                "state": "active",
                "to_destroy": "tbd",
                "desired_users": ["arn:aws:iam::XXXXXXXXXXXX:user/user_2"],
            },
        }
        self.resource = aws.IAMGroup(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_users_property_works_as_expected(self):
        self.assertEqual(self.resource.users, ["arn:aws:iam::XXXXXXXXXXXX:user/user_1"])

    def test_desired_users_property_works_as_expected(self):
        self.assertEqual(
            self.resource.desired_users, ["arn:aws:iam::XXXXXXXXXXXX:user/user_2"]
        )

    def test_desired_inline_policies_property_works_as_expected(self):
        self.assertEqual(self.resource.inline_policies, ["Inlinepolicy"])

    def test_desired_attached_policies_property_works_as_expected(self):
        self.assertEqual(
            self.resource.attached_policies, ["arn:aws:iam::aws:policy/Attachedpolicy"]
        )

    def test_search_by_users_in_group(self):
        self.assertTrue(self.resource.search(".*user_1"))

    def test_search_by_desired_users_in_group(self):
        self.assertTrue(self.resource.search(".*user_2"))

    def test_search_by_inline_policies_in_group(self):
        self.assertTrue(self.resource.search(".*Inlinepolicy"))

    def test_search_by_attached_policies_in_group(self):
        self.assertTrue(self.resource.search(".*Attachedpolicy"))

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("arn:aws:iam::XXXXXXXXXXXX:group/Administrator"),
            call("  Name: resource_name"),
            call("  Description: This is the description"),
            call("  Users:"),
            call("    - arn:aws:iam::XXXXXXXXXXXX:user/user_1"),
            call("  AttachedPolicies:"),
            call("    - arn:aws:iam::aws:policy/Attachedpolicy"),
            call("  InlinePolicies:"),
            call("    - Inlinepolicy"),
            call("  State: active"),
            call("  Destroy: tbd"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(11, len(self.print.mock_calls))


class TestIAMUser(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        self.module_name = "aws"
        super().setUp()

        self.id = "arn:aws:iam::XXXXXXXXXXXX:user/user_1"
        self.raw = {
            "arn:aws:iam::XXXXXXXXXXXX:user/user_1": {
                "Path": "/",
                "CreateDate": datetime.datetime(2019, 2, 7, 12, 15, 57, tzinfo=tzutc()),
                "UserId": "XXXXXXXXXXXXXXXXXXXXX",
                "Arn": "arn:aws:iam::XXXXXXXXXXXX:user/user_1",
                "name": "resource_name",
                "description": "This is the description",
                "state": "active",
                "to_destroy": "tbd",
            },
        }
        self.resource = aws.IAMUser(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("arn:aws:iam::XXXXXXXXXXXX:user/user_1"),
            call("  Name: resource_name"),
            call("  Description: This is the description"),
            call("  State: active"),
            call("  Destroy: tbd"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(5, len(self.print.mock_calls))


class TestSecurityGroup(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        self.module_name = "aws"
        self.id = "sg-xxxxxxxx"

        super().setUp()

        self.raw = {
            "sg-xxxxxxxx": {
                "state": "active",
                "to_destroy": "tbd",
                "description": "This is the description",
                "GroupName": "resource_name",
                "region": "us-east-1",
                "IpPermissions": [
                    {
                        "FromPort": 0,
                        "IpProtocol": "udp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": 65535,
                        "UserIdGroupPairs": [],
                    },
                    {
                        "FromPort": -1,
                        "IpProtocol": "icmp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": -1,
                        "UserIdGroupPairs": [],
                    },
                    {
                        "FromPort": 0,
                        "IpProtocol": "tcp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": 65535,
                        "UserIdGroupPairs": [],
                    },
                ],
                "IpPermissionsEgress": [],
                "ingress": [
                    {
                        "FromPort": 0,
                        "IpProtocol": "udp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": 65535,
                        "UserIdGroupPairs": [],
                    },
                    {
                        "FromPort": -1,
                        "IpProtocol": "icmp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": -1,
                        "UserIdGroupPairs": [],
                    },
                    {
                        "FromPort": 0,
                        "IpProtocol": "tcp",
                        "IpRanges": [],
                        "Ipv6Ranges": [],
                        "PrefixListIds": [],
                        "ToPort": 65535,
                        "UserIdGroupPairs": [],
                    },
                ],
                "egress": [],
                "VpcId": "vpc-xxxxxxxxxxx",
            },
        }
        self.resource = aws.SecurityGroup(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_is_synchronized_returns_true_if_is_synchronized(self):
        self.assertTrue(self.resource.is_synchronized())

    def test_is_synchronized_returns_false_if_ingress_not_in_sync(self):
        self.resource.raw["ingress"].pop()
        self.assertFalse(self.resource.is_synchronized())

    def test_is_synchronized_returns_false_if_egress_not_in_sync(self):
        self.resource.raw["egress"] = self.resource.raw["ingress"]
        self.assertFalse(self.resource.is_synchronized())

    def test_print_security_rule_prints_tcp_with_range_of_ports(self):
        security_rule = {
            "FromPort": 0,
            "IpProtocol": "tcp",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "ToPort": 65535,
        }

        self.resource._print_security_rule(security_rule)

        self.assertEqual([call("    TCP: 0-65535")], self.print.mock_calls)

    def test_print_security_rule_prints_tcp_with_one_port(self):
        security_rule = {
            "FromPort": 443,
            "IpProtocol": "tcp",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "ToPort": 443,
        }

        self.resource._print_security_rule(security_rule)

        self.assertEqual([call("    TCP: 443")], self.print.mock_calls)

    def test_print_security_rule_prints_icmp_without_ip_range(self):
        security_rule = {
            "FromPort": -1,
            "IpProtocol": "icmp",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "ToPort": -1,
        }

        self.resource._print_security_rule(security_rule)

        self.assertEqual([call("    ICMP: ")], self.print.mock_calls)

    def test_print_security_rule_supports_all_traffic(self):
        security_rule = {
            "IpProtocol": "-1",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
        }

        self.resource._print_security_rule(security_rule)

        self.assertEqual([call("    All Traffic: ")], self.print.mock_calls)

    def test_print_security_rule_supports_ipranges(self):
        security_rule = {
            "IpProtocol": "tcp",
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "FromPort": 443,
            "ToPort": 443,
        }

        self.resource._print_security_rule(security_rule)

        self.assertEqual(
            [call("    TCP: 443"), call("      - 0.0.0.0/0")], self.print.mock_calls
        )

    def test_print_security_rule_supports_security_group_sources(self):
        security_rule = {
            "IpProtocol": "tcp",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "FromPort": 443,
            "ToPort": 443,
            "UserIdGroupPairs": [{"GroupId": "sg-yyyyyyyy", "UserId": "zzzzzzzzzzzz"}],
        }

        self.resource._print_security_rule(security_rule)

        self.assertEqual(
            [call("    TCP: 443"), call("      - sg-yyyyyyyy")], self.print.mock_calls
        )

    def test_print_security_rule_supports_sg_sources_with_description(self):
        security_rule = {
            "IpProtocol": "tcp",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "FromPort": 443,
            "ToPort": 443,
            "UserIdGroupPairs": [
                {
                    "GroupId": "sg-yyyyyyyy",
                    "UserId": "zzzzzzzzzzzz",
                    "Description": "sg description",
                }
            ],
        }

        self.resource._print_security_rule(security_rule)

        self.assertEqual(
            [call("    TCP: 443"), call("      - sg-yyyyyyyy: sg description")],
            self.print.mock_calls,
        )

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("sg-xxxxxxxx"),
            call("  Name: resource_name"),
            call("  Description: This is the description"),
            call("  State: active"),
            call("  Synchronized: True"),
            call("  Destroy: tbd"),
            call("  Region: us-east-1"),
            call("  VPC: vpc-xxxxxxxxxxx"),
            call("  Ingress:"),
            call("    UDP: 0-65535"),
            call("    ICMP: "),
            call("    TCP: 0-65535"),
            call("  Egress:"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(13, len(self.print.mock_calls))

    def test_is_related_identifies_source_cidrs(self):
        security_rule = {
            "IpProtocol": "tcp",
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "FromPort": 443,
            "ToPort": 443,
        }

        self.assertTrue(
            self.resource._is_security_rule_related("0.0.0.0.*", security_rule)
        )

    def test_is_related_identifies_source_ports(self):
        security_rule = {
            "IpProtocol": "tcp",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "FromPort": 443,
            "ToPort": 443,
        }

        self.assertTrue(self.resource._is_security_rule_related("443", security_rule))

    def test_is_related_identifies_source_range_of_ports(self):
        security_rule = {
            "IpProtocol": "tcp",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "FromPort": 441,
            "ToPort": 445,
        }

        self.assertTrue(self.resource._is_security_rule_related("443", security_rule))

    def test_is_related_identifies__security_group_sources(self):
        security_rule = {
            "IpProtocol": "tcp",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "FromPort": 443,
            "ToPort": 443,
            "UserIdGroupPairs": [{"GroupId": "sg-yyyyyyyy", "UserId": "zzzzzzzzzzzz"}],
        }

        self.assertTrue(
            self.resource._is_security_rule_related("sg-yyy.*", security_rule)
        )

    @patch("clinv.sources.aws.SecurityGroup._is_security_rule_related")
    def test_is_related_uses_is_related_security_group_on_ingress(
        self, relatedMock,
    ):

        security_rule = {
            "FromPort": 0,
            "IpProtocol": "udp",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "ToPort": 65535,
        }

        self.resource.raw["IpPermissions"] = [security_rule]
        self.resource.is_related(".*")
        self.assertEqual(
            relatedMock.assert_called_with(".*", security_rule), None,
        )

    @patch("clinv.sources.aws.SecurityGroup._is_security_rule_related")
    def test_is_related_uses_is_related_security_group_on_egress(
        self, relatedMock,
    ):

        security_rule = {
            "FromPort": 0,
            "IpProtocol": "udp",
            "IpRanges": [],
            "Ipv6Ranges": [],
            "PrefixListIds": [],
            "ToPort": 65535,
        }

        self.resource.raw["IpPermissions"] = []
        self.resource.raw["IpPermissionsEgress"] = [security_rule]
        self.resource.is_related(".*")
        self.assertEqual(
            relatedMock.assert_called_with(".*", security_rule), None,
        )

    @patch("clinv.sources.aws.SecurityGroup.is_related")
    def test_search_uses_is_related(self, relatedMock):

        self.resource.search("sg-yyyyyyyy")
        self.assertEqual(
            relatedMock.assert_called_with("sg-yyyyyyyy"), None,
        )

    def test_vpc_returns_expected_value(self):
        self.assertEqual(self.resource.vpc, self.resource.raw["VpcId"])

    def test_vpc_returns_none_if_no_vpc(self):
        self.resource.raw.pop("VpcId", None)
        self.assertEqual(self.resource.vpc, None)

    def test_search_uses_vpc(self):
        self.assertTrue(self.resource.search("vpc-xx.*"))

    def test_search_doesnt_fail_if_vpc_is_none(self):
        self.resource.raw.pop("VpcId", None)
        self.assertFalse(self.resource.search("vpc-xx.*"))


class TestVPC(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        self.module_name = "aws"
        self.id = "vpc-xxxxxxxxxxxx"

        super().setUp()

        self.raw = {
            "vpc-xxxxxxxxxxxx": {
                "CidrBlock": "172.16.0.0/16",
                "DhcpOptionsId": "dopt-xxxxxxxx",
                "InstanceTenancy": "default",
                "IsDefault": False,
                "region": "us-east-1",
                "State": "available",
                "Tags": [{"Key": "Name", "Value": "resource_name"}],
                "state": "active",
                "to_destroy": "tbd",
                "description": "This is the description",
            }
        }
        self.resource = aws.VPC(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_instance_name_return_null_if_empty(self):
        self.raw["vpc-xxxxxxxxxxxx"].pop("Tags", None)
        self.assertEqual(self.resource.name, "none")

    def test_cidr_returns_expected_value(self):
        self.assertEqual(self.resource.cidr, self.resource.raw["CidrBlock"])

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("vpc-xxxxxxxxxxxx"),
            call("  Name: resource_name"),
            call("  Description: This is the description"),
            call("  State: active"),
            call("  Destroy: tbd"),
            call("  Region: us-east-1"),
            call("  CIDR: 172.16.0.0/16"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(7, len(self.print.mock_calls))
