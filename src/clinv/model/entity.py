"""Define the basic entity."""

from contextlib import suppress
from enum import Enum
from typing import Any, Dict, Optional, Type, TypeVar, Union

from pydantic import BaseModel  # noqa: E0611
from pydantic import root_validator
from repository_orm import Entity as BasicEntity

EntityAttrs = Dict[str, Any]
EntityID = Union[str, int]


class Environment(str, Enum):
    """Set the possible logical environments."""

    STAGING = "Staging"
    PRODUCTION = "Production"
    TESTING = "Testing"


class EntityState(str, Enum):
    """Set the possible entity states."""

    RUNNING = "active"
    PENDING = "pending"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    TBD = "tbd"


class Entity(BasicEntity):
    """Define the generic clinv entity.

    Args:
        id_: unique identifier of the entity.
        name:
        state:
        description:
    """

    name: Optional[str] = None
    state: EntityState
    description: Optional[str] = None


EntityType = TypeVar("EntityType", bound=Entity)


class EntityUpdate(BaseModel):
    """Define the updates of an entity."""

    id_: EntityID
    model: Type[Entity]
    data: Dict[str, Any]

    @root_validator(pre=True)
    @classmethod
    def set_id_and_model(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Set the id_ and model attributes."""
        values["id_"] = values["data"]["id_"]
        with suppress(KeyError):
            values["model"] = values["data"].pop("model")

        return values
