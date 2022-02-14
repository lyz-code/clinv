"""Define all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

import itertools
import logging
import operator
from contextlib import suppress
from enum import EnumMeta
from functools import lru_cache
from typing import Any, Dict, Generator, List, Optional, Type

from pydantic import ValidationError
from repository_orm import EntityNotFoundError, Repository
from rich.progress import track

from .adapters import AdapterSource
from .model import MODELS, RESOURCE_TYPES, Choices, Entity
from .model.aws import IAMGroup
from .model.risk import (
    AuthenticationMethod,
    Information,
    People,
    Project,
    Service,
    ServiceAccess,
)

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
    repo.close()


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

    repo.close()
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

    repo.close()
    return list(unused_entities)


def build_choices(repo: Repository, model: Type[Entity]) -> Choices:
    """Create the possible choices of the attributes of a model."""
    choices: Choices = {}

    if model == Project:
        attribute_models: Dict[str, Any] = {
            "responsible": People,
            "services": Service,
            "informations": Information,
            "people": People,
        }
    elif model == Service:
        attribute_models = {
            "access": ServiceAccess,
            "responsible": People,
            "authentication": AuthenticationMethod,
            "informations": Information,
            "dependencies": Service,
            "people": People,
        }

    for key, value in attribute_models.items():
        choices[key] = _build_attribute_choices(repo=repo, model=value)

    return choices


@lru_cache()
def _build_attribute_choices(repo: Repository, model: Any) -> Dict[str, str]:
    """Create the possible choices of the attributes of the project model."""
    if isinstance(model, type(Entity)):
        return {
            entity.name: str(entity.id_)
            for entity in repo.search({"state": "active"}, [model])
            if entity.name is not None
        }
    elif isinstance(model, EnumMeta):
        return {attribute: "" for attribute in model}
    raise ValueError("Model not recognized when extracting possible choices")


def next_id(repo: Repository, model: Type[Entity]) -> str:
    """Return the next id of a model."""
    try:
        last_entity = max(repo.all([model]))
    except ValueError:
        raise ValueError(model)
    last_id = str(last_entity.id_).split("_")
    new_id = f"{last_id[0]}_{int(last_id[1]) + 1}"
    return new_id


def add(repo: Repository, entity: Entity) -> None:
    """Add an entity to the repository."""
    repo.add(entity)
    repo.commit()
