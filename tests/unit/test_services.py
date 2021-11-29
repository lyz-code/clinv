"""Tests the service layer."""

from datetime import datetime
from typing import Type

import pytest
from repository_orm import FakeRepository, Repository

from clinv.adapters import FakeSource
from clinv.model import aws
from clinv.model.entity import Entity
from clinv.model.risk import Information, People, Project, Service
from clinv.services import search, unused, update_sources

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


class TestUnused:
    """Test the unused service implementation."""

    @pytest.mark.parametrize(
        "entity",
        [
            pytest.param(EC2Factory.create(state="active", id_="i-xx"), id="EC2"),
            pytest.param(
                aws.RDS(
                    id_="db-xx",
                    state="active",
                    engine="postgres",
                    endpoint="endpoint",
                    region="us-east-1",
                    size="big",
                    vpc="vpc",
                    start_date=datetime.now(),
                ),
                id="RDS",
            ),
            pytest.param(
                aws.Route53(
                    id_="AAAAAAAAAAAAA-test.com-A",
                    state="active",
                    hosted_zone="zone",
                    type_="A",
                ),
                id="Route53",
            ),
            pytest.param(
                aws.S3(
                    id_="s3-xx",
                    state="active",
                    public_read=False,
                    public_write=False,
                    start_date=datetime.now(),
                ),
                id="S3",
            ),
            pytest.param(
                aws.SecurityGroup(id_="sg-xx", state="active"), id="SecurityGroup"
            ),
        ],
    )
    def test_unused_detects_unused_infra_resources(
        self, repo: Repository, entity: Entity
    ) -> None:
        """
        Given: One service without any resource assigned, and an infrastructure
            resource in the inventory.
        When: unused is called.
        Then: the entity resource and the service are returned.
        """
        entity = repo.add(entity)
        service = repo.add(Service(id_="ser_01", access="public", state="active"))
        repo.commit()

        result = unused(repo)

        assert len(result) == 2
        assert entity in result
        assert service in result

    @pytest.mark.parametrize(
        "entity",
        [
            pytest.param(Project(state="active", id_="pro_01"), id="Project"),
            pytest.param(
                aws.IAMGroup(state="active", arn="arn", id_="iamg-xx"), id="IAMGroup"
            ),
            pytest.param(
                aws.VPC(id_="vpc-xx", state="active", cidr="cidr", region="us-east-1"),
                id="VPC",
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
                * The VPC doesn't make any sense to be assigned to a project or service
                    either.
        When: unused is called.
        Then: the resource is not shown.
        """
        entity = repo.add(entity)
        repo.commit()

        result = unused(repo)

        assert len(result) == 0

    def test_unused_detects_assigned_resources(self, repo: Repository) -> None:
        """
        Given: One project with an assignated service, one service with a
            resource assigned, and that infrastructure resource in the inventory.

            We're testing with an EC2 resource, but we should do it with the rest of
            AWS infrastructure resources. To be able to do that, we'd need to create
            the factories of all the models, which I can't do right now. If you're
            reading this vote the next issues pleeease.

            https://github.com/FactoryBoy/factory_boy/issues/869
            https://github.com/FactoryBoy/factory_boy/issues/869
        When: unused is called.
        Then: No result is returned.
        """
        entity = repo.add(EC2Factory.create(state="active", id_="i-xx"))
        service = repo.add(
            Service(
                id_="ser_01", access="public", state="active", resources=[entity.id_]
            )
        )
        repo.add(Project(id_="pro_01", state="active", services=[service.id_]))
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
        entity = repo.add(EC2Factory.create(state="active"))
        service = repo.add(Service(id_="ser_01", access="public", state="active"))
        project = repo.add(Project(id_="pro_01", state="active"))
        repo.commit()

        result = unused(repo, ["ec2"])

        assert len(result) == 1
        assert entity in result
        assert service not in result
        assert project not in result

    @pytest.mark.parametrize("model", [Project, Service])
    def test_unused_detects_assigned_informations(
        self, repo: Repository, model: Type[Entity]
    ) -> None:
        """
        Given: One project/service with an assigned information.
        When: unused is called.
        Then: the Information resource is not returned.
        """
        entity = repo.add(Information(state="active", id_="inf_01"))
        repo.add(model(id_="id_01", state="active", informations=[entity.id_]))
        repo.commit()

        result = unused(repo, ["info"])

        assert len(result) == 0

    def test_unused_detects_assigned_people(self, repo: Repository) -> None:
        """
        Given: One project with an assigned Person.
        When: unused is called.
        Then: the Person resource is not returned.
        """
        entity = repo.add(People(state="active", id_="peo_01"))
        repo.add(Project(id_="pro_01", state="active", people=[entity.id_]))
        repo.commit()

        result = unused(repo, ["peo"])

        assert len(result) == 0

    def test_unused_detects_assigned_iam_users(self, repo: Repository) -> None:
        """
        Given: One Person with an assigned IAM User.
        When: unused is called.
        Then: the IAM User resource is not returned.
        """
        entity = aws.IAMUser(state="active", arn="arn", id_="iamu-01")
        repo.add(People(state="active", id_="peo_01", iam_user="iamu-01"))
        repo.add(entity)
        repo.commit()

        result = unused(repo, ["iamu"])

        assert len(result) == 0
