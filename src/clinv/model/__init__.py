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
from .risk import Information, Person, Project, Service

RESOURCE_TYPES = {
    "asg": ASG,
    "ec2": EC2,
    "iamg": IAMGroup,
    "iamu": IAMUser,
    "inf": Information,
    "per": Person,
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

Choices = Dict[str, Dict[str, Any]]

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
    "Person",
    "Entity",
    "EntityAttrs",
    "EntityID",
    "EntityT",
    "EntityState",
    "EntityUpdate",
]
