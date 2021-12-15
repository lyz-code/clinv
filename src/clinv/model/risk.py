"""Define the Risk management entities."""

import re
from enum import Enum
from typing import List, Optional, Set

from pydantic import ConstrainedStr, Field

from .aws import IAMUserID
from .entity import Entity, Environment

# -------------------------------
# --        Resource IDs       --
# -------------------------------

# Once https://github.com/samuelcolvin/pydantic/issues/2551 is solved, use Annotated
# Fields instead, as it's a cleaner solution.
# For example: EC2ID = Annotated[str, Field(regex="^i-.*")]


class InformationID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^inf_[0-9]+$")


class ServiceID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^ser_[0-9]+$")


class ProjectID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^pro_[0-9]+$")


class PersonID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^peo_[0-9]+$")


# -------------------------------
# --      Resource Models      --
# -------------------------------


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

    id_: InformationID
    responsible: Optional[PersonID] = None
    personal_data: bool = False

    def uses(self, unused: Set[Entity]) -> Set[Entity]:
        """Return the used entities by self."""
        return {entity for entity in unused if entity.id_ == self.responsible}


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

    id_: PersonID
    iam_user: Optional[IAMUserID] = None
    email: Optional[str] = None

    def uses(self, unused: Set[Entity]) -> Set[Entity]:
        """Return the used entities by self."""
        return {entity for entity in unused if entity.id_ == self.iam_user}


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

    id_: ProjectID
    responsible: Optional[PersonID] = None
    aliases: List[str] = Field(default_factory=list)
    services: List[ServiceID] = Field(default_factory=list)
    informations: List[InformationID] = Field(default_factory=list)
    people: List[PersonID] = Field(default_factory=list)

    def uses(self, unused: Set[Entity]) -> Set[Entity]:
        """Return the used entities by self."""
        return {
            entity
            for entity in unused
            if entity.id_ == self.responsible
            or entity.id_ in self.people
            or entity.id_ in self.services
            or entity.id_ in self.informations
        }


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

    id_: ServiceID
    access: Optional[ServiceAccess] = None
    responsible: Optional[PersonID] = None
    authentication: List[str] = Field(default_factory=list)
    informations: List[InformationID] = Field(default_factory=list)
    dependencies: List[ServiceID] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    users: List[str] = Field(default_factory=list)
    environment: Optional[Environment] = None

    def uses(self, unused: Set[Entity]) -> Set[Entity]:
        """Return the used entities by self."""
        return {
            entity
            for entity in unused
            if entity.id_ == self.responsible
            or entity.id_ in self.dependencies
            or entity.id_ in self.resources
            or entity.id_ in self.informations
        }
