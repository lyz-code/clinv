"""Module to store the common business model of all entities."""

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
from .entity import Entity, EntityAttrs, EntityID, EntityState, EntityType, EntityUpdate
from .risk import Information, People, Project, Service

RESOURCE_TYPES = {
    "asg": ASG,
    "ec2": EC2,
    "iamg": IAMGroup,
    "iamu": IAMUser,
    "info": Information,
    "peo": People,
    "pro": Project,
    "rds": RDS,
    "r53": Route53,
    "s3": S3,
    "ser": Service,
    "sg": SecurityGroup,
    "vpc": VPC,
}

RESOURCE_NAMES = list(RESOURCE_TYPES.keys())
MODELS = [value for _, value in RESOURCE_TYPES.items()]

__all__ = [
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
    "People",
    "Entity",
    "EntityAttrs",
    "EntityID",
    "EntityType",
    "EntityState",
    "EntityUpdate",
]
