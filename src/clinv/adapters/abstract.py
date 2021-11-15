"""Define the interface for the source adapters."""

import abc
from typing import List, Optional

from ..model.entity import EntityType, EntityUpdate


class AbstractSource(abc.ABC):
    """Define common methods and define the interface of the source adapters."""

    @abc.abstractmethod
    def update(
        self,
        resource_types: Optional[List[str]] = None,
        active_resources: Optional[List[EntityType]] = None,
    ) -> List[EntityUpdate]:
        """Get the latest state of the source entities.

        Args:
            resource_types: Limit the update to these type of resources.
            active_resources: List of active resources in the repository.

        Returns:
            List of entity updates.
        """
        raise NotImplementedError
