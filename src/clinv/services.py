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
from typing import TYPE_CHECKING, Any, Dict, Generator, List, Optional, Type

from pydantic import ValidationError
from repository_orm import EntityNotFoundError, Repository
from rich.progress import track

from .adapters import AdapterSource
from .model import MODELS, RESOURCE_TYPES, Choices, Entity
from .model.aws import ASG, EC2, RDS, S3, IAMGroup, IAMUser, Route53
from .model.entity import Environment
from .model.risk import (
    AuthenticationMethod,
    Information,
    NetworkAccess,
    Person,
    Project,
    Service,
)

if TYPE_CHECKING:
    from .config import Config

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
    active_resources = [
        entity for model in models for entity in repo.search({"state": "active"}, model)
    ]
    stopped_resources = [
        entity
        for model in models
        for entity in repo.search({"state": "stopped"}, model)
    ]

    for source in adapter_sources:
        source_updates = source.update(
            resource_types, active_resources + stopped_resources
        )
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
    entities = _filter_entities(
        [entity for model in models for entity in repo.all(model)], all_, inactive
    )

    if len(entities) == 0:
        if resource_types is None or len(resource_types) == 0:
            raise EntityNotFoundError(
                "There are no entities in the repository that match the criteria."
            )
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
    criteria = operator.attrgetter("model_name")
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

    # ignore: Suddenly it started returning a type of List[ModelMetaClass] and I don't
    # know why
    return models  # type: ignore


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
    for model in models:
        new_entities = _filter_entities(
            [
                entity
                for attribute in attributes
                for entity in repo.search({attribute: regexp}, model)
            ],
            all_,
            inactive,
        )
        yield list(set(new_entities) - set(entities))
        entities += new_entities

    repo.close()
    if len(entities) == 0:
        if resource_types is None or len(resource_types) == 0:
            raise EntityNotFoundError(
                "There are no entities in the repository that match the criteria."
            )
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
    active_entities = [
        entity
        for model in _deduce_models()
        for entity in repo.search({"state": "active"}, model)
    ]

    models_to_test = _deduce_models(resource_types, ignore=[Project, IAMGroup])
    unused_entities = {
        entity
        for model in models_to_test
        for entity in repo.search({"state": "active"}, model)
    }

    for entity in active_entities:
        unused_entities = unused_entities - entity.uses(unused_entities)
        if len(unused_entities) == 0:
            break

    repo.close()
    return list(unused_entities)


def build_choices(repo: Repository, config: "Config", model: Type[Entity]) -> Choices:
    """Create the possible choices of the attributes of a model."""
    choices: Choices = {}

    # Build choices from models
    if model == Project:
        attribute_models: Dict[str, Any] = {
            "responsible": Person,
            "services": Service,
            "informations": Information,
            "people": Person,
        }
    elif model == Service:
        attribute_models = {
            "access": NetworkAccess,
            "responsible": Person,
            "authentication": AuthenticationMethod,
            "informations": Information,
            "dependencies": Service,
            "resources": (ASG, EC2, RDS, S3, IAMGroup, IAMUser, Route53),
            "environment": Environment,
        }
    elif model == Information:
        attribute_models = {
            "responsible": Person,
        }
    elif model == Person:
        attribute_models = {
            "iam_user": IAMUser,
        }

    for key, value in attribute_models.items():
        choices[key] = _build_attribute_choices(repo=repo, model=value)

    # Build choices from config
    if model == Service:
        choices["users"] = {value: value for value in config.service_users}

    return choices


@lru_cache()
def _build_attribute_choices(
    repo: Repository,
    # ANN401: Any is not allowed. This case it's hard to create a typing for model,
    # and all cases are handled.
    model: Any,  # noqa: ANN401
    model_name: bool = False,
) -> Dict[str, Any]:
    """Create the possible choices of the attributes of the project model."""
    choices: Dict[str, str] = {}
    if isinstance(model, tuple):
        for item in model:
            choices.update(_build_attribute_choices(repo, item, model_name=True))
        return choices
    if isinstance(model, type(Entity)):
        for entity in repo.search({"state": "active"}, model):
            if entity.name is None:
                continue
            if model_name:
                name = f"{entity.name} ({entity.model_name})"
            else:
                name = entity.name
            choices[name] = str(entity.id_)
        return choices
    if isinstance(model, EnumMeta):
        return {  # type: ignore
            str(attribute.value): str(attribute.value) for attribute in model
        }
    raise ValueError("Model not recognized when extracting possible choices")


def next_id(repo: Repository, model: Type[Entity]) -> str:
    """Return the next id of a model."""
    try:
        last_entity = max(repo.all(model))
    except ValueError:
        return f"{model.__name__.lower()[:3]}_001"
    last_id = str(last_entity.id_).split("_")
    new_id = f"{last_id[0]}_{int(last_id[1]) + 1:03}"
    return new_id


def add(repo: Repository, entity: Entity) -> None:
    """Add an entity to the repository."""
    repo.add(entity)
    repo.commit()
