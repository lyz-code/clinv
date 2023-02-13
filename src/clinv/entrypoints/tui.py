"""Define the TUI interfaces."""

import abc
import logging
import re
from typing import Any, Dict, Optional, Type

from prompt_toolkit.completion import FuzzyWordCompleter
from pydantic import ValidationError
from questionary import Style, autocomplete, confirm, text

from ..model import Choices
from ..model.entity import Entity, EntityAttrs

log = logging.getLogger(__name__)


class Prompter(abc.ABC):
    """Define the prompter interface."""

    @abc.abstractmethod
    def fill(
        self,
        model: Type[Entity],
        entity_data: EntityAttrs,
        choices: Optional[Choices] = None,
    ) -> Entity:
        """Ask the user to fill up the model attributes."""
        raise NotImplementedError


class PydanticQuestions(Prompter):
    """Define the prompter to fill up pydantic attributes using the questionary lib."""

    def fill(
        self,
        model: Type[Entity],
        entity_data: EntityAttrs,
        choices: Optional[Choices] = None,
    ) -> Entity:
        """Ask the user to fill up the model attributes.

        Args:
            model: the type of entity to add
            choices: A dictionary with the possible values of the attributes, where
                the key is the attribute name, and the value is a dictionary of the
                text to show in the completer, and the value is the desired value
                of that key. For example:

                choices = {
                    'services': {
                        'First service': 'ser_01',
                        'Second service': 'ser_02',
                    }
                }

        Raises:
            KeyboardInterrupt: if the user canceled the fill up.
        """
        print("Enter q to abort")
        if choices is None:
            choices = {}

        schema = model.schema()

        for attribute in schema["tui_fields"]:
            try:
                default = entity_data[attribute]
            except KeyError:
                default = None
            attribute_schema = self._get_attribute_schema(schema, attribute)
            attribute_type = attribute_schema["type"]
            attribute_title = attribute_schema["title"]

            if attribute_type == "string":
                question_text = f"{attribute_title}: "
                entity_data[attribute] = self._ask_choice(
                    question_text, attribute, choices, default
                )
            elif attribute_type == "integer":
                question_text = f"{attribute_title}: "
                entity_data[attribute] = int(
                    self._ask_choice(question_text, attribute, choices, default)
                )
            elif attribute_type == "boolean":
                entity_data[attribute] = confirm(f"{attribute_title}: ").unsafe_ask()
            elif attribute_type == "array":
                question_text = f"{attribute_title} (Enter to continue): "
                entity_data[attribute] = []
                while True:
                    choice = self._ask_choice(question_text, attribute, choices)
                    if choice == "":
                        break
                    entity_data[attribute].append(choice)
        try:
            return model(**entity_data)
        except ValidationError as error:
            log.warning("Error filling up the model")
            print(error)
            return self.fill(model=model, entity_data=entity_data, choices=choices)

    @staticmethod
    def _get_attribute_schema(schema: Dict[str, Any], attribute: str) -> Dict[str, Any]:
        """Get the schema of the attribute."""
        attribute_schema = schema["properties"][attribute]
        if "$ref" in attribute_schema:
            definition = re.sub("#/definitions/", "", attribute_schema["$ref"])
            attribute_schema = schema["definitions"][definition]
        elif (
            "type" in attribute_schema
            and attribute_schema["type"] == "array"
            and "$ref" in attribute_schema["items"]
        ):
            definition = re.sub("#/definitions/", "", attribute_schema["items"]["$ref"])
            attribute_schema = schema["definitions"][definition]
            attribute_schema["type"] = "array"
        return attribute_schema

    def _ask_choice(
        self,
        question_text: str,
        attribute: str,
        choices: Choices,
        default: Optional[str] = None,
    ) -> str:
        """Ask the user to fill up a choice.

        Returns:
            The desired text

        Raises:
            KeyboardInterrupt: if the user canceled the fill up.
        """
        try:
            attribute_choices = list(choices[attribute].keys())
        except KeyError:
            attribute_choices = []

        if len(attribute_choices) == 0:
            if default is not None:
                choice = text(question_text, default=default).unsafe_ask()
            else:
                choice = text(question_text).unsafe_ask()
        else:
            style = Style(
                [
                    ("separator", "bg:#002b36 fg:#cc5454"),
                    ("qmark", "bg:#002b36  fg:#673ab7 bold"),
                    ("question", "bg:#002b36 fg:#657b83"),
                    ("selected", "fg:#657b83 bg:#002b36"),
                    ("pointer", "fg:#673ab7 bold"),
                    ("highlighted", "fg:#673ab7 bold"),
                    ("answer", "bg:#002b36 #657b83"),
                    ("text", "bg:#002b36 fg:#657b83"),
                ]
            )
            choice = autocomplete(
                question_text,
                choices=attribute_choices,
                completer=FuzzyWordCompleter(attribute_choices),
                style=style,
            ).unsafe_ask()

            if choice not in ["q", ""]:
                try:
                    choice = choices[attribute][choice]
                except KeyError:
                    log.warning(f"The choice {choice} is not between the valid ones")
                    choice = self._ask_choice(question_text, attribute, choices)

        if choice == "q":
            raise KeyboardInterrupt("Canceled the addition of the entity")

        return choice
