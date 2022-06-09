"""Test the command line interface."""

import logging
import re
from typing import Generator

import pexpect  # noqa: E0401
import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from prompt_toolkit.input.ansi_escape_sequences import REVERSE_ANSI_SEQUENCES
from prompt_toolkit.keys import Keys
from repository_orm import Repository, TinyDBRepository
from tests.factories import (
    IAMUserFactory,
    InformationFactory,
    PersonFactory,
    RDSFactory,
    ServiceFactory,
)

from clinv.config import Config
from clinv.entrypoints.cli import cli
from clinv.model import SecurityGroup, SecurityGroupRule
from clinv.model.entity import EntityState
from clinv.model.risk import (
    Authentication,
    Information,
    NetworkAccess,
    Person,
    Project,
    Risk,
    SecurityMeasure,
    Service,
)
from clinv.version import __version__

from ..factories import (
    AuthenticationFactory,
    EC2Factory,
    NetworkAccessFactory,
    ProjectFactory,
)

# E0401: Unable to import pexpect, but the tests run, so it's a pylint error.


log = logging.getLogger(__name__)


@pytest.fixture(name="runner")
def fixture_runner(config: Config) -> CliRunner:
    """Configure the Click cli test runner."""
    return CliRunner(mix_stderr=False)


@pytest.fixture(name="repo")
def repo_(config: Config) -> Generator[TinyDBRepository, None, None]:
    """Configure a TinyDBRepository instance"""
    repo = TinyDBRepository(database_url=config.database_url)
    yield repo
    repo.close()


def test_version(runner: CliRunner) -> None:
    """Prints program version when called with --version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.search(
        rf" *clinv: {__version__}\n *Python: .*\n *Platform: .*",
        result.stdout,
    )


class TestUpdate:
    """Test the command line to update the resources information."""

    def test_update_inventory(
        self, config: Config, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: A valid configuration
        When: clinv update is run
        Then: the inventory is update
        """
        caplog.set_level(logging.DEBUG)

        result = runner.invoke(cli, ["update"])

        assert result.exit_code == 0
        assert (
            "clinv.adapters.risk",
            logging.DEBUG,
            "Updating Risk Management entities.",
        ) in caplog.record_tuples

    def test_update_inventory_can_specify_type(
        self, config: Config, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: A valid configuration
        When: clinv update is run with a resource type
        Then: the inventory is update
        """
        caplog.set_level(logging.DEBUG)

        result = runner.invoke(cli, ["update", "per"])

        assert result.exit_code == 0
        assert (
            "clinv.adapters.risk",
            logging.DEBUG,
            "Updating Risk Management entities.",
        ) in caplog.record_tuples

    def test_update_inventory_can_specify_many_types(
        self, config: Config, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: A valid configuration
        When: clinv update is run with two resource types
        Then: the inventory is update
        """
        caplog.set_level(logging.DEBUG)

        result = runner.invoke(cli, ["update", "per", "inf"])

        assert result.exit_code == 0
        assert (
            "clinv.adapters.risk",
            logging.DEBUG,
            "Updating Risk Management entities.",
        ) in caplog.record_tuples


class TestPrint:
    """Test the command line to print the information of the resources."""

    def test_print_returns_entity_information(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: An entity in the repository
        When: printing by it's id
        Then: The entity attributes are shown.
        """
        entity = PersonFactory.build()
        repo.add(entity)
        repo.commit()

        result = runner.invoke(cli, ["print", entity.id_])

        assert result.exit_code == 0
        assert "Person" in result.stdout
        assert entity.id_ in result.stdout

    def test_print_can_handle_complex_objects(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: An entity that contains other entities in their attributes
        When: printing by it's id
        Then: The data of the associated entity is printed in a separate table
        """
        complex_entity = SecurityGroup(
            id_="sg-xxxxxx",  # type: ignore
            name="test security group",
            state="active",  # type: ignore
            ingress=[
                SecurityGroupRule(
                    protocol="TCP",  # type: ignore
                    ports=[80, 443],
                    sg_range=["sg-yyyyyy"],  # type: ignore
                ),
            ],
        )
        repo.add(complex_entity)
        repo.commit()

        result = runner.invoke(cli, ["print", "sg-xxxxxx"])

        assert result.exit_code == 0
        assert "SecurityGroup" in result.stdout
        assert "sg-yyyyyy" in result.stdout

    def test_print_handles_entity_not_found(
        self, config: Config, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: An empty repository
        When: printing by it's id
        Then: A message is shown.
        """
        result = runner.invoke(cli, ["print", "inexistent-id"])

        assert result.exit_code == 1
        assert (
            "clinv.entrypoints.cli",
            logging.ERROR,
            "There are no entities of type Service, Project, EC2, Route53, RDS, S3, "
            "ASG, SecurityGroup, IAMGroup, IAMUser, Information, Person, VPC, "
            "Authentication, NetworkAccess, Risk, SecurityMeasure in the repository "
            "with id inexistent-id.",
        ) in caplog.record_tuples


class TestList:
    """Test the command line implementation of the listing resources command."""

    def test_list_returns_entity_information(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: Two entities in the repository
        When: listing is called
        Then: The entity id and names are shown
        """
        entities = PersonFactory.batch(2, state="active")
        entities.append(PersonFactory.build(state="terminated"))
        for entity in entities:
            repo.add(entity)
        repo.commit()

        result = runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "Person" in result.stdout
        assert entities[0].id_ in result.stdout
        assert not re.match(rf"{entities[2].id_} *", result.stdout)

    def test_list_returns_entity_information_can_specify_type(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: Two active entities and an inactive in the repository
        When: listing is called with the resource type
        Then: The entity id and names of the active are shown
        """
        entities = PersonFactory.batch(2, state="active")
        for entity in entities:
            repo.add(entity)
        repo.commit()

        result = runner.invoke(cli, ["list", "per"])

        assert result.exit_code == 0
        assert "Person" in result.stdout
        assert entities[0].id_ in result.stdout

    def test_list_returns_entity_information_can_specify_many_types(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: Two active entities and an inactive in the repository
        When: listing is called with two resource types
        Then: The entity id and names of the active are shown
        """
        entities = PersonFactory.batch(2, state="active")
        for entity in entities:
            repo.add(entity)
        repo.commit()

        result = runner.invoke(cli, ["list", "per", "inf"])

        assert result.exit_code == 0
        assert "Person" in result.stdout
        assert entities[0].id_ in result.stdout

    def test_list_returns_entity_information_can_show_inactive(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: Two entities in the repository, one active and another inactive
        When: listing is called with the --inactive flag
        Then: The entity id and names of the inactive entities are shown.
        """
        entities = [
            PersonFactory.build(state="active"),
            PersonFactory.build(state="terminated"),
        ]
        for entity in entities:
            repo.add(entity)
        repo.commit()

        result = runner.invoke(cli, ["list", "--inactive"])

        assert result.exit_code == 0
        assert "Person" in result.stdout
        assert entities[0].id_ not in result.stdout
        assert entities[1].id_ in result.stdout

    def test_list_returns_entity_information_can_show_all(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: Two entities in the repository, one active and another inactive
        When: listing is called with the --all flag
        Then: The entity id and names of all entitites are shown
        """
        entities = [
            PersonFactory.build(state="active"),
            PersonFactory.build(state="terminated"),
        ]
        for entity in entities:
            repo.add(entity)
        repo.commit()

        result = runner.invoke(cli, ["list", "--all"])

        assert result.exit_code == 0
        assert "Person" in result.stdout
        assert entities[0].id_ in result.stdout
        assert entities[1].id_ in result.stdout

    def test_list_handles_entity_not_found(
        self, config: Config, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: An empty repository
        When: listing is called
        Then: A message is shown.
        """
        result = runner.invoke(cli, ["list"])

        assert result.exit_code == 1
        assert (
            "clinv.entrypoints.cli",
            logging.ERROR,
            "There are no entities in the repository that match the criteria.",
        ) in caplog.record_tuples

    def test_list_handles_entity_not_found_when_type_is_specified(
        self, config: Config, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: An empty repository
        When: listing is called with the resource type
        Then: A message is shown.
        """
        result = runner.invoke(cli, ["list", "per"])

        assert result.exit_code == 1
        assert (
            "clinv.entrypoints.cli",
            logging.ERROR,
            (
                "There are no entities of type per in the repository that match the "
                "criteria."
            ),
        ) in caplog.record_tuples


class TestSearch:
    """Test the command line implementation of the searching of resources."""

    def test_search_returns_entity_information(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: Two entities in the repository
        When: search is called with a regular expression that matches the first element
        Then: The entity id and names of the first element are shown
        """
        entities = PersonFactory.batch(2, state="active")
        entities.append(PersonFactory.build(name="entity_12352", state="active"))
        for entity in entities:
            repo.add(entity)
        repo.commit()
        search_regexp = "entity_.*"

        result = runner.invoke(cli, ["search", search_regexp])

        assert result.exit_code == 0
        assert "Person" in result.stdout
        assert entities[0].id_ not in result.stdout
        assert entities[1].id_ not in result.stdout
        assert entities[2].id_ in result.stdout

    def test_search_returns_entity_information_with_type(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: Two entities in the repository
        When: search is called with a regular expression that matches the first element
            and the resource_type
        Then: The entity id and names of the first element are shown
        """
        entities = PersonFactory.batch(2, state="active")
        entities.append(PersonFactory.build(name="entity_12352", state="active"))
        for entity in entities:
            repo.add(entity)
        repo.commit()
        search_regexp = "entity_.*"

        result = runner.invoke(cli, ["search", search_regexp, "per"])

        assert result.exit_code == 0
        assert "Person" in result.stdout
        assert entities[0].id_ not in result.stdout
        assert entities[1].id_ not in result.stdout
        assert entities[2].id_ in result.stdout

    def test_search_handles_entity_not_found_when_type_is_specified(
        self, config: Config, runner: CliRunner, caplog: LogCaptureFixture
    ) -> None:
        """
        Given: An empty repository
        When: searching is called with a regexp
        Then: A message is shown.
        """
        result = runner.invoke(cli, ["search", "regexp"])

        assert result.exit_code == 1
        assert (
            "clinv.entrypoints.cli",
            logging.ERROR,
            ("There are no entities in the repository that match the criteria."),
        ) in caplog.record_tuples


class TestUnused:
    """Test the command line implementation of the unused service."""

    def test_unused_detects_unused_resources(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: One project with no service assigned, one service without any
            resource assigned, and an infrastructure resource in the inventory.
        When: unused is called.
        Then: the EC2 resource and the service are returned.
        """
        entity = repo.add(EC2Factory.build(state="active"))
        service = repo.add(Service(id_="ser_001", state="active"))  # type: ignore
        project = repo.add(Project(id_="pro_001", state="active"))  # type: ignore
        repo.commit()

        result = runner.invoke(cli, ["unused"])

        assert result.exit_code == 0
        assert entity.id_ in result.stdout
        assert str(service.id_) in result.stdout
        assert str(project.id_) not in result.stdout

    def test_unused_can_filter_unused_resources(
        self, config: Config, runner: CliRunner, repo: Repository
    ) -> None:
        """
        Given: One project with no service assigned, one service without any
            resource assigned, and an infrastructure resource in the inventory.
        When: unused is called with only the infra resource model.
        Then: the EC2 resource is returned, but not the service.
        """
        entity = repo.add(EC2Factory.build(state="active"))
        service = repo.add(Service(id_="ser_001", state="active"))  # type: ignore
        project = repo.add(Project(id_="pro_001", state="active"))  # type: ignore
        repo.commit()

        result = runner.invoke(cli, ["unused", "ec2"])

        assert result.exit_code == 0
        assert entity.id_ in result.stdout
        assert str(service.id_) not in result.stdout
        assert str(project.id_) not in result.stdout


class TestAdd:
    """Test the command line implementation of the add service."""

    def test_add_creates_project(  # noqa: AAA01
        self,
        config: Config,
        runner: CliRunner,
        repo: Repository,
    ) -> None:
        """
        Given: A repository with two services, a person, a project and an information
        When: add is called with the pro argument and the tui interface is used to
            define the project data.
        Then: the Project resource is added
        """
        repo.add(Project(id_="pro_001", state="active"))  # type: ignore
        repo.add(ServiceFactory.build(state="active", id_="ser_001", name="ldap"))
        repo.add(ServiceFactory.build(state="active", id_="ser_002", name="haproxy"))
        repo.add(
            ServiceFactory.build(state="active", id_="ser_003", name="monitorization")
        )
        repo.add(PersonFactory.build(state="active", id_="per_001", name="Alice"))
        repo.add(
            InformationFactory.build(state="active", id_="inf_001", name="user data")
        )
        repo.commit()

        tui = pexpect.spawn("clinv add pro", timeout=5)
        tui.expect(".*Name:.*")
        tui.sendline("project_2")
        tui.expect(".*Description:.*")
        tui.sendline("description")
        tui.expect(".*Responsible:.*")
        # Select the first element shown
        tui.send("a")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.expect(".*Aliases.*")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        # Fuzzy search of haproxy
        tui.expect(".*Services.*")
        tui.send("h")
        tui.send("a")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        # Fuzzy search of ldap
        # WARNING: your terminal doesn't support cursor position requests (CPR)
        tui.expect(".*Services.*")
        tui.sendline("ldap")
        # Nothing more to add to services
        tui.expect(".*Services.*")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.expect(".*Informations.*")
        # Fuzzy search of user data
        tui.sendline("user data")
        # Nothing more to add to informations
        tui.expect(".*Informations.*")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.expect(".*People.*")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.expect_exact(pexpect.EOF)
        # If we don't do the expect_exact twice, the status is None instead of 0
        tui.expect_exact(pexpect.EOF)

        assert tui.status == 0
        project = repo.get("pro_002", Project)
        assert project == Project(
            id_="pro_002",  # type: ignore
            name="project_2",
            state=EntityState.RUNNING,
            description="description",
            responsible="per_001",  # type: ignore
            aliases=[],
            services=["ser_002", "ser_001"],  # type: ignore
            informations=["inf_001"],  # type: ignore
            people=[],
        )

    # R0915: too many statements, but that's how to define the TUI steps
    def test_add_creates_service(  # noqa: AAA01, R0915
        self,
        config: Config,
        runner: CliRunner,
        repo: Repository,
    ) -> None:
        """
        Given: A repository with two services, a person, a project, an EC2 resource,
            an RDS resource, and an information
        When: add is called with the ser argument and the tui interface is used to
            define the service data.
        Then: the Service resource is added
        """
        repo.add(ProjectFactory.build(id_="pro_001", state="active"))
        repo.add(
            NetworkAccessFactory.build(id_="net_001", name="Internet", state="active")
        )
        repo.add(
            AuthenticationFactory.build(id_="auth_001", name="LDAP", state="active")
        )
        repo.add(ServiceFactory.build(state="active", id_="ser_001", name="ldap"))
        repo.add(ServiceFactory.build(state="active", id_="ser_002", name="haproxy"))
        repo.add(PersonFactory.build(state="active", id_="per_001", name="Alice"))
        repo.add(
            InformationFactory.build(state="active", id_="inf_001", name="user data")
        )
        repo.add(EC2Factory.build(state="active", id_="i-01", name="instance"))
        repo.add(RDSFactory.build(state="active", id_="db-01", name="database"))
        repo.commit()

        tui = pexpect.spawn("clinv add ser", timeout=5)
        tui.expect(".*Name:.*")
        tui.sendline("new service")
        tui.expect(".*Description:.*")
        tui.sendline("description")
        tui.expect(".*Responsible:.*")
        # Select the first element shown
        tui.send("a")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.expect(".*Access.*")
        tui.send("i")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.expect(".*Authentication.*")
        tui.send("l")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        # Fuzzy search for user data
        tui.expect(".*Informations.*")
        tui.send("u")
        tui.send("s")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        # Fuzzy search of haproxy
        tui.expect(".*Dependencies.*")
        tui.send("h")
        tui.send("a")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        # Fuzzy search for database
        tui.expect(".*Resources.*")
        tui.send("d")
        tui.send("a")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        # Fuzzy search for admins
        tui.expect(".*Users.*")
        tui.send("a")
        tui.send("d")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.expect(".*Environment.*")
        tui.send("p")
        tui.send("r")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.expect_exact(pexpect.EOF)
        tui.expect_exact(pexpect.EOF)

        assert tui.status == 0
        service = repo.get("ser_003", Service)
        assert service == Service(
            id_="ser_003",  # type: ignore
            name="new service",
            state=EntityState.RUNNING,
            description="description",
            access="net_001",  # type: ignore
            responsible="per_001",  # type: ignore
            authentication=["auth_001"],  # type: ignore
            informations=["inf_001"],  # type: ignore
            dependencies=["ser_002"],  # type: ignore
            resources=["db-01"],
            users=["admins"],
            environment="Production",  # type: ignore
        )

    def test_add_creates_information(  # noqa: AAA01
        self,
        config: Config,
        runner: CliRunner,
        repo: Repository,
    ) -> None:
        """
        Given: A repository with a person
        When: add is called with the inf argument and the tui interface is used to
            define the information data.
        Then: the Information resource is added
        """
        repo.add(PersonFactory.build(state="active", id_="per_001", name="Alice"))
        repo.commit()

        tui = pexpect.spawn("clinv add inf", timeout=5)
        tui.expect(".*Name:.*")
        tui.sendline("new information")
        tui.expect(".*Description:.*")
        tui.sendline("description")
        tui.expect(".*Responsible:.*")
        # Select the first element shown
        tui.send("a")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.expect(".*Personal Data:.*")
        tui.send("y")
        tui.expect_exact(pexpect.EOF)
        tui.expect_exact(pexpect.EOF)

        assert tui.status == 0
        information = repo.get("inf_001", Information)
        assert information == Information(
            id_="inf_001",  # type: ignore
            name="new information",
            state=EntityState.RUNNING,
            description="description",
            responsible="per_001",  # type: ignore
            personal_data=True,
        )

    def test_add_creates_person(  # noqa: AAA01
        self,
        config: Config,
        runner: CliRunner,
        repo: Repository,
    ) -> None:
        """
        Given: A repository with an iam user
        When: add is called with the per argument and the tui interface is used to
            define the person data.
        Then: the Person resource is added
        """
        repo.add(IAMUserFactory.build(state="active", id_="iamu-1", name="Alice"))
        repo.commit()

        tui = pexpect.spawn("clinv add per", timeout=5)
        tui.expect(".*Name:.*")
        tui.sendline("new person")
        tui.expect(".*Description:.*")
        tui.sendline("description")
        tui.expect(".*IAM User:.*")
        # Select the first element shown
        tui.send("a")
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Tab])
        tui.send(REVERSE_ANSI_SEQUENCES[Keys.Enter])
        tui.expect(".*Email:.*")
        tui.sendline("test@test.org")
        tui.expect_exact(pexpect.EOF)
        tui.expect_exact(pexpect.EOF)

        assert tui.status == 0
        person = repo.get("per_001", Person)
        assert person == Person(
            id_="per_001",  # type: ignore
            name="new person",
            state=EntityState.RUNNING,
            description="description",
            iam_user="iamu-1",  # type: ignore
            email="test@test.org",
        )

    def test_add_cancels_object_building(  # noqa: AAA01
        self,
        config: Config,
        runner: CliRunner,
        repo: Repository,
    ) -> None:
        """
        Given: An empty repository
        When: add is called with the per argument and at the first argument we want to
            quit using `q`
        Then: the Person resource is not added
        """
        tui = pexpect.spawn("clinv add per", timeout=5)
        tui.expect(".*Name:.*")
        tui.sendline("q")
        tui.expect_exact(pexpect.EOF)
        tui.expect_exact(pexpect.EOF)

        assert tui.status == 256
        assert len(repo.all(Person)) == 0

    def test_add_creates_authentication(  # noqa: AAA01
        self,
        config: Config,
        runner: CliRunner,
        repo: Repository,
    ) -> None:
        """
        Given: A bare repository
        When: add is called with the auth argument and the tui interface is used to
            define the authentication data.
        Then: the Authentication resource is added
        """
        tui = pexpect.spawn("clinv add auth", timeout=5)
        tui.expect(".*Name:.*")
        tui.sendline("new authentication")
        tui.expect(".*Description:.*")
        tui.sendline("description")
        tui.expect(".*Security Value:.*")
        tui.sendline("10")
        tui.expect_exact(pexpect.EOF)

        tui.expect_exact(pexpect.EOF)  # act

        assert tui.status == 0
        auth = repo.get("auth_001", Authentication)
        assert auth == Authentication(
            id_="auth_001",  # type: ignore
            name="new authentication",
            state=EntityState.RUNNING,
            description="description",
            security_value=10,
        )

    def test_add_creates_network_access(  # noqa: AAA01
        self,
        config: Config,
        runner: CliRunner,
        repo: Repository,
    ) -> None:
        """
        Given: A bare repository
        When: add is called with the net argument and the tui interface is used to
            define the network access data.
        Then: the NetworkAccess resource is added
        """
        tui = pexpect.spawn("clinv add net", timeout=5)
        tui.expect(".*Name:.*")
        tui.sendline("new network access")
        tui.expect(".*Description:.*")
        tui.sendline("description")
        tui.expect(".*Security Value:.*")
        tui.sendline("10")
        tui.expect_exact(pexpect.EOF)

        tui.expect_exact(pexpect.EOF)  # act

        assert tui.status == 0
        network_access = repo.get("net_001", NetworkAccess)
        assert network_access == NetworkAccess(
            id_="net_001",  # type: ignore
            name="new network access",
            state=EntityState.RUNNING,
            description="description",
            security_value=10,
        )

    def test_add_creates_risk(  # noqa: AAA01
        self,
        config: Config,
        runner: CliRunner,
        repo: Repository,
    ) -> None:
        """
        Given: A bare repository
        When: add is called with the risk argument and the tui interface is used to
            define the risk data.
        Then: the Risk resource is added
        """
        tui = pexpect.spawn("clinv add risk", timeout=5)
        tui.expect(".*Name:.*")
        tui.sendline("new risk")
        tui.expect(".*Description:.*")
        tui.sendline("description")
        tui.expect(".*Security Value:.*")
        tui.sendline("10")
        tui.expect_exact(pexpect.EOF)

        tui.expect_exact(pexpect.EOF)  # act

        assert tui.status == 0
        risk = repo.get("risk_001", Risk)
        assert risk == Risk(
            id_="risk_001",  # type: ignore
            name="new risk",
            state=EntityState.RUNNING,
            description="description",
            security_value=10,
        )

    def test_add_creates_security_measure(  # noqa: AAA01
        self,
        config: Config,
        runner: CliRunner,
        repo: Repository,
    ) -> None:
        """
        Given: A bare repository
        When: add is called with the sec argument and the tui interface is used to
            define the security measure data.
        Then: the SecurityMeasure resource is added
        """
        tui = pexpect.spawn("clinv add sec", timeout=5)
        tui.expect(".*Name:.*")
        tui.sendline("new security measure")
        tui.expect(".*Description:.*")
        tui.sendline("description")
        tui.expect(".*Security Value:.*")
        tui.sendline("10")
        tui.expect_exact(pexpect.EOF)

        tui.expect_exact(pexpect.EOF)  # act

        assert tui.status == 0
        security_measure = repo.get("sec_001", SecurityMeasure)
        assert security_measure == SecurityMeasure(
            id_="sec_001",  # type: ignore
            name="new security measure",
            state=EntityState.RUNNING,
            description="description",
            security_value=10,
        )


class TestRisk:
    """Test the command line implementation of the risk report."""

    def test_prints_report(  # noqa: AAA01
        self,
        config: Config,
        runner: CliRunner,
        repo: Repository,
    ) -> None:
        """
        Given: A repository with two services one with intranet access and other with
            internet.
        When: risk is called.
        Then: the list with the services is returned.
        """
        services = [
            ServiceFactory.build(
                id_="ser_001",
                name="internal",
                state="active",
                risks=[],
                dependencies=[],
                informations=[],
                authentication=[],
                access=None,
                security_measures=[],
            ),
            ServiceFactory.build(
                id_="ser_002",
                name="public",
                state="active",
                risks=[],
                informations=[],
                dependencies=[],
                authentication=[],
                access=None,
                security_measures=[],
            ),
        ]
        repo.add(services)
        repo.commit()

        result = runner.invoke(cli, ["risk"])

        assert result.exit_code == 0
        assert re.search(
            r"ID.*Name.*Exposition.*Risk.*Protection.*Security Value", result.stdout
        )
        assert "ser_001" in result.stdout
        assert "ser_002" in result.stdout
