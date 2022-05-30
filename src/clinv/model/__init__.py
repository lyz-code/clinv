"""Module to store the common business model of all entities."""

from typing import Any, Dict

from .aws import (
    ASG,
    EC2,
    RDS,
    S3,
    VPC,
    IAMGroup,
    IAMUser,
    NetworkProtocol,
    Route53,
    SecurityGroup,
    SecurityGroupRule,
)
from .entity import Entity, EntityAttrs, EntityID, EntityState, EntityT, EntityUpdate
from .risk import (
    Authentication,
    Information,
    NetworkAccess,
    Person,
    Project,
    Risk,
    SecurityMeasure,
    Service,
)

# Elements are ordered so that the important ones show first when searching
RESOURCE_TYPES = {
    "ser": Service,
    "pro": Project,
    "ec2": EC2,
    "r53": Route53,
    "rds": RDS,
    "s3": S3,
    "asg": ASG,
    "sg": SecurityGroup,
    "iamg": IAMGroup,
    "iamu": IAMUser,
    "inf": Information,
    "per": Person,
    "vpc": VPC,
    "auth": Authentication,
    "net": NetworkAccess,
    "risk": Risk,
    "sec": SecurityMeasure,
}

RESOURCE_NAMES = list(RESOURCE_TYPES.keys())
MODELS = [value for _, value in RESOURCE_TYPES.items()]

Choices = Dict[str, Dict[str, Any]]

__all__ = [
    "Authentication",
    "NetworkAccess",
    "EC2",
    "RDS",
    "S3",
    "Route53",
    "VPC",
    "ASG",
    "SecurityGroup",
    "SecurityGroupRule",
    "IAMUser",
    "IAMGroup",
    "NetworkProtocol",
    "Project",
    "Information",
    "Service",
    "Person",
    "Entity",
    "EntityAttrs",
    "EntityID",
    "EntityT",
    "EntityState",
    "EntityUpdate",
]
