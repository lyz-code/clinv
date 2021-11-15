"""Tests the service layer."""

from repository_orm import FakeRepository, Repository

from clinv.adapters import FakeSource
from clinv.services import search, update_sources

from ..factories import EC2Factory, PeopleFactory


def test_update_sources_creates_new_entity(
    repo: FakeRepository, source: FakeSource
) -> None:
    """
    Given: An empty fake repository.
    When: update_sources contains data of a new entity
    Then: The entity is added to the repo
    """
    entity = PeopleFactory.create()
    source.add_change(entity, entity.dict())

    update_sources(repo, [source], ["peo"])  # act

    repo_entity = repo.get(entity.id_, type(entity))
    assert repo_entity == entity


def test_update_sources_updates_entity_data(
    repo: FakeRepository, source: FakeSource
) -> None:
    """
    Given: A fake repository with an existent entity
    When: update_sources contains data that updates part of its attributes
    Then: The updated attributes are changed, and the others aren't.
    """
    # Add the existent entity
    entity = PeopleFactory.create(state="active")
    repo.add(entity)
    repo.commit()
    # Change the entity attribute
    entity.name = "Changed name"
    # Configure the fake source adapter to show the changes
    source.add_change(entity, {"name": entity.name})

    update_sources(repo, [source], ["peo"])  # act

    repo_entity = repo.get(entity.id_, type(entity))
    assert repo_entity.name == "Changed name"
    assert repo_entity.description == entity.description


def test_search_finds_ips_in_ec2_instances(repo: Repository) -> None:
    """
    Given: A repository with an ec2 instance
    When: search by a regular expression of the ip
    Then: the entity is found.
    """
    entity = EC2Factory.create(state="active")
    entity.private_ips = ["192.168.1.2"]
    repo.add(entity)
    repo.commit()
    regexp = r"192.*"
    found_entities = []

    for entities in search(repo, regexp):  # act
        found_entities += entities

    assert found_entities == [entity]
