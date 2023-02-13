"""Define the models of the AWS resources."""

import re
from datetime import datetime
from enum import Enum
from typing import List, Optional, Set

from pydantic import BaseModel  # noqa: E0611
from pydantic import ConstrainedStr, Field

from .entity import Entity, Environment

# -------------------------------
# --        Resource IDs       --
# -------------------------------

# Once https://github.com/samuelcolvin/pydantic/issues/2551 is solved, use Annotated
# Fields instead, as it's a cleaner solution.
# For example: EC2ID = Annotated[str, Field(regex="^i-.*")]


class AMIID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^ami-[0-9a-zA-Z]+$")


class ASGID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^asg-[0-9a-zA-Z_-]+$")


class EC2ID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^i-[0-9a-zA-Z]+$")


class IAMUserID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^iamu-[0-9a-zA-Z_-]+$")


class IAMGroupID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^iamg-[0-9a-zA-Z_-]+$")


class RDSID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^db-[0-9a-zA-Z_-]+$")


class Route53ID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("[A-Z0-9]+-.*-(cname|a|txt|soa|ns|mx)")


class S3ID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^s3-[0-9a-zA-Z._-]+$")


class SecurityGroupID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^sg-[0-9a-za-z]+$")


class SubnetID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^subnet-[0-9a-za-z]+$")


class VPCID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^vpc-[0-9a-za-z]+$")


class IPvAnyAddress(ConstrainedStr):
    """Define the regular expression of an IP address.

    The pydantic's IPvAnyAddress will be usable once repository_orm supports it.
    """

    regex = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")


class IPvAnyNetwork(ConstrainedStr):
    """Define the regular expression of an IP network.

    The pydantic's IPvAnyNetwork will be usable once repository_orm supports it.
    """

    regex = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}(?:/\d\d?)?")


# -------------------------------
# --      Resource Models      --
# -------------------------------


class AWSEntity(Entity):
    """Represent a generic AWS resource.

    Args:
        start_date:
        monitor: If the instance is being monitored
        environment: Logical environment (production, staging)
    """

    environment: Optional[List[Environment]] = Field(default_factory=list)
    monitor: Optional[bool] = None


class ASGHealthcheck(str, Enum):
    """Set the possible ASG healtchecks."""

    ELB = "ELB"
    EC2 = "EC2"


class ASG(AWSEntity):
    """Represent an AWS ASG.

    Args:
        description:
        environment: Logical environment (production, staging).
        id_: unique identifier of the entity.
        monitor: If the instance is being monitored
        name:
        region: AWS region where the instance lives. For example `us-east-1`
        state:
        min_size:
        max_size:
        desired_size:
        launch_configuration:
        launch_template:
        availability_zones:
        instances: List of instance ids of the autoscaling group
        healthcheck: if the healthcheck is of type EC2 or ELB
    """

    id_: ASGID
    min_size: int
    max_size: int
    desired_size: int
    region: str
    launch_configuration: Optional[str] = None
    launch_template: Optional[str] = None
    availability_zones: List[str] = Field(default_factory=list)
    instances: List[EC2ID] = Field(default_factory=list)
    healthcheck: ASGHealthcheck

    def uses(self, unused: Set[Entity]) -> Set[Entity]:
        """Return the used entities."""
        return {entity for entity in unused if entity.id_ in self.instances}


class EC2(AWSEntity):
    """Represent an Elastic Compute Cloud AWS instance.

    Args:
        ami: AMI base image.
        description:
        environment: Logical environment (production, staging)
        id_: unique identifier of the entity.
        monitor: If the instance is being monitored
        name:
        private_ips:
        public_ips:
        security_groups: List of security groups id's attached to the instance.
        region: AWS region where the instance lives. For example `us-east-1`
        size: Instance type.
        start_date:
        state:
        subnet:
        vpc:
    """

    id_: EC2ID
    ami: AMIID
    private_ips: List[IPvAnyAddress] = Field(default_factory=list)
    public_ips: List[IPvAnyAddress] = Field(default_factory=list)
    region: str
    start_date: datetime
    security_groups: List[SecurityGroupID] = Field(default_factory=list)
    size: str
    state_transition: Optional[str] = None
    subnet: Optional[SubnetID] = None
    vpc: Optional[VPCID] = None

    def uses(self, unused: Set[Entity]) -> Set[Entity]:
        """Return the used entities."""
        return {
            entity
            for entity in unused
            if entity.id_ in self.security_groups
            or entity.id_ == self.vpc
            or entity.id_ == self.subnet
        }


class IAMGroup(Entity):
    """Represent an IAM user.

    Args:
        arn: AWS ARN identifier of the resource.
        users: list of users ids.
    """

    id_: IAMGroupID
    arn: str
    users: List[IAMUserID] = Field(default_factory=list)

    def uses(self, unused: Set[Entity]) -> Set[Entity]:
        """Return the used resources.

        Until we don't have the concept of group of people in the risk models, it
        doesn't make sense to be assigned to any service or project.
        """
        return {entity for entity in unused if entity.id_ in self.users}


class IAMUser(Entity):
    """Represent an IAM user.

    Args:
        arn: AWS ARN identifier of the resource.
    """

    id_: IAMUserID
    arn: str


class RDS(AWSEntity):
    """Represent an AWS RDS database.

    Args:
        description:
        engine: Database type and version.
        endpoint: Endpoint to connect to the database
        environment: Logical environment (production, staging)
        id_: unique identifier of the entity.
        monitor: If the instance is being monitored
        name:
        security_groups: List of security groups id's attached to the instance.
        region: AWS region where the instance lives. For example `us-east-1`
        size: Instance type.
        start_date:
        state:
        subnets:
        vpc:
    """

    id_: RDSID
    engine: str
    endpoint: str
    start_date: datetime
    region: str
    security_groups: List[SecurityGroupID] = Field(default_factory=list)
    size: str
    subnets: List[SubnetID] = Field(default_factory=list)
    vpc: VPCID

    def uses(self, unused: Set[Entity]) -> Set[Entity]:
        """Return the used entities."""
        return {
            entity
            for entity in unused
            if entity.id_ in self.security_groups
            or entity.id_ == self.vpc
            or entity.id_ in self.subnets
        }


class Route53(AWSEntity):
    """Represent an AWS Route53 record.

    Args:
        description:
        environment: Logical environment (production, staging)
        id_: unique identifier of the entity.
        monitor: If the instance is being monitored
        name:
        state:
        hosted_zone: AWS HostedZone containing the record.
        value: Where does the record point to, or the information it holds.
        type_: Record type. Such as `A` or `CNAME`.
        public: If the record is accessed by the general public.
    """

    id_: Route53ID
    hosted_zone: str
    values: List[str] = Field(default_factory=list)
    type_: str
    public: Optional[bool] = None


class S3(AWSEntity):
    """Represent an AWS S3 bucket.

    Args:
        description:
        public_read: If anyone has public read permissions on the bucket.
        public_write: If anyone has public write permissions on the bucket.
        environment: Logical environment (production, staging)
        id_: unique identifier of the entity.
        monitor: If the instance is being monitored
        name:
        start_date:
        state:
    """

    id_: S3ID
    public_read: bool
    public_write: bool
    start_date: datetime


class VPC(AWSEntity):
    """Represent an AWS VPC.

    Args:
        description:
        environment: Logical environment (production, staging)
        id_: unique identifier of the entity.
        monitor: If the instance is being monitored
        cidr:
        name:
        region: AWS region where the instance lives. For example `us-east-1`
        state:
    """

    id_: VPCID
    cidr: IPvAnyNetwork
    region: str


class NetworkProtocol(str, Enum):
    """Set the possible network protocols."""

    TCP = "TCP"
    UPD = "UDP"
    ICMP = "ICMP"
    ALL = "TCP & UDP & ICMP"


class SecurityGroupRule(BaseModel):
    """Represent an AWS Security Group Rule.

    Args:
        protocol:
        ports: List of ports to open. To model the special cases we use negative ints:
            * All ports: -1
            * Not applicable: -2. For example for ICMP.
        ip_range: List of ips that are related to the rule.
        ipv6_range: List of ips of version 6 that are related to the rule.
        sg_range: List of security group ids that are related to the rule.

    """

    protocol: NetworkProtocol
    ports: List[int] = Field(default_factory=list)
    sg_range: List[SecurityGroupID] = Field(default_factory=list)
    ip_range: List[IPvAnyAddress] = Field(default_factory=list)
    ipv6_range: List[str] = Field(default_factory=list)


class SecurityGroup(AWSEntity):
    """Represent an AWS Security Group.

    Args:
        description:
        environment: Logical environment (production, staging).
        id_: unique identifier of the entity.
        monitor: If the instance is being monitored
        name:
        region: AWS region where the instance lives. For example `us-east-1`
        state:
    """

    id_: SecurityGroupID
    egress: List[SecurityGroupRule] = Field(default_factory=list)
    ingress: List[SecurityGroupRule] = Field(default_factory=list)
