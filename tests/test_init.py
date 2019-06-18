import unittest
from unittest.mock import patch

from clinv import main


class TestMain(unittest.TestCase):

    @patch('clinv.load_parser')
    def test_main_loads_parser(self, parserMock):
        parserMock.parse_args = True
        main()
        self.assertTrue(parserMock.called)

    @patch('clinv.load_parser')
    @patch('clinv.load_logger')
    def test_main_loads_logger(self, loggerMock, parserMock):
        parserMock.parse_args = True
        main()
        self.assertTrue(loggerMock.called)

    @patch('clinv.load_parser')
    @patch('clinv.Clinv', autospect=True)
    def test_search_subcommand(self, clinvMock, parserMock):
        parserMock.return_value.parse_args.return_value.subcommand = 'search'
        parserMock.return_value.parse_args.return_value.search_string = 'inst'
        parserMock.return_value.parse_args.return_value.inventory_path = 'path'
        main()
        self.assertEqual(
            clinvMock.assert_called_with('path'),
            None,
        )
        self.assertTrue(clinvMock.return_value.load_inventory.called)
        self.assertEqual(
            clinvMock.return_value.print_ec2.assert_called_with('inst'),
            None,
        )

    @patch('clinv.load_parser')
    @patch('clinv.Clinv', autospect=True)
    def test_generate_subcommand(self, clinvMock, parserMock):
        parserMock.return_value.parse_args.return_value.subcommand = 'generate'
        main()
        self.assertTrue(clinvMock.return_value._fetch_ec2.called)
        self.assertTrue(clinvMock.return_value.save_inventory.called)
