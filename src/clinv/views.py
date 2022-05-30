"""Define the representations of the data."""

from contextlib import suppress
from operator import attrgetter
from typing import TYPE_CHECKING, Any, Dict, List

from rich import box
from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from .model import Entity, Service
    from .model.risk import NetworkAccessID


def print_entity(entity: "Entity") -> None:
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


def list_entities(entities: List["Entity"]) -> None:
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


def add_entities_to_table(table: Table, entities: List["Entity"]) -> None:
    """Add rows to a list table of entities."""
    for entity in entities:
        table.add_row(str(entity.id_), entity.name, entity.model_name)


# R0912: Too many branches 15/12, we should refactor the function when we have some
# time
def get_data_to_print(entity: "Entity") -> List[Dict[str, Any]]:  # noqa: R0912
    """Prepare the Entity attributes data to be printed.

    Args:
        entity: Entity to extract the data from.

    Returns:
        attributes: Dictionary with the attribute description and value
    """
    attrs_list: List[Dict[str, Any]] = [{"_model_name": entity.model_name}]
    for key, value in entity.dict().items():
        key = _snake_to_upper(key)
        if key == "Id ":
            key = "ID"
        if value is None or value == "":
            continue
        if isinstance(value, str):
            attrs_list[0][key] = value
        elif isinstance(value, (bool, int)):
            attrs_list[0][key] = str(value)
        elif isinstance(value, list):
            if len(value) == 0:
                continue
            if isinstance(value[0], (str, int)):
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


def service_risk(
    services: List["Service"], accesses: Dict["NetworkAccessID", str]
) -> None:
    """Print the list of entities."""
    table = Table(box=box.MINIMAL_HEAVY_HEAD)
    table.add_column("ID", justify="center", style="green")
    table.add_column("Name", justify="left", style="magenta")
    table.add_column("Exposition", justify="center", style="cyan")
    table.add_column("Risk", justify="center", style="cyan")
    table.add_column("Protection", justify="center", style="cyan")
    table.add_column("Security Value", justify="center", style="cyan")

    for service in services:

        if service.access is None:
            access = ""
        else:
            access = accesses[service.access]

        # W0212: Access of a protected attribute of service, but it's a property we
        # control so there is no problem
        table.add_row(
            str(service.id_),
            service.name,
            access,
            str(service._risk),  # noqa: W0212
            str(service._protection),  # noqa: W0212
            str(service._security),  # noqa: W0212
        )

    console = Console()
    console.print(table)
