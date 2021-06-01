"""Define the models of the AWS resources."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel  # noqa: E0611
from pydantic import Field

from .entity import Entity, Environment


class AWSEntity(Entity):
    """Represent a generic AWS resource.

    Args:
        start_date:
        monitor: If the instance is being monitored
        environment: Logical environment (production, staging)
    """

    environment: Optional[List[Environment]] = Field(default_factory=list)
    monitor: Optional[bool] = None


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

    min_size: int
    max_size: int
    desired_size: int
    region: str
    launch_configuration: Optional[str] = None
    launch_template: Optional[str] = None
    availability_zones: List[str] = Field(default_factory=list)
    instances: List[str] = Field(default_factory=list)
    healthcheck: str


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

    ami: str
    private_ips: List[str] = Field(default_factory=list)
    public_ips: List[str] = Field(default_factory=list)
    region: str
    start_date: datetime
    security_groups: List[str] = Field(default_factory=list)
    size: str
    state_transition: Optional[str] = None
    subnet: Optional[str] = None
    vpc: str


class IAMGroup(Entity):
    """Represent an IAM user.

    Args:
        arn: AWS ARN identifier of the resource.
        users: list of users ids.
    """

    arn: str
    users: List[str] = Field(default_factory=list)


class IAMUser(Entity):
    """Represent an IAM user.

    Args:
        arn: AWS ARN identifier of the resource.
    """

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

    engine: str
    endpoint: str
    start_date: datetime
    region: str
    security_groups: List[str] = Field(default_factory=list)
    size: str
    subnets: List[str] = Field(default_factory=list)
    vpc: str


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

    cidr: str
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
    sg_range: List[str] = Field(default_factory=list)
    ip_range: List[str] = Field(default_factory=list)
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

    egress: List[SecurityGroupRule] = Field(default_factory=list)
    ingress: List[SecurityGroupRule] = Field(default_factory=list)
