"""
Module to store the AWS sources used by Clinv.

Classes:
    AWSBasesrc: Class to gather the common methods for the AWS sources.
    Route53src: Class to gather and manipulate the AWS Route53 resources.
    RDSsrc: Class to gather and manipulate the AWS RDS resources.
"""

from clinv.resources import Route53, RDS
from clinv.sources import ClinvSourcesrc
import boto3
import re


class AWSBasesrc(ClinvSourcesrc):
    """
    Class to gather the common methods for the AWS sources.

    Public properties:
        regions (list): List of the AWS regions.

    Public attributes:
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)

    @property
    def regions(self):
        """
        Do aggregation of the AWS regions to generate the self.regions list.

        Returns:
            list: AWS Regions.
        """
        ec2 = boto3.client('ec2')
        return [
            region['RegionName']
            for region in ec2.describe_regions()['Regions']
        ]


class RDSsrc(AWSBasesrc):
    """
    Class to gather and manipulate the AWS RDS resources.

    Parameters:
        source_data (dict): RDSsrc compatible source_data
        dictionary.
        user_data (dict): RDSsrc compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = 'rds'

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
            'us-east-1': [
                {
                    'AllocatedStorage': 100,
                    'AssociatedRoles': [],
                    'AutoMinorVersionUpgrade': True,
                    'AvailabilityZone': 'us-east-1a',
                    'BackupRetentionPeriod': 7,
                    'CACertificateIdentifier': 'rds-ca-2015',
                    'DBInstanceArn': 'arn:aws:rds:us-east-1:224119285:db:db',
                    'DBInstanceClass': 'db.t2.micro',
                    'DBInstanceIdentifier': 'rds-name',
                    'DBInstanceStatus': 'available',
                    'DBSecurityGroups': [],
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
                },
            ],
        }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info('Fetching RDS inventory')
        self.source_data = {}

        for region in self.regions:
            rds = boto3.client('rds', region_name=region)
            self.source_data[region] = \
                rds.describe_db_instances()['DBInstances']

        prune_keys = [
            'CopyTagsToSnapshot',
            'DBParameterGroups',
            'DbInstancePort',
            'DomainMemberships',
            'EnhancedMonitoringResourceArn',
            'IAMDatabaseAuthenticationEnabled',
            'LicenseModel',
            'MonitoringInterval',
            'MonitoringRoleArn',
            'OptionGroupMemberships',
            'PendingModifiedValues',
            'PerformanceInsightsEnabled',
            'PerformanceInsightsKMSKeyId',
            'PerformanceInsightsRetentionPeriod',
            'ReadReplicaDBInstanceIdentifiers',
            'StorageType',
            'VpcSecurityGroups',
        ]

        for region in self.source_data.keys():
            for resource in self.source_data[region]:
                for prune_key in prune_keys:
                    try:
                        resource.pop(prune_key)
                    except KeyError:
                        pass

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        self.user_data = {}

        for region in self.source_data.keys():
            for resource in self.source_data[region]:
                resource_id = resource['DbiResourceId']
                # Define the default user_data of the resource
                try:
                    self.user_data[resource_id]
                except KeyError:
                    self.user_data[resource_id] = {
                        'description': '',
                        'to_destroy': 'tbd',
                        'environment': 'tbd',
                        'region': region,
                    }
        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with RDS resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: RDS inventory with user and source data
        """

        inventory = {}

        for region in self.source_data.keys():
            for resource in self.source_data[region]:
                resource_id = resource['DbiResourceId']

                for key, value in \
                        self.user_data[resource_id].items():
                    resource[key] = value

                inventory[resource_id] = RDS(
                    {
                        resource_id: resource
                    }
                )

        return inventory


class Route53src(AWSBasesrc):
    """
    Class to gather and manipulate the AWS Route53 resources.

    Parameters:
        source_data (dict): Route53src compatible source_data dictionary.
        user_data (dict): Route53src compatible user_data dictionary.

    Public methods:
        generate_source_data: Generates the source_data attribute and returns
            it.
        generate_user_data: Generates the user_data attribute and returns it.
        generate_inventory: Generates the inventory dictionary with the source
            resource.

    Public attributes:
        id (str): ID of the resource.
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):
    """

    def __init__(self, source_data={}, user_data={}):
        super().__init__(source_data, user_data)
        self.id = 'route53'

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
                'hosted_zones': [
                    {
                        'Config': {
                            'Comment': 'This is the description',
                            'PrivateZone': False,
                        },
                        'Id': '/hostedzone/hosted_zone_id',
                        'Name': 'hostedzone.org',
                        'ResourceRecordSetCount': 1,
                        'records': [
                            {
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
                                'Type': 'CNAME'
                            },
                        ],
                    },
                ],
            }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info('Fetching Route53 inventory')
        self.source_data = {}

        route53 = boto3.client('route53')

        # Fetch the hosted zones
        self.source_data['hosted_zones'] = \
            route53.list_hosted_zones()['HostedZones']

        # Prune unneeded information
        prune_keys = ['CallerReference']
        for zone in self.source_data['hosted_zones']:
            for prune_key in prune_keys:
                try:
                    zone.pop(prune_key)
                except KeyError:
                    pass

        # Fetch the records
        for zone in self.source_data['hosted_zones']:
            raw_records = route53.list_resource_record_sets(
                HostedZoneId=zone['Id'],
            )

            zone['records'] = raw_records['ResourceRecordSets']

            while raw_records['IsTruncated']:
                raw_records = route53.list_resource_record_sets(
                    HostedZoneId=zone['Id'],
                    StartRecordName=raw_records['NextRecordName'],
                    StartRecordType=raw_records['NextRecordType'],
                )
                for record in raw_records['ResourceRecordSets']:
                    zone['records'].append(record)

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        self.user_data = {}

        for zone in self.source_data['hosted_zones']:
            for record in zone['records']:
                record_id = '{}-{}-{}'.format(
                    re.sub(r'/hostedzone/', '', zone['Id']),
                    re.sub(r'\.$', '', record['Name']),
                    record['Type'].lower(),
                )

                # Define the default user_data of the record
                try:
                    self.user_data[record_id]
                except KeyError:
                    self.user_data[record_id] = {
                        'description': 'tbd',
                        'to_destroy': 'tbd',
                        'state': 'active',
                    }
        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with Route53 resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: Route53 inventory with user and source data
        """

        inventory = {}

        for zone in self.source_data['hosted_zones']:
            for record in zone['records']:
                record_id = '{}-{}-{}'.format(
                    re.sub(r'/hostedzone/', '', zone['Id']),
                    re.sub(r'\.$', '', record['Name']),
                    record['Type'].lower(),
                )

                # Load the user_data into the source_data record
                for key, value in self.user_data[record_id].items():
                    record[key] = value

                # Add clinv needed information
                record['hosted_zone'] = {
                    'id': zone['Id'],
                    'name': zone['Name'],
                    'private': zone['Config']['PrivateZone'],
                }

                inventory[record_id] = Route53({record_id: record})
        return inventory
