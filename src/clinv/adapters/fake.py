"""Define the fake adapters used for testing."""

from typing import Any, Dict, List, Optional

from ..model import EntityT, EntityUpdate
from .abstract import AbstractSource


class FakeSource(AbstractSource):
    """Define Fake source to be used in the edge to edge tests."""

    def __init__(self) -> None:
        """Initialize the source attributes.

        Args:
            supported_models: List of models supported by the source.
        """
        self.supported_models: List[str] = ["Entity"]
        self._entity_updates: List[EntityUpdate] = []

    def update(
        self,
        resource_types: Optional[List[str]] = None,
        active_resources: Optional[List[EntityT]] = None,
    ) -> List[EntityUpdate]:
        """Get the latest state of the source entities.

        Args:
            resource_types: Limit the update to these type of resources.
            active_resources: List of active resources in the repository.

        Returns:
            List of entity updates.
        """
        return self._entity_updates

    def add_change(self, entity: EntityT, entity_data: Dict[str, Any]) -> None:
        """Record changes on entities to be returned when calling the update method.

        Args:
            entity_data: dictionary with key value to update.
        """
        entity_data["id_"] = entity.id_
        self._entity_updates.append(
            EntityUpdate(data={**entity.dict(), **entity_data}, model=type(entity))
        )
