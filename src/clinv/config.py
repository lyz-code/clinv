"""Define the configuration of the main program."""

import os
from typing import List

from goodconf import GoodConf


class Config(GoodConf):  # type: ignore
    """Configure the frontend."""

    database_url: str = "tinydb://~/.local/share/clinv/database.tinydb"

    # Where should clinv search for entities for the inventory.
    sources: List[str] = ["aws", "risk"]

    # Level of logging verbosity. One of ['info', 'debug', 'warning'].
    verbose: str = "info"

    class Config:
        """Define the default files to check."""

        env_previx = "CLINV_"
        default_files = [
            os.path.expanduser("~/.local/share/clinv/config.yaml"),
            "config.yaml",
        ]
