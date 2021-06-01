"""Define the factories of the program models."""

import factory
from faker_enum import EnumProvider

from clinv.model import EC2, EntityState, People

factory.Faker.add_provider(EnumProvider)


class PeopleFactory(factory.Factory):  # type: ignore
    """Generate a fake entity."""

    id_ = factory.Faker("word")
    name = factory.Faker("name")
    description = factory.Faker("sentence")
    state = factory.Faker("enum", enum_cls=EntityState)

    class Meta:
        """Declare the model of the factory."""

        model = People


class EC2Factory(factory.Factory):  # type: ignore
    """Create a fake Elastic Compute Cloud AWS instance."""

    id_ = factory.Faker("word")
    name = factory.Faker("name")
    description = factory.Faker("sentence")
    state = factory.Faker("enum", enum_cls=EntityState)
    ami = factory.Faker("word")
    # I know it's not ideal, but it's the best I can do right now
    private_ips = factory.Faker("pylist", value_types=str)
    public_ips = factory.Faker("pylist", value_types=str)
    region = factory.Faker("word")
    start_date = factory.Faker("date_time")
    security_groups = factory.Faker("pylist", value_types=str)
    size = factory.Faker("word")
    state_transition = factory.Faker("word")
    subnet = factory.Faker("word")
    vpc = factory.Faker("word")

    class Meta:
        """Declare the model of the factory."""

        model = EC2
