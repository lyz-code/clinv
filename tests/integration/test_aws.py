"""Test the AWS adapter."""

import re
from typing import Any, Dict

import pytest

from clinv.adapters.aws import AWSSource
from clinv.model import EntityUpdate, aws

from ..factories import EC2Factory


# W0613: all_aws is not being used. But it is, we need it to mock all the aws calls.
@pytest.mark.slow()
def test_update_asks_for_all_resources_by_default(all_aws: Any) -> None:  # noqa: W0613
    """
    Given: A working adapter
    When: adapter's update method is called without arguments
    Then: more than one type of resource is updated
    """
    result = AWSSource().update()

    models = {resource.model for resource in result}
    assert len(result) > 40
    assert len(models) > 1


@pytest.mark.slow()
def test_update_creates_ec2_instances_with_minimum_parameters(ec2: Any) -> None:
    """
    Given: A working adapter and an ec2 instance with the least possible information
        in "AWS"
    When: adapter's update method is called
    Then: the ec2 data is extracted from the source, in an EC2 compliant dictionary.
    """
    image_id = ec2.describe_images()["Images"][0]["ImageId"]
    instance = ec2.run_instances(ImageId=image_id, MinCount=1, MaxCount=1)["Instances"][
        0
    ]
    private_ip = instance["NetworkInterfaces"][0]["PrivateIpAddresses"][0][
        "PrivateIpAddress"
    ]
    public_ip = instance["NetworkInterfaces"][0]["PrivateIpAddresses"][0][
        "Association"
    ]["PublicIp"]
    entity_data: Dict[str, Any] = {
        "ami": instance["ImageId"],
        "id_": instance["InstanceId"],
        "model": aws.EC2,
        "private_ips": [private_ip],
        "public_ips": [public_ip],
        "region": "us-east-1",
        "security_groups": [],
        "size": instance["InstanceType"],
        "start_date": instance["LaunchTime"],
        "state": "active",
        "state_transition": "",
        "subnet": instance["SubnetId"],
        "vpc": instance["VpcId"],
    }

    result = AWSSource().update(["ec2"])

    assert result == [EntityUpdate(data=entity_data, model=aws.EC2)]
    assert aws.EC2(**entity_data).id_ == instance["InstanceId"]


@pytest.mark.slow()
def test_update_handles_no_ec2_in_zone(ec2: Any) -> None:
    """
    Given: A working adapter and an no ec2 instances in AWS
    When: adapter's update method is called
    Then: No data is returned, but no error either.
    """
    result = AWSSource().update(["ec2"])

    assert result == []


@pytest.mark.slow()
@pytest.mark.secondary()
def test_update_creates_ec2_instances_with_maximum_parameters(ec2: Any) -> None:
    """
    Given: A working adapter and an ec2 instance with the most possible information
        in "AWS"
    When: adapter's update method is called
    Then: the ec2 data is extracted from the source, in an EC2 compliant dictionary.
    """
    security_group_id = ec2.create_security_group(
        GroupName="TestSecurityGroup", Description="SG description"
    )["GroupId"]
    image_id = ec2.describe_images()["Images"][0]["ImageId"]
    instance = ec2.run_instances(
        ImageId=image_id,
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "instance name",
                    },
                    {
                        "Key": "monitor",
                        "Value": "True",
                    },
                ],
            }
        ],
    )["Instances"][0]
    private_ip = instance["NetworkInterfaces"][0]["PrivateIpAddresses"][0][
        "PrivateIpAddress"
    ]
    public_ip = instance["NetworkInterfaces"][0]["PrivateIpAddresses"][0][
        "Association"
    ]["PublicIp"]
    entity_data: Dict[str, Any] = {
        "ami": instance["ImageId"],
        "id_": instance["InstanceId"],
        "private_ips": [private_ip],
        "public_ips": [public_ip],
        "model": aws.EC2,
        "region": "us-east-1",
        "security_groups": [security_group_id],
        "size": instance["InstanceType"],
        "start_date": instance["LaunchTime"],
        "state": "active",
        "state_transition": "",
        "subnet": instance["SubnetId"],
        "vpc": instance["VpcId"],
        "name": "instance name",
        "monitor": True,
    }

    result = AWSSource().update(["ec2"])

    assert result == [EntityUpdate(data=entity_data, model=aws.EC2)]
    assert aws.EC2(**entity_data).id_ == instance["InstanceId"]


@pytest.mark.slow()
def test_update_creates_rds_instances_with_minimum_parameters(
    ec2: Any, rds: Any
) -> None:
    """
    Given: A working adapter and an rds instance with the most possible information
        in "AWS"
    When: adapter's update method is called
    Then: the rds data is extracted from the source, in an RDS compliant dictionary.
    """
    subnets = [subnet["SubnetId"] for subnet in ec2.describe_subnets()["Subnets"]]
    rds.create_db_subnet_group(
        DBSubnetGroupName="dbsg", SubnetIds=subnets, DBSubnetGroupDescription="Text"
    )
    instance = rds.create_db_instance(
        DBInstanceIdentifier="db-xxxx",
        DBInstanceClass="db.m3.2xlarge",
        Engine="postgres",
        DBSubnetGroupName="dbsg",
    )["DBInstance"]
    entity_data: Dict[str, Any] = {
        "id_": instance["DbiResourceId"],
        "model": aws.RDS,
        "name": "db-xxxx",
        "security_groups": [],
        "region": "us-east-1",
        "engine": f"{instance['Engine']} {instance['EngineVersion']}",
        "endpoint": (
            f"{instance['Endpoint']['Address']}:{instance['Endpoint']['Port']}"
        ),
        "size": instance["DBInstanceClass"],
        "start_date": instance["InstanceCreateTime"],
        "state": "active",
        "subnets": [
            subnet["SubnetIdentifier"]
            for subnet in instance["DBSubnetGroup"]["Subnets"]
        ],
        "vpc": instance["DBSubnetGroup"]["VpcId"],
    }

    result = AWSSource().update(["rds"])

    assert result == [EntityUpdate(data=entity_data, model=aws.RDS)]
    assert aws.RDS(**entity_data).id_ == instance["DbiResourceId"]


@pytest.mark.slow()
@pytest.mark.secondary()
def test_update_creates_rds_instances_with_maximum_parameters(
    ec2: Any, rds: Any
) -> None:
    """
    Given: A working adapter and an rds instance with the least possible information
        in "AWS"
    When: adapter's update method is called
    Then: the rds data is extracted from the source, in an RDS compliant dictionary.
    """
    subnets = [subnet["SubnetId"] for subnet in ec2.describe_subnets()["Subnets"]]
    rds.create_db_subnet_group(
        DBSubnetGroupName="dbsg", SubnetIds=subnets, DBSubnetGroupDescription="Text"
    )
    security_group_id = ec2.create_security_group(
        GroupName="TestSecurityGroup", Description="SG description"
    )["GroupId"]
    instance = rds.create_db_instance(
        DBInstanceIdentifier="db-xxxx",
        DBInstanceClass="db.m3.2xlarge",
        Engine="postgres",
        DBSubnetGroupName="dbsg",
        VpcSecurityGroupIds=[security_group_id],
        Tags=[{"Key": "monitor", "Value": "True"}],
    )["DBInstance"]
    entity_data: Dict[str, Any] = {
        "id_": instance["DbiResourceId"],
        "model": aws.RDS,
        "name": "db-xxxx",
        "monitor": True,
        "security_groups": [security_group_id],
        "region": "us-east-1",
        "engine": f"{instance['Engine']} {instance['EngineVersion']}",
        "endpoint": (
            f"{instance['Endpoint']['Address']}:{instance['Endpoint']['Port']}"
        ),
        "size": instance["DBInstanceClass"],
        "start_date": instance["InstanceCreateTime"],
        "state": "active",
        "subnets": [
            subnet["SubnetIdentifier"]
            for subnet in instance["DBSubnetGroup"]["Subnets"]
        ],
        "vpc": instance["DBSubnetGroup"]["VpcId"],
    }

    result = AWSSource().update(["rds"])

    assert result == [EntityUpdate(data=entity_data, model=aws.RDS)]
    assert aws.RDS(**entity_data).id_ == instance["DbiResourceId"]


def test_update_creates_s3_instances(s3_mock: Any) -> None:
    """
    Given: A working adapter and an s3 bucket with private permissions
    When: adapter's update method is called
    Then: the s3 data is extracted from the source, in an S3 compliant dictionary.
    """
    s3_mock.create_bucket(Bucket="mybucket")
    instance = s3_mock.list_buckets()["Buckets"][0]
    entity_data: Dict[str, Any] = {
        "id_": f"s3-{instance['Name']}",
        "model": aws.S3,
        "name": instance["Name"],
        "start_date": instance["CreationDate"],
        "state": "active",
        "public_read": False,
        "public_write": False,
    }

    result = AWSSource().update(["s3"])

    assert result == [EntityUpdate(data=entity_data, model=aws.S3)]
    assert aws.S3(**entity_data).id_ == entity_data["id_"]


@pytest.mark.skip(
    """
    The S3 interface has changed and now it doesn't return a list of objects but a
    list of strings, moto hasn't yet updated their interface, so the tests fail.

    So we need to skip this until they do.
    """
)
@pytest.mark.secondary()
def test_update_detects_s3_buckets_with_public_permissions(s3_mock: Any) -> None:
    """
    Given: A working adapter and an s3 bucket with public permissions
    When: adapter's update method is called
    Then: the s3 data is extracted from the source, in an S3 compliant dictionary.
        And the permissions are captured.
    """
    s3_mock.create_bucket(Bucket="mybucket", ACL="public-read-write")
    instance = s3_mock.list_buckets()["Buckets"][0]
    entity_data: Dict[str, Any] = {
        "id_": f"s3-{instance['Name']}",
        "model": aws.S3,
        "name": instance["Name"],
        "start_date": instance["CreationDate"],
        "state": "active",
        "public_read": True,
        "public_write": True,
    }

    result = AWSSource().update(["s3"])

    assert result == [EntityUpdate(data=entity_data, model=aws.S3)]
    assert aws.S3(**entity_data).id_ == entity_data["id_"]


def test_update_creates_route53_instances(route53: Any) -> None:
    """
    Given: A working adapter and a route53 record
    When: adapter's update method is called
    Then: the route53 data is extracted from the source, in an Route53 compliant
        dictionary.
    """
    hosted_zone = route53.create_hosted_zone(
        Name="example.com", CallerReference="Test"
    )["HostedZone"]
    hosted_zone_id = re.sub(".hostedzone.", "", hosted_zone["Id"])
    route53.change_resource_record_sets(
        ChangeBatch={
            "Changes": [
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": "example.com",
                        "ResourceRecords": [
                            {
                                "Value": "192.0.2.44",
                            },
                        ],
                        "TTL": 60,
                        "Type": "A",
                    },
                },
            ],
            "Comment": "Web server for example.com",
        },
        HostedZoneId=hosted_zone_id,
    )
    entity_data: Dict[str, Any] = {
        "id_": f"{hosted_zone_id}-example.com-a",
        "model": aws.Route53,
        "name": "example.com",
        "state": "active",
        "hosted_zone": hosted_zone_id,
        "values": ["192.0.2.44"],
        "type_": "A",
        "public": True,
    }

    result = AWSSource().update(["r53"])

    assert EntityUpdate(data=entity_data, model=aws.Route53) in result
    assert aws.Route53(**entity_data).id_ == entity_data["id_"]


@pytest.mark.skip("Until https://github.com/spulec/moto/issues/3879 is solved.")
def test_update_creates_route53_instances_when_there_are_a_lot(route53: Any) -> None:
    """
    Given: A working adapter and many route53 record
    When: adapter's update method is called
    Then: the route53 data is extracted from the source even though it will need
        to use the paginator, in an Route53 compliant dictionary.
    """
    hosted_zone = route53.create_hosted_zone(
        Name="example.com", CallerReference="Test"
    )["HostedZone"]
    hosted_zone_id = re.sub(".hostedzone.", "", hosted_zone["Id"])
    for counter in range(0, 400):
        route53.change_resource_record_sets(
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "CREATE",
                        "ResourceRecordSet": {
                            "Name": "example.com",
                            "ResourceRecords": [
                                {
                                    "Value": f"192.0.2.{counter}",
                                },
                            ],
                            "TTL": 60,
                            "Type": "A",
                        },
                    },
                ],
                "Comment": "Web server for example.com",
            },
            HostedZoneId=hosted_zone_id,
        )

    result = AWSSource().update(["r53"])

    assert len(result) == 256


@pytest.mark.secondary()
@pytest.mark.secondary()
def test_update_creates_route53_private_instances(route53: Any) -> None:
    """
    Given: A working adapter and a route53 record in a private hosted zone
    When: adapter's update method is called
    Then: the route53 data is extracted from the source, in an Route53 compliant
        dictionary.
    """
    hosted_zone = route53.create_hosted_zone(
        Name="example.com",
        CallerReference="Test",
        HostedZoneConfig={"PrivateZone": True, "Comment": "Comment"},
    )["HostedZone"]
    hosted_zone_id = re.sub(".hostedzone.", "", hosted_zone["Id"])
    route53.change_resource_record_sets(
        ChangeBatch={
            "Changes": [
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": "example.com",
                        "ResourceRecords": [
                            {
                                "Value": "192.0.2.44",
                            },
                        ],
                        "TTL": 60,
                        "Type": "A",
                    },
                },
            ],
            "Comment": "Web server for example.com",
        },
        HostedZoneId=hosted_zone_id,
    )
    entity_data: Dict[str, Any] = {
        "id_": f"{hosted_zone_id}-example.com-a",
        "model": aws.Route53,
        "name": "example.com",
        "state": "active",
        "hosted_zone": hosted_zone_id,
        "values": ["192.0.2.44"],
        "type_": "A",
        "public": False,
    }

    result = AWSSource().update(["r53"])

    assert EntityUpdate(data=entity_data, model=aws.Route53) in result
    assert aws.Route53(**entity_data).id_ == entity_data["id_"]


@pytest.mark.secondary()
def test_update_creates_route53_alias_instances(route53: Any) -> None:
    """
    Given: A working adapter and a route53 alias record
    When: adapter's update method is called
    Then: the route53 data is extracted from the source, in an Route53 compliant
        dictionary.
    """
    hosted_zone = route53.create_hosted_zone(
        Name="example.com", CallerReference="Test"
    )["HostedZone"]
    hosted_zone_id = re.sub(".hostedzone.", "", hosted_zone["Id"])
    route53.change_resource_record_sets(
        ChangeBatch={
            "Changes": [
                {
                    "Action": "CREATE",
                    "ResourceRecordSet": {
                        "Name": "example.com",
                        "AliasTarget": {
                            "HostedZoneId": hosted_zone_id,
                            "DNSName": "example2.com",
                            "EvaluateTargetHealth": False,
                        },
                        "TTL": 60,
                        "Type": "A",
                    },
                },
            ],
            "Comment": "Web server for example.com",
        },
        HostedZoneId=hosted_zone_id,
    )
    entity_data: Dict[str, Any] = {
        "id_": f"{hosted_zone_id}-example.com-a",
        "model": aws.Route53,
        "name": "example.com",
        "state": "active",
        "hosted_zone": hosted_zone_id,
        "values": ["example2.com"],
        "type_": "A",
        "public": True,
    }

    result = AWSSource().update(["r53"])

    assert EntityUpdate(data=entity_data, model=aws.Route53) in result
    assert aws.Route53(**entity_data).id_ == entity_data["id_"]


def test_update_creates_vpc_instances(ec2: Any) -> None:
    """
    Given: A working adapter and a vpc resource.
    When: adapter's update method is called
    Then: the vpc data is extracted from the source, in an VPC compliant
        dictionary.
    """
    instance = ec2.create_vpc(
        CidrBlock="172.16.0.0/16",
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": "instance name",
                    },
                ],
            }
        ],
    )["Vpc"]
    entity_data: Dict[str, Any] = {
        "id_": instance["VpcId"],
        "model": aws.VPC,
        "state": "active",
        "name": "instance name",
        "region": "us-east-1",
        "subnets": [],
        "cidr": "172.16.0.0/16",
    }

    result = AWSSource().update(["vpc"])

    assert EntityUpdate(data=entity_data, model=aws.VPC) in result
    assert aws.VPC(**entity_data).id_ == entity_data["id_"]


@pytest.mark.slow()
def test_update_creates_autoscaling_groups(ec2: Any, autoscaling: Any) -> None:
    """
    Given: A working adapter and an autoscaling group.
    When: adapter's update method is called
    Then: the autoscaling group data is extracted from the source, in an ASG compliant
        dictionary.
    """
    image_id = ec2.describe_images()["Images"][0]["ImageId"]
    autoscaling.create_launch_configuration(
        LaunchConfigurationName="LaunchConfiguration",
        ImageId=image_id,
        InstanceType="t2.medium",
    )
    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName="test-production",
        MinSize=1,
        MaxSize=3,
        LaunchConfigurationName="LaunchConfiguration",
        AvailabilityZones=["us-east-1a"],
    )
    instance = autoscaling.describe_auto_scaling_groups()["AutoScalingGroups"][0]
    entity_data: Dict[str, Any] = {
        "id_": "asg-test-production",
        "model": aws.ASG,
        "name": "test-production",
        "state": "active",
        "region": "us-east-1",
        "launch_configuration": "LaunchConfiguration",
        "min_size": 1,
        "max_size": 3,
        "desired_size": 1,
        "availability_zones": ["us-east-1a"],
        "healthcheck": "EC2",
        "instances": [
            ec2_instance["InstanceId"] for ec2_instance in instance["Instances"]
        ],
    }

    result = AWSSource().update(["asg"])

    assert EntityUpdate(data=entity_data, model=aws.ASG) in result
    assert aws.ASG(**entity_data).id_ == entity_data["id_"]


@pytest.mark.slow()
def test_update_creates_empty_security_groups(ec2: Any) -> None:
    """
    Given: A working adapter and an empty security group resource.
    When: adapter's update method is called
    Then: the security group data is extracted from the source, in an SecurityGroup
        compliant dictionary.
    """
    instance_id = ec2.create_security_group(
        GroupName="TestSecurityGroup", Description="SG description"
    )["GroupId"]
    ec2.revoke_security_group_egress(
        GroupId=instance_id,
        IpPermissions=[
            {"IpProtocol": "-1", "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
        ],
    )
    entity_data: Dict[str, Any] = {
        "id_": instance_id,
        "model": aws.SecurityGroup,
        "name": "TestSecurityGroup",
        "description": "SG description",
        "state": "active",
        "region": "us-east-1",
        "egress": [],
        "ingress": [],
    }

    result = AWSSource().update(["sg"])

    assert EntityUpdate(data=entity_data, model=aws.SecurityGroup) in result
    assert aws.SecurityGroup(**entity_data).id_ == entity_data["id_"]


@pytest.mark.slow()
def test_update_creates_security_groups_with_egress_and_ingress_rules(ec2: Any) -> None:
    """
    Given: A working adapter and an security group resource with egress and ingress
        rules.
    When: adapter's update method is called
    Then: the security group data is extracted from the source, in an SecurityGroup
        compliant dictionary.
    """
    instance_id = ec2.create_security_group(
        GroupName="TestSecurityGroup", Description="SG description"
    )["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=instance_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 80,
                "ToPort": 81,
                "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "Authorize HTTP"}],
            },
        ],
    )
    entity_data: Dict[str, Any] = {
        "id_": instance_id,
        "model": aws.SecurityGroup,
        "state": "active",
        "name": "TestSecurityGroup",
        "description": "SG description",
        "region": "us-east-1",
        "egress": [
            {
                "protocol": "TCP & UDP & ICMP",
                "ports": [-1],
                "ip_range": ["0.0.0.0/0"],
                "ipv6_range": [],
                "sg_range": [],
            },
        ],
        "ingress": [
            {
                "protocol": "TCP",
                "ports": [80, 81],
                "ip_range": ["0.0.0.0/0"],
                "ipv6_range": [],
                "sg_range": [],
                "description": "Authorize HTTP",
            },
        ],
    }

    result = AWSSource().update(["sg"])

    assert EntityUpdate(data=entity_data, model=aws.SecurityGroup) in result
    assert aws.SecurityGroup(**entity_data).id_ == entity_data["id_"]


def test_update_creates_iam_users(iam: Any) -> None:
    """
    Given: A working adapter and an IAM user
    When: update is called
    Then: the user data is returned in an IAMUser compatible dictionary.
    """
    instance = iam.create_user(UserName="User")["User"]
    entity_data: Dict[str, Any] = {
        "id_": f'iamu-{instance["UserName"].lower()}',
        "model": aws.IAMUser,
        "state": "active",
        "name": instance["UserName"],
        "arn": instance["Arn"],
    }

    result = AWSSource().update(["iamu"])

    assert EntityUpdate(data=entity_data, model=aws.IAMUser) in result
    assert aws.IAMUser(**entity_data).id_ == entity_data["id_"]


def test_update_creates_iam_groups(iam: Any) -> None:
    """
    Given: A working adapter, an IAM group and an IAM user belonging to that group.
    When: update is called
    Then: the group data is returned in an IAMGroup compatible dictionary.
    """
    user = iam.create_user(UserName="User")["User"]
    instance = iam.create_group(GroupName="UserGroup")["Group"]
    iam.add_user_to_group(GroupName=instance["GroupName"], UserName=user["UserName"])
    desired_users = [f'iamu-{user["UserName"].lower()}']
    entity_data: Dict[str, Any] = {
        "id_": "iamg-usergroup",
        "model": aws.IAMGroup,
        "state": "active",
        "name": "UserGroup",
        "arn": instance["Arn"],
        "users": desired_users,
    }

    result = AWSSource().update(["iamg"])

    assert EntityUpdate(data=entity_data, model=aws.IAMGroup) in result
    assert aws.IAMGroup(**entity_data).id_ == entity_data["id_"]


def test_update_marks_aws_resources_as_terminated_if_they_dont_appear(ec2: Any) -> None:
    """
    Given: A repository with an aws resource with state active
    When: update_sources doesn't contain data of that entity
    Then: the entity is marked as terminated
    """
    entity = EC2Factory.build(state="active")

    result = AWSSource().update(["ec2"], [entity])

    assert len(result) == 1
    assert result[0].id_ == entity.id_
    assert result[0].data["state"] == "terminated"


def test_update_doesnt_marks_unprocessed_resources_as_terminated(
    rds: Any, ec2: Any
) -> None:
    """
    Given: A repository with an EC2 resource with state active
    When: update_sources doesn't contain data of that entity, but it wasn't processed
    Then: the entity is not marked as terminated
    """
    entity = EC2Factory.build(state="active")

    result = AWSSource().update(["rds"], [entity])

    assert len(result) == 0
