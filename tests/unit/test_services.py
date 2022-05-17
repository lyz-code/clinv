"""Tests the service layer."""

import pytest
from repository_orm import FakeRepository, Repository
from tests.factories import (
    EC2Factory,
    IAMGroupFactory,
    PersonFactory,
    ProjectFactory,
    ServiceFactory,
)

from clinv.adapters import FakeSource
from clinv.model.entity import Entity
from clinv.services import search, unused, update_sources


def test_update_sources_creates_new_entity(
    repo: FakeRepository, source: FakeSource
) -> None:
    """
    Given: An empty fake repository.
    When: update_sources contains data of a new entity
    Then: The entity is added to the repo
    """
    entity = PersonFactory.build()
    source.add_change(entity, entity.dict())

    update_sources(repo, [source], ["per"])  # act

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
    entity = PersonFactory.build(state="active")
    repo.add(entity)
    repo.commit()
    # Change the entity attribute
    entity.name = "Changed name"
    # Configure the fake source adapter to show the changes
    source.add_change(entity, {"name": entity.name})

    update_sources(repo, [source], ["per"])  # act

    repo_entity = repo.get(entity.id_, type(entity))
    assert repo_entity.name == "Changed name"
    assert repo_entity.description == entity.description


class TestSearch:
    """Test the search service implementation."""

    def test_search_finds_ips_in_ec2_instances(self, repo: Repository) -> None:
        """
        Given: A repository with an ec2 instance
        When: search by a regular expression of the ip
        Then: the entity is found.
        """
        entity = EC2Factory.build(state="active")
        entity.private_ips = ["192.168.1.2"]
        repo.add(entity)
        repo.commit()
        regexp = r"192.*"
        found_entities = []

        for entities in search(repo, regexp):  # act
            found_entities += entities

        assert found_entities == [entity]

    def test_search_doesnt_duplicate_results(self, repo: Repository) -> None:
        """
        Given: A repository with an ec2 instance that two of it's attributes match the
            search criteria
        When: search by a regular expression of the ip
        Then: the entity is returned only once.
        """
        entity = EC2Factory.build(
            state="active", private_ips=["192.168.1.2"], public_ips=["192.168.1.2"]
        )
        repo.add(entity)
        repo.commit()
        regexp = r"192.*"
        found_entities = []

        for entities in search(repo, regexp):  # act
            found_entities += entities

        assert found_entities == [entity]


class TestUnused:
    """Test the unused service implementation."""

    def test_unused_detects_unused_resources(
        self,
        repo: Repository,
    ) -> None:
        """
        Given: One service that is not used by any other resource
        When: unused is called.
        Then: the service is returned.
        """
        service = repo.add(ServiceFactory.build(state="active"))
        repo.commit()

        result = unused(repo)

        assert len(result) == 1
        assert result == [service]

    @pytest.mark.parametrize(
        "entity",
        [
            pytest.param(
                ProjectFactory.build(state="active"),
                id="Project",
            ),
            pytest.param(
                IAMGroupFactory.build(state="active"),
                id="IAMGroup",
            ),
        ],
    )
    def test_unused_ignores_resources_that_cant_be_assigned(
        self, repo: Repository, entity: Entity
    ) -> None:
        """
        Given: One entity that makes no sense to assign to other resources.
            For example:
                * The Project can't be assigned to any other resource.
                * The IAMGroups still doesn't make any sense to be used by other
                    resources.
        When: unused is called.
        Then: the resource is not shown.
        """
        entity = repo.add(entity)  # type: ignore
        repo.commit()

        result = unused(repo)

        assert len(result) == 0

    def test_unused_detects_assigned_resources(self, repo: Repository) -> None:
        """
        Given: One project with an assignated service, one service with a
            resource assigned, and that infrastructure resource in the inventory.
        When: unused is called.
        Then: No result is returned.
        """
        entity = repo.add(EC2Factory.build(state="active"))
        service = repo.add(
            ServiceFactory.build(id_="ser_001", state="active", resources=[entity.id_])
        )
        repo.add(ProjectFactory.build(state="active", services=[service.id_]))
        repo.commit()

        result = unused(repo)

        assert len(result) == 0

    def test_unused_can_filter_unused_resources(self, repo: Repository) -> None:
        """
        Given: One project with no service assigned, one service without any
            resource assigned, and an infrastructure resource in the inventory.
        When: unused is called with only the infra resource model.
        Then: the EC2 resource is returned, but not the service.
        """
        entity = repo.add(EC2Factory.build(state="active"))
        service = repo.add(ServiceFactory.build(state="active"))
        project = repo.add(ProjectFactory.build(state="active"))
        repo.commit()

        result = unused(repo, ["ec2"])

        assert len(result) == 1
        assert entity in result
        assert service not in result
        assert project not in result
