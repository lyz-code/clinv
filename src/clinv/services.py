"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

import itertools
import logging
import operator
from contextlib import suppress
from typing import Generator, List, Optional, Type

from repository_orm import EntityNotFoundError, Repository
from rich.progress import track

from .adapters import AdapterSource
from .model import MODELS, RESOURCE_TYPES, Entity
from .model.aws import VPC, IAMGroup, SecurityGroup
from .model.risk import People, Project, Service

log = logging.getLogger(__name__)


def update_sources(
    repo: Repository,
    adapter_sources: List[AdapterSource],
    resource_types: Optional[List[str]] = None,
) -> None:
    """Update the repository entities with the source adapters current state.

    Args:
        repo: Repository with all the entities.
        adapter_sources: List of source adapters to check.
        resource_types: Only retrieve the state of these types.
    """
    models = _deduce_models(resource_types)
    try:
        active_resources = repo.search({"state": "active"}, models)
    except EntityNotFoundError:
        active_resources = []

    for source in adapter_sources:
        source_updates = source.update(resource_types, active_resources)
        for entity_data in track(source_updates, description="Updating repo data"):
            entity = entity_data.model(**entity_data.data)

            repo.add(entity)

    log.info("Committing changes")
    repo.commit()


def list_entities(
    repo: Repository,
    resource_types: Optional[List[str]] = None,
    all_: bool = False,
    inactive: bool = False,
) -> List[Entity]:
    """List the resources of the repository.

    Args:
        repo: Repository with all the entities.
        resource_types: Only retrieve the state of these types.
        all_: Whether to show active and inactive resources. Default: False
        inactive: Whether to show inactive resources. Default: False

    Returns:
        List of entities that match the criteria
    """
    models = _deduce_models(resource_types)
    entities = _filter_entities(repo.all(models), all_, inactive)

    if len(entities) == 0:
        if resource_types is None or len(resource_types) == 0:
            raise EntityNotFoundError(
                "There are no entities in the repository that match the criteria."
            )
        else:
            raise EntityNotFoundError(
                f"There are no entities of type {', '.join(resource_types)} in the "
                "repository that match the criteria."
            )
    return entities


def _filter_entities(
    entities: List[Entity], all_: bool = False, inactive: bool = False
) -> List[Entity]:
    """Group by type and filter out entities that don't match the criteria.

    Args:
        table: where to add the columns
        entities: List of entities
        all_: Whether to show active and inactive resources. Default: False
        inactive: Whether to show inactive resources. Default: False
    """
    criteria = operator.attrgetter("_model_name")
    input_entities = sorted(entities, key=criteria)
    entity_groups = {
        sorted_key: list(element)
        for sorted_key, element in itertools.groupby(input_entities, key=criteria)
    }

    output_entities = []
    for _, elements in entity_groups.items():
        for element in elements:
            if (element.state == "terminated" and not inactive and not all_) or (
                element.state != "terminated" and inactive
            ):
                continue

            output_entities.append(element)

    return output_entities


ListTypeEntity = List[Type[Entity]]


def _deduce_models(
    resource_types: Optional[List[str]] = None,
    ignore: Optional[ListTypeEntity] = None,
) -> List[Type[Entity]]:
    """Select the model classes from a list of resource type strings.

    Args:
        resource_types: Identifiers of the models to select.
        ignore: List of models to ignore
    """
    if resource_types is None or len(resource_types) == 0:
        models = MODELS
    else:
        models = [RESOURCE_TYPES[resource_type] for resource_type in resource_types]

    if ignore is not None:
        for model in ignore:
            with suppress(ValueError):
                models.remove(model)

    return models


def search(
    repo: Repository,
    regexp: str,
    all_: bool = False,
    inactive: bool = False,
    resource_types: Optional[List[str]] = None,
) -> Generator[List[Entity], None, None]:
    """Search resources whose attribute match the regular expression.

    Args:
        repo: Repository with all the entities.
        regexp: Regular expression that the entity attributes must match.
        resource_types: Only retrieve the state of these type.
        all_: Whether to show active and inactive resources. Default: False
        inactive: Whether to show inactive resources. Default: False

    Returns:
        List of entities that match the criteria.
    """
    models = _deduce_models(resource_types)

    # Attributes to search
    attributes = []
    for model in models:
        for attribute in model.schema()["properties"].keys():
            if attribute not in attributes:
                attributes.append(attribute)

    entities = []
    for attribute in attributes:
        with suppress(EntityNotFoundError):
            new_entities = _filter_entities(
                repo.search({attribute: regexp}, models), all_, inactive
            )
            yield new_entities
            entities += new_entities

    if len(entities) == 0:
        if resource_types is None or len(resource_types) == 0:
            raise EntityNotFoundError(
                "There are no entities in the repository that match the criteria."
            )
        else:
            raise EntityNotFoundError(
                f"There are no entities of type {', '.join(resource_types)} in the "
                "repository that match the criteria."
            )


def unused(
    repo: Repository,
    resource_types: Optional[List[str]] = None,
) -> List[Entity]:
    """Search for not used resources.

    Resources are marked as unused if they are:

    * Infrastructure resources that are not used by a Service or other infrastructure
        resources.
    * Service resources that are not used by a Project.

    The next resources won't show up in the report because:

    * Project: can't be used by any other resource.
    * IAMGroup: until we don't have the concept of group of people doesn't make sense
        to be used by any service or project.
    * VPC: doesn't make any sense to be used by a project or service either.

    Args:
        repo: Repository with all the entities.
        resource_types: Only retrieve the state of these type.

    Returns:
        List of unused entities.
    """
    # Projects are never unused
    models = _deduce_models(
        resource_types, ignore=[Project, IAMGroup, VPC, SecurityGroup]
    )

    try:
        services = repo.search({"state": "active"}, [Service])
        service_resources = (
            # Informations used by Services
            [str(info_id) for service in services for info_id in service.informations]
            # Resources used by Services
            + [
                str(resource_id)
                for service in services
                for resource_id in service.resources
            ]
        )
    except EntityNotFoundError:
        service_assigned_resources = []

    try:
        projects = repo.search({"state": "active"}, [Project])
        project_assigned_resources = (
            # Services assigned to Projects
            [str(service_id) for project in projects for service_id in project.services]
            # People assigned to Projects
            + [str(person_id) for project in projects for person_id in project.people]
            # Informations assigned to Projects
            + [str(info_id) for project in projects for info_id in project.informations]
        )
    except EntityNotFoundError:
        project_assigned_resources = []

    try:
        people = repo.search({"state": "active"}, [People])
        people_assigned_resources = (
            # IAM Users assigned to People
            [person.iam_user for person in people if person.iam_user]
        )
    except EntityNotFoundError:
        people_assigned_resources = []

    try:
        resources = repo.search({"state": "active"}, models)
    except EntityNotFoundError:
        return []

    assigned_resources = set(
        project_assigned_resources
        + people_assigned_resources
        + service_assigned_resources
    )

    return [
        resource for resource in resources if resource.id_ not in assigned_resources
    ]
