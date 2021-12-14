"""Test the command line interface."""

import logging
import re

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from py._path.local import LocalPath
from repository_orm import Repository, TinyDBRepository
from tests.factories import PersonFactory

from clinv.config import Config
from clinv.entrypoints.cli import cli
from clinv.model import Entity, SecurityGroup, SecurityGroupRule
from clinv.model.risk import Project, Service
from clinv.version import __version__

from ..factories import EC2Factory

log = logging.getLogger(__name__)


@pytest.fixture(name="runner")
def fixture_runner(config: Config) -> CliRunner:
    """Configure the Click cli test runner."""
    return CliRunner(mix_stderr=False, env={"CLINV_CONFIG_PATH": config.config_path})


@pytest.fixture(name="repo")
def repo_(config: Config) -> TinyDBRepository:
    """Configure a TinyDBRepository instance"""
    return TinyDBRepository([Entity], config["database_url"])


def test_version(runner: CliRunner) -> None:
    """Prints program version when called with --version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.match(
        fr" *clinv version: {__version__}\n" r" *python version: .*\n *platform: .*",
        result.stdout,
    )


def test_load_config_handles_wrong_file_format(
    runner: CliRunner, tmpdir: LocalPath, caplog: LogCaptureFixture
) -> None:
    """
    Given: A wrong configuration file
    When: cli is used
    Then: an error is returned.
    """
    config_file = tmpdir.join("config.yaml")  # type: ignore
    config_file.write("[ invalid yaml")

    result = runner.invoke(cli, ["-c", str(config_file), "null"])

    assert result.exit_code == 1
    assert (
        "clinv.entrypoints",
        logging.ERROR,
        f"Error parsing yaml of configuration file {config_file}: "
        f'while parsing a flow sequence\n  in "{config_file}", '
        "line 1, column 1\nexpected ',' or ']', but got '<stream end>'\n  in"
        f' "{config_file}", line 1, column 15',
    ) in caplog.record_tuples


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

        result = runner.invoke(cli, ["--config_path", config.config_path, "update"])

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

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "update", "peo"]
        )

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

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "update", "peo", "info"]
        )

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

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "print", entity.id_]
        )

        assert result.exit_code == 0
        assert "People" in result.stdout
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
            id_="sg-xxxxxx",
            name="test security group",
            state="active",
            ingress=[
                SecurityGroupRule(
                    protocol="TCP",
                    ports=[80, 443],
                    sg_range=["sg-yyyyyy"],
                ),
            ],
        )
        repo.add(complex_entity)
        repo.commit()

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "print", "sg-xxxxxx"]
        )

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
        result = runner.invoke(
            cli, ["--config_path", config.config_path, "print", "inexistent-id"]
        )

        assert result.exit_code == 1
        assert (
            "clinv.entrypoints.cli",
            logging.ERROR,
            "There are no entities in the repository with id inexistent-id.",
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

        result = runner.invoke(cli, ["--config_path", config.config_path, "list"])

        assert result.exit_code == 0
        assert "People" in result.stdout
        assert entities[0].id_ in result.stdout
        assert entities[2].id_ not in result.stdout

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

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "list", "peo"]
        )

        assert result.exit_code == 0
        assert "People" in result.stdout
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

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "list", "peo", "info"]
        )

        assert result.exit_code == 0
        assert "People" in result.stdout
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

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "list", "--inactive"]
        )

        assert result.exit_code == 0
        assert "People" in result.stdout
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

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "list", "--all"]
        )

        assert result.exit_code == 0
        assert "People" in result.stdout
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
        result = runner.invoke(cli, ["--config_path", config.config_path, "list"])

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
        result = runner.invoke(
            cli, ["--config_path", config.config_path, "list", "peo"]
        )

        assert result.exit_code == 1
        assert (
            "clinv.entrypoints.cli",
            logging.ERROR,
            (
                "There are no entities of type peo in the repository that match the "
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
        for entity in entities:
            repo.add(entity)
        repo.commit()
        search_regexp = f"{entities[0].name[:-1]}."

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "search", search_regexp]
        )

        assert result.exit_code == 0
        assert "People" in result.stdout
        assert entities[0].id_ in result.stdout
        assert entities[1].id_ not in result.stdout

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

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "search", search_regexp, "peo"]
        )

        assert result.exit_code == 0
        assert "People" in result.stdout
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
        result = runner.invoke(
            cli, ["--config_path", config.config_path, "search", "regexp"]
        )

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
        service = repo.add(Service(id_="ser_01", access="public", state="active"))
        project = repo.add(Project(id_="pro_01", state="active"))
        repo.commit()

        result = runner.invoke(cli, ["--config_path", config.config_path, "unused"])

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
        service = repo.add(Service(id_="ser_01", access="public", state="active"))
        project = repo.add(Project(id_="pro_01", state="active"))
        repo.commit()

        result = runner.invoke(
            cli, ["--config_path", config.config_path, "unused", "ec2"]
        )

        assert result.exit_code == 0
        assert entity.id_ in result.stdout
        assert str(service.id_) not in result.stdout
        assert str(project.id_) not in result.stdout
