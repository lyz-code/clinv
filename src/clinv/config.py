"""Define the configuration of the main program."""

import os
from enum import Enum
from typing import List

from goodconf import GoodConf


class LogLevel(str, Enum):
    """Define the possible log levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Config(GoodConf):  # type: ignore
    """Define the configuration of the program."""

    log_level: LogLevel = LogLevel.INFO
    database_url: str = "tinydb://~/.local/share/clinv/database.tinydb"

    # Where should clinv search for entities for the inventory.
    sources: List[str] = ["aws", "risk"]

    # Level of logging verbosity. One of ['info', 'debug', 'warning'].
    verbose: str = "info"

    # Type of users
    service_users: List[str] = [
        "admins",
        "authenticated_users",
        "unauthenticated_users",
        "internal_services",
        "external_services",
    ]

    class Config:
        """Define the default files to check."""

        env_previx = "CLINV_"
        default_files = [
            os.path.expanduser("~/.local/share/clinv/config.yaml"),
            "config.yaml",
        ]
