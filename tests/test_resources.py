from clinv.resources import EC2, Project, Service, Information
from dateutil.tz import tzutc
from unittest.mock import patch, call
import datetime
import unittest


class ClinvGenericResourceTests(object):

    '''Must be combined with a unittest.TestCase that defines:
        * self.resource as a ClinvGenericResource subclass instance
        * self.raw as a dictionary with the data of the resource
        * self.id as a string with the resource id'''

    def setUp(self):
        self.print_patch = patch('clinv.resources.print', autospect=True)
        self.print = self.print_patch.start()

    def tearDown(self):
        self.print_patch.stop()

    def test_raw_attribute_is_created(self):
        self.assertEqual(self.resource.raw, self.raw[self.id])

    def test_get_field_returns_expected_value(self):
        self.assertEqual(
            self.resource._get_field('description'),
            self.raw[self.id]['description']
        )

    def test_get_field_returns_missing_key(self):
        with self.assertRaisesRegex(
            KeyError,
            "{} doesn't have the unexistent key defined".format(self.id),
        ):
            self.resource._get_field('unexistent')

    def test_get_field_raises_error_if_key_is_None(self):
        self.resource.raw['key_is_none'] = None
        with self.assertRaisesRegex(
            ValueError,
            "{} key_is_none key is set to None, ".format(self.id) +
            "please assign it a defined value",
        ):
            self.resource._get_field('key_is_none')

    def test_get_optional_field_returns_expected_value(self):
        self.assertEqual(
            self.resource._get_optional_field('description'),
            self.raw[self.id]['description']
        )

    def test_get_optional_field_returns_none_on_missing_key(self):
        self.assertEqual(self.resource._get_optional_field('unexistent'), None)

    def test_id_property_works_as_expected(self):
        self.assertEqual(self.resource.id, self.id)

    def test_description_property_works_as_expected(self):
        self.assertEqual(
            self.resource.description,
            self.raw[self.id]['description']
        )

    def test_search_resource_by_regexp_on_name(self):
        self.assertTrue(self.resource.search('.*name'))

    def test_search_resource_by_id(self):
        self.assertTrue(self.resource.search(self.id))

    def test_search_resource_by_description(self):
        self.assertTrue(self.resource.search('.*the description.*'))


class ClinvActiveResourceTests(ClinvGenericResourceTests):

    '''Must be combined with a unittest.TestCase that defines:
        * self.resource as a ClinvActiveResource subclass instance
        * self.raw as a dictionary with the data of the resource
        * self.id as a string with the resource id'''

    def test_name_property_works_as_expected(self):
        self.assertEqual(self.resource.name, self.raw[self.id]['name'])

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call('{}: {}'.format(self.resource.id, self.resource.name)),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))

    def test_get_resource_state(self):
        self.assertEqual(self.resource.state, 'active')


class TestProject(ClinvActiveResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = 'pro_01'
        self.raw = {
            'pro_01': {
                'aliases': 'Awesome Project',
                'description': 'This is the description',
                'informations': [
                    'inf_01',
                ],
                'links': {
                    'homepage': 'www.homepage.com'
                },
                'members': {
                    'developers': [
                        'developer_1',
                    ],
                    'devops': [
                        'devops_1'
                    ],
                    'po': 'product owner',
                    'stakeholders': [
                        'stakeholder_1'
                    ],
                    'ux': None,
                    'qa': None,
                },
                'name': 'This is the name',
                'services': [
                    'ser_01'
                ],
                'state': 'active',
            }
        }

        self.resource = Project(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_services(self):
        self.assertEqual(self.resource.services, ['ser_01'])

    def test_get_informations(self):
        self.assertEqual(self.resource.informations, ['inf_01'])

    def test_get_aliases(self):
        self.assertEqual(self.resource.aliases, 'Awesome Project')

    def test_search_by_aliases(self):
        self.assertTrue(self.resource.search('Awesome Project'))

    def test_search_by_aliases_doesn_not_work_if_alias_is_none(self):
        self.resource.raw['aliases'] = None
        self.assertFalse(self.resource.search('Awesome Project'))


class TestInformation(ClinvActiveResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = 'inf_01'
        self.raw = {
            'inf_01': {
                'description': 'This is the description',
                'name': 'This is the name',
                'personal_data': True,
                'responsible': 'responsible@clinv.com',
                'state': 'active',
            }
        }

        self.resource = Information(self.raw)

    def tearDown(self):
        super().tearDown()


class TestService(ClinvActiveResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = 'ser_01'
        self.raw = {
            'ser_01': {
                'access': 'public',
                'authentication': {
                    '2fa': True,
                    'method': 'Oauth2'
                },
                'aws': {
                    'ec2': {
                        'i-01'
                    },
                },
                'description': 'This is the description',
                'endpoints': [
                    'https://endpoint1.com'
                ],
                'informations': [
                    'inf_01',
                ],
                'links': {
                    'docs': {
                        'internal': 'https://internaldocs',
                        'external': 'https://internaldocs',
                    },
                },
                'name': 'This is the name',
                'responsible': 'responsible@clinv.com',
                'state': 'active',
            }
        }

        self.resource = Service(self.raw)

    def tearDown(self):
        super().tearDown()


class TestEC2(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = 'i-01'
        self.raw = {
            'i-01': {
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
                'InstanceId': 'i-01',
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
                'region': 'us-east-1',
            }
        }
        self.resource = EC2(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_instance_name(self):
        self.assertEqual(self.resource.name, 'inst_name')

    def test_get_instance_name_return_null_if_empty(self):
        self.raw['i-01'].pop('Tags', None)
        self.assertEqual(self.resource.name, 'none')

    def test_get_security_groups(self):
        self.assertEqual(
            self.resource.security_groups,
            ['sg-f2234gf6', 'sg-cwfccs17']
        )

    def test_get_private_ip(self):
        self.assertEqual(self.resource.private_ips, ['142.33.2.113'])

    def test_get_multiple_private_ips(self):
        self.resource.raw['NetworkInterfaces'][0]['PrivateIpAddresses'].append(
            {
                'PrivateIpAddress':  '142.33.2.114',
            }

        )
        self.assertEqual(
            self.resource.private_ips,
            ['142.33.2.113', '142.33.2.114']
        )

    def test_get_public_ip(self):
        self.assertEqual(self.resource.public_ips, ['32.312.444.22'])

    def test_get_multiple_public_ips(self):
        self.resource.raw['NetworkInterfaces'][0]['PrivateIpAddresses'].append(
            {
                'Association': {
                    'PublicIp': '32.312.444.23'

                }
            }

        )
        self.assertEqual(
            self.resource.public_ips,
            ['32.312.444.22', '32.312.444.23']
        )

    def test_get_state(self):
        self.assertEqual(self.resource.state, 'running')

    def test_get_type(self):
        self.assertEqual(self.resource.type, 'c4.4xlarge')

    def test_get_state_transition_reason(self):
        self.assertEqual(self.resource.state_transition, 'reason')

    def test_get_region(self):
        self.assertEqual(
            self.resource.region,
            'us-east-1',
        )

    def test_print_ec2_instance_information(self):
        self.resource.print()
        print_calls = (
            call('- Name: inst_name'),
            call('  ID: i-01'),
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
        self.raw['i-01']['State']['Name'] = 'stopped'
        self.resource.print()
        print_calls = (
            call('- Name: inst_name'),
            call('  ID: i-01'),
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

    def test_search_ec2_by_public_ip(self):
        self.assertTrue(self.resource.search('32.312.444.22'))

    def test_search_ec2_by_private_ip(self):
        self.assertTrue(self.resource.search('142.33.2.113'))

    def test_search_ec2_by_security_group(self):
        self.assertTrue(self.resource.search('sg-f2234gf6'))

    def test_search_ec2_by_region(self):
        self.assertTrue(self.resource.search('us-east-1'))
