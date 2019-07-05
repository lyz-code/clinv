from clinv.clinv import Clinv
from collections import OrderedDict
from dateutil.tz import tzutc
from unittest.mock import patch, call, PropertyMock
from yaml import YAMLError
import datetime
import os
import shutil
import tempfile
import unittest


class TestClinv(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.inventory_dir = self.tmp
        self.boto_patch = patch('clinv.clinv.boto3', autospect=True)
        self.boto = self.boto_patch.start()
        self.logging_patch = patch('clinv.clinv.logging', autospect=True)
        self.logging = self.logging_patch.start()
        self.print_patch = patch('clinv.clinv.print', autospect=True)
        self.print = self.print_patch.start()
        self.ec2instance_patch = patch(
            'clinv.clinv.EC2', autospect=True
        )
        self.ec2instance = self.ec2instance_patch.start()
        self.project_patch = patch(
            'clinv.clinv.Project', autospect=True
        )
        self.project = self.project_patch.start()
        self.service_patch = patch(
            'clinv.clinv.Service', autospect=True
        )
        self.service = self.service_patch.start()
        self.information_patch = patch(
            'clinv.clinv.Information', autospect=True
        )
        self.information = self.information_patch.start()

        self.clinv = Clinv(self.inventory_dir)
        self.boto_describe_instances = {
            'Reservations': [
                {
                    'Groups': [],
                    'Instances': [
                        {
                            'AmiLaunchIndex': 0,
                            'Architecture': 'x86_64',
                            'BlockDeviceMappings': [
                                {
                                    'DeviceName': '/dev/sda1',
                                    'Ebs': {
                                        'AttachTime': datetime.datetime(
                                            2018, 5, 10, 2, 58, 4,
                                            tzinfo=tzutc()
                                        ),
                                        'DeleteOnTermination': True,
                                        'Status': 'attached',
                                        'VolumeId': 'vol-02257f9299430042f'
                                    }
                                }
                            ],
                            'CapacityReservationSpecification': {
                                'CapacityReservationPreference': 'open'
                            },
                            'ClientToken': '',
                            'CpuOptions': {
                                'CoreCount': 8,
                                'ThreadsPerCore': 2
                            },
                            'EbsOptimized': True,
                            'HibernationOptions': {'Configured': False},
                            'Hypervisor': 'xen',
                            'ImageId': 'ami-ffcsssss',
                            'InstanceId': 'i-023desldk394995ss',
                            'InstanceType': 'c4.4xlarge',
                            'KeyName': 'ssh_keypair',
                            'LaunchTime': datetime.datetime(
                                2018, 5, 10, 7, 13, 17, tzinfo=tzutc()
                            ),
                            'Monitoring': {'State': 'enabled'},
                            'NetworkInterfaces': [
                                {
                                    'Association': {
                                        'IpOwnerId': '585394229490',
                                        'PublicDnsName': 'ec21.amazonaws.com',
                                        'PublicIp': '32.312.444.22'
                                    },
                                    'Attachment': {
                                        'AttachTime': datetime.datetime(
                                            2018, 5, 10, 2, 58, 3,
                                            tzinfo=tzutc()
                                        ),
                                        'AttachmentId': 'eni-attach-032346',
                                        'DeleteOnTermination': True,
                                        'DeviceIndex': 0,
                                        'Status': 'attached'
                                    },
                                    'Description': 'Primary ni',
                                    'Groups': [
                                        {
                                            'GroupId': 'sg-f2234gf6',
                                            'GroupName': 'sg-1'
                                        },
                                        {
                                            'GroupId': 'sg-cwfccs17',
                                            'GroupName': 'sg-2'
                                        }
                                    ],
                                    'InterfaceType': 'interface',
                                    'Ipv6Addresses': [],
                                    'MacAddress': '0a:ff:ff:ff:ff:aa',
                                    'NetworkInterfaceId': 'eni-3fssaw0a',
                                    'OwnerId': '583949112399',
                                    'PrivateDnsName': 'ip-112.ec2.internal',
                                    'PrivateIpAddress': '142.33.2.113',
                                    'PrivateIpAddresses': [
                                        {
                                            'Association': {
                                                'IpOwnerId': '585394460090',
                                                'PublicDnsName': 'ec2.com',
                                                'PublicIp': '32.312.444.22'
                                            },
                                            'Primary': True,
                                            'PrivateDnsName': 'ec2.nternal',
                                            'PrivateIpAddress': '1.1.1.1',
                                        }
                                    ],
                                    'SourceDestCheck': True,
                                    'Status': 'in-use',
                                    'SubnetId': 'subnet-3ssaafs1',
                                    'VpcId': 'vpc-fs12f872'
                                }
                            ],
                            'Placement': {
                                'AvailabilityZone': 'eu-east-1a',
                                'GroupName': '',
                                'Tenancy': 'default'
                            },
                            'PrivateDnsName': 'ip-112.ec2.internal',
                            'PrivateIpAddress': '142.33.2.113',
                            'ProductCodes': [],
                            'PublicDnsName': 'ec2.com',
                            'PublicIpAddress': '32.312.444.22',
                            'RootDeviceName': '/dev/sda1',
                            'RootDeviceType': 'ebs',
                            'SecurityGroups': [
                                {
                                    'GroupId': 'sg-f2234gf6',
                                    'GroupName': 'sg-1'
                                },
                                {
                                    'GroupId': 'sg-cwfccs17',
                                    'GroupName': 'sg-2'
                                }
                            ],
                            'SourceDestCheck': True,
                            'State': {'Code': 16, 'Name': 'running'},
                            'StateTransitionReason': '',
                            'SubnetId': 'subnet-sfsdwf12',
                            'Tags': [{'Key': 'Name', 'Value': 'name'}],
                            'VirtualizationType': 'hvm',
                            'VpcId': 'vpc-31084921'
                        }
                    ],
                    'OwnerId': '585394460090',
                    'ReservationId': 'r-039ed99cad2bb3da5'
                }
            ]
        }
        self.clinv.raw_inv = {
            'ec2': {
                'us-east-1': self.boto_describe_instances['Reservations']
            }
        }
        self.clinv.raw_data = {
            'ec2': {
                'i-023desldk394995ss': {
                    'description': '',
                    'to_destroy': False,
                }
            },
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
        self.raw_inv_path = os.path.join(
            self.inventory_dir,
            'raw_inventory.yaml',
        )
        self.raw_data_path = os.path.join(
            self.inventory_dir,
            'raw_data.yaml',
        )
        self.clinv.inv = {
            'ec2': {
                'i-023desldk394995ss': self.ec2instance.return_value
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
        self.ec2instance.return_value.name = 'inst_name'
        self.ec2instance.return_value.id = 'i-023desldk394995ss'
        self.ec2instance.return_value.public_ips = ['32.312.444.22']
        self.ec2instance.return_value.private_ips = ['142.33.2.113']
        self.ec2instance.return_value.security_groups = ['sg-f2234gf6']

    def tearDown(self):
        self.boto_patch.stop()
        self.logging_patch.stop()
        self.print_patch.stop()
        self.ec2instance_patch.stop()
        self.project_patch.stop()
        self.service_patch.stop()
        self.information_patch.stop()
        shutil.rmtree(self.tmp)

    @patch('clinv.clinv.Clinv.regions', new_callable=PropertyMock)
    def test_aws_resources_ec2_populated_by_boto(self, regionsMock):
        regionsMock.return_value = ['us-east-1']

        expected_ec2_aws_resources = {
            'us-east-1': [
                dict(self.boto_describe_instances['Reservations'][0]),
            ],
        }
        self.boto.client.return_value.describe_instances.return_value = \
            self.boto_describe_instances

        self.clinv._update_raw_ec2()
        self.assertEqual(
            self.clinv.raw_inv['ec2'],
            expected_ec2_aws_resources,
        )

    @patch('clinv.clinv.Clinv.regions', new_callable=PropertyMock)
    def test_short_ec2_inventory_created(self, regionsMock):
        regionsMock.return_value = ['us-east-1']
        prune_keys = [
            'AmiLaunchIndex',
            'Architecture',
            'BlockDeviceMappings',
            'CapacityReservationSpecification',
            'ClientToken',
            'CpuOptions',
            'EbsOptimized',
            'HibernationOptions',
            'Hypervisor',
            'ImageId',
            'KeyName',
            'LaunchTime',
            'Monitoring',
            'Placement',
            'PrivateDnsName',
            'PrivateIpAddress',
            'ProductCodes',
            'PublicDnsName',
            'PublicIpAddress',
            'RootDeviceName',
            'RootDeviceType',
            'SourceDestCheck',
            'SubnetId',
            'VirtualizationType',
        ]
        network_prune_keys = [
            'Association',
            'Attachment',
            'Description',
            'Groups',
            'InterfaceType',
            'Ipv6Addresses',
            'MacAddress',
            'NetworkInterfaceId',
            'OwnerId',
            'PrivateDnsName',
            'PrivateIpAddress',
            'SourceDestCheck',
            'Status',
            'SubnetId',
            'VpcId',
        ]
        self.boto.client.return_value.describe_instances.return_value = \
            self.boto_describe_instances

        self.clinv._update_raw_ec2()

        for prune_key in prune_keys:
            self.assertTrue(
                prune_key not in
                self.clinv.raw_inv['ec2']['us-east-1'][0]['Instances'][0].keys(
                ),
            )
        for prune_key in network_prune_keys:
            self.assertTrue(
                prune_key not in
                self.clinv.raw_inv['ec2']['us-east-1'][0]['Instances'][0][
                    'NetworkInterfaces'
                ][0].keys(),
            )

    @patch('clinv.clinv.Clinv._update_raw_ec2')
    def test_update_raw_inventory_calls_expected_resource_updates(
        self,
        ec2Mock,
    ):
        self.clinv._update_raw_inventory()

        self.assertTrue(ec2Mock.called)

    def test_update_inventory_adds_ec2_instances(self):
        self.ec2instance.return_value.id = 'i-023desldk394995ss'
        self.clinv._update_inventory()

        desired_input = \
            self.clinv.raw_inv['ec2']['us-east-1'][0]['Instances'][0]
        desired_input['description'] = ''
        desired_input['to_destroy'] = 'tbd'
        desired_input['environment'] = 'tbd'
        desired_input['region'] = 'us-east-1'
        self.assertEqual(
            self.ec2instance.assert_called_with(
                {
                    'i-023desldk394995ss': self.clinv.raw_inv['ec2']
                    ['us-east-1'][0]['Instances'][0]
                },
            ),
            None,
        )
        self.assertEqual(
            self.clinv.inv['ec2']['i-023desldk394995ss'],
            self.ec2instance()
        )

    def test_update_inventory_adds_project_instances(self):
        self.clinv._update_inventory()

        self.assertEqual(
            self.project.assert_called_with(
                self.clinv.raw_data['projects']
            ),
            None,
        )
        self.assertEqual(
            self.clinv.inv['projects']['pro_01'],
            self.project.return_value
        )

    def test_update_inventory_adds_service_instances(self):
        self.clinv._update_inventory()

        self.assertEqual(
            self.service.assert_called_with(
                self.clinv.raw_data['services']
            ),
            None,
        )
        self.assertEqual(
            self.clinv.inv['services']['ser_01'],
            self.service.return_value
        )

    def test_update_inventory_adds_information_instances(self):
        self.clinv._update_inventory()

        self.assertEqual(
            self.information.assert_called_with(
                self.clinv.raw_data['informations']
            ),
            None,
        )
        self.assertEqual(
            self.clinv.inv['informations']['inf_01'],
            self.information.return_value
        )

    def test_yaml_saving(self):
        save_file = os.path.join(self.tmp, 'yaml_save_test.yaml')
        dictionary = {'a': 'b', 'c': 'd'}
        self.clinv._save_yaml(save_file, dictionary)
        with open(save_file, 'r') as f:
            self.assertEqual("a: b\nc: d\n", f.read())

    def test_load_yaml(self):
        with open(self.raw_inv_path, 'w') as f:
            f.write('test: this is a test')
        yaml_content = self.clinv._load_yaml(self.raw_inv_path)
        self.assertEqual(yaml_content['test'], 'this is a test')

    @patch('clinv.clinv.os')
    @patch('clinv.clinv.yaml')
    def test_load_yaml_raises_error_if_wrong_format(self, yamlMock, osMock):
        yamlMock.safe_load.side_effect = YAMLError('error')

        with self.assertRaises(YAMLError):
            self.clinv._load_yaml(self.raw_inv_path)
        self.assertEqual(
            str(self.logging.getLogger.return_value.error.mock_calls),
            str([call(YAMLError('error'))])
        )

    @patch('clinv.clinv.open')
    def test_load_yaml_raises_error_if_file_not_found(self, openMock):
        openMock.side_effect = FileNotFoundError()

        with self.assertRaises(FileNotFoundError):
            self.clinv._load_yaml(self.raw_inv_path)
        self.assertEqual(
            str(self.logging.getLogger.return_value.error.mock_calls),
            str([call(
                'Error opening yaml file {}'.format(self.raw_inv_path)
            )])
        )

    @patch('clinv.clinv.Clinv._save_yaml')
    def test_inventory_saving_saves_raw_inventory(self, saveMock):
        self.clinv.save_inventory()
        self.assertTrue(
            call(self.raw_inv_path, self.clinv.raw_inv) in saveMock.mock_calls
        )

    @patch('clinv.clinv.Clinv._save_yaml')
    def test_inventory_saving_saves_raw_data(self, saveMock):
        self.clinv.save_inventory()
        self.assertTrue(
            call(self.raw_data_path, self.clinv.raw_data)
            in saveMock.mock_calls
        )

    @patch('clinv.clinv.Clinv._load_yaml')
    def test_inventory_loading_loads_raw_inventory(self, loadMock):
        self.clinv.load_inventory()
        self.assertTrue(call(self.raw_inv_path) in loadMock.mock_calls)
        self.assertEqual(self.clinv.raw_inv, loadMock())

    @patch('clinv.clinv.Clinv._load_yaml')
    @patch('clinv.clinv.Clinv._update_inventory')
    def test_data_loading_loads_raw_data(self, updateMock, loadMock):
        self.clinv.load_data()
        self.assertTrue(call(self.raw_data_path) in loadMock.mock_calls)
        self.assertEqual(self.clinv.raw_data, loadMock())

    @patch('clinv.clinv.Clinv._load_yaml')
    @patch('clinv.clinv.Clinv._update_inventory')
    def test_data_loading_updates_dictionary(self, updateMock, loadMock):
        self.clinv.load_data()
        self.assertTrue(updateMock.called)

    def test_search_ec2_returns_instances(self):
        self.ec2instance.return_value.search.return_value = True
        instances = self.clinv._search_ec2('inst_name')
        self.assertEqual(
            instances,
            [self.ec2instance()]
        )

    def test_search_projects_returns_instances(self):
        self.project.return_value.search.return_value = True
        instances = self.clinv._search_projects('inst_name')
        self.assertEqual(
            instances,
            [self.project.return_value]
        )

    def test_search_services_returns_instances(self):
        self.service.return_value.search.return_value = True
        instances = self.clinv._search_services('inst_name')
        self.assertEqual(
            instances,
            [self.service.return_value]
        )

    def test_search_informations_returns_instances(self):
        self.information.return_value.search.return_value = True
        instances = self.clinv._search_informations('inst_name')
        self.assertEqual(
            instances,
            [self.information.return_value]
        )

    @patch('clinv.clinv.Clinv._search_ec2')
    def test_print_search_prints_ec2_instance_information(self, searchMock):
        searchMock.return_value = [self.ec2instance()]
        self.clinv.print_search('inst_name')
        self.assertEqual(
            searchMock.assert_called_with('inst_name'),
            None,
        )
        print_calls = (
            call('\nType: EC2 instances'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.ec2instance.return_value.print.called)

    @patch('clinv.clinv.Clinv._search_ec2')
    @patch('clinv.clinv.Clinv._search_projects')
    def test_print_nothing_found(self, projectsMock, searchMock):
        searchMock.return_value = []
        projectsMock.return_value = []
        self.clinv.print_search('inst_name')
        self.assertEqual(
            searchMock.assert_called_with('inst_name'),
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
        self.clinv.print_search('inst_name')
        self.assertEqual(
            searchMock.assert_called_with('inst_name'),
            None,
        )
        print_calls = (
            call('Type: Projects'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.project.return_value.print.called)

    @patch('clinv.clinv.Clinv._search_services')
    def test_print_search_prints_services_information(self, searchMock):
        searchMock.return_value = [self.service()]
        self.clinv.print_search('inst_name')
        self.assertEqual(
            searchMock.assert_called_with('inst_name'),
            None,
        )
        print_calls = (
            call('\nType: Services'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.service.return_value.print.called)

    @patch('clinv.clinv.Clinv._search_informations')
    def test_print_search_prints_informations_information(self, searchMock):
        searchMock.return_value = [self.information()]
        self.clinv.print_search('inst_name')
        self.assertEqual(
            searchMock.assert_called_with('inst_name'),
            None,
        )
        print_calls = (
            call('\nType: Informations'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.information.return_value.print.called)

    def test_unassigned_ec2_prints_instances(self):
        self.clinv.raw_data = {
            'services': {
                'ser_01': {
                    'aws': {
                        'ec2': [
                            'i-xxxxxxxxxxxxxxxxx'
                        ],
                    },
                },
            },
            'ec2': {
                'i-023desldk394995ss': []
            },
        }
        self.clinv._unassigned_ec2()
        print_calls = (
            call('i-023desldk394995ss: inst_name'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))

    def test_unassigned_ec2_does_not_fail_on_empty_service(self):
        self.clinv.raw_data = {
            'services': {
                'ser_01': {
                    'aws': {
                        'ec2': None
                    },
                },
            },
            'ec2': {
                'i-023desldk394995ss': []
            },
        }
        self.clinv._unassigned_ec2()
        print_calls = (
            call('i-023desldk394995ss: inst_name'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))

    @patch('clinv.clinv.Clinv._print_resources')
    def test_unassigned_services_prints_instances(self, printMock):
        self.project.return_value.informations = ['ser_02']
        self.clinv._unassigned_services()
        self.assertEqual(
            printMock.assert_called_with(
                [self.clinv.inv['services']['ser_01']]
            ),
            None,
        )

    @patch('clinv.clinv.Clinv._print_resources')
    def test_unassigned_services_does_not_fail_on_empty_project_services(
        self,
        printMock,
    ):
        self.project.return_value.services = None
        self.clinv._unassigned_services()
        self.assertEqual(
            printMock.assert_called_with(
                [self.clinv.inv['services']['ser_01']]
            ),
            None,
        )

    @patch('clinv.clinv.Clinv._print_resources')
    def test_unassigned_informations_prints_instances(self, printMock):
        self.project.return_value.informations = ['inf_02']
        self.clinv._unassigned_informations()
        self.assertEqual(
            printMock.assert_called_with(
                [self.clinv.inv['informations']['inf_01']]
            ),
            None,
        )

    @patch('clinv.clinv.Clinv._print_resources')
    def test_unassigned_informations_does_not_fail_on_empty_project(
        self,
        printMock,
    ):
        self.project.return_value.informations = None
        self.clinv._unassigned_informations()
        self.assertEqual(
            printMock.assert_called_with(
                [self.clinv.inv['informations']['inf_01']]
            ),
            None,
        )

    @patch('clinv.clinv.Clinv._unassigned_ec2')
    def test_general_unassigned_can_use_ec2_resource(self, unassignMock):
        self.clinv.unassigned('ec2')
        self.assertTrue(unassignMock.called)

    @patch('clinv.clinv.Clinv._unassigned_services')
    def test_general_unassigned_can_use_service_resource(self, unassignMock):
        self.clinv.unassigned('services')
        self.assertTrue(unassignMock.called)

    @patch('clinv.clinv.Clinv._unassigned_informations')
    def test_general_unassigned_can_use_informations_resource(
        self,
        unassignMock,
    ):
        self.clinv.unassigned('informations')
        self.assertTrue(unassignMock.called)

    @patch('clinv.clinv.Clinv._print_resources')
    def test_list_informations_prints_instances(self, printMock):
        self.clinv._list_informations()
        self.assertEqual(
            printMock.assert_called_with(
                [self.clinv.inv['informations']['inf_01']]
            ),
            None,
        )

    @patch('clinv.clinv.Clinv._print_resources')
    def test_list_services_prints_instances(self, printMock):
        self.clinv._list_services()
        self.assertEqual(
            printMock.assert_called_with(
                [self.clinv.inv['services']['ser_01']]
            ),
            None,
        )

    @patch('clinv.clinv.Clinv._print_resources')
    def test_list_projects_prints_instances(self, printMock):
        self.clinv._list_projects()
        self.assertEqual(
            printMock.assert_called_with(
                [self.clinv.inv['projects']['pro_01']]
            ),
            None,
        )

    def test_list_ec2_prints_instances(self):
        self.clinv._list_ec2()
        print_calls = (
            call('i-023desldk394995ss: inst_name'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))

    @patch('clinv.clinv.Clinv._list_ec2')
    def test_general_list_can_use_ec2_resource(self, unassignMock):
        self.clinv.list('ec2')
        self.assertTrue(unassignMock.called)

    @patch('clinv.clinv.Clinv._list_services')
    def test_general_list_can_use_service_resource(self, unassignMock):
        self.clinv.list('services')
        self.assertTrue(unassignMock.called)

    @patch('clinv.clinv.Clinv._list_informations')
    def test_general_list_can_use_informations_resource(self, unassignMock):
        self.clinv.list('informations')
        self.assertTrue(unassignMock.called)

    @patch('clinv.clinv.Clinv._list_projects')
    def test_general_list_can_use_projects_resource(self, unassignMock):
        self.clinv.list('projects')
        self.assertTrue(unassignMock.called)

    @patch('clinv.clinv.pyexcel')
    def test_export_generates_ods(self, pyexcelMock):
        self.clinv.raw_data = {
            'projects': {
                'pro_01': {
                    'name': 'Project 1',
                    'services': ['ser_01']
                },
                'pro_02': {'name': 'Project 2'},
            },
            'services': {
                'ser_01': {
                    'name': 'Service 1',
                    'responsible': 'Person 1',
                    'aws': {
                        'ec2': ['i-023desldk394995ss']
                    },
                },
            },
        }
        ec2_exported_data = [
            [
                'ID',
                'Name',
                'Services',
                'To destroy',
                'Responsible',
                'Comments',
            ],
            [
                'i-023desldk394995ss',
                'inst_name',
                'Service 1',
                False,
                'Person 1',
                'Test instance',
             ]
        ]
        expected_book = OrderedDict()
        expected_book.update({'EC2 Instances': ec2_exported_data})

        self.ec2instance.return_value.name = 'inst_name'
        self.ec2instance.return_value.id = 'i-023desldk394995ss'
        self.ec2instance.return_value._get_field.return_value = False
        self.ec2instance.return_value.description = 'Test instance'

        self.clinv.export('file.ods')
        self.assertEqual(
            pyexcelMock.save_book_as.assert_called_with(
                bookdict=expected_book,
                dest_file_name='file.ods',
            ),
            None,
        )

    def test_get_regions(self):
        self.boto.client.return_value.describe_regions.return_value = {
            'Regions': [
                {
                    'RegionName': 'us-east-1'
                },
                {
                    'RegionName': 'eu-west-1'
                },
            ]
        }
        self.assertEqual(self.clinv.regions, ['us-east-1', 'eu-west-1'])
