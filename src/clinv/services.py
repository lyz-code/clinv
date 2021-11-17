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
from .model.risk import Project, Service

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


def unassigned(
    repo: Repository,
    resource_types: Optional[List[str]] = None,
) -> List[Entity]:
    """Search for not assigned resources.

    Resources are marked as unassigned if they are:
    * Infrastructure resources that are not assigned to a Service
    * Service resources that are not assigned to a Project

    Args:
        repo: Repository with all the entities.
        resource_types: Only retrieve the state of these type.

    Returns:
        List of unassigned entities.
    """
    # Projects are never unassigned
    models = _deduce_models(resource_types, ignore=[Project])

    try:
        services = repo.search({"state": "active"}, [Service])
    except EntityNotFoundError:
        services = []
    try:
        projects = repo.search({"state": "active"}, [Project])
    except EntityNotFoundError:
        projects = []
    try:
        resources = repo.search({"state": "active"}, models)
    except EntityNotFoundError:
        return []

    assigned_resources = (
        # Services assigned to Projects
        [str(service_id) for project in projects for service_id in project.services]
        # People assigned to Projects
        + [str(person_id) for project in projects for person_id in project.people]
        # Informations assigned to Projects
        + [str(info_id) for project in projects for info_id in project.informations]
        # Informations assigned to Services
        + [str(info_id) for service in services for info_id in service.informations]
        # Resources assigned to Services
        + [
            str(resource_id)
            for service in services
            for resource_id in service.resources
        ]
    )
    return [
        resource for resource in resources if resource.id_ not in assigned_resources
    ]
