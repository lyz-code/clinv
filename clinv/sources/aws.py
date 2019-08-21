"""
Module to store the AWS sources used by Clinv.

Classes:
    Route53src: Class to gather and manipulate the AWS Route53 resources.
"""

from clinv.resources import Route53
import boto3
import logging
import re


class AWSsrc():
    """
    Abstract class to gather common method and attributes for all AWS
    sources.

    Public methods:
        None.

    Public properties:
        id: source ID.
    """


class Route53src():
    """
    Class to gather and manipulate the AWS Route53 resources.

    Parameters:
        source_data (dict): Route53src compatible source_data dictionary
        user_data (dict): Route53src compatible user_data dictionary

    Public methods:
        generate_source_data: Return the source data dictionary.
        generate_user_data: Return the user data dictionary.
        generate_inventory: Build the inventory dictionary with the source
            and user data.

    Public attributes:
        source_data (dict): Aggregated source data of the different sources.
        user_data (dict): Aggregated user data of the different sources.
    """

    def __init__(self, source_data={}, user_data={}):
        self.id = 'route53'
        self.source_data = source_data
        self.user_data = user_data
        self.log = logging.getLogger('main')

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
        route53 = boto3.client('route53')

        self.source_data = {}

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
