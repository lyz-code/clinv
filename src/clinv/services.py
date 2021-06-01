"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

import itertools
import logging
import operator
from contextlib import suppress
from typing import Generator, List, Optional

from repository_orm import EntityNotFoundError, Repository
from rich.progress import track

from .adapters import AdapterSource
from .model import MODELS, RESOURCE_TYPES, Entity

log = logging.getLogger(__name__)


def update_sources(
    repo: Repository,
    adapter_sources: List[AdapterSource],
    resource_types: List[str],
) -> None:
    """Update the repository entities with the source adapters current state.

    Args:
        repo: Repository with all the entities.
        adapter_sources: List of source adapters to check.
        resource_types: Only retrieve the state of these types.
    """
    resource_models = [
        RESOURCE_TYPES[resource_type] for resource_type in resource_types
    ]
    try:
        active_resources = repo.search({"state": "active"}, resource_models)
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
    if resource_types is None or len(resource_types) == 0:
        models = MODELS
    else:
        models = [RESOURCE_TYPES[resource_type] for resource_type in resource_types]

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
    if resource_types is None or len(resource_types) == 0:
        models = MODELS
    else:
        models = [RESOURCE_TYPES[resource_type] for resource_type in resource_types]

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
