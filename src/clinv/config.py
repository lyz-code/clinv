"""Define the configuration of the main program."""

import logging
import os
from collections import UserDict
from typing import Any, Dict, List, Union

from ruyaml import YAML
from ruyaml.parser import ParserError
from ruyaml.scanner import ScannerError

# It complains that ruamel.yaml doesn't have the object YAML, but it does.

log = logging.getLogger(__name__)


class ConfigError(Exception):
    """Catch configuration errors."""


# R0901: UserDict has too many ancestors. Right now I don't feel like switching to
#   another base class, as `dict` won't work straight ahead.
# type ignore: I haven't found a way to specify the type of the generic UserDict class.
class Config(UserDict):  # type: ignore # noqa: R0901
    """Expose the configuration in a friendly way.

    Public methods:
        get: Fetch the configuration value of the specified key.
        load: Load the configuration from the configuration YAML file.
        save: Saves the configuration in the configuration YAML file.

    Attributes and properties:
        config_path (str): Path to the configuration file.
        data(dict): Program configuration.
    """

    def __init__(self, config_path: str = "~/.local/share/clinv/config.yaml") -> None:
        """Configure the attributes and load the configuration."""
        super().__init__()
        self.config_path = os.path.expanduser(config_path)
        self.load()

    def get(
        self, key: str, default: Any = None
    ) -> Union[str, int, Dict[str, Any], List[Any]]:
        """Fetch the configuration value of the specified key.

        If there are nested dictionaries, a dot notation can be used.

        So if the configuration contents are:

        self.data = {
            'first': {
                'second': 'value'
            },
        }

        self.data.get('first.second') == 'value'
        """
        original_key = key
        config_keys = key.split(".")
        value = self.data.copy()

        for config_key in config_keys:
            try:
                value = value[config_key]
            except KeyError as error:
                if default is not None:
                    return default
                raise ConfigError(
                    f"Failed to fetch the configuration {config_key} "
                    f"when searching for {original_key}"
                ) from error

        return value

    def set(self, key: str, value: Union[str, int]) -> None:
        """Set the configuration value of the specified key.

        If there are nested dictionaries, a dot notation can be used.

        So if you want to set the configuration:

        self.data = {
            'first': {
                'second': 'value'
            },
        }

        self.data.set('first.second', 'value')
        """
        config_keys: List[str] = key.split(".")
        last_key = config_keys.pop(-1)

        # Initialize the dictionary structure
        parent = self.data
        for config_key in config_keys:
            try:
                parent = parent[config_key]
            except KeyError:
                parent[config_key] = {}
                parent = parent[config_key]

        # Set value
        parent[last_key] = value

    def load(self) -> None:
        """Load the configuration from the configuration YAML file."""
        try:
            with open(os.path.expanduser(self.config_path), "r") as file_cursor:
                try:
                    self.data = YAML().load(file_cursor)
                except (ParserError, ScannerError) as error:
                    raise ConfigError(str(error)) from error
        except FileNotFoundError as error:
            raise ConfigError(
                "The configuration file {self.config_path} could not be found."
            ) from error

    def save(self) -> None:
        """Save the configuration in the configuration YAML file."""
        with open(os.path.expanduser(self.config_path), "w+") as file_cursor:
            yaml = YAML()
            yaml.default_flow_style = False
            yaml.dump(self.data, file_cursor)
