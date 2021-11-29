"""Define the factories of the program models."""

from factory import Factory, Faker
from faker_enum import EnumProvider
from pydantic_factories import ModelFactory

from clinv.model import aws, risk
from clinv.model.entity import EntityState

Faker.add_provider(EnumProvider)


class ASGFactory(ModelFactory):  # type: ignore
    """Define the factory for the model ASG."""

    __model__ = aws.ASG


class EC2Factory(ModelFactory):  # type: ignore
    """Define the factory for the model EC2."""

    __model__ = aws.EC2


class SecurityGroupFactory(ModelFactory):  # type: ignore
    """Define the factory for the model SecurityGroup."""

    __model__ = aws.SecurityGroup


class VPCFactory(ModelFactory):  # type: ignore
    """Define the factory for the model VPC."""

    __model__ = aws.VPC


class PeopleFactory(Factory):  # type: ignore
    """Generate a fake entity."""

    id_ = Faker("pystr_format", string_format="peo_#######{{random_letter}}")
    name = Faker("name")
    description = Faker("sentence")
    state = Faker("enum", enum_cls=EntityState)

    class Meta:
        """Declare the model of the factory."""

        model = risk.People
