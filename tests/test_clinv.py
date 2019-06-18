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

        self.clinv = Clinv(self.inventory_dir)
        self.clinv.raw_inv = {
            'ec2': [
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
                                        'PublicDnsName': 'ec2.aws.com',
                                        'PublicIp': '32.312.444.22'
                                    },
                                    'Attachment': {
                                        'AttachTime': datetime.datetime(
                                            2018, 5, 10, 2, 58, 3,
                                            tzinfo=tzutc()
                                        ),
                                        'AttachmentId': 'eni-032346',
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
                                    'PrivateDnsName': 'ipec2.internal',
                                    'PrivateIpAddress': '142.33.2.113',
                                    'PrivateIpAddresses': [
                                        {
                                            'Association': {
                                                'IpOwnerId': '584460090',
                                                'PublicDnsName': 'ec2.com',
                                                'PublicIp': '32.312.444.22'
                                            },
                                            'Primary': True,
                                            'PrivateDnsName': 'ecernal',
                                            'PrivateIpAddress':
                                                '142.33.2.113',
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
                            'Tags': [
                                {'Key': 'Name', 'Value': 'inst_name'}
                            ],
                            'VirtualizationType': 'hvm',
                            'VpcId': 'vpc-31084921'
                        }
                    ],
                    'OwnerId': '585394460090',
                    'ReservationId': 'r-039ed99cad2bb3da5',
                    'assigned_service': False,
                    'exposed_services': [],
                }
            ],
        }
        self.raw_inv_path = os.path.join(
            self.inventory_dir,
            'raw_inventory.yaml',
        )
        self.ec2_instance = \
            self.clinv.raw_inv['ec2'][0]['Instances'][0]

    def tearDown(self):
        self.boto_patch.stop()
        self.logging_patch.stop()
        self.print_patch.stop()
        shutil.rmtree(self.tmp)

    def test_aws_resources_ec2_populated_by_boto(self):
        self.clinv.raw_inv = {'ec2': []}
        expected_boto_response = {
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
        expected_ec2_aws_resources = [
            dict(expected_boto_response['Reservations'][0]),
        ]
        expected_ec2_aws_resources[0]['assigned_service'] = False
        expected_ec2_aws_resources[0]['exposed_services'] = []
        self.boto.client.return_value.describe_instances.return_value = \
            expected_boto_response

        self.clinv._fetch_ec2()
        self.assertEqual(
            self.clinv.raw_inv['ec2'],
            expected_ec2_aws_resources,
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
    def test_inventory_saving(self, saveMock):
        self.clinv.save_inventory()
        self.assertEqual(
            saveMock.assert_called_with(self.raw_inv_path, self.clinv.raw_inv),
            None,
        )

    @patch('clinv.clinv.Clinv._load_yaml')
    def test_inventory_loading(self, loadMock):
        self.clinv.load_inventory()
        self.assertEqual(
            loadMock.assert_called_with(self.raw_inv_path),
            None,
        )

    def test_search_ec2_by_name(self):
        instance = self.clinv._search_ec2('inst_name')
        self.assertEqual(
            instance,
            self.ec2_instance
        )

    def test_search_ec2_by_id(self):
        instance = self.clinv._search_ec2('i-023desldk394995ss')
        self.assertEqual(
            instance,
            self.ec2_instance
        )

    def test_search_ec2_by_public_ip(self):
        instance = self.clinv._search_ec2('32.312.444.22')
        self.assertEqual(
            instance,
            self.ec2_instance
        )

    def test_search_ec2_by_private_ip(self):
        instance = self.clinv._search_ec2('142.33.2.113')
        self.assertEqual(
            instance,
            self.ec2_instance
        )

    def test_search_ec2_by_security_group(self):
        instance = self.clinv._search_ec2('sg-f2234gf6')
        self.assertEqual(
            instance,
            self.ec2_instance
        )

    def test_get_ec2_instance_name(self):
        self.assertEqual(
            self.clinv._get_ec2_instance_name(self.ec2_instance),
            'inst_name'
        )

    def test_get_ec2_security_groups(self):
        self.assertEqual(
            self.clinv._get_ec2_security_groups(self.ec2_instance),
            ['sg-f2234gf6', 'sg-cwfccs17']
        )

    def test_get_ec2_private_ip(self):
        self.assertEqual(
            self.clinv._get_ec2_private_ip(self.ec2_instance),
            ['142.33.2.113']
        )

    def test_get_multiple_ec2_private_ip(self):
        instance = self.ec2_instance
        instance['NetworkInterfaces'][0]['PrivateIpAddresses'].append(
            {
                'PrivateIpAddress':  '142.33.2.114',
            }

        )
        self.assertEqual(
            self.clinv._get_ec2_private_ip(self.ec2_instance),
            ['142.33.2.113', '142.33.2.114']
        )

    def test_get_ec2_public_ip(self):
        self.assertEqual(
            self.clinv._get_ec2_public_ip(self.ec2_instance),
            ['32.312.444.22']
        )

    def test_get_multiple_ec2_public_ip(self):
        instance = self.ec2_instance
        instance['NetworkInterfaces'][0]['PrivateIpAddresses'].append(
            {
                'Association': {
                    'PublicIp': '32.312.444.23'

                }
            }

        )
        self.assertEqual(
            self.clinv._get_ec2_public_ip(self.ec2_instance),
            ['32.312.444.22', '32.312.444.23']
        )

    def test_get_ec2_state(self):
        self.assertEqual(
            self.clinv._get_ec2_state(self.ec2_instance),
            'running'
        )

    @patch('clinv.clinv.Clinv._search_ec2')
    def test_print_ec2_instance_information(self, searchMock):
        searchMock.return_value = self.ec2_instance
        self.clinv.print_ec2('inst_name')
        self.assertEqual(
            searchMock.assert_called_with('inst_name'),
            None,
        )
        print_calls = (
            call('Type: EC2 instance'),
            call('Name: inst_name'),
            call('ID: i-023desldk394995ss'),
            call('State: running'),
            call('SecurityGroups: sg-f2234gf6, sg-cwfccs17'),
            call("PrivateIP: ['142.33.2.113']"),
            call("PublicIP: ['32.312.444.22']"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(7, len(self.print.mock_calls))

    @patch('clinv.clinv.Clinv._search_ec2')
    def test_print_nothing_found(self, searchMock):
        searchMock.return_value = None
        self.clinv.print_ec2('inst_name')
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
