from clinv.sources.risk_management import RiskManagementsrc
from tests.sources import ClinvSourceBaseTestClass
from unittest.mock import patch
import unittest


class TestRiskManagementSource(ClinvSourceBaseTestClass, unittest.TestCase):
    '''
    Test the RiskManagement implementation in the inventory.
    '''

    def setUp(self):
        super().setUp()
        self.class_obj = RiskManagementsrc

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.class_obj(source_data, user_data)

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        expected_source_data = {}

        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data,
            expected_source_data,
        )
        self.assertEqual(
            generated_source_data,
            expected_source_data,
        )

    def test_generate_user_data_creates_expected_user_data_attrib(self):
        expected_user_data = {}

        generated_user_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.user_data,
            expected_user_data,
        )
        self.assertEqual(
            generated_user_data,
            expected_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.user_data = {}
        self.assertEqual(
            self.src.generate_inventory(),
            {
                'informations': {},
                'projects': {},
                'services': {},
            }
        )

    @patch('clinv.sources.risk_management.Information')
    def test_generate_inventory_creates_information_objects(
        self,
        resource_mock
    ):
        resource_id = 'inf_01'
        self.src.user_data = {
            'informations': {
                resource_id: 'tbd'
            },
        }

        desired_mock_input = 'tbd'

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with(
                {
                    resource_id: desired_mock_input
                },
            ),
            None,
        )

        self.assertEqual(
            desired_inventory,
            {
                'services': {},
                'informations': {
                    resource_id: resource_mock.return_value
                },
                'projects': {},
            },
        )

    @patch('clinv.sources.risk_management.Project')
    def test_generate_inventory_creates_project_objects(self, resource_mock):
        resource_id = 'pro_01'
        self.src.user_data = {
            'projects': {
                resource_id: 'tbd'
            },
        }

        desired_mock_input = 'tbd'

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with(
                {
                    resource_id: desired_mock_input
                },
            ),
            None,
        )

        self.assertEqual(
            desired_inventory,
            {
                'informations': {},
                'projects': {
                    resource_id: resource_mock.return_value
                },
                'services': {},
            },
        )

    @patch('clinv.sources.risk_management.Service')
    def test_generate_inventory_creates_service_objects(self, resource_mock):
        resource_id = 'ser_01'
        self.src.user_data = {
            'services': {
                resource_id: 'tbd'
            },
        }

        desired_mock_input = 'tbd'

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with(
                {
                    resource_id: desired_mock_input
                },
            ),
            None,
        )

        self.assertEqual(
            desired_inventory,
            {
                'informations': {},
                'services': {
                    resource_id: resource_mock.return_value
                },
                'projects': {},
            },
        )
