import logging
import unittest
from unittest.mock import call, patch

import pytest
from clinv.cli import load_logger, load_parser, resource_types


@pytest.fixture
def parser():
    yield load_parser()


class TestArgparse:
    def test_can_specify_data_path(self, parser):
        parsed = parser.parse_args(["-d", "/tmp/inventory.yaml"])

        assert parsed.data_path == "/tmp/inventory.yaml"

    def test_default_data_path(self, parser):
        parsed = parser.parse_args([])

        assert parsed.data_path == "~/.local/share/clinv"

    def test_can_specify_search_subcommand(self, parser):
        parsed = parser.parse_args(["search", "instance_name"])

        assert parsed.subcommand == "search"
        assert parsed.search_string == "instance_name"

    def test_generate_subcommand_defaults_to_all(self, parser):
        parsed = parser.parse_args(["generate"])

        assert parsed.subcommand == "generate"
        assert parsed.resource_type == "all"

    @pytest.mark.parametrize("resource_type", resource_types)
    def test_can_specify_resource_type_in_generate_subcommand(
        self, parser, resource_type
    ):
        parsed = parser.parse_args(["generate", resource_type])

        assert parsed.subcommand == "generate"
        assert parsed.resource_type == resource_type

    def test_unassigned_subcommand_defaults_to_all(self, parser):
        parsed = parser.parse_args(["unassigned"])

        assert parsed.subcommand == "unassigned"
        assert parsed.resource_type == "all"

    @pytest.mark.parametrize("resource_type", resource_types)
    def test_can_specify_resource_type_in_unassigned_subcommand(
        self, parser, resource_type
    ):
        parsed = parser.parse_args(["unassigned", resource_type])

        assert parsed.subcommand == "unassigned"
        assert parsed.resource_type == resource_type

    def test_can_specify_list_subcommand_defaults_to_None(self, parser):
        parsed = parser.parse_args(["list"])

        assert parsed.subcommand == "list"
        assert parsed.resource_type is None

    @pytest.mark.parametrize("resource_type", resource_types)
    def test_can_specify_resource_type_in_list_subcommand(self, parser, resource_type):
        parsed = parser.parse_args(["list", resource_type])

        assert parsed.subcommand == "list"
        assert parsed.resource_type == resource_type

    def test_can_specify_export_subcommand(self, parser):
        parsed = parser.parse_args(["export"])
        assert parsed.subcommand == "export"

    def test_export_has_default_file(self, parser):
        parsed = parser.parse_args(["export"])
        assert parsed.export_path == "~/.local/share/clinv/inventory.ods"

    def test_export_can_specify_file_path(self, parser):
        parsed = parser.parse_args(["export", "file.ods"])
        assert parsed.export_path == "file.ods"

    def test_can_specify_print_subcommand(self, parser):
        parsed = parser.parse_args(["print", "resource_id"])
        assert parsed.subcommand == "print"
        assert parsed.search_string == "resource_id"

    def test_can_specify_monitor_subcommand(self, parser):
        parsed = parser.parse_args(["monitor"])
        assert parsed.subcommand == "monitor"
        assert parsed.monitor_status == "true"

    def test_can_specify_monitor_monitor_subcommand(self, parser):
        parsed = parser.parse_args(["monitor", "true"])
        assert parsed.subcommand == "monitor"
        assert parsed.monitor_status == "true"

    def test_can_specify_monitor_unmonitor_subcommand(self, parser):
        parsed = parser.parse_args(["monitor", "false"])
        assert parsed.subcommand == "monitor"
        assert parsed.monitor_status == "false"

    def test_can_specify_monitor_unknown_subcommand(self, parser):
        parsed = parser.parse_args(["monitor", "unknown"])
        assert parsed.subcommand == "monitor"
        assert parsed.monitor_status == "unknown"

    def test_can_specify_unused_subcommand(self, parser):
        parsed = parser.parse_args(["unused"])
        assert parsed.subcommand == "unused"

    def test_can_specify_active_subcommand(self, parser):
        parsed = parser.parse_args(["active"])
        assert parsed.subcommand == "active"
        assert parsed.resource_type is None

    def test_can_specify_active_resource_type(self, parser):
        parsed = parser.parse_args(["active", "ec2"])
        assert parsed.subcommand == "active"
        assert parsed.resource_type == "ec2"


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.logging_patch = patch("clinv.cli.logging", autospect=True)
        self.logging = self.logging_patch.start()

        self.logging.DEBUG = 10
        self.logging.INFO = 20
        self.logging.WARNING = 30
        self.logging.ERROR = 40

    def tearDown(self):
        self.logging_patch.stop()

    def test_logger_is_configured_by_default(self):
        load_logger()
        self.assertEqual(
            self.logging.addLevelName.assert_has_calls(
                [
                    call(logging.INFO, "[\033[36m+\033[0m]"),
                    call(logging.ERROR, "[\033[31m+\033[0m]"),
                    call(logging.DEBUG, "[\033[32m+\033[0m]"),
                    call(logging.WARNING, "[\033[33m+\033[0m]"),
                ]
            ),
            None,
        )
        self.assertEqual(
            self.logging.basicConfig.assert_called_with(
                level=logging.WARNING, format="  %(levelname)s %(message)s",
            ),
            None,
        )
