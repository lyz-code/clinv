"""Command line interface definition."""

import logging
import sys
from contextlib import suppress
from typing import List, Optional

import click
from click.core import Context
from repository_orm import EntityNotFoundError, load_repository
from rich import box
from rich.live import Live
from rich.table import Table

from .. import services, views
from ..model import MODELS, RESOURCE_NAMES, RESOURCE_TYPES
from ..model.entity import EntityState
from ..version import version_info
from . import load_adapters, load_config, load_logger
from .tui import PydanticQuestions

log = logging.getLogger(__name__)


@click.group()
@click.version_option(version="", message=version_info())
@click.option(
    "-c",
    "--config_path",
    default="~/.local/share/clinv/config.yaml",
    help="configuration file path",
    envvar="CLINV_CONFIG_PATH",
)
@click.option("-v", "--verbose", is_flag=True)
@click.pass_context
def cli(ctx: Context, config_path: str, verbose: bool) -> None:
    """Command line DevSecOps asset inventory."""
    ctx.ensure_object(dict)
    load_logger(verbose)
    config = load_config(config_path)
    ctx.obj["config"] = config
    ctx.obj["repo"] = load_repository(config.database_url)
    ctx.obj["adapters"] = load_adapters(config)
    ctx.obj["prompter"] = PydanticQuestions()


@cli.command()
@click.pass_context
@click.argument(
    "resource_types",
    type=click.Choice(RESOURCE_NAMES),
    required=False,
    nargs=-1,
)
def update(ctx: Context, resource_types: List[str]) -> None:
    """Sync the inventory state with the resource providers."""
    if len(resource_types) == 0:
        resource_types = RESOURCE_NAMES

    services.update_sources(ctx.obj["repo"], ctx.obj["adapters"], resource_types)


@cli.command(name="print")
@click.pass_context
@click.argument("resource_id", type=str)
def print_(ctx: Context, resource_id: str) -> None:
    """Print the information of the resource."""
    repo = ctx.obj["repo"]

    for model in MODELS:
        with suppress(EntityNotFoundError):
            entity = repo.get(resource_id, model)
            repo.close()
            views.print_entity(entity)
            break

    if not repo.is_closed:
        model_names = [model.__name__ for model in MODELS]
        log.error(
            f'There are no entities of type {", ".join(model_names)} in the repository '
            f"with id {resource_id}."
        )
        repo.close()
        sys.exit(1)


@cli.command(name="list")
@click.pass_context
@click.argument(
    "resource_types", type=click.Choice(RESOURCE_NAMES), required=False, nargs=-1
)
@click.option("-a", "--all", "all_", is_flag=True)
@click.option("-i", "--inactive", is_flag=True)
def list_(
    ctx: Context, all_: bool, inactive: bool, resource_types: Optional[List[str]] = None
) -> None:
    """List the resources in the repository."""
    try:
        entities = services.list_entities(
            ctx.obj["repo"], resource_types, all_=all_, inactive=inactive
        )
    except EntityNotFoundError as error:
        log.error(str(error))
        ctx.obj["repo"].close()
        sys.exit(1)
    ctx.obj["repo"].close()

    views.list_entities(entities)


@cli.command(name="search")
@click.pass_context
@click.argument("regexp", type=str)
@click.argument(
    "resource_types", type=click.Choice(RESOURCE_NAMES), required=False, nargs=-1
)
@click.option("-a", "--all", "all_", is_flag=True)
@click.option("-i", "--inactive", is_flag=True)
def search(
    ctx: Context,
    regexp: str,
    all_: bool,
    inactive: bool,
    resource_types: Optional[List[str]] = None,
) -> None:
    """Search resources whose attribute match the regular expression."""
    # Build table
    table = Table(box=box.MINIMAL_HEAVY_HEAD)
    table.add_column("ID", justify="left", style="green")
    table.add_column("Name", justify="left", style="magenta")
    table.add_column("Type", justify="center", style="cyan")
    with Live(table, refresh_per_second=4, vertical_overflow="visible"):
        try:
            for entities in services.search(
                ctx.obj["repo"],
                regexp,
                all_=all_,
                inactive=inactive,
                resource_types=resource_types,
            ):
                views.add_entities_to_table(
                    table,
                    entities,
                )
        except EntityNotFoundError as error:
            log.error(str(error))
            ctx.obj["repo"].close()
            sys.exit(1)
    ctx.obj["repo"].close()


@cli.command(name="unused")
@click.pass_context
@click.argument(
    "resource_types", type=click.Choice(RESOURCE_NAMES), required=False, nargs=-1
)
def unused(
    ctx: Context,
    resource_types: Optional[List[str]] = None,
) -> None:
    """Search resources that don't belong to a Service or Project."""
    entities = services.unused(ctx.obj["repo"], resource_types)
    ctx.obj["repo"].close()

    views.list_entities(entities)


@cli.command(name="add")
@click.pass_context
@click.argument(
    "resource_type",
    type=click.Choice(["pro", "ser", "per", "inf", "auth", "net", "risk", "sec"]),
)
def add(ctx: Context, resource_type: str) -> None:
    """Add resources."""
    prompter = ctx.obj["prompter"]
    repo = ctx.obj["repo"]
    config = ctx.obj["config"]

    model = RESOURCE_TYPES[resource_type]
    choices = services.build_choices(repo, config, model)  # type: ignore
    entity_data = {
        "id_": services.next_id(repo, model),  # type: ignore
        "state": EntityState.RUNNING,
    }
    resource = prompter.fill(model=model, choices=choices, entity_data=entity_data)

    services.add(repo, resource)


@cli.command(name="risk")
@click.pass_context
def risk(
    ctx: Context,
) -> None:
    """Show an ordered list of services by the security value."""
    services_ = services.service_risk(ctx.obj["repo"])
    accesses = services.accesses(ctx.obj["repo"])
    ctx.obj["repo"].close()

    views.service_risk(services_, accesses)


@cli.command(hidden=True)
def null() -> None:
    """Do nothing.

    Used for the tests until we have a better solution.
    """


if __name__ == "__main__":  # pragma: no cover
    cli()  # pylint: disable=E1120
