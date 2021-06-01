"""Test the views of the program."""

from clinv import views
from clinv.model import Entity, EntityState, Information, Project


def test_get_data_to_print_omits_empty_fields() -> None:
    """
    Given: An entity with fields with value None or ''
    When: get_data_to_print is called
    Then: The empty fields are not shown
    """
    entity = Entity(id_=1, name=None, description="", state=EntityState.RUNNING)

    result = views.get_data_to_print(entity)

    assert result == [
        {"ID": "1", "State": EntityState.RUNNING, "_model_name": "Entity"}
    ]


def test_get_data_to_print_converts_bool_to_strings() -> None:
    """
    Given: An entity with fields of type bool
    When: get_data_to_print is called
    Then: The fields are converted to strings
    """
    entity = Information(id_=1, state=EntityState.RUNNING, personal_data=True)

    result = views.get_data_to_print(entity)

    assert result == [
        {
            "ID": "1",
            "State": EntityState.RUNNING,
            "Personal Data": "True",
            "_model_name": "Information",
        }
    ]


def test_get_data_to_print_handles_list_of_strings() -> None:
    """
    Given: An entity with fields of type List[str]
    When: get_data_to_print is called
    Then: The fields are converted to strings
    """
    entity = Project(id_=1, state=EntityState.RUNNING, aliases=["alias1", "alias2"])

    result = views.get_data_to_print(entity)

    assert result == [
        {
            "ID": "1",
            "State": EntityState.RUNNING,
            "Aliases": "alias1\nalias2",
            "_model_name": "Project",
        }
    ]
