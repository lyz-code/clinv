import unittest
from unittest.mock import patch

from clinv import main


class TestMain(unittest.TestCase):
    def setUp(self):
        self.parser_patch = patch("clinv.load_parser", autospect=True)
        self.parser = self.parser_patch.start()
        self.parser_args = self.parser.return_value.parse_args.return_value

        self.inventory_patch = patch("clinv.Inventory", autospect=True)
        self.inventory = self.inventory_patch.start()

    def tearDown(self):
        self.parser_patch.stop()
        self.inventory_patch.stop()

    def test_main_loads_parser(self):
        self.parser.parse_args = True
        main()
        self.assertTrue(self.parser.called)

    @patch("clinv.load_logger")
    def test_main_loads_logger(self, loggerMock):
        self.parser.parse_args = True
        main()
        self.assertTrue(loggerMock.called)

    def test_main_loads_inventory(self):
        self.parser.parse_args = True
        self.parser_args.data_path = "path"
        main()
        self.assertEqual(
            self.inventory.assert_called_with("path"), None,
        )

    def test_generate_subcommand(self):
        self.parser_args.subcommand = "generate"
        main()
        self.assertTrue(self.inventory.return_value.generate.called)

    def test_generate_subcommand_with_resource_type(self):
        self.parser_args.subcommand = "generate"
        self.parser_args.resource_type = "ec2"
        main()

        self.inventory.return_value.generate.assert_called_with("ec2")

    @patch("clinv.SearchReport")
    def test_search_subcommand(self, reportMock):
        self.parser_args.subcommand = "search"
        self.parser_args.search_string = "inst"
        main()
        self.assertTrue(self.inventory.return_value.load.called)
        self.assertEqual(
            reportMock.assert_called_with(self.inventory.return_value), None,
        )
        self.assertEqual(
            reportMock.return_value.output.assert_called_with("inst"), None,
        )

    @patch("clinv.UnassignedReport")
    def test_unassigned_subcommand(self, reportMock):
        self.parser_args.subcommand = "unassigned"
        self.parser_args.resource_type = "ec2"
        main()
        self.assertTrue(self.inventory.return_value.load.called)
        self.assertEqual(
            reportMock.assert_called_with(self.inventory.return_value), None,
        )
        self.assertEqual(
            reportMock.return_value.output.assert_called_with("ec2"), None,
        )

    @patch("clinv.ListReport")
    def test_list_subcommand(self, reportMock):
        self.parser_args.resource_type = "ec2"
        self.parser_args.subcommand = "list"
        main()
        self.assertTrue(self.inventory.return_value.load.called)
        self.assertEqual(
            reportMock.assert_called_with(self.inventory.return_value), None,
        )
        self.assertEqual(
            reportMock.return_value.output.assert_called_with("ec2"), None,
        )

    @patch("clinv.ActiveReport")
    def test_active_subcommand(self, reportMock):
        self.parser_args.resource_type = "ec2"
        self.parser_args.subcommand = "active"
        main()
        self.assertTrue(self.inventory.return_value.load.called)
        self.assertEqual(
            reportMock.assert_called_with(self.inventory.return_value), None,
        )
        self.assertEqual(
            reportMock.return_value.output.assert_called_with("ec2"), None,
        )

    @patch("clinv.ExportReport")
    def test_export_subcommand(self, reportMock):
        self.parser_args.subcommand = "export"
        self.parser_args.export_path = "file.ods"
        main()
        self.assertTrue(self.inventory.return_value.load.called)
        self.assertEqual(
            reportMock.assert_called_with(self.inventory.return_value), None,
        )
        self.assertEqual(
            reportMock.return_value.output.assert_called_with("file.ods"), None,
        )

    @patch("clinv.PrintReport")
    def test_print_subcommand(self, reportMock):
        self.parser_args.subcommand = "print"
        self.parser_args.search_string = "resource_id"
        main()
        self.assertTrue(self.inventory.return_value.load.called)
        self.assertEqual(
            reportMock.assert_called_with(self.inventory.return_value), None,
        )
        self.assertEqual(
            reportMock.return_value.output.assert_called_with("resource_id"), None,
        )

    @patch("clinv.MonitorReport")
    def test_monitor_subcommand(self, reportMock):
        self.parser_args.subcommand = "monitor"
        self.parser_args.monitor_status = "true"
        main()
        self.assertTrue(self.inventory.return_value.load.called)
        self.assertEqual(
            reportMock.assert_called_with(self.inventory.return_value), None,
        )
        self.assertEqual(
            reportMock.return_value.output.assert_called_with("true"), None,
        )

    @patch("clinv.UnusedReport")
    def test_unused_subcommand(self, reportMock):
        self.parser_args.subcommand = "unused"
        main()
        self.assertTrue(self.inventory.return_value.load.called)
        self.assertEqual(
            reportMock.assert_called_with(self.inventory.return_value), None,
        )
        self.assertEqual(
            reportMock.return_value.output.assert_called_with(), None,
        )
