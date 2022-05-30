"""Define the factories of the program models."""

from typing import Any

from pydantic_factories import ModelFactory

from clinv.model import aws, risk

# -------------------------------
# --      AWS Factories
# -------------------------------


class ASGFactory(ModelFactory[Any]):
    """Define the factory for the model ASG."""

    __model__ = aws.ASG


class EC2Factory(ModelFactory[Any]):
    """Define the factory for the model EC2."""

    __model__ = aws.EC2


class IAMUserFactory(ModelFactory[Any]):
    """Define the factory for the model IAM User."""

    __model__ = aws.IAMUser


class IAMGroupFactory(ModelFactory[Any]):
    """Define the factory for the model IAM Group."""

    __model__ = aws.IAMGroup


class RDSFactory(ModelFactory[Any]):
    """Define the factory for the model RDS."""

    __model__ = aws.RDS


class Route53Factory(ModelFactory[Any]):
    """Define the factory for the model Route53."""

    __model__ = aws.RDS


class S3Factory(ModelFactory[Any]):
    """Define the factory for the model S3."""

    __model__ = aws.SecurityGroup


class SecurityGroupFactory(ModelFactory[Any]):
    """Define the factory for the model SecurityGroup."""

    __model__ = aws.SecurityGroup


class VPCFactory(ModelFactory[Any]):
    """Define the factory for the model VPC."""

    __model__ = aws.VPC


# -------------------------------
# --      Risk Factories
# -------------------------------


class InformationFactory(ModelFactory[Any]):
    """Define the factory for the model Information."""

    __model__ = risk.Information


class PersonFactory(ModelFactory[Any]):
    """Define the factory for the model Person."""

    __model__ = risk.Person


class ProjectFactory(ModelFactory[Any]):
    """Define the factory for the model Project."""

    __model__ = risk.Project


class ServiceFactory(ModelFactory[Any]):
    """Define the factory for the model Service."""

    __model__ = risk.Service


class NetworkAccessFactory(ModelFactory[Any]):
    """Define the factory for the model Service."""

    __model__ = risk.NetworkAccess


class AuthenticationFactory(ModelFactory[Any]):
    """Define the factory for the model Service."""

    __model__ = risk.Authentication


class RiskFactory(ModelFactory[Any]):
    """Define the factory for the model Service."""

    __model__ = risk.Risk


class SecurityMeasureFactory(ModelFactory[Any]):
    """Define the factory for the model Service."""

    __model__ = risk.SecurityMeasure
