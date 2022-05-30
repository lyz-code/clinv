"""Define the Risk management entities."""

import re
from typing import List, Optional, Set

from pydantic import ConstrainedStr, Field, PrivateAttr

from .aws import IAMUserID
from .entity import Entity, EntityState, Environment

# -------------------------------
# --        Resource IDs       --
# -------------------------------

# Once https://github.com/samuelcolvin/pydantic/issues/2551 is solved, use Annotated
# Fields instead, as it's a cleaner solution.
# For example: EC2ID = Annotated[str, Field(regex="^i-.*")]


class InformationID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^inf_[0-9]{3}$")


class ServiceID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^ser_[0-9]{3}$")


class ProjectID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^pro_[0-9]{3}$")


class PersonID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^per_[0-9]{3}$")


class AuthenticationID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^auth_[0-9]{3}$")


class RiskID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^risk_[0-9]{3}$")


class SecurityMeasureID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^sec_[0-9]{3}$")


class NetworkAccessID(ConstrainedStr):
    """Define the resource id format."""

    regex = re.compile("^net_[0-9]{3}$")


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
    personal_data: bool = Field(default=False, title="Personal Data")

    def uses(self, unused: Set[Entity]) -> Set[Entity]:
        """Return the used entities by self."""
        return {entity for entity in unused if entity.id_ == self.responsible}

    class Config:
        """Configure the model."""

        schema_extra = {
            "tui_fields": [
                "name",
                "description",
                "responsible",
                "personal_data",
            ]
        }


class Person(Entity):
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
    iam_user: Optional[IAMUserID] = Field(default=None, title="IAM User")
    email: Optional[str] = None

    def uses(self, unused: Set[Entity]) -> Set[Entity]:
        """Return the used entities by self."""
        return {entity for entity in unused if entity.id_ == self.iam_user}

    class Config:
        """Configure the model."""

        schema_extra = {
            "tui_fields": [
                "name",
                "description",
                "iam_user",
                "email",
            ]
        }


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

    class Config:
        """Configure the model."""

        schema_extra = {
            "tui_fields": [
                "name",
                "description",
                "responsible",
                "aliases",
                "services",
                "informations",
                "people",
            ]
        }


class RiskEntity(Entity):
    """Aggregates common attributes of risk entities."""

    security_value: int
    state: EntityState = EntityState.RUNNING

    class Config:
        """Configure the model."""

        schema_extra = {
            "tui_fields": [
                "name",
                "description",
                "security_value",
            ]
        }


class NetworkAccess(RiskEntity):
    """Represent the different ways to access a service in network terms."""

    id_: NetworkAccessID


class Authentication(RiskEntity):
    """Represent the authentication and authorisation mechanisms."""

    id_: AuthenticationID


class Risk(RiskEntity):
    """Represent the security risks a service may have."""

    id_: RiskID


class SecurityMeasure(RiskEntity):
    """Represent the security measures a service may have to protect itself."""

    id_: SecurityMeasureID


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
        _risk: The value of all the risks that apply to the service.
        _protection: The value of all the security measures applied to the service.
        _security: Overall security score taking into account risks and protections.
    """

    id_: ServiceID
    access: Optional[NetworkAccessID] = None
    responsible: Optional[PersonID] = None
    authentication: List[AuthenticationID] = Field(default_factory=list)
    informations: List[InformationID] = Field(default_factory=list)
    dependencies: List[ServiceID] = Field(default_factory=list)
    security_measures: List[SecurityMeasureID] = Field(default_factory=list)
    risks: List[RiskID] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    users: List[str] = Field(default_factory=list)
    environment: Optional[Environment] = None
    _risk: int = PrivateAttr()
    _protection: int = PrivateAttr()
    _security: int = PrivateAttr()

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

    class Config:
        """Configure the model."""

        schema_extra = {
            "tui_fields": [
                "name",
                "description",
                "responsible",
                "access",
                "authentication",
                "informations",
                "dependencies",
                "resources",
                "users",
                "environment",
            ]
        }
