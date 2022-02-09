"""Define all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

import itertools
import logging
import operator
from contextlib import suppress
from typing import Generator, List, Optional, Type

from pydantic import ValidationError
from repository_orm import EntityNotFoundError, Repository
from rich.progress import track

from .adapters import AdapterSource
from .model import MODELS, RESOURCE_TYPES, Entity
from .model.aws import IAMGroup
from .model.risk import Project

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
            try:
                entity = entity_data.model(**entity_data.data)
            except ValidationError as error:
                log.error(
                    f"Can't build object {entity_data.model} "
                    f"with content {entity_data.data}"
                )
                raise error

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
        models = MODELS.copy()
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

    entities: List[Entity] = []
    for attribute in attributes:
        with suppress(EntityNotFoundError):
            new_entities = _filter_entities(
                repo.search({attribute: regexp}, models), all_, inactive
            )
            yield list(set(new_entities) - set(entities))
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

    Args:
        repo: Repository with all the entities.
        resource_types: Only retrieve the state of these type.

    Returns:
        List of unused entities.
    """
    active_entities = repo.search({"state": "active"}, _deduce_models())
    models_to_test = _deduce_models(resource_types, ignore=[Project, IAMGroup])
    try:
        unused_entities = set(repo.search({"state": "active"}, models_to_test))
    except EntityNotFoundError:
        return []

    for entity in active_entities:
        unused_entities = unused_entities - entity.uses(unused_entities)
        if len(unused_entities) == 0:
            break

    return list(unused_entities)
