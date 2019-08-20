import unittest
from unittest.mock import patch

from clinv import main


class TestMain(unittest.TestCase):

    def setUp(self):
        self.parser_patch = patch('clinv.load_parser', autospect=True)
        self.parser = self.parser_patch.start()
        self.parser_args = self.parser.return_value.parse_args.return_value

        self.clinv_patch = patch('clinv.Clinv', autospect=True)
        self.clinv = self.clinv_patch.start()

    def tearDown(self):
        self.parser_patch.stop()
        self.clinv_patch.stop()

    def test_main_loads_parser(self):
        self.parser.parse_args = True
        main()
        self.assertTrue(self.parser.called)

    @patch('clinv.load_logger')
    def test_main_loads_logger(self, loggerMock):
        self.parser.parse_args = True
        main()
        self.assertTrue(loggerMock.called)

    def test_search_subcommand(self):
        self.parser_args.subcommand = 'search'
        self.parser_args.search_string = 'inst'
        self.parser_args.data_path = 'path'
        main()
        self.assertEqual(
            self.clinv.assert_called_with('path'),
            None,
        )
        self.assertTrue(self.clinv.return_value.load_source_data_from_file.called)
        self.assertTrue(self.clinv.return_value.load_user_data_from_file.called)
        self.assertEqual(
            self.clinv.return_value.print_search.assert_called_with('inst'),
            None,
        )

    def test_generate_subcommand(self):
        self.parser_args.subcommand = 'generate'
        main()
        self.assertTrue(self.clinv.return_value._fetch_aws_inventory.called)
        self.assertTrue(self.clinv.return_value.load_user_data_from_file.called)
        self.assertTrue(self.clinv.return_value.save.called)

    def test_unassigned_subcommand(self):
        self.parser_args.subcommand = 'unassigned'
        self.parser_args.resource_type = 'ec2'
        main()
        self.assertTrue(self.clinv.return_value.load_source_data_from_file.called)
        self.assertTrue(self.clinv.return_value.load_user_data_from_file.called)
        self.assertEqual(
            self.clinv.return_value.unassigned.assert_called_with('ec2'),
            None,
        )

    def test_list_subcommand(self):
        self.parser_args.subcommand = 'list'
        self.parser_args.resource_type = 'ec2'
        main()
        self.assertTrue(self.clinv.return_value.load_source_data_from_file.called)
        self.assertTrue(self.clinv.return_value.load_user_data_from_file.called)
        self.assertEqual(
            self.clinv.return_value.list.assert_called_with('ec2'),
            None,
        )

    def test_export_subcommand(self):
        self.parser_args.subcommand = 'export'
        self.parser_args.export_path = 'file.ods'
        main()
        self.assertTrue(self.clinv.return_value.load_source_data_from_file.called)
        self.assertTrue(self.clinv.return_value.load_user_data_from_file.called)
        self.assertEqual(
            self.clinv.return_value.export.assert_called_with(
                'file.ods',
            ),
            None,
        )

    def test_print_subcommand(self):
        self.parser_args.subcommand = 'print'
        self.parser_args.resource_id = 'resource_id'
        main()
        self.assertTrue(self.clinv.return_value.load_source_data_from_file.called)
        self.assertTrue(self.clinv.return_value.load_user_data_from_file.called)
        self.assertEqual(
            self.clinv.return_value.print.assert_called_with('resource_id'),
            None,
        )
