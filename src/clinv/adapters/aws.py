"""Define the AWS sources used by Clinv."""

import logging
import re
from contextlib import suppress
from typing import Any, Dict, List, Optional, Type

import boto3
from botocore.client import Config
from botocore.exceptions import (
    ClientError,
    ConnectTimeoutError,
    EndpointConnectionError,
)
from rich.progress import track

from ..model import RESOURCE_TYPES, aws
from ..model.entity import EntityAttrs, EntityState, EntityT, EntityUpdate
from .abstract import AbstractSource

log = logging.getLogger(__name__)

config = Config(connect_timeout=3, retries={"max_attempts": 0})


class AWSSource(AbstractSource):
    """Define the interface to interact with the source of AWS entities."""

    @property
    def regions(self) -> List[str]:
        """Get the AWS regions.

        Returns:
            list: AWS Regions.
        """
        ec2 = boto3.client("ec2", region_name="us-east-1", config=config)
        return [region["RegionName"] for region in ec2.describe_regions()["Regions"]]

    def update(
        self,
        resource_types: Optional[List[str]] = None,
        active_resources: Optional[List[EntityT]] = None,
    ) -> List[EntityUpdate]:
        """Get the latest state of the source entities.

        Args:
            resource_types: Limit the update to these type of resources.
            active_resources: List of active resources in the repository.

        Returns:
            List of entity updates.
        """
        log.info("Updating AWS entities.")

        update_mapper = {
            "asg": self._update_asg,
            "ec2": self._update_ec2,
            "iamg": self._update_iam_groups,
            "iamu": self._update_iam_users,
            "s3": self._update_s3,
            "sg": self._update_sg,
            "rds": self._update_rds,
            "r53": self._update_route53,
            "vpc": self._update_vpc,
        }
        if resource_types is None:
            resource_types = list(update_mapper.keys())
        else:
            # Only process the AWS resources
            resource_types = [
                resource_type
                for resource_type in resource_types
                if resource_type in update_mapper
            ]

        entity_updates = []
        if active_resources is None:
            remaining_entities = []
        else:
            remaining_entities = active_resources

        # Create entity updates
        for resource_type in track(resource_types, description="Get AWS data"):
            with suppress(KeyError):
                entity_updates += update_mapper[resource_type](remaining_entities)

        # Mark entities that were no present in the updates as terminated
        resource_models = [
            RESOURCE_TYPES[resource_type] for resource_type in resource_types
        ]
        for entity in remaining_entities:
            if type(entity) in resource_models:
                log.info(
                    f"Marking '{entity.model_name}' with id '{entity.id_}' and name "
                    f"'{entity.name}' as terminated"
                )
                entity.state = EntityState.TERMINATED
                entity_updates.append(
                    EntityUpdate(model=type(entity), data=entity.dict())
                )

        return entity_updates

    def _update_ec2(self, remaining_entities: List[EntityT]) -> List[EntityUpdate]:
        """Fetch the data of the EC2 instances.

        Args:
            remaining_entities: entities that haven't yet been processed by the update

        Returns:
            List of entity updates.
        """
        log.info("Updating EC2 instances.")
        entity_updates = []
        entity_data: EntityAttrs = {}

        for region in self.regions:
            ec2 = boto3.client("ec2", region_name=region, config=config)
            region_data = ec2.describe_instances()["Reservations"]
            for instance in region_data:
                instance = instance["Instances"][0]
                entity_data = {
                    "ami": instance["ImageId"],
                    "id_": instance["InstanceId"],
                    "region": region,
                    "size": instance["InstanceType"],
                    "start_date": instance["LaunchTime"],
                    "state": instance["State"]["Name"],
                }

                # Correct the state
                if entity_data["state"] == "running":
                    entity_data["state"] = "active"

                # Get the instance name and monitor status
                with suppress(KeyError):
                    for tag in instance["Tags"]:
                        if tag["Key"] == "Name":
                            entity_data["name"] = tag["Value"]
                        elif tag["Key"] == "monitor":
                            entity_data["monitor"] = bool(tag["Value"])

                # Get the security groups
                with suppress(KeyError):
                    entity_data["security_groups"] = [
                        security_group["GroupId"]
                        for security_group in instance["SecurityGroups"]
                    ]

                # Get the instance network information
                with suppress(KeyError):
                    entity_data["vpc"] = instance["VpcId"]
                    entity_data["subnet"] = instance["SubnetId"]

                # Get the private ips
                with suppress(KeyError):
                    entity_data["private_ips"] = []
                    for interface in instance["NetworkInterfaces"]:
                        for address in interface["PrivateIpAddresses"]:
                            entity_data["private_ips"].append(
                                address["PrivateIpAddress"]
                            )

                # Get the public ips
                with suppress(KeyError):
                    entity_data["public_ips"] = []
                    for interface in instance["NetworkInterfaces"]:
                        for association in interface["PrivateIpAddresses"]:
                            entity_data["public_ips"].append(
                                association["Association"]["PublicIp"]
                            )

                # Get the state transition
                with suppress(KeyError):
                    entity_data["state_transition"] = instance["StateTransitionReason"]

                # ignore: I don't know why it's not able to infer the type of the
                # argument 1 of _build_entity_update ¯\(°_o)/¯
                entity_updates.append(
                    _build_entity_update(  # type: ignore
                        entity_data, aws.EC2, remaining_entities
                    )
                )
        return entity_updates

    def _update_rds(self, remaining_entities: List[EntityT]) -> List[EntityUpdate]:
        """Fetch the data of the RDS instances.

        Args:
            remaining_entities: entities that haven't yet been processed by the update

        Returns:
            List of entity updates.
        """
        log.info("Updating RDS instances.")
        entity_updates = []

        for region in self.regions:
            rds = boto3.client("rds", region_name=region, config=config)
            try:
                region_data = rds.describe_db_instances()["DBInstances"]
            except (ClientError, ConnectTimeoutError, EndpointConnectionError):
                log.debug(f"Error fetching the RDS info from {region}")
            for instance in region_data:
                endpoint = (
                    f"{instance['Endpoint']['Address']}:{instance['Endpoint']['Port']}"
                )
                entity_data = {
                    "id_": instance["DbiResourceId"],
                    "region": region,
                    "engine": f"{instance['Engine']} {instance['EngineVersion']}",
                    "endpoint": endpoint,
                    "size": instance["DBInstanceClass"],
                    "start_date": instance["InstanceCreateTime"],
                    "subnets": [
                        subnet["SubnetIdentifier"]
                        for subnet in instance["DBSubnetGroup"]["Subnets"]
                    ],
                    "vpc": instance["DBSubnetGroup"]["VpcId"],
                }

                # Get the instance name
                with suppress(KeyError):
                    entity_data["name"] = instance["DBInstanceIdentifier"]

                # Get the instance state
                with suppress(KeyError):
                    state = instance["DBInstanceStatus"]
                    if state == "available":
                        state = "active"
                    entity_data["state"] = state

                # Get the security groups
                with suppress(KeyError):
                    entity_data["security_groups"] = [
                        security_group["VpcSecurityGroupId"]
                        for security_group in instance["VpcSecurityGroups"]
                    ]

                # Get the monitor status
                with suppress(KeyError):
                    for tag in instance["TagList"]:
                        if tag["Key"] == "monitor":
                            entity_data["monitor"] = bool(tag["Value"])

                # ignore: I don't know why it's not able to infer the type of the
                # argument 1 of _build_entity_update ¯\(°_o)/¯
                entity_updates.append(
                    _build_entity_update(  # type: ignore
                        entity_data, aws.RDS, remaining_entities
                    )
                )
        return entity_updates

    @classmethod
    def _update_s3(cls, remaining_entities: List[EntityT]) -> List[EntityUpdate]:
        """Fetch the data of the S3 buckets.

        Args:
            remaining_entities: entities that haven't yet been processed by the update

        Returns:
            List of entity updates.
        """
        log.info("Updating S3 instances.")

        entity_updates = []

        # Create S3 client, describe buckets.
        s3_client = boto3.client("s3", config=config)
        buckets = s3_client.list_buckets()["Buckets"]

        for instance in buckets:
            entity_data = {
                "id_": f"s3-{instance['Name']}",
                "name": instance["Name"],
                "start_date": instance["CreationDate"],
                "state": "active",
                "public_read": False,
                "public_write": False,
            }

            # Check if there is any public access to the bucket
            for grant in s3_client.get_bucket_acl(Bucket=instance["Name"])["Grants"]:
                with suppress(KeyError):
                    if (
                        grant["Grantee"]["URI"]
                        == "http://acs.amazonaws.com/groups/global/AllUsers"
                    ):
                        permissions = grant["Permission"]
                        if isinstance(permissions, str):
                            permissions = [permissions]
                        for permission in permissions:
                            if permission == "READ":
                                entity_data["public_read"] = True
                            elif permission == "WRITE":
                                entity_data["public_write"] = True
                            elif permission == "READ_ACP":
                                entity_data["public_read"] = False
                            elif permission == "WRITE_ACP":
                                entity_data["public_write"] = False

            # ignore: I don't know why it's not able to infer the type of the
            # argument 1 of _build_entity_update ¯\(°_o)/¯
            entity_updates.append(
                _build_entity_update(  # type: ignore
                    entity_data, aws.S3, remaining_entities
                )
            )

        return entity_updates

    @classmethod
    def _update_route53(cls, remaining_entities: List[EntityT]) -> List[EntityUpdate]:
        """Fetch the data of the Route53 records.

        Args:
            remaining_entities: entities that haven't yet been processed by the update

        Returns:
            List of entity updates.
        """
        log.info("Updating Route53 records.")

        entity_updates = []

        route53 = boto3.client("route53", config=config)
        hosted_zones = route53.list_hosted_zones()["HostedZones"]

        for hosted_zone in hosted_zones:
            records = route53.list_resource_record_sets(
                HostedZoneId=hosted_zone["Id"],
            )

            instances = records["ResourceRecordSets"]

            # We can't test it until https://github.com/spulec/moto/issues/3879 is
            # solved. The test is done but it's skipped
            while records["IsTruncated"]:
                records = route53.list_resource_record_sets(
                    HostedZoneId=hosted_zone["Id"],
                    StartRecordName=records["NextRecordName"],
                    StartRecordType=records["NextRecordType"],
                )
                instances += records["ResourceRecordSets"]

            for instance in instances:
                hosted_zone_id = re.sub(r"/hostedzone/", "", hosted_zone["Id"])
                name = re.sub(r"\.$", "", instance["Name"])
                entity_data = {
                    "id_": f"{hosted_zone_id}-{name}-{instance['Type'].lower()}",
                    "hosted_zone": hosted_zone_id,
                    "name": name,
                    "type_": instance["Type"],
                    "state": "active",
                    "public": not hosted_zone["Config"]["PrivateZone"],
                }

                try:
                    entity_data["values"] = [
                        record["Value"] for record in instance["ResourceRecords"]
                    ]
                except KeyError:
                    entity_data["values"] = [instance["AliasTarget"]["DNSName"]]

                # ignore: I don't know why it's not able to infer the type of the
                # argument 1 of _build_entity_update ¯\(°_o)/¯
                entity_updates.append(
                    _build_entity_update(  # type: ignore
                        entity_data, aws.Route53, remaining_entities
                    )
                )
        return entity_updates

    def _update_vpc(self, remaining_entities: List[EntityT]) -> List[EntityUpdate]:
        """Fetch the data of the VPC resources.

        Args:
            remaining_entities: entities that haven't yet been processed by the update

        Returns:
            List of entity updates.
        """
        log.info("Updating VPCs.")

        entity_updates = []

        for region in self.regions:
            ec2 = boto3.client("ec2", region_name=region, config=config)
            for instance in ec2.describe_vpcs()["Vpcs"]:
                entity_data = {
                    "id_": instance["VpcId"],
                    "region": region,
                    "state": "active",
                    "cidr": instance["CidrBlock"],
                }

                # Get the instance name
                with suppress(KeyError):
                    for tag in instance["Tags"]:
                        if tag["Key"] == "Name":
                            entity_data["name"] = tag["Value"]

                # Get the subnets
                subnets = ec2.describe_subnets(
                    Filters=[
                        {
                            "Name": "vpc-id",
                            "Values": [
                                entity_data["id_"],
                            ],
                        },
                    ],
                )["Subnets"]
                entity_data["subnets"] = [subnet["SubnetId"] for subnet in subnets]

                # ignore: I don't know why it's not able to infer the type of the
                # argument 1 of _build_entity_update ¯\(°_o)/¯
                entity_updates.append(
                    _build_entity_update(  # type: ignore
                        entity_data, aws.VPC, remaining_entities
                    )
                )
        return entity_updates

    def _update_asg(self, remaining_entities: List[EntityT]) -> List[EntityUpdate]:
        """Fetch the data of the ASG resources.

        Args:
            remaining_entities: entities that haven't yet been processed by the update

        Returns:
            List of entity updates.
        """
        log.info("Updating Auto Scaling Groups.")

        entity_updates = []

        for region in self.regions:
            autoscaling = boto3.client("autoscaling", region_name=region, config=config)
            try:
                instances = autoscaling.describe_auto_scaling_groups()[
                    "AutoScalingGroups"
                ]
            except (ClientError, ConnectTimeoutError, EndpointConnectionError):
                log.debug(f"Error fetching the ASG info from {region}")
            for instance in instances:
                entity_data = {
                    "id_": f"asg-{instance['AutoScalingGroupName']}",
                    "name": instance["AutoScalingGroupName"],
                    "region": region,
                    "state": "active",
                    "min_size": instance["MinSize"],
                    "max_size": instance["MaxSize"],
                    "desired_size": instance["DesiredCapacity"],
                    "availability_zones": instance["AvailabilityZones"],
                    "healthcheck": instance["HealthCheckType"],
                    "instances": [
                        ec2_instance["InstanceId"]
                        for ec2_instance in instance["Instances"]
                    ],
                }

                # Get the instance name
                with suppress(KeyError):
                    entity_data["launch_configuration"] = instance[
                        "LaunchConfigurationName"
                    ]

                # Won't test it until they are supported by moto
                # https://github.com/spulec/moto/issues/2003
                with suppress(KeyError):
                    entity_data["launch_template"] = (
                        f'{instance["LaunchTemplate"]["LaunchTemplateName"][:35]}'
                        f':{instance["LaunchTemplate"]["Version"]}'
                    )

                # ignore: I don't know why it's not able to infer the type of the
                # argument 1 of _build_entity_update ¯\(°_o)/¯
                entity_updates.append(
                    _build_entity_update(  # type: ignore
                        entity_data, aws.ASG, remaining_entities
                    )
                )

        return entity_updates

    def _update_sg(self, remaining_entities: List[EntityT]) -> List[EntityUpdate]:
        """Fetch the data of the Security Group resources.

        Args:
            remaining_entities: entities that haven't yet been processed by the update

        Returns:
            List of entity updates.
        """
        log.info("Updating Security Groups.")

        entity_updates = []

        for region in self.regions:
            ec2 = boto3.client("ec2", region_name=region, config=config)
            instances = ec2.describe_security_groups()["SecurityGroups"]
            for instance in instances:
                entity_data = {
                    "id_": instance["GroupId"],
                    "name": instance["GroupName"],
                    "description": instance["Description"],
                    "region": region,
                    "state": "active",
                    "egress": [],
                    "ingress": [],
                }

                for egress_rule in instance["IpPermissionsEgress"]:
                    entity_data["egress"].append(
                        build_security_group_rule_data(egress_rule)
                    )

                for ingress_rule in instance["IpPermissions"]:
                    entity_data["ingress"].append(
                        build_security_group_rule_data(ingress_rule)
                    )

                # ignore: I don't know why it's not able to infer the type of the
                # argument 1 of _build_entity_update ¯\(°_o)/¯
                entity_updates.append(
                    _build_entity_update(  # type: ignore
                        entity_data, aws.SecurityGroup, remaining_entities
                    )
                )
        return entity_updates

    @classmethod
    def _update_iam_users(cls, remaining_entities: List[EntityT]) -> List[EntityUpdate]:
        """Fetch the data of the IAM users.

        Args:
            remaining_entities: entities that haven't yet been processed by the update

        Returns:
            List of entity updates.
        """
        log.info("Updating IAM Users.")

        entity_updates = []

        iam = boto3.client("iam", config=config)

        user_instances = iam.list_users()["Users"]
        for instance in user_instances:
            entity_data = {
                "id_": f'iamu-{instance["UserName"].lower()}',
                "name": instance["UserName"],
                "arn": instance["Arn"],
                "state": "active",
            }

            # ignore: I don't know why it's not able to infer the type of the
            # argument 1 of _build_entity_update ¯\(°_o)/¯
            entity_updates.append(
                _build_entity_update(  # type: ignore
                    entity_data, aws.IAMUser, remaining_entities
                )
            )
        return entity_updates

    @classmethod
    def _update_iam_groups(
        cls, remaining_entities: List[EntityT]
    ) -> List[EntityUpdate]:
        """Fetch the data of the IAM groups.

        Args:
            remaining_entities: entities that haven't yet been processed by the update

        Returns:
            List of entity updates.
        """
        log.info("Updating IAM Groups.")

        entity_updates = []

        iam = boto3.client("iam", config=config)

        group_instances = iam.list_groups()["Groups"]
        for instance in group_instances:
            group_data = iam.get_group(GroupName=instance["GroupName"])
            users = [f'iamu-{user["UserName"].lower()}' for user in group_data["Users"]]
            entity_data: EntityAttrs = {
                "id_": f'iamg-{instance["GroupName"].lower()}',
                "name": instance["GroupName"],
                "arn": instance["Arn"],
                "users": users,
                "state": "active",
            }

            # ignore: I don't know why it's not able to infer the type of the
            # argument 1 of _build_entity_update ¯\(°_o)/¯
            entity_updates.append(
                _build_entity_update(  # type: ignore
                    entity_data, aws.IAMGroup, remaining_entities
                )
            )

        return entity_updates


def build_security_group_rule_data(rule_data: Dict[str, Any]) -> Dict[str, Any]:
    """Adapt the security group rule from the AWS format to the SecurityGroupRule.

    Args:
        rule_data: dictionary of the security group data.

    Returns:
        dictionary compatible with the SecurityGroupRule fields.
    """
    rule = {
        "protocol": rule_data["IpProtocol"].upper(),
        "ip_range": [],
        "ipv6_range": [],
        "sg_range": [],
    }

    if rule["protocol"] == "ICMP":
        rule["ports"] = [-2]
    elif rule["protocol"] == "-1":
        rule["protocol"] = "TCP & UDP & ICMP"
        rule["ports"] = [-1]
    else:
        rule["ports"] = list(range(rule_data["FromPort"], rule_data["ToPort"] + 1))

    with suppress(KeyError):
        rule["ip_range"] = [cidr["CidrIp"] for cidr in rule_data["IpRanges"]]

    with suppress(KeyError):
        rule["ipv6_range"] = [cidr["CidrIp"] for cidr in rule_data["Ipv6Ranges"]]

    with suppress(KeyError):
        rule["sg_range"] = [sg["GroupId"] for sg in rule_data["UserIdGroupPairs"]]

    # The description of the security group rules is attached to each of the
    # elements of the lists.
    for description_place in ["IpRanges", "Ipv6Ranges", "UserIdGroupPairs"]:
        with suppress(KeyError, IndexError):
            rule["description"] = [
                cidr["Description"] for cidr in rule_data[description_place]
            ][0]
            break

    return rule


def _build_entity_update(
    entity_data: EntityAttrs,
    entity_model: Type[EntityT],
    remaining_entities: List[EntityT],
) -> EntityUpdate:
    """Create the EntityUpdate object from the entity_data and model.

    Also remove the entity identified by the data from the list of remaining entities.

    """
    # Remove entity from remaining_entities
    for entity in remaining_entities:
        if isinstance(entity, entity_model) and entity.id_ == entity_data["id_"]:
            remaining_entities.remove(entity)
            saved_entity_data = entity.dict()
            break
    else:
        saved_entity_data = {}

    return EntityUpdate(model=entity_model, data={**saved_entity_data, **entity_data})
