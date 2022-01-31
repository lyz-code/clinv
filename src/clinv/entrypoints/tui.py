"""Define the TUI interfaces."""

import abc
import logging
from typing import Optional, Type

from prompt_toolkit.completion import FuzzyWordCompleter
from pydantic import ValidationError
from questionary import Style, autocomplete, text

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
            attribute_schema = schema["properties"][attribute]

            if attribute_schema["type"] == "string":
                question_text = f"{attribute_schema['title']}: "
                entity_data[attribute] = self._ask_choice(
                    question_text, attribute, choices, default
                )

            elif attribute_schema["type"] == "array":
                question_text = f"{attribute_schema['title']} (Enter to continue): "
                entity_data[attribute] = []
                while True:
                    choice = self._ask_choice(question_text, attribute, choices)
                    if choice == "":
                        break
                    entity_data[attribute].append(choice)
        try:
            return model(**entity_data)
        except ValidationError as error:
            log.warn("Error filling up the model")
            print(error)
            raise error
            return self.fill(model=model, entity_data=entity_data, choices=choices)

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
            attribute_choices = [choice for choice in choices[attribute].keys()]
        except KeyError:
            attribute_choices = []

        if len(attribute_choices) == 0:
            if default is not None:
                choice = text(question_text, default=default).ask()
            else:
                choice = text(question_text).ask()
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
            ).ask()

            if choice not in ["q", ""]:
                try:
                    choice = choices[attribute][choice]
                except KeyError:
                    log.warn(f"The choice {choice} is not between the valid ones")
                    choice = self._ask_choice(question_text, attribute, choices)

        if choice == "q":
            raise KeyboardInterrupt("Canceled the addition of the entity")

        return choice
