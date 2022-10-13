"""Tests the service layer."""

import pytest
from repository_orm import EntityNotFoundError, FakeRepository, Repository
from tests.factories import (
    EC2Factory,
    IAMGroupFactory,
    PersonFactory,
    ProjectFactory,
    SecurityGroupFactory,
    ServiceFactory,
)

from clinv.adapters import FakeSource
from clinv.model.entity import Entity
from clinv.services import search, service_risk, unused, update_sources

from ..factories import (
    AuthenticationFactory,
    NetworkAccessFactory,
    RiskFactory,
    SecurityMeasureFactory,
)


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

    def test_searching_by_security_groups_does_not_raise_error(
        self, repo_tinydb: Repository
    ) -> None:
        """
        Given: A security group
        When: searching for a string
        Then: it doesn't return an error

        Until https://github.com/lyz-code/repository-orm/issues/15 is fixed we can't
        search by the egress and ingress of the security groups
        """
        repo = repo_tinydb
        entity = SecurityGroupFactory.build()
        repo.add(entity)
        repo.commit()

        with pytest.raises(EntityNotFoundError):
            list(search(repo, "test", resource_types=["sg"]))


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


class TestRisk:
    """Test the risk service implementation."""

    def test_services_with_risks(self, repo: Repository) -> None:
        """
        Given: A repo with a service with a risk and no attached informations.
        When: service is called
        Then: The Risk security value is taken into account in the service risk.
        """
        risk = RiskFactory.build(state="active")
        service = ServiceFactory.build(
            authentication=[],
            access=None,
            security_measures=[],
            risks=[risk.id_],
            informations=[],
            dependencies=[],
            state="active",
        )
        repo.add(risk)
        repo.add(service)
        repo.commit()

        result = service_risk(repo)

        assert len(result) == 1
        assert result[0]._risk == risk.security_value  # noqa: W0212
        assert result[0]._security == -risk.security_value  # noqa: W0212

    def test_services_with_informations(self, repo: Repository) -> None:
        """
        Given: A repo with a service with an information and no attached risks.
        When: service is called
        Then: The number of attached informations is taken into account in the risk.
        """
        service = ServiceFactory.build(
            authentication=[],
            access=None,
            risks=[],
            security_measures=[],
            dependencies=[],
            informations=["inf_001"],
            state="active",
        )
        repo.add(service)
        repo.commit()

        result = service_risk(repo)

        assert len(result) == 1
        assert result[0]._risk == 1  # noqa: W0212

    def test_services_with_dependencies(self, repo: Repository) -> None:
        """
        Given: A repo with a service that depends on another service
        When: service is called
        Then: The service being depended upon has an increased risk value.
        """
        depended_service = ServiceFactory.build(
            authentication=[],
            access=None,
            risks=[],
            dependencies=[],
            security_measures=[],
            informations=[],
            state="active",
        )
        service = ServiceFactory.build(
            authentication=[],
            access=None,
            risks=[],
            dependencies=[depended_service.id_],
            security_measures=[],
            informations=[],
            state="active",
        )
        repo.add(depended_service)
        repo.add(service)
        repo.commit()

        result = service_risk(repo)

        assert len(result) == 2
        assert result[0].id_ == depended_service.id_
        assert result[0]._risk == 2  # noqa: W0212

    def test_services_with_network_access(self, repo: Repository) -> None:
        """
        Given: A repo with a service with a network access.
        When: service is called
        Then: The Network access security value is taken into account in the protection.
        """
        access = NetworkAccessFactory.build(state="active")
        service = ServiceFactory.build(
            authentication=[],
            risks=[],
            security_measures=[],
            dependencies=[],
            state="active",
            access=access.id_,
        )
        repo.add(access)
        repo.add(service)
        repo.commit()

        result = service_risk(repo)

        assert len(result) == 1
        assert result[0]._protection == access.security_value  # noqa: W0212

    def test_services_with_authentication(self, repo: Repository) -> None:
        """
        Given: A repo with a service with an authentication.
        When: service is called
        Then: The Authentication security value is taken into account in the protection.
        """
        authentication = AuthenticationFactory.build(state="active")
        service = ServiceFactory.build(
            risks=[],
            state="active",
            access=None,
            dependencies=[],
            authentication=[authentication.id_],
            security_measures=[],
        )
        repo.add(authentication)
        repo.add(service)
        repo.commit()

        result = service_risk(repo)

        assert len(result) == 1
        assert result[0]._protection == authentication.security_value  # noqa: W0212

    def test_services_with_security_measures(self, repo: Repository) -> None:
        """
        Given: A repo with a service with a security measure.
        When: service is called
        Then: The SecurityMeasure security value is taken into account in the
            protection.
        """
        security_measure = SecurityMeasureFactory.build(state="active")
        service = ServiceFactory.build(
            risks=[],
            state="active",
            access=None,
            dependencies=[],
            authentication=[],
            security_measures=[security_measure.id_],
        )
        repo.add(security_measure)
        repo.add(service)
        repo.commit()

        result = service_risk(repo)

        assert len(result) == 1
        assert result[0]._protection == security_measure.security_value  # noqa: W0212

    def test_services_ordered_by_security_value(self, repo: Repository) -> None:
        """
        Given: A repo with two services with different security value score.
        When: service is called
        Then: The services are ordered by security value.
        """
        risky_service = ServiceFactory.build(
            risks=[],
            state="active",
            access=None,
            dependencies=[],
            authentication=[],
            security_measures=[],
        )
        service = ServiceFactory.build(
            risks=[],
            state="active",
            informations=[],
            dependencies=[],
            access=None,
            authentication=[],
            security_measures=[],
        )
        repo.add(risky_service)
        repo.add(service)
        repo.commit()

        result = service_risk(repo)

        assert len(result) == 2
        assert result[0].id_ == risky_service.id_
        assert result[1].id_ == service.id_

    def test_services_ordered_by_id_at_same_security_id(self, repo: Repository) -> None:
        """
        Given: A repo with two services with same security value score.
        When: service is called
        Then: The services are ordered by id_.
        """
        services = ServiceFactory.batch(
            risks=[],
            state="active",
            informations=[],
            dependencies=[],
            access=None,
            authentication=[],
            security_measures=[],
            size=5,
        )
        repo.add(services)
        repo.commit()

        result = service_risk(repo)

        assert len(result) == 5
        assert result[0].id_ < result[1].id_
        assert result[1].id_ < result[2].id_
        assert result[2].id_ < result[3].id_
        assert result[3].id_ < result[4].id_
