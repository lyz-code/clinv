"""Tests the service layer."""

from datetime import datetime
from typing import Type

import pytest
from repository_orm import FakeRepository, Repository

from clinv.adapters import FakeSource
from clinv.model import aws
from clinv.model.entity import Entity
from clinv.model.risk import Information, People, Project, Service
from clinv.services import search, unassigned, update_sources

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


class TestUnassigned:
    """Test the unassigned service implementation."""

    @pytest.mark.parametrize(
        "entity",
        [
            pytest.param(
                aws.ASG(
                    id_="asg-1",
                    state="active",
                    min_size=1,
                    max_size=3,
                    desired_size=2,
                    region="us-east-1",
                    healthcheck="ELB",
                ),
                id="ASG",
            ),
            pytest.param(EC2Factory.create(state="active", id_="i-xx"), id="EC2"),
            pytest.param(
                aws.IAMGroup(state="active", arn="arn", id_="iamg-xx"), id="IAMGroup"
            ),
            pytest.param(
                aws.IAMUser(state="active", arn="arn", id_="iamu-xx"), id="IAMUser"
            ),
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
                    id_="r53-xx", state="active", hosted_zone="zone", type_="A"
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
                aws.VPC(id_="vpc-xx", state="active", cidr="cidr", region="us-east-1"),
                id="VPC",
            ),
            pytest.param(
                aws.SecurityGroup(id_="sg-xx", state="active"), id="SecurityGroup"
            ),
        ],
    )
    def test_unassigned_detects_unassigned_infra_resources(
        self, repo: Repository, entity: Entity
    ) -> None:
        """
        Given: One project with no service assigned, one service without any
            resource assigned, and an infrastructure resource in the inventory.

            We're testing with an EC2 resource, but we should do it with the rest of
            AWS infrastructure resources. To be able to do that, we'd need to create
            the factories of all the models, which I can't do right now. If you're
            reading this vote the next issues pleeease.

            https://github.com/FactoryBoy/factory_boy/issues/869
            https://github.com/FactoryBoy/factory_boy/issues/869
        When: unassigned is called.
        Then: the EC2 resource and the service are returned.
        """
        entity = repo.add(entity)
        service = repo.add(Service(id_="ser_01", access="public", state="active"))
        project = repo.add(Project(id_="pro_01", state="active"))
        repo.commit()

        result = unassigned(repo)

        assert len(result) == 2
        assert entity in result
        assert service in result
        assert project not in result

    def test_unassigned_detects_assigned_resources(self, repo: Repository) -> None:
        """
        Given: One project with an assignated service, one service with a
            resource assigned, and that infrastructure resource in the inventory.

            We're testing with an EC2 resource, but we should do it with the rest of
            AWS infrastructure resources. To be able to do that, we'd need to create
            the factories of all the models, which I can't do right now. If you're
            reading this vote the next issues pleeease.

            https://github.com/FactoryBoy/factory_boy/issues/869
            https://github.com/FactoryBoy/factory_boy/issues/869
        When: unassigned is called.
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

        result = unassigned(repo)

        assert len(result) == 0

    def test_unassigned_can_filter_unassigned_resources(self, repo: Repository) -> None:
        """
        Given: One project with no service assigned, one service without any
            resource assigned, and an infrastructure resource in the inventory.
        When: unassigned is called with only the infra resource model.
        Then: the EC2 resource is returned, but not the service.
        """
        entity = repo.add(EC2Factory.create(state="active"))
        service = repo.add(Service(id_="ser_01", access="public", state="active"))
        project = repo.add(Project(id_="pro_01", state="active"))
        repo.commit()

        result = unassigned(repo, ["ec2"])

        assert len(result) == 1
        assert entity in result
        assert service not in result
        assert project not in result

    @pytest.mark.parametrize("model", [Project, Service])
    def test_unassigned_detects_assigned_informations(
        self, repo: Repository, model: Type[Entity]
    ) -> None:
        """
        Given: One project/service with an assigned information.
        When: unassigned is called.
        Then: the Information resource is not returned.
        """
        entity = repo.add(Information(state="active", id_="inf_01"))
        repo.add(model(id_="id_01", state="active", informations=[entity.id_]))
        repo.commit()

        result = unassigned(repo, ["info"])

        assert len(result) == 0

    def test_unassigned_detects_assigned_people(self, repo: Repository) -> None:
        """
        Given: One project with an assigned Person.
        When: unassigned is called.
        Then: the Person resource is not returned.
        """
        entity = repo.add(People(state="active", id_="peo_01"))
        repo.add(Project(id_="pro_01", state="active", people=[entity.id_]))
        repo.commit()

        result = unassigned(repo, ["peo"])

        assert len(result) == 0
