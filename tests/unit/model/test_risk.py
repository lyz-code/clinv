"""Test the Risk management models."""

from typing import Type

import pytest
from pydantic.error_wrappers import ValidationError
from tests.factories import (
    EC2Factory,
    IAMUserFactory,
    InformationFactory,
    PersonFactory,
    ProjectFactory,
    ServiceFactory,
)

from clinv.model.entity import Entity
from clinv.model.risk import Information, People, Project, Service


@pytest.mark.parametrize("access", ["public", "internal"])
def test_service_access_attribute_happy_path(access: str) -> None:
    """
    Given: The Service model
    When: initializing with valid values
    Then: the model is created without problem.
    """
    result = Service(
        id_="ser_01",
        state="active",
        name="Test Service",
        access=access,
    )

    assert result.access == access


def test_service_access_attribute_unhappy_path() -> None:
    """
    Given: The Service model
    When: initializing with invalid values
    Then: the model returns an error.
    """
    with pytest.raises(ValidationError):
        Service(
            id_="ser_01",
            state="active",
            name="Test Service",
            access="inexistent",
        )


@pytest.mark.parametrize("model", [Service, People, Project, Information])
def test_risk_models_have_validation_of_id_content(model: Type[Entity]) -> None:
    """
    Given: One entity with a wrong id format.
    When: The object is initialized
    Then: A validation error is shown
    """
    with pytest.raises(ValidationError):
        model(id_="wrong_id", state="active")


@pytest.mark.parametrize(
    ("used", "entity"),
    [
        pytest.param(
            PersonFactory.build(id_="peo_01"),
            InformationFactory.build(responsible="peo_01"),
            id="Information uses Person",
        ),
        pytest.param(
            IAMUserFactory.build(id_="iamu-01"),
            PersonFactory.build(iam_user="iamu-01"),
            id="Person uses IAM User",
        ),
        pytest.param(
            PersonFactory.build(id_="peo_01"),
            ProjectFactory.build(responsible="peo_01"),
            id="Project uses Person as responsible",
        ),
        pytest.param(
            PersonFactory.build(id_="peo_01"),
            ProjectFactory.build(people=["peo_01"]),
            id="Project uses Person as project member",
        ),
        pytest.param(
            ServiceFactory.build(id_="ser_01"),
            ProjectFactory.build(services=["ser_01"]),
            id="Project uses Service",
        ),
        pytest.param(
            InformationFactory.build(id_="inf_01"),
            ProjectFactory.build(informations=["inf_01"]),
            id="Project uses Informations",
        ),
        pytest.param(
            PersonFactory.build(id_="peo_01"),
            ServiceFactory.build(responsible="peo_01"),
            id="Service uses Person as responsible",
        ),
        pytest.param(
            InformationFactory.build(id_="inf_01"),
            ServiceFactory.build(informations=["inf_01"]),
            id="Service uses Informations",
        ),
        pytest.param(
            ServiceFactory.build(id_="ser_02"),
            ServiceFactory.build(dependencies=["ser_02"]),
            id="Service uses Service",
        ),
        pytest.param(
            EC2Factory.build(id_="i-01"),
            ServiceFactory.build(resources=["i-01"]),
            id="Service uses Infra resource",
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
