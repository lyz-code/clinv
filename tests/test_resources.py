from clinv.resources import EC2, RDS, Route53, Project, Service, Information
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

    def test_get_field_returns_list_when_asked_even_if_value_is_str(self):
        self.resource.raw['key'] = 'value'
        self.assertEqual(
            self.resource._get_field('key', 'list'),
            ['value']
        )

    def test_get_optional_field_returns_list_when_asked_even_if_value_is_str(
        self
    ):
        self.resource.raw['key'] = 'value'
        self.assertEqual(
            self.resource._get_optional_field('key', 'list'),
            ['value']
        )

    def test_get_field_returns_str_when_asked_even_if_value_is_list(self):
        self.resource.raw['key'] = ['value1', 'value2']
        self.assertEqual(
            self.resource._get_field('key', 'str'),
            'value1, value2'
        )

    def test_get_optional_field_returns_str_when_asked_even_if_value_is_list(
        self
    ):
        self.resource.raw['key'] = ['value1', 'value2']
        self.assertEqual(
            self.resource._get_optional_field('key', 'str'),
            'value1, value2'
        )

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

    def test_name_property_works_as_expected(self):
        self.assertEqual(self.resource.name, 'resource_name')

    def test_search_resource_by_regexp_on_name(self):
        self.assertTrue(self.resource.search('.*name'))

    def test_search_resource_by_id(self):
        self.assertTrue(self.resource.search(self.id))

    def test_search_resource_by_description(self):
        self.assertTrue(self.resource.search('.*the description.*'))

    def test_get_resource_state(self):
        self.assertEqual(self.resource.state, 'active')

    def test_short_print_resource_information(self):
        self.resource.short_print()
        print_calls = (
            call('{}: {}'.format(self.resource.id, self.resource.name)),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(1, len(self.print.mock_calls))

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call(self.resource.id),
            call('  Name: {}'.format(self.resource.name)),
            call('  State: {}'.format(self.resource.state)),
            call('  Description: {}'.format(self.resource.description)),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(4, len(self.print.mock_calls))


class ClinvActiveResourceTests(ClinvGenericResourceTests):
    '''Must be combined with a unittest.TestCase that defines:
        * self.resource as a ClinvActiveResource subclass instance
        * self.raw as a dictionary with the data of the resource
        * self.id as a string with the resource id'''

    def test_get_instance_responsible(self):
        self.assertEqual(self.resource.responsible, 'responsible@clinv.com')


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
                'responsible': 'responsible@clinv.com',
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
                'name': 'resource_name',
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
        self.assertEqual(self.resource.aliases, ['Awesome Project'])

    def test_search_by_aliases(self):
        self.assertTrue(self.resource.search('Awesome Project'))

    def test_search_by_aliases_doesn_not_work_if_alias_is_none(self):
        self.resource.raw['aliases'] = None
        self.assertFalse(self.resource.search('Awesome Project'))

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call('pro_01'),
            call('  Name: resource_name'),
            call('  Aliases: Awesome Project'),
            call('  Description: This is the description'),
            call('  State: active'),
            call('  Services: ser_01'),
            call('  Informations: inf_01'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(7, len(self.print.mock_calls))


class TestInformation(ClinvActiveResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = 'inf_01'
        self.raw = {
            'inf_01': {
                'description': 'This is the description',
                'name': 'resource_name',
                'personal_data': True,
                'responsible': 'responsible@clinv.com',
                'state': 'active',
            }
        }

        self.resource = Information(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_personal_data(self):
        self.assertEqual(self.resource.personal_data, True)

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call('inf_01'),
            call('  Name: resource_name'),
            call('  Description: This is the description'),
            call('  State: active'),
            call('  Personal Information: True'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(5, len(self.print.mock_calls))


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
                'name': 'resource_name',
                'responsible': 'responsible@clinv.com',
                'state': 'active',
            }
        }

        self.resource = Service(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_access(self):
        self.assertEqual(self.resource.access, 'public')

    def test_get_informations(self):
        self.assertEqual(self.resource.informations, ['inf_01'])

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call('ser_01'),
            call('  Name: resource_name'),
            call('  Description: This is the description'),
            call('  State: active'),
            call('  Access: public'),
            call('  Informations: inf_01'),
            call('  Related resources:'),
            call('    ec2:'),
            call('      i-01'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(9, len(self.print.mock_calls))


class ClinvAWSResourceTests(ClinvGenericResourceTests):
    '''Must be combined with a unittest.TestCase that defines:
        * self.resource as a ClinvAWSResource subclass instance
        * self.raw as a dictionary with the data of the resource
        * self.id as a string with the resource id

    And the following properties must be set:
        * resource name: resource_name
        * security groups: ['sg-f2234gf6', 'sg-cwfccs17']
        * type: 'c4.4xlarge'
        * region: 'us-east-1'
    '''

    def test_get_security_groups(self):
        self.assertEqual(
            self.resource.security_groups,
            ['sg-f2234gf6', 'sg-cwfccs17']
        )

    def test_get_type(self):
        self.assertEqual(self.resource.type, 'c4.4xlarge')

    def test_get_region(self):
        self.assertEqual(
            self.resource.region,
            'us-east-1',
        )

    def test_search_by_security_group(self):
        self.assertTrue(self.resource.search('sg-f2234gf6'))

    def test_search_by_region(self):
        self.assertTrue(self.resource.search('us-east-1'))

    def test_search_by_type(self):
        self.assertTrue(self.resource.search('c4.4xlarge'))


class TestEC2(ClinvAWSResourceTests, unittest.TestCase):
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
                'State': {'Code': 16, 'Name': 'active'},
                'StateTransitionReason': 'reason',
                'SubnetId': 'subnet-sfsdwf12',
                'Tags': [
                    {'Key': 'Name', 'Value': 'resource_name'}
                ],
                'VirtualizationType': 'hvm',
                'VpcId': 'vpc-31084921',
                'description': 'This is in the description of the instance',
                'region': 'us-east-1',
                'to_destroy': 'tbd',
                'environment': 'tbd',
            }
        }
        self.resource = EC2(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_instance_name_return_null_if_empty(self):
        self.raw['i-01'].pop('Tags', None)
        self.assertEqual(self.resource.name, 'none')

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

    def test_get_state_transition_reason(self):
        self.assertEqual(self.resource.state_transition, 'reason')

    def test_print_resource_information(self):
        self.resource.raw['State']['Name'] = 'running'

        self.resource.print()
        print_calls = (
            call('i-01'),
            call('  Name: resource_name'),
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
            call('i-01'),
            call('  Name: resource_name'),
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


class TestRDS(ClinvAWSResourceTests, unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.id = 'db-YDFL2'
        self.raw = {
            'db-YDFL2': {
                'AllocatedStorage': 100,
                'AssociatedRoles': [],
                'AutoMinorVersionUpgrade': True,
                'AvailabilityZone': 'us-east-1a',
                'BackupRetentionPeriod': 7,
                'CACertificateIdentifier': 'rds-ca-2015',
                'DBInstanceArn': 'arn:aws:rds:us-east-1:224119285:db:db',
                'DBInstanceClass': 'c4.4xlarge',
                'DBInstanceIdentifier': 'resource_name',
                'DBInstanceStatus': 'active',
                'DBSecurityGroups': ['sg-f2234gf6', 'sg-cwfccs17'],
                'DBSubnetGroup': {
                    'DBSubnetGroupDescription': 'Created from the RDS '
                    'Management Console',
                    'DBSubnetGroupName': 'default-vpc-v2dcp2jh',
                    'SubnetGroupStatus': 'Complete',
                    'Subnets': [
                        {
                            'SubnetAvailabilityZone': {
                                'Name': 'us-east-1a'
                            },
                            'SubnetIdentifier': 'subnet-42sfl222',
                            'SubnetStatus': 'Active'
                        },
                        {
                            'SubnetAvailabilityZone': {
                                'Name': 'us-east-1e'
                            },
                            'SubnetIdentifier': 'subnet-42sfl221',
                            'SubnetStatus': 'Active'
                        },
                    ],
                    'VpcId': 'vpc-v2dcp2jh'},
                'DbiResourceId': 'db-YDFL2',
                'DeletionProtection': True,
                'Endpoint': {
                    'Address': 'rds-name.us-east-1.rds.amazonaws.com',
                    'HostedZoneId': '202FGHSL2JKCFW',
                    'Port': 5521
                },
                'Engine': 'mariadb',
                'EngineVersion': '1.2',
                'InstanceCreateTime': datetime.datetime(
                    2019, 6, 17, 15, 15, 8, 461000, tzinfo=tzutc()
                ),
                'Iops': 1000,
                'LatestRestorableTime': datetime.datetime(
                    2019, 7, 8, 6, 23, 55, tzinfo=tzutc()
                ),
                'MasterUsername': 'root',
                'MultiAZ': True,
                'PreferredBackupWindow': '03:00-04:00',
                'PreferredMaintenanceWindow': 'fri:04:00-fri:05:00',
                'PubliclyAccessible': False,
                'StorageEncrypted': True,
                'description': 'This is in the description of the instance',
                'region': 'us-east-1',
                'to_destroy': 'tbd',
                'environment': 'production',
            }
        }
        self.resource = RDS(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call('db-YDFL2'),
            call('  Name: resource_name'),
            call('  Type: c4.4xlarge'),
            call('  Description: This is in the description of the instance'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(4, len(self.print.mock_calls))


class TestRoute53(ClinvGenericResourceTests, unittest.TestCase):

    def setUp(self):
        super().setUp()

        self.id = 'hosted_zone_id-record1.clinv.org-cname'
        self.raw = {
            'hosted_zone_id-record1.clinv.org-cname': {
                'Name': 'record1.clinv.org',
                'ResourceRecords': [
                    {
                        'Value': '127.0.0.1'
                    },
                    {
                        'Value': 'localhost'
                    },
                ],
                'TTL': 172800,
                'Type': 'CNAME',
                'description': 'This is the description',
                'to_destroy': 'tbd',
                'state': 'active',
                'hosted_zone': {
                    'id': '/hostedzone/hosted_zone_id',
                    'private': False,
                    'name': 'hostedzone.org',
                },
            },
        }
        self.resource = Route53(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_name_property_works_as_expected(self):
        '''
        Override the parent test, as the name == id
        '''

        self.assertEqual(self.resource.name, 'record1.clinv.org')

    def test_search_resource_by_regexp_on_name(self):
        '''
        Override the parent test, as the name == id
        '''

        self.assertTrue(self.resource.search('.*record1'))

    def test_short_print_resource_information(self):
        '''
        Override the parent test, as the name == id
        '''

        self.resource.short_print()

        self.assertEqual(
            self.print.assert_called_with(self.resource.id),
            None,
        )

    def test_value_property_works_as_expected(self):
        self.assertEqual(self.resource.value, ['127.0.0.1', 'localhost'])

    def test_value_property_supports_aliases(self):
        self.raw = {
            'record1.clinv.org': {
                'Name': 'record1.clinv.org',
                'AliasTarget': {
                    'DNSName': 'aliasdns.org',
                    'EvaluateTargetHealth': False,
                    'HostedZoneId': 'XXXXXXXXXXXXXX'
                },
                'TTL': 172800,
                'Type': 'A',
                'description': 'This is the description',
                'to_destroy': 'tbd',
                'state': 'active',
                'hosted_zone': {
                    'id': '/hostedzone/hosted_zone_id',
                    'private': False,
                    'name': 'hostedzone.org',
                },
            },
        }
        self.resource = Route53(self.raw)
        self.assertEqual(self.resource.value, ['aliasdns.org'])

    def test_type_property_works_as_expected(self):
        self.assertEqual(self.resource.type, 'CNAME')

    def test_to_destroy_property_works_as_expected(self):
        self.assertEqual(self.resource.to_destroy, 'tbd')

    def test_hosted_zone_property_works_as_expected(self):
        self.assertEqual(self.resource.hosted_zone, 'hostedzone.org')

    def test_hosted_zone_id_property_works_as_expected(self):
        self.assertEqual(
            self.resource.hosted_zone_id,
            '/hostedzone/hosted_zone_id',
        )

    def test_access_property_works_as_expected_if_public(self):
        self.assertEqual(self.resource.access, 'public')

    def test_access_property_works_as_expected_if_private(self):
        self.resource.raw['hosted_zone']['private'] = True
        self.assertEqual(self.resource.access, 'private')

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call('hosted_zone_id-record1.clinv.org-cname'),
            call('  Name: record1.clinv.org'),
            call('  Value:'),
            call('    127.0.0.1'),
            call('    localhost'),
            call('  Type: CNAME'),
            call('  Zone: /hostedzone/hosted_zone_id'),
            call('  Access: public'),
            call('  Description: This is the description'),
            call('  Destroy: tbd'),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(10, len(self.print.mock_calls))

    def test_search_resource_by_regexp_on_value(self):
        self.assertTrue(self.resource.search('.*alhost'))

    def test_search_resource_by_type(self):
        self.assertTrue(self.resource.search('CNAME'))

    def test_search_resource_by_type_insensitive(self):
        self.assertTrue(self.resource.search('cname'))
