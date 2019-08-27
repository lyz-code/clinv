from clinv.clinv import Clinv, Inventory
from collections import OrderedDict
from unittest.mock import patch, call
from yaml import YAMLError
import os
import shutil
import tempfile
import unittest


class ClinvBaseTestClass(object):
    '''
    Base class to setup the setUp and tearDown methods for the test cases.
    '''

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.inventory_dir = self.tmp
        self.logging_patch = patch('clinv.clinv.logging', autospect=True)
        self.logging = self.logging_patch.start()
        self.print_patch = patch('clinv.clinv.print', autospect=True)
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
        self.source_data_path = os.path.join(
            self.inventory_dir,
            'source_data.yaml',
        )
        self.user_data_path = os.path.join(
            self.inventory_dir,
            'user_data.yaml',
        )

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
        save_file = os.path.join(self.tmp, 'yaml_save_test.yaml')
        dictionary = {'a': 'b', 'c': 'd'}
        self.inv._save_yaml(save_file, dictionary)
        with open(save_file, 'r') as f:
            self.assertEqual("a: b\nc: d\n", f.read())

    def test_load_yaml(self):
        with open(self.source_data_path, 'w') as f:
            f.write('test: this is a test')
        yaml_content = self.inv._load_yaml(self.source_data_path)
        self.assertEqual(yaml_content['test'], 'this is a test')

    @patch('clinv.clinv.os')
    @patch('clinv.clinv.yaml')
    def test_load_yaml_raises_error_if_wrong_format(self, yamlMock, osMock):
        yamlMock.safe_load.side_effect = YAMLError('error')

        with self.assertRaises(YAMLError):
            self.inv._load_yaml(self.source_data_path)
        self.assertEqual(
            str(self.logging.getLogger.return_value.error.mock_calls),
            str([call(YAMLError('error'))])
        )

    @patch('clinv.clinv.open')
    def test_load_yaml_raises_error_if_file_not_found(self, openMock):
        openMock.side_effect = FileNotFoundError()

        with self.assertRaises(FileNotFoundError):
            self.inv._load_yaml(self.source_data_path)
        self.assertEqual(
            str(self.logging.getLogger.return_value.error.mock_calls),
            str([call(
                'Error opening yaml file {}'.format(self.source_data_path)
            )])
        )

    @patch('clinv.clinv.Inventory._load_yaml')
    def test_load_loads_source_data(self, loadMock):
        self.inv.load()
        self.assertTrue(call(self.source_data_path) in loadMock.mock_calls)
        self.assertEqual(self.inv.source_data, loadMock())

    @patch('clinv.clinv.Inventory._load_yaml')
    def test_load_loads_user_data(self, loadMock):
        self.inv.load()
        self.assertTrue(call(self.user_data_path) in loadMock.mock_calls)
        self.assertEqual(self.inv.user_data, loadMock())

    @patch('clinv.clinv.Inventory._load_yaml')
    @patch('clinv.clinv.Inventory._load_plugins')
    @patch('clinv.clinv.Inventory._generate_inventory_objects')
    def test_load_loads_plugins(self, invMock, loadMock, yamlMock):
        self.inv.load()
        self.assertTrue(loadMock.called)

    @patch('clinv.clinv.Inventory._load_yaml')
    @patch('clinv.clinv.Inventory._generate_inventory_objects')
    def test_load_generates_inventory_objects(self, invMock, yamlMock):
        self.inv.load()
        self.assertTrue(invMock.called)

    @patch('clinv.clinv.Inventory._save_yaml')
    def test_save_saves_source_data(self, saveMock):
        self.inv.save()
        self.assertTrue(
            call(self.source_data_path, self.inv.source_data)
            in saveMock.mock_calls
        )

    @patch('clinv.clinv.Inventory._save_yaml')
    def test_save_saves_user_data(self, saveMock):
        self.inv.save()
        self.assertTrue(
            call(self.user_data_path, self.inv.user_data)
            in saveMock.mock_calls
        )


class TestInventoryPluginLoad(InventoryBaseTestClass, unittest.TestCase):
    """
    Test class to assess that the Inventory plugins methods work as expected
    """

    def setUp(self):
        super().setUp()
        self.source_patch = patch('clinv.clinv.Route53src', autospect=True)
        self.source = self.source_patch.start()
        self.source.return_value.id = 'source_id'
        self.source_plugins = [self.source]

        self.inv = Inventory(self.inventory_dir, self.source_plugins)
        self.inv._load_plugins()

    def tearDown(self):
        super().tearDown()

    def test_load_plugins_creates_expected_list_if_user_data(self):
        self.inv.user_data = {'source_id': {'user': 'data'}}

        self.inv._load_plugins()

        self.assertEqual(
            self.source.assert_called_with({'user': 'data'}),
            None
        )
        self.assertEqual(
            self.inv.sources,
            [
                self.source.return_value
            ]
        )

    def test_load_plugins_creates_expected_list_if_no_user_data(self):
        self.inv.user_data = {}

        self.inv._load_plugins()

        self.assertEqual(
            self.source.assert_called_with({}),
            None
        )
        self.assertEqual(
            self.inv.sources,
            [
                self.source.return_value
            ]
        )

    def test_generate_source_data_loads_data_from_plugins(self):
        self.inv._generate_source_data()

        self.assertEqual(
            self.inv.source_data,
            {
                'source_id':
                    self.source.return_value.generate_source_data.return_value
            }
        )

    def test_generate_user_data_loads_data_from_plugins(self):
        self.inv._generate_user_data()

        self.assertEqual(
            self.inv.user_data,
            {
                'source_id':
                    self.source.return_value.generate_user_data.return_value
            }
        )

    def test_generate_inventory_objects_loads_data_from_plugins(self):
        self.inv._generate_inventory_objects()

        self.assertEqual(
            self.inv.inv,
            {
                'source_id':
                    self.source.return_value.generate_inventory.return_value
            }
        )

    @patch('clinv.clinv.Inventory._generate_inventory_objects')
    @patch('clinv.clinv.Inventory._generate_user_data')
    @patch('clinv.clinv.Inventory._generate_source_data')
    @patch('clinv.clinv.Inventory.save')
    def test_generate_loads_data_from_plugins(
        self,
        saveMock,
        sourceMock,
        userMock,
        inventoryMock,
    ):
        self.inv.generate()

        self.assertTrue(saveMock.called)
        self.assertTrue(sourceMock.called)
        self.assertTrue(userMock.called)
        self.assertTrue(inventoryMock.called)


class TestClinv(ClinvBaseTestClass, unittest.TestCase):
    '''
    Monolith test class
    '''

    def setUp(self):
        super().setUp()
        self.clinv = Clinv(self.inventory_dir)
        self.clinv.raw_inv = {
            'ec2': {
                'us-east-1': self.boto_ec2_describe_instances['Reservations']
            },
            'rds': {
                'us-east-1': self.boto_rds_describe_instances['DBInstances']
            },
            'route53': {
            },
        }
        self.clinv.user_data = {
            'ec2': {
                'i-023desldk394995ss': {
                    'description': '',
                    'to_destroy': False,
                }
            },
            'rds': {},
            'route53': {},
            'projects': {
                'pro_01': {
                    'name': 'project 1',
                },
            },
            'services': {
                'ser_01': {
                    'name': 'service 1',
                },
            },
            'informations': {
                'inf_01': {
                    'name': 'information 1',
                },
            },
        }
        self.clinv.inv = {
            'ec2': {
                'i-023desldk394995ss': self.ec2instance.return_value
            },
            'rds': {
                'db-YDFL2': self.rdsinstance.return_value
            },
            'route53': {
                'record1.clinv.org': self.route53instance.return_value
            },
            'projects': {
                'pro_01': self.project.return_value
            },
            'services': {
                'ser_01': self.service.return_value
            },
            'informations': {
                'inf_01': self.information.return_value
            },
        }
        self.ec2instance.return_value.name = 'resource_name'
        self.ec2instance.return_value.id = 'i-023desldk394995ss'
        self.ec2instance.return_value.public_ips = ['32.312.444.22']
        self.ec2instance.return_value.private_ips = ['142.33.2.113']
        self.ec2instance.return_value.security_groups = ['sg-f2234gf6']

    def tearDown(self):
        super().tearDown()
        self.ec2instance_patch.stop()
        self.rdsinstance_patch.stop()
        self.project_patch.stop()
        self.service_patch.stop()
        self.information_patch.stop()
        self.route53_patch.stop()
        self.route53instance_patch.stop()

    def test_search_ec2_returns_instances(self):
        self.ec2instance.return_value.search.return_value = True
        instances = self.clinv._search_ec2('resource_name')
        self.assertEqual(
            instances,
            [self.ec2instance()]
        )

    def test_search_rds_returns_instances(self):
        self.rdsinstance.return_value.search.return_value = True
        instances = self.clinv._search_rds('resource_name')
        self.assertEqual(
            instances,
            [self.rdsinstance()]
        )

    def test_search_projects_returns_instances(self):
        self.project.return_value.search.return_value = True
        instances = self.clinv._search_projects('resource_name')
        self.assertEqual(
            instances,
            [self.project.return_value]
        )

    def test_search_services_returns_instances(self):
        self.service.return_value.search.return_value = True
        instances = self.clinv._search_services('resource_name')
        self.assertEqual(
            instances,
            [self.service.return_value]
        )

    def test_search_informations_returns_instances(self):
        self.information.return_value.search.return_value = True
        instances = self.clinv._search_informations('resource_name')
        self.assertEqual(
            instances,
            [self.information.return_value]
        )

    @patch('clinv.clinv.Clinv._search_ec2')
    def test_print_search_prints_ec2_instance_information(self, searchMock):
        searchMock.return_value = [self.ec2instance()]
        self.clinv.print_search('resource_name')
        self.assertEqual(
            searchMock.assert_called_with('resource_name'),
            None,
        )
        print_calls = (
            call('\nType: EC2 instances'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.ec2instance.return_value.short_print.called)

    @patch('clinv.clinv.Clinv._search_ec2')
    @patch('clinv.clinv.Clinv._search_projects')
    def test_print_nothing_found(self, projectsMock, searchMock):
        searchMock.return_value = []
        projectsMock.return_value = []
        self.clinv.print_search('resource_name')
        self.assertEqual(
            searchMock.assert_called_with('resource_name'),
            None,
        )
        print_calls = (
            call('I found nothing with that search_string'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))

    @patch('clinv.clinv.Clinv._search_projects')
    def test_print_search_prints_projects_information(self, searchMock):
        searchMock.return_value = [self.project()]
        self.clinv.print_search('resource_name')
        self.assertEqual(
            searchMock.assert_called_with('resource_name'),
            None,
        )
        print_calls = (
            call('Type: Projects'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.project.return_value.short_print.called)

    @patch('clinv.clinv.Clinv._search_services')
    def test_print_search_prints_services_information(self, searchMock):
        searchMock.return_value = [self.service()]
        self.clinv.print_search('resource_name')
        self.assertEqual(
            searchMock.assert_called_with('resource_name'),
            None,
        )
        print_calls = (
            call('\nType: Services'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.service.return_value.short_print.called)

    @patch('clinv.clinv.Clinv._search_informations')
    def test_print_search_prints_informations_information(self, searchMock):
        searchMock.return_value = [self.information()]
        self.clinv.print_search('resource_name')
        self.assertEqual(
            searchMock.assert_called_with('resource_name'),
            None,
        )
        print_calls = (
            call('\nType: Informations'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.information.return_value.short_print.called)

    @patch('clinv.clinv.Clinv._search_rds')
    def test_print_search_prints_rds_information(self, searchMock):
        searchMock.return_value = [self.rdsinstance()]
        self.clinv.print_search('resource_name')
        self.assertEqual(
            searchMock.assert_called_with('resource_name'),
            None,
        )
        print_calls = (
            call('\nType: RDS instances'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.rdsinstance.return_value.short_print.called)


class TestRoute53Reports(ClinvBaseTestClass, unittest.TestCase):
    '''
    Test the Route53 reports
    '''

    def setUp(self):
        super().setUp()

        # Required mocks
        self.route53instance_patch = patch(
            'clinv.clinv.Route53', autospect=True
        )
        self.route53instance = self.route53instance_patch.start()
        self.service_patch = patch(
            'clinv.clinv.Service', autospect=True
        )
        self.service = self.service_patch.start()

        # Initialize object to test
        self.clinv = Clinv(self.inventory_dir)

        self.clinv.inv = {
            'services': {
                'ser_01': self.service.return_value
            },
            'route53': {
                'hosted_zone_id-record1.clinv.org-cname':
                self.route53instance.return_value
            },
        }

    def tearDown(self):
        super().tearDown()
        self.route53instance_patch.stop()
        self.service_patch.stop()

    def test_search_route53_returns_instances(self):
        self.route53instance.return_value.search.return_value = True
        instances = self.clinv._search_route53('resource_name')
        self.assertEqual(
            instances,
            [self.route53instance()]
        )

    @patch('clinv.clinv.Clinv._search_route53')
    @patch('clinv.clinv.Clinv._search_projects')
    @patch('clinv.clinv.Clinv._search_services')
    @patch('clinv.clinv.Clinv._search_informations')
    @patch('clinv.clinv.Clinv._search_rds')
    @patch('clinv.clinv.Clinv._search_ec2')
    def test_print_search_prints_route53_instance_information(
        self,
        ec2Mock,
        rdsMock,
        informationsMock,
        servicesMock,
        projectsMock,
        route53Mock,
    ):
        ec2Mock.return_value = []
        rdsMock.return_value = []
        informationsMock.return_value = []
        servicesMock.return_value = []
        projectsMock.return_value = []
        route53Mock.return_value = [self.route53instance()]
        self.clinv.print_search('resource_name')
        self.assertEqual(
            route53Mock.assert_called_with('resource_name'),
            None,
        )
        print_calls = (
            call('\nType: Route53 instances'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.route53instance.return_value.short_print.called)
