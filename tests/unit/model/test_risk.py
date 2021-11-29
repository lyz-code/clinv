"""Test the Risk management models."""

from typing import Type

import pytest
from pydantic.error_wrappers import ValidationError
from repository_orm import Entity

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
