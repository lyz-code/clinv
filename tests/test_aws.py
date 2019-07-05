from clinv.aws import EC2Instance
from dateutil.tz import tzutc
from unittest.mock import patch, call
import datetime
import unittest


class TestEC2Instance(unittest.TestCase):
    def setUp(self):
        self.print_patch = patch('clinv.aws.print', autospect=True)
        self.print = self.print_patch.start()

        self.raw_instance = {
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
            'StateTransitionReason': 'reason',
            'SubnetId': 'subnet-sfsdwf12',
            'Tags': [
                {'Key': 'Name', 'Value': 'inst_name'}
            ],
            'VirtualizationType': 'hvm',
            'VpcId': 'vpc-31084921',
            'description': 'This is in the description of the instance',
        }
        self.ec2 = EC2Instance(self.raw_instance)

    def tearDown(self):
        self.print_patch.stop()

    def test_get_instance_name(self):
        self.assertEqual(self.ec2.name, 'inst_name')

    def test_get_instance_name_return_null_if_empty(self):
        self.raw_instance.pop('Tags', None)
        self.assertEqual(self.ec2.name, 'none')

    def test_get_security_groups(self):
        self.assertEqual(
            self.ec2.security_groups,
            ['sg-f2234gf6', 'sg-cwfccs17']
        )

    def test_get_private_ip(self):
        self.assertEqual(self.ec2.private_ips, ['142.33.2.113'])

    def test_get_multiple_private_ips(self):
        self.ec2.instance['NetworkInterfaces'][0]['PrivateIpAddresses'].append(
            {
                'PrivateIpAddress':  '142.33.2.114',
            }

        )
        self.assertEqual(
            self.ec2.private_ips,
            ['142.33.2.113', '142.33.2.114']
        )

    def test_get_public_ip(self):
        self.assertEqual(self.ec2.public_ips, ['32.312.444.22'])

    def test_get_multiple_public_ips(self):
        self.ec2.instance['NetworkInterfaces'][0]['PrivateIpAddresses'].append(
            {
                'Association': {
                    'PublicIp': '32.312.444.23'

                }
            }

        )
        self.assertEqual(
            self.ec2.public_ips,
            ['32.312.444.22', '32.312.444.23']
        )

    def test_get_state(self):
        self.assertEqual(self.ec2.state, 'running')

    def test_get_type(self):
        self.assertEqual(self.ec2.type, 'c4.4xlarge')

    def test_get_state_transition_reason(self):
        self.assertEqual(self.ec2.state_transition, 'reason')

    def test_get_description(self):
        self.assertEqual(
            self.ec2.description,
            'This is in the description of the instance',
        )

    def test_print_ec2_instance_information(self):
        self.ec2.print()
        print_calls = (
            call('- Name: inst_name'),
            call('  ID: i-023desldk394995ss'),
            call('  State: running'),
            call('  Type: c4.4xlarge'),
            call("  SecurityGroups: ['sg-f2234gf6', 'sg-cwfccs17']"),
            call("  PrivateIP: ['142.33.2.113']"),
            call("  PublicIP: ['32.312.444.22']"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(7, len(self.print.mock_calls))

    def test_print_ec2_reason_if_stopped(self):
        self.raw_instance['State']['Name'] = 'stopped'
        self.ec2.print()
        print_calls = (
            call('- Name: inst_name'),
            call('  ID: i-023desldk394995ss'),
            call('  State: stopped'),
            call('  State Reason: reason'),
            call('  Type: c4.4xlarge'),
            call("  SecurityGroups: ['sg-f2234gf6', 'sg-cwfccs17']"),
            call("  PrivateIP: ['142.33.2.113']"),
            call("  PublicIP: ['32.312.444.22']"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(8, len(self.print.mock_calls))

    def test_search_ec2_by_name(self):
        self.assertTrue(self.ec2.search('inst_name'))

    def test_search_ec2_by_regexp_on_name(self):
        self.assertTrue(self.ec2.search('.*name'))

    def test_search_ec2_by_id(self):
        self.assertTrue(self.ec2.search('i-023desldk394995ss'))

    def test_search_ec2_by_public_ip(self):
        self.assertTrue(self.ec2.search('32.312.444.22'))

    def test_search_ec2_by_private_ip(self):
        self.assertTrue(self.ec2.search('142.33.2.113'))

    def test_search_ec2_by_security_group(self):
        self.assertTrue(self.ec2.search('sg-f2234gf6'))

    def test_search_ec2_by_description(self):
        self.assertTrue(self.ec2.search('.*in the description.*'))
