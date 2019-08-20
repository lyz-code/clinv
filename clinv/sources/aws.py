"""
Module to store the AWS sources used by Clinv.

Classes:
    Route53src: Class to gather and manipulate the AWS Route53 resources.
"""

import boto3
import logging
import re


class Route53src():
    """
    Class to gather and manipulate the AWS Route53 resources.

    Parameters:
        user_data (dict): Route53src compatible user_data dictionary

    Public methods:
        generate_source_data: Return the source data dictionary.
        generate_user_data: Return the user data dictionary.
        generate_inventory: Build the inventory dictionary with the source
            and user data.

    Internal methods:
        _fetch_source_data: Aggregate the source data dictionary.
        _fetch_user_data: Aggregate the user data dictionary.
    """

    def __init__(self, user_data={}):
        self.user_data = user_data
        self.log = logging.getLogger('main')
        self._fetch_source_data()

    def _fetch_source_data(self):
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
            Nothing
        """

        self.log.info('Fetching Route53 inventory')
        route53 = boto3.client('route53')

        self.source_data = {}

        # Fetch the hosted zones
        self.source_data['hosted_zones'] = \
            route53.list_hosted_zones()['HostedZones']

        prune_keys = ['CallerReference']

        for resource in self.source_data['hosted_zones']:
            for prune_key in prune_keys:
                try:
                    resource.pop(prune_key)
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

    def generate_source_data(self):
        """
        Return the source data dictionary

        Returns:
            dict: Source information.
        """

        return self.source_data

    def _fetch_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        Returns:
            Nothing
        """

        self.user_data = {}

        for zone in self.source_data['hosted_zones']:
            for resource in zone['records']:
                resource_id = '{}-{}-{}'.format(
                    re.sub(r'/hostedzone/', '', zone['Id']),
                    re.sub(r'\.$', '', resource['Name']),
                    resource['Type'].lower(),
                )

                # Define the default user_data of the resource
                try:
                    self.user_data[resource_id]
                except KeyError:
                    self.user_data[resource_id] = {
                        'description': 'tbd',
                        'to_destroy': 'tbd',
                    }

    def generate_user_data(self):
        """
        Return the user data dictionary

        Returns:
            dict: User information.
        """

        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with Route53 resources.

        Returns:
            dict: Route53 inventory with user and source data
        """

        inventory = {}

        for zone in self.source_data['hosted_zones']:
            for resource in zone['records']:
                resource_id = '{}-{}-{}'.format(
                    re.sub(r'/hostedzone/', '', zone['Id']),
                    re.sub(r'\.$', '', resource['Name']),
                    resource['Type'].lower(),
                )

                # Define the default user_data of the resource
                try:
                    self.user_data[resource_id]
                except KeyError:
                    self.user_data[resource_id] = {
                        'description': 'tbd',
                        'to_destroy': 'tbd',
                    }

                # Load the user_data into the source_data resource
                for key, value in self.user_data[resource_id].items():
                    resource[key] = value

                resource['hosted_zone'] = {
                    'id': zone['Id'],
                    'name': zone['Name'],
                    'private': zone['Config']['PrivateZone'],
                }
                resource['state'] = 'active'

                inventory[resource_id] = resource
        return inventory
