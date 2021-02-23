"""Test the Risk management models."""

import pytest
from pydantic.error_wrappers import ValidationError

from clinv.model.risk import Service


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
