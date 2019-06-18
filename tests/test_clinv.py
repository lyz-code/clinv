from clinv.clinv import Clinv
from dateutil.tz import tzutc
from unittest.mock import patch, call
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
            'clinv.clinv.EC2Instance', autospect=True
        )
        self.ec2instance = self.ec2instance_patch.start()

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
            'ec2': self.boto_describe_instances['Reservations']
        }
        self.clinv.raw_data = {
            'ec2': {
                'i-023desldk394995ss': {
                    'description': '',
                    'to_destroy': False,
                }
            }
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
            }
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
        shutil.rmtree(self.tmp)

    def test_aws_resources_ec2_populated_by_boto(self):
        expected_ec2_aws_resources = [
            dict(self.boto_describe_instances['Reservations'][0]),
        ]
        self.boto.client.return_value.describe_instances.return_value = \
            self.boto_describe_instances

        self.clinv._update_raw_inventory()
        self.assertEqual(
            self.clinv.raw_inv['ec2'],
            expected_ec2_aws_resources,
        )

    def test_short_ec2_inventory_created(self):
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
            'StateTransitionReason',
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

        self.clinv._update_raw_inventory()

        for prune_key in prune_keys:
            self.assertTrue(
                prune_key not in
                self.clinv.raw_inv['ec2'][0]['Instances'][0].keys(),
            )
        for prune_key in network_prune_keys:
            self.assertTrue(
                prune_key not in
                self.clinv.raw_inv['ec2'][0]['Instances'][0][
                    'NetworkInterfaces'
                ][0].keys(),
            )

    def test_update_inventory_adds_raw_data(self):
        self.ec2instance.return_value.id = 'i-023desldk394995ss'
        self.clinv._update_inventory()

        desired_input = self.clinv.raw_inv['ec2'][0]['Instances'][0]
        desired_input['description'] = ''
        desired_input['to_destroy'] = False
        self.assertEqual(
            self.ec2instance.assert_called_with(
                self.clinv.raw_inv['ec2'][0]['Instances'][0]
            ),
            None,
        )
        self.assertEqual(
            self.clinv.inv['ec2']['i-023desldk394995ss'],
            self.ec2instance()
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
    def test_data_loading_loads_raw_data(self, loadMock):
        self.clinv.load_data()
        self.assertTrue(call(self.raw_data_path) in loadMock.mock_calls)
        self.assertEqual(self.clinv.raw_data, loadMock())

    def test_search_ec2_by_name(self):
        instances = self.clinv._search_ec2('inst_name')
        self.assertEqual(
            instances,
            [self.ec2instance()]
        )

    def test_search_ec2_by_id(self):
        instances = self.clinv._search_ec2('i-023desldk394995ss')
        self.assertEqual(
            instances,
            [self.ec2instance()]
        )

    def test_search_ec2_by_public_ip(self):
        instances = self.clinv._search_ec2('32.312.444.22')
        self.assertEqual(
            instances,
            [self.ec2instance()]
        )

    def test_search_ec2_by_private_ip(self):
        instances = self.clinv._search_ec2('142.33.2.113')
        self.assertEqual(
            instances,
            [self.ec2instance()]
        )

    def test_search_ec2_by_security_group(self):
        instances = self.clinv._search_ec2('sg-f2234gf6')
        self.assertEqual(
            instances,
            [self.ec2instance()]
        )

    @patch('clinv.clinv.Clinv._search_ec2')
    def test_print_ec2_instance_information(self, searchMock):
        searchMock.return_value = [self.ec2instance()]
        self.clinv.print_search('inst_name')
        self.assertEqual(
            searchMock.assert_called_with('inst_name'),
            None,
        )
        print_calls = (
            call('Type: EC2 instances'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))
        self.assertTrue(self.ec2instance.return_value.print.called)

    @patch('clinv.clinv.Clinv._search_ec2')
    def test_print_nothing_found(self, searchMock):
        searchMock.return_value = []
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

    def test_unassigned_ec2_prints_instances(self):
        self.clinv.raw_data = {
            'services': {
                'ser-01': {
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

    def test_unassigned_services_prints_instances(self):
        self.clinv.raw_data = {
            'projects': {
                'pro-01': {
                    'services': ['ser-01'],
                },
            },
            'services': {
                'ser-02': {'name': 'Service 2'},
                },
        }
        self.clinv._unassigned_services()
        print_calls = (
            call('ser-02: Service 2'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))

    def test_unassigned_informations_prints_instances(self):
        self.clinv.raw_data = {
            'projects': {
                'pro-01': {
                    'informations': ['inf-01'],
                },
            },
            'informations': {
                'inf-02': {'name': 'Information 2'},
                },
        }
        self.clinv._unassigned_informations()
        print_calls = (
            call('inf-02: Information 2'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))

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
