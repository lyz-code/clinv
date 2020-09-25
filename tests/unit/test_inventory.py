import os
import shutil
import tempfile
import unittest
from unittest.mock import call, patch

import pytest
from clinv.inventory import Inventory
from yaml import YAMLError


class ClinvBaseTestClass(object):
    """
    Base class to setup the setUp and tearDown methods for the test cases.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.inventory_dir = self.tmp
        self.logging_patch = patch("clinv.inventory.logging", autospect=True)
        self.logging = self.logging_patch.start()
        self.print_patch = patch("clinv.inventory.print", autospect=True)
        self.print = self.print_patch.start()

    def tearDown(self):
        self.logging_patch.stop()
        self.print_patch.stop()
        shutil.rmtree(self.tmp)


class InventoryBaseTestClass(ClinvBaseTestClass):
    """
    Base class to setup the setUp and tearDown methods for the Inventory test
    cases.
    """

    def setUp(self):
        super().setUp()
        self.source_data_path = os.path.join(self.inventory_dir, "source_data.yaml",)
        self.user_data_path = os.path.join(self.inventory_dir, "user_data.yaml",)

    def tearDown(self):
        super().tearDown()


class TestInventory(InventoryBaseTestClass, unittest.TestCase):
    """
    Test class to assess that the Inventory class works as expected
    """

    def setUp(self):
        super().setUp()
        self.source_plugins = []

        self.inv = Inventory(self.inventory_dir, self.source_plugins)

    def tearDown(self):
        super().tearDown()

    def test_init_sets_inventory_dir(self):
        self.assertEqual(self.inv.inventory_dir, self.inventory_dir)

    def test_init_sets_source_plugins(self):
        self.assertEqual(self.inv._source_plugins, self.source_plugins)

    def test_init_sets_source_data_path(self):
        self.assertEqual(self.inv.source_data_path, self.source_data_path)

    def test_init_sets_user_data_path(self):
        self.assertEqual(self.inv.user_data_path, self.user_data_path)

    def test_yaml_saving(self):
        save_file = os.path.join(self.tmp, "yaml_save_test.yaml")
        dictionary = {"a": "b", "c": "d"}
        self.inv._save_yaml(save_file, dictionary)
        with open(save_file, "r") as f:
            self.assertEqual("a: b\nc: d\n", f.read())

    def test_load_yaml(self):
        with open(self.source_data_path, "w") as f:
            f.write("test: this is a test")
        yaml_content = self.inv._load_yaml(self.source_data_path)
        self.assertEqual(yaml_content["test"], "this is a test")

    @patch("clinv.inventory.os")
    @patch("clinv.inventory.yaml")
    def test_load_yaml_raises_error_if_wrong_format(self, yamlMock, osMock):
        yamlMock.safe_load.side_effect = YAMLError("error")

        with self.assertRaises(YAMLError):
            self.inv._load_yaml(self.source_data_path)
        self.assertEqual(
            str(self.logging.getLogger.return_value.error.mock_calls),
            str([call(YAMLError("error"))]),
        )

    @patch("clinv.inventory.open")
    def test_load_yaml_raises_error_if_file_not_found(self, openMock):
        openMock.side_effect = FileNotFoundError()

        with self.assertRaises(FileNotFoundError):
            self.inv._load_yaml(self.source_data_path)
        self.assertEqual(
            str(self.logging.getLogger.return_value.error.mock_calls),
            str([call("Error opening yaml file {}".format(self.source_data_path))]),
        )

    @patch("clinv.inventory.Inventory._load_yaml")
    def test_load_loads_source_data(self, loadMock):
        self.inv.load()
        self.assertTrue(call(self.source_data_path) in loadMock.mock_calls)
        self.assertEqual(self.inv.source_data, loadMock())

    @patch("clinv.inventory.Inventory._load_yaml")
    def test_load_loads_user_data(self, loadMock):
        self.inv.load()
        self.assertTrue(call(self.user_data_path) in loadMock.mock_calls)
        self.assertEqual(self.inv.user_data, loadMock())

    @patch("clinv.inventory.Inventory._load_yaml")
    @patch("clinv.inventory.Inventory._load_plugins")
    @patch("clinv.inventory.Inventory._generate_inventory_objects")
    def test_load_loads_plugins(self, invMock, loadMock, yamlMock):
        self.inv.load()
        self.assertTrue(loadMock.called)

    @patch("clinv.inventory.Inventory._load_yaml")
    @patch("clinv.inventory.Inventory._generate_inventory_objects")
    def test_load_generates_inventory_objects(self, invMock, yamlMock):
        self.inv.load()
        self.assertTrue(invMock.called)

    @patch("clinv.inventory.Inventory._save_yaml")
    def test_save_saves_source_data(self, saveMock):
        self.inv.save()
        self.assertTrue(
            call(self.source_data_path, self.inv.source_data) in saveMock.mock_calls
        )

    @patch("clinv.inventory.Inventory._save_yaml")
    def test_save_saves_user_data(self, saveMock):
        self.inv.save()
        self.assertTrue(
            call(self.user_data_path, self.inv.user_data) in saveMock.mock_calls
        )


class TestInventoryPluginLoad(InventoryBaseTestClass, unittest.TestCase):
    """
    Test class to assess that the Inventory plugins methods work as expected
    """

    def setUp(self):
        super().setUp()
        self.source_patch = patch("clinv.inventory.aws.Route53src", autospect=True)
        self.source = self.source_patch.start()
        self.source.return_value.id = "source_id"
        self.source_plugins = [self.source]

        self.inv = Inventory(self.inventory_dir, self.source_plugins)
        self.inv._load_plugins()

    def tearDown(self):
        super().tearDown()
        self.source_patch.stop()

    def test_load_plugins_creates_expected_list_if_user_data(self):
        self.inv.user_data = {"source_id": {"user": "data"}}

        self.inv._load_plugins()

        self.assertEqual(
            self.source.assert_called_with(source_data={}, user_data={"user": "data"},),
            None,
        )
        self.assertEqual(self.inv.sources, [self.source.return_value])

    def test_load_plugins_creates_expected_list_if_no_user_data(self):
        self.inv.user_data = {}

        self.inv._load_plugins()

        self.assertEqual(
            self.source.assert_called_with(source_data={}, user_data={}), None
        )
        self.assertEqual(self.inv.sources, [self.source.return_value])

    def test_generate_source_data_loads_data_from_plugins(self):
        self.inv._generate_source_data()

        self.assertEqual(
            self.inv.source_data,
            {"source_id": self.source.return_value.generate_source_data.return_value},
        )

    def test_generate_user_data_loads_data_from_plugins(self):
        self.inv._generate_user_data()

        self.assertEqual(
            self.inv.user_data,
            {"source_id": self.source.return_value.generate_user_data.return_value},
        )

    def test_generate_inventory_objects_loads_data_from_plugins(self):
        self.inv._generate_inventory_objects()

        self.assertEqual(
            self.inv.inv,
            {"source_id": self.source.return_value.generate_inventory.return_value},
        )

    @patch("clinv.inventory.Inventory._generate_inventory_objects")
    @patch("clinv.inventory.Inventory._generate_user_data")
    @patch("clinv.inventory.Inventory._generate_source_data")
    @patch("clinv.inventory.Inventory.save")
    @patch("clinv.inventory.Inventory._load_yaml")
    def test_generate_loads_data_from_plugins(
        self, loadMock, saveMock, sourceMock, userMock, inventoryMock,
    ):
        self.inv.generate()

        self.assertTrue(saveMock.called)
        self.assertTrue(sourceMock.called)
        self.assertTrue(userMock.called)
        self.assertTrue(inventoryMock.called)
        self.assertTrue(call(self.user_data_path) in loadMock.mock_calls)

    @pytest.mark.skip("Wait till we don't use mocks ")
    def test_generate_inventory_accepts_resource_type(self):

        pass
