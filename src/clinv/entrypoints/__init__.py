"""Define the different ways to expose the program functionality.

Functions:
    load_logger: Configure the Logging logger.
"""

import logging
import sys
from typing import List

from rich.logging import RichHandler

from ..adapters import AVAILABLE_SOURCES, AdapterSource
from ..config import Config, ConfigError

log = logging.getLogger(__name__)


# I have no idea how to test this function :(. If you do, please send a PR.
def load_logger(verbose: bool = False) -> None:  # pragma: no cover
    """Configure the Logging logger.

    Args:
        verbose: Set the logging level to Debug.
    """
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    if verbose:
        logging.basicConfig(
            stream=sys.stderr, level=logging.DEBUG, format="%(message)s"
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )


def load_config(config_path: str) -> Config:
    """Load the configuration from the file."""
    log.debug(f"Loading the configuration from file {config_path}")
    try:
        config = Config(config_path)
    except ConfigError as error:
        log.error(
            f"Error parsing yaml of configuration file {config_path}: {str(error)}"
        )
        sys.exit(1)

    return config


def load_adapters(config: Config) -> List[AdapterSource]:
    """Configure the source adapters.

    Args:
        config: program configuration object.

    Returns:
        List of configured sources adapters to work with.
    """
    sources: List[AdapterSource] = []
    log.debug("Initializing the adapters")
    for source_name in config["sources"]:
        # ignore. AdapterSource is not callable. I still don't know how to fix this.
        sources.append(AVAILABLE_SOURCES[source_name]())  # type: ignore

    return sources
