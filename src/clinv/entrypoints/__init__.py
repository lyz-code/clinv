"""Define the different ways to expose the program functionality.

Functions:
    load_logger: Configure the Logging logger.
"""

import logging
import os
from typing import List

from rich.logging import RichHandler

from ..adapters import AVAILABLE_SOURCES, AdapterSource
from ..config import Config

log = logging.getLogger(__name__)


# I have no idea how to test this function :(. If you do, please send a PR.
def load_logger(verbose: bool = False) -> None:  # pragma: no cover
    """Configure the Logging logger.

    Args:
        verbose: Set the logging level to Debug.
    """
    if verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="  %(message)s (%(name)s)",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="  %(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("goodconf").setLevel(logging.WARNING)


def load_config(config_path: str) -> Config:
    """Configure the Logging logger.

    Args:
        config_file: Path to the config file
    """
    config = Config()
    try:
        config.load(os.path.expanduser(config_path))
    except FileNotFoundError:
        config.load()

    return config


def load_adapters(config: "Config") -> List[AdapterSource]:
    """Configure the source adapters.

    Args:
        config: program configuration object.

    Returns:
        List of configured sources adapters to work with.
    """
    sources: List[AdapterSource] = []
    log.debug("Initializing the adapters")
    for source_name in config.sources:
        # ignore. AdapterSource is not callable. I still don't know how to fix this.
        sources.append(AVAILABLE_SOURCES[source_name]())  # type: ignore

    return sources
