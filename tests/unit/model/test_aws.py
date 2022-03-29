"""Test the implementation of the AWS Models."""

from datetime import datetime
from typing import Any, Dict, Type

import pytest
from pydantic import ValidationError
from tests.factories import IAMGroupFactory, IAMUserFactory, RDSFactory

from clinv.model import aws
from clinv.model.entity import Entity

from ...factories import ASGFactory, EC2Factory, SecurityGroupFactory, VPCFactory


@pytest.mark.parametrize(
    ("model", "arguments"),
    [
        pytest.param(
            aws.ASG,
            {
                "min_size": 1,
                "max_size": 3,
                "desired_size": 2,
                "region": "us-east-1",
                "healthcheck": "ELB",
            },
            id="ASG",
        ),
        pytest.param(aws.EC2, {}, id="EC2"),
        pytest.param(aws.IAMGroup, {"arn": "arn"}, id="IAMGroup"),
        pytest.param(aws.IAMUser, {"arn": "arn"}, id="IAMUser"),
        pytest.param(
            aws.RDS,
            {
                "engine": "postgres",
                "endpoint": "endpoint",
                "region": "us-east-1",
                "size": "big",
                "vpc": "vpc",
                "start_date": datetime.now(),
            },
            id="RDS",
        ),
        pytest.param(aws.Route53, {"hosted_zone": "zone", "type_": "A"}, id="Route53"),
        pytest.param(
            aws.S3,
            {
                "public_read": False,
                "public_write": False,
                "start_date": datetime.now(),
            },
            id="S3",
        ),
        pytest.param(
            aws.VPC,
            {"cidr": "cidr", "region": "us-east-1"},
            id="VPC",
        ),
        pytest.param(aws.SecurityGroup, {}, id="SecurityGroup"),
    ],
)
def test_aws_models_have_validation_of_id_content(
    model: Type[Entity], arguments: Dict[str, Any]
) -> None:
    """
    Given: One entity with a wrong id format.
    When: The object is initialized
    Then: A validation error is shown
    """
    with pytest.raises(ValidationError):
        model(id_="wrong_id", state="active", **arguments)  # type: ignore


@pytest.mark.parametrize(
    ("used", "entity"),
    [
        pytest.param(
            EC2Factory.build(id_="i-xx"),
            ASGFactory.build(instances=["i-xx"]),
            id="ASG uses EC2",
        ),
        pytest.param(
            SecurityGroupFactory.build(id_="sg-xx"),
            EC2Factory.build(security_groups=["sg-xx"]),
            id="EC2 uses SG",
        ),
        pytest.param(
            VPCFactory.build(id_="vpc-xx"),
            EC2Factory.build(vpc="vpc-xx"),
            id="EC2 uses VPC",
        ),
        pytest.param(
            IAMUserFactory.build(id_="iamu-xx"),
            IAMGroupFactory.build(users=["iamu-xx"]),
            id="IAM Group uses IAM User",
        ),
        pytest.param(
            SecurityGroupFactory.build(id_="sg-xx"),
            RDSFactory.build(security_groups=["sg-xx"]),
            id="RDS uses SG",
        ),
        pytest.param(
            VPCFactory.build(id_="vpc-xx"),
            RDSFactory.build(vpc="vpc-xx"),
            id="RDS uses VPC",
        ),
    ],
)
def test_entity_detects_used_entity(used: Entity, entity: Entity) -> None:
    """
    Given: An entity that uses the `used` entity
    When: uses is called with the entity that is using the other one
    Then: The used entity is returned.
    """
    result = entity.uses({used})

    assert result == {used}
