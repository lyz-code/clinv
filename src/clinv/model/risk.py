"""Define the Risk management entities."""

from enum import Enum
from typing import List, Optional

from pydantic import Field

from .entity import Entity, Environment


class Information(Entity):
    """Represent the data used by a service or project.

    Args:
        id_: unique identifier of the entity.
        name:
        state:
        description:
        personal_data: Whether the information contains personal data in terms of
            RGPD.
        responsible: Person who is legally responsible of the entity.
    """

    responsible: Optional[str] = None
    personal_data: bool = False


class People(Entity):
    """Represent the people of the team.

    Args:
        id_: unique identifier of the entity.
        name:
        state:
        description:
        iam_user:
        email:
    """

    iam_user: Optional[str] = None
    email: Optional[str] = None


class Project(Entity):
    """Represent the reason for a group of service and information.

    Args:
        id_: unique identifier of the entity.
        name:
        state:
        description:
        aliases: Alternative names of the project.
        services: Service ids used by the project.
        informations: Information ids used by the project.
        people: People ids that work on the project.
        responsible: Person who is legally responsible of the entity.
    """

    responsible: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    services: List[str] = Field(default_factory=list)
    informations: List[str] = Field(default_factory=list)
    people: List[str] = Field(default_factory=list)


class ServiceAccess(str, Enum):
    """Represent possible states of the service access."""

    PUBLIC = "public"
    INTERNAL = "internal"
    TBD = "tbd"


class Service(Entity):
    """Represent aggregation of IT resources to present an utility to users.

    Args:
        id_: unique identifier of the entity.
        name:
        state:
        description:
        authentication: List of authentication methods required to access the service.
        environment: Logical environment (production, staging)
        access: Level of exposition of the resource.
        responsible: Person who is legally responsible of the entity.
        informations: Information ids used by the project.
    """

    access: ServiceAccess
    responsible: Optional[str] = None
    authentication: List[str] = Field(default_factory=list)
    informations: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    users: List[str] = Field(default_factory=list)
    environment: Optional[Environment] = None
