import logging
import unittest
from unittest.mock import call, patch
from clinv.cli import load_parser, load_logger


class TestArgparse(unittest.TestCase):
    def setUp(self):
        self.parser = load_parser()

    def test_can_specify_data_path(self):
        parsed = self.parser.parse_args(['-d', '/tmp/inventory.yaml'])
        self.assertEqual(parsed.data_path, '/tmp/inventory.yaml')

    def test_default_data_path(self):
        parsed = self.parser.parse_args([])
        self.assertEqual(
            parsed.data_path,
            '~/.local/share/clinv',
        )

    def test_can_specify_search_subcommand(self):
        parsed = self.parser.parse_args(['search', 'instance_name'])
        self.assertEqual(parsed.subcommand, 'search')
        self.assertEqual(parsed.search_string, 'instance_name')

    def test_can_specify_generate_subcommand(self):
        parsed = self.parser.parse_args(['generate'])
        self.assertEqual(parsed.subcommand, 'generate')

    def test_can_specify_unassigned_ec2_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'ec2'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'ec2')

    def test_can_specify_unassigned_services_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'services'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'services')

    def test_can_specify_unassigned_informations_subcommand(self):
        parsed = self.parser.parse_args(['unassigned', 'informations'])
        self.assertEqual(parsed.subcommand, 'unassigned')
        self.assertEqual(parsed.resource_type, 'informations')

    def test_can_specify_list_ec2_subcommand(self):
        parsed = self.parser.parse_args(['list', 'ec2'])
        self.assertEqual(parsed.subcommand, 'list')
        self.assertEqual(parsed.resource_type, 'ec2')

    def test_can_specify_list_services_subcommand(self):
        parsed = self.parser.parse_args(['list', 'services'])
        self.assertEqual(parsed.subcommand, 'list')
        self.assertEqual(parsed.resource_type, 'services')

    def test_can_specify_list_informations_subcommand(self):
        parsed = self.parser.parse_args(['list', 'informations'])
        self.assertEqual(parsed.subcommand, 'list')
        self.assertEqual(parsed.resource_type, 'informations')

    def test_can_specify_export_subcommand(self):
        parsed = self.parser.parse_args(['export'])
        self.assertEqual(parsed.subcommand, 'export')

    def test_export_has_default_format(self):
        parsed = self.parser.parse_args(['export'])
        self.assertEqual(parsed.export_format, 'ods')

    def test_can_specify_export_format(self):
        parsed = self.parser.parse_args(['export', 'ods'])
        self.assertEqual(parsed.subcommand, 'export')
        self.assertEqual(parsed.export_format, 'ods')

    def test_export_has_default_file(self):
        parsed = self.parser.parse_args(['export'])
        self.assertEqual(
            parsed.export_path,
            '~/.local/share/clinv/inventory.ods'
        )

    def test_export_can_specify_file_path(self):
        parsed = self.parser.parse_args(['export', '-f', 'file.ods'])
        self.assertEqual(parsed.export_path, 'file.ods')


class TestLogger(unittest.TestCase):

    def setUp(self):
        self.logging_patch = patch('clinv.cli.logging', autospect=True)
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
                    call(logging.INFO, '[\033[36mINFO\033[0m]'),
                    call(logging.ERROR, '[\033[31mERROR\033[0m]'),
                    call(logging.DEBUG, '[\033[32mDEBUG\033[0m]'),
                    call(logging.WARNING, '[\033[33mWARNING\033[0m]'),
                ]
            ),
            None
        )
        self.assertEqual(
            self.logging.basicConfig.assert_called_with(
                level=logging.WARNING,
                format="  %(levelname)s %(message)s",
            ),
            None
        )
