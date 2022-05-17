"""Define the Risk management sources used by Clinv."""

import logging
from typing import List, Optional

from ..model import EntityT, EntityUpdate
from .abstract import AbstractSource

log = logging.getLogger(__name__)


class RiskSource(AbstractSource):
    """Define the interface to interact with the source of Risk Management entities."""

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
        log.debug("Updating Risk Management entities.")
        return []
