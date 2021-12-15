"""Define the representations of the data."""

from contextlib import suppress
from operator import attrgetter
from typing import Any, Dict, List

from rich import box
from rich.console import Console
from rich.table import Table

from .model import Entity


def print_entity(entity: Entity) -> None:
    """Print the entity attributes.

    Args:
        entity: Entity whose attributes to print.
    """
    data = get_data_to_print(entity)
    console = Console()

    # There are two types of data to print, one contains the attributes of an
    # element, and the other contains a list of element attributes. The last case
    # is common of attributes that contain a list of other Pydantic objects.

    for attr_group in data:
        model_name = attr_group.pop("_model_name")

        if "header" in attr_group:
            table = Table(box=box.MINIMAL_HEAVY_HEAD, title=model_name)
            for header in attr_group["header"]:
                table.add_column(header, justify="left")

            for element in attr_group["elements"]:
                table.add_row(*element)
        else:
            table = Table(box=box.MINIMAL_HEAVY_HEAD)
            table.add_column("Type", justify="left", style="green")
            table.add_column(model_name, justify="left")

            for attribute, value in attr_group.items():
                table.add_row(attribute, value)

        console.print(table)


def list_entities(entities: List[Entity]) -> None:
    """Print the list of entities."""
    table = Table(box=box.MINIMAL_HEAVY_HEAD)
    table.add_column("ID", justify="left", style="green")
    table.add_column("Name", justify="left", style="magenta")
    table.add_column("Type", justify="center", style="cyan")

    # Group the entities by entity type
    entities.sort()
    entities.sort(key=attrgetter("__class__.__name__"))
    add_entities_to_table(table, entities)

    console = Console()
    console.print(table)


def add_entities_to_table(table: Table, entities: List[Entity]) -> None:
    """Add rows to a list table of entities."""
    for entity in entities:
        table.add_row(str(entity.id_), entity.name, entity._model_name)


def get_data_to_print(entity: Entity) -> List[Dict[str, Any]]:
    """Prepare the Entity attributes data to be printed.

    Args:
        entity: Entity to extract the data from.

    Returns:
        attributes: Dictionary with the attribute description and value
    """
    # W0212: accessed to a private attribute, but we need it to be that way
    attrs_list: List[Dict[str, Any]] = [
        {"_model_name": entity._model_name}  # noqa: W0212
    ]
    for key, value in entity.dict().items():
        key = _snake_to_upper(key)
        if key == "Id ":
            key = "ID"
        if value is None or value == "":
            continue
        elif isinstance(value, str):
            attrs_list[0][key] = value
        elif isinstance(value, (bool, int)):
            attrs_list[0][key] = str(value)
        elif isinstance(value, list):
            if len(value) == 0:
                continue
            elif isinstance(value[0], (str, int)):
                try:
                    attrs_list[0][key] = "\n".join(value)
                except TypeError:
                    # We don't yet have any entity with type List[int] so we can't
                    # test this functionality yet
                    attrs_list[0][key] = "\n".join([str(element) for element in value])
            else:
                with suppress(AttributeError):
                    submodel_attrs: Dict[str, Any] = {
                        "_model_name": key,
                        "header": [
                            _snake_to_upper(attr_name) for attr_name in value[0].keys()
                        ],
                        "elements": [],
                    }

                    for sub_value in value:
                        row = []
                        for _, sub_attr in sub_value.items():
                            if sub_attr is None or isinstance(sub_attr, (str, int)):
                                row.append(sub_attr)
                            elif isinstance(sub_attr, list):
                                try:
                                    row.append("\n".join(sub_attr))
                                except TypeError:
                                    row.append(
                                        "\n".join(
                                            [str(element) for element in sub_attr]
                                        )
                                    )

                        submodel_attrs["elements"].append(row)
                    attrs_list.append(submodel_attrs)
    return attrs_list


def _snake_to_upper(string: str) -> str:
    """Convert a string from snake case to upper case words.

    Args:
        string:
    """
    return " ".join([word.capitalize() for word in string.split("_")])
