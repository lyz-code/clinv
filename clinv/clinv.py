#!/usr/bin/python3

# Copyright (C) 2019 lyz <lyz@riseup.net>
# This file is part of clinv.
#
# clinv is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# clinv is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with clinv.  If not, see <http://www.gnu.org/licenses/>.

# Program to maintain an inventory of assets.

# from clinv.sources.aws import Route53src

"""
Module to store the Clinv main classes

Classes:
    Inventory: Class to gather and manipulate the inventory data.
"""

from clinv.resources import EC2, RDS, Project, Service, Information
from clinv.sources.aws import Route53src
from collections import OrderedDict
from operator import itemgetter
from yaml import YAMLError
import boto3
import logging
import os
import pyexcel
import yaml

active_source_plugins = [
    Route53src,
]


class Inventory():
    """
    Class to gather and manipulate the inventory data.

    Parameters:
        inventory_dir (str): Path to the directory where the source_data.yml
            and user_data.yml are located.
        source_plugins (list): List of source plugins objects, for example:
            [EC2src, RDSsrc, Route53src]

    Public methods:
        load_source_data_from_file: Load the source data from the
            source_data.yaml file.
        save: Saves source and user data into the yaml files.
        generate_source_data: Build the source data dictionary from the
            sources.

    Internal methods:
        _load_yaml: Load a variable from a yaml file.
        _save_yaml: Save a variable to a yaml file.
        _load_plugins: Initializes the source plugins.
    """

    def __init__(self, inventory_dir, source_plugins=active_source_plugins):
        self.log = logging.getLogger('main')
        self.inventory_dir = inventory_dir
        self._source_plugins = source_plugins
        self.source_data_path = os.path.join(
            self.inventory_dir,
            'source_data.yaml',
        )
        self.user_data_path = os.path.join(
            self.inventory_dir,
            'user_data.yaml',
        )
        self.user_data = {}
        self.source_data = {}
        self.inv = {}

    def _load_yaml(self, yaml_path):
        """
        Load the content of a variable from a yaml file.

        Parameters:
            yaml_path (str): Path to the file to read.

        Returns:
            (str|dict|list|set|bool): Variable with the content of the file.
        """

        try:
            with open(os.path.expanduser(yaml_path), 'r') as f:
                try:
                    return yaml.safe_load(f)
                except YAMLError as e:
                    self.log.error(e)
                    raise
        except FileNotFoundError as e:
            self.log.error('Error opening yaml file {}'.format(yaml_path))
            raise(e)

    def _save_yaml(self, yaml_path, variable):
        """
        Save the content of a variable into a yaml file.

        Parameters:
            yaml_path (str): Path to the file to write.
            variable (str|dict|list|set|bool): Variable to save to the file.

        Returns:
            Nothing.
        """

        with open(os.path.expanduser(yaml_path), 'w+') as f:
            yaml.dump(variable, f, default_flow_style=False)

    def load_source_data_from_file(self):
        """
        Load the source data from the source_data.yaml file into
        self.source_data.

        Parameters:
            None

        Returns:
            Nothing.
        """
        self.source_data = self._load_yaml(self.source_data_path)

    def load_user_data_from_file(self):
        """
        Load the user data from the user_data.yaml file into
        self.user_data.

        Parameters:
            None

        Returns:
            Nothing.
        """
        self.user_data = self._load_yaml(self.user_data_path)
        if self.user_data is None:
            self.user_data = {
                'ec2': {},
                'projects': {},
                'services': {},
                'informations': {},
            }

    def save(self):
        """
        Saves source and user data into the yaml files.

        Parameters:
            None.

        Returns:
            Nothing.
        """
        self._save_yaml(self.source_data_path, self.source_data)
        self._save_yaml(self.user_data_path, self.user_data)

    def _load_plugins(self):
        """
        Initializes the source plugins and saves them in the self._sources
        list with the following structure:
        [
            source_1,
            source_2,
        ]

        Parameters:
            None.

        Returns:
            Nothing.
        """

        self.sources = []

        for source in self._source_plugins:
            try:
                user_data = self.user_data[source.id]
            except KeyError:
                user_data = {}
            self.sources.append(source(user_data))

    def generate_source_data(self):
        """
        Build the source data dictionary from the sources. Generates the
        self.source_data dictionary with the following structure:
        {
            'source_1_id': [source_1_resource, source_1_resource, ...]
            'source_2_id': [source_2_resource, source_2_resource, ...]
        }

        Parameters:
            None.

        Returns:
            Nothing.
        """

        for source in self._source_plugins:
            self.source_data[source.id] = source.generate_source_data()


class Clinv():
    def __init__(self, inventory_dir):
        self.log = logging.getLogger('main')
        self.inv = {}

    def _fetch_ec2_inventory(self):
        """
        Do aggregation of data to populate the raw_inv with the aws information
        of the EC2 resources with the following structure:

        self.raw_inv['ec2'] = {
            'us-east-1': [
                {
                    'Groups': [],
                    'Instances': [
                        {
                            'ImageId': 'ami-ffcsssss',
                            'InstanceId': 'i-023desldk394995ss',
                            'InstanceType': 'c4.4xlarge',
                            'LaunchTime': datetime.datetime(
                                2018, 5, 10, 7, 13, 17, tzinfo=tzutc()
                            ),
                            'NetworkInterfaces': [
                                {
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
                                }
                            ],
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
                            'State': {'Code': 16, 'Name': 'running'},
                            'StateTransitionReason': '',
                            'Tags': [{'Key': 'Name', 'Value': 'name'}],
                            'VpcId': 'vpc-31084921'
                        }
                    ],
                    'OwnerId': '585394460090',
                    'ReservationId': 'r-039ed99cad2bb3da5'
                },
            ],
        }
        """

        self.log.info('Fetching EC2 inventory')
        self.raw_inv['ec2'] = {}

        for region in self.regions:
            ec2 = boto3.client('ec2', region_name=region)
            self.raw_inv['ec2'][region] = \
                ec2.describe_instances()['Reservations']

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
            'KeyName',
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

        for region in self.raw_inv['ec2'].keys():
            for resource in self.raw_inv['ec2'][region]:
                for instance in resource['Instances']:
                    for prune_key in prune_keys:
                        try:
                            instance.pop(prune_key)
                        except KeyError:
                            pass
                    for interface in instance['NetworkInterfaces']:
                        for prune_key in network_prune_keys:
                            try:
                                interface.pop(prune_key)
                            except KeyError:
                                pass

    def _fetch_rds_inventory(self):
        """
        Do aggregation of data to populate the raw_inv with the aws information
        of the RDS resources with the following structure:

        self.raw_inv['rds'] = {
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
        """

        self.log.info('Fetching RDS inventory')
        self.raw_inv['rds'] = {}

        for region in self.regions:
            rds = boto3.client('rds', region_name=region)
            self.raw_inv['rds'][region] = \
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

        for region in self.raw_inv['rds'].keys():
            for resource in self.raw_inv['rds'][region]:
                for prune_key in prune_keys:
                    try:
                        resource.pop(prune_key)
                    except KeyError:
                        pass

    def _fetch_aws_inventory(self):
        """
        Do aggregation of data to populate the raw_inv with the following AWS
        resources:
            * EC2
            * RDS
            * Route53

        Related methods:
            * _fetch_ec2_inventory
            * _fetch_rds_inventory
            * _fetch_route53_inventory
        """

        self._fetch_ec2_inventory()
        self._fetch_rds_inventory()
        self._fetch_route53_inventory()

    def _update_ec2_inventory(self):
        """
        Do aggregation of data to populate self.user_data and self.inv
        attributes with EC2 resources.

        self.user_data is populated with the user_data.yaml information or with
        default values.

        self.inv is populated with EC2 resources.
        """

        try:
            self.user_data['ec2']
        except KeyError:
            self.user_data['ec2'] = {}

        for region in self.raw_inv['ec2'].keys():
            for resource in self.raw_inv['ec2'][region]:
                for instance in resource['Instances']:
                    instance_id = instance['InstanceId']
                    try:
                        self.user_data['ec2'][instance_id]
                    except KeyError:
                        self.user_data['ec2'][instance_id] = {
                            'description': '',
                            'to_destroy': 'tbd',
                            'environment': 'tbd',
                            'region': region,
                        }
                    for key, value in \
                            self.user_data['ec2'][instance_id].items():
                        instance[key] = value

                    self.inv['ec2'][instance_id] = EC2(
                        {
                            instance_id: instance
                        }
                    )

    def _update_rds_inventory(self):
        """
        Do aggregation of data to populate self.user_data and self.inv
        attributes with RDS resources.

        self.user_data is populated with the user_data.yaml information or with
        default values.

        self.inv is populated with RDS resources.
        """

        try:
            self.user_data['rds']
        except KeyError:
            self.user_data['rds'] = {}

        for region in self.raw_inv['rds'].keys():
            for resource in self.raw_inv['rds'][region]:
                resource_id = resource['DbiResourceId']
                try:
                    self.user_data['rds'][resource_id]
                except KeyError:
                    self.user_data['rds'][resource_id] = {
                        'description': '',
                        'to_destroy': 'tbd',
                        'environment': 'tbd',
                        'region': region,
                    }
                for key, value in \
                        self.user_data['rds'][resource_id].items():
                    resource[key] = value

                self.inv['rds'][resource_id] = RDS(
                    {
                        resource_id: resource
                    }
                )

    def _update_active_inventory(self, resource_type):
        """
        Do aggregation of data to populate self.user_data and self.inv
        attributes with resource_type resources.

        self.user_data is populated with the user_data.yaml information or with
        default values.

        self.inv is populated with resource_type resources.

        Parameters:
            resource_type (str): Type of active resource to be processed.
                It must be one of ['projects', 'services', 'informations']
        """

        try:
            self.user_data[resource_type]
        except KeyError:
            self.user_data[resource_type] = {}

        for resource_id, resource_data in \
                self.user_data[resource_type].items():
            if resource_type == 'projects':
                resource = Project({resource_id: resource_data})
            elif resource_type == 'services':
                resource = Service({resource_id: resource_data})
            elif resource_type == 'informations':
                resource = Information({resource_id: resource_data})
            self.inv[resource_type][resource_id] = resource

    def _update_inventory(self):
        self.inv = {
            'ec2': {},
            'rds': {},
            'projects': {},
            'services': {},
            'informations': {},
        }

        self._update_ec2_inventory()
        self._update_rds_inventory()
        self._update_route53_inventory()
        self._update_active_inventory('projects')
        self._update_active_inventory('informations')
        self._update_active_inventory('services')

    def _search_in_resources(self, resource_type, search_string):
        result = []
        for resource_id, resource in self.inv[resource_type].items():
            if resource.search(search_string) is True:
                result.append(resource)
        return result

    def _search_ec2(self, search_string):
        return self._search_in_resources('ec2', search_string)

    def _search_projects(self, search_string):
        return self._search_in_resources('projects', search_string)

    def _search_services(self, search_string):
        return self._search_in_resources('services', search_string)

    def _search_informations(self, search_string):
        return self._search_in_resources('informations', search_string)

    def _search_route53(self, search_string):
        return self._search_in_resources('route53', search_string)

    def _search_rds(self, search_string):
        return self._search_in_resources('rds', search_string)

    def _short_print_resources(self, resource_list):
        for resource in resource_list:
            resource.short_print()

    def print_search(self, search_string):
        projects = self._search_projects(search_string)

        if projects != []:
            print('Type: Projects')
            self._short_print_resources(projects)

        services = self._search_services(search_string)

        if services != []:
            print('\nType: Services')
            self._short_print_resources(services)

        informations = self._search_informations(search_string)

        if informations != []:
            print('\nType: Informations')
            self._short_print_resources(informations)

        ec2_instances = self._search_ec2(search_string)

        if ec2_instances != []:
            print('\nType: EC2 instances')
            self._short_print_resources(ec2_instances)

        rds_instances = self._search_rds(search_string)

        if rds_instances != []:
            print('\nType: RDS instances')
            self._short_print_resources(rds_instances)

        route53_instances = self._search_route53(search_string)

        if route53_instances != []:
            print('\nType: Route53 instances')
            self._short_print_resources(route53_instances)

        if ec2_instances == [] and \
                route53_instances == [] and \
                rds_instances == [] and \
                projects == [] and \
                services == [] and \
                informations == []:
            print('I found nothing with that search_string')
            return

    def _unassigned_aws_resource(self, resource_type):
        """
        Do aggregation of data to print the resource_type resources that are
        not associated to any service.

        Parameters:
            resource_type (str): Type of clinv resource to be processed.
                It must be one of [
                    'ec2',
                    'rds',
                ]

        Returns:
            stdout: Prints the list of unassigned items.
        """

        all_assigned_instances = []
        for service_id, service in sorted(self.inv['services'].items()):
            try:
                for instance in service.raw['aws'][resource_type]:
                    all_assigned_instances.append(instance)
            except TypeError:
                pass
            except KeyError:
                pass

        for instance_id, instance in sorted(self.inv[resource_type].items()):
            if instance_id not in all_assigned_instances:
                if instance.state != 'terminated':
                    instance.print()

    def _unassigned_ec2(self):
        """
        Do aggregation of data to print the EC2 resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_aws_resource('ec2')

    def _unassigned_rds(self):
        """
        Do aggregation of data to print the RDS resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        self._unassigned_aws_resource('rds')

    def _unassigned_route53(self):
        """
        Do aggregation of data to print the Route53 resources that are not
        associated to any service.

        Returns:
            stdout: Prints the list of unassigned items.
        """

        resource_type = 'route53'
        all_assigned_instances = []
        for service_id, service in sorted(self.inv['services'].items()):
            try:
                for instance in service.raw['aws'][resource_type]:
                    all_assigned_instances.append(instance)
            except TypeError:
                pass
            except KeyError:
                pass

        for instance_id, instance in sorted(self.inv[resource_type].items()):
            if instance_id not in all_assigned_instances:
                if instance.type != 'SOA' and instance.type != 'NS':
                    instance.print()

    def _unassigned_services(self):
        all_assigned_services = []
        for project_id, project in sorted(self.inv['projects'].items()):
            if project.services is None:
                continue
            else:
                for service in project.services:
                    all_assigned_services.append(service)

        unassigned_services = []
        for service_id, service in sorted(self.inv['services'].items()):
            if service_id not in all_assigned_services:
                unassigned_services.append(service)
        self._short_print_resources(unassigned_services)

    def _unassigned_informations(self):
        all_assigned_informations = []
        for project_id, project in self.inv['projects'].items():
            if project.informations is None:
                continue
            else:
                for information in project.informations:
                    all_assigned_informations.append(information)

        unassigned_informations = []
        for information_id, information in \
                sorted(self.inv['informations'].items()):
            if information_id not in all_assigned_informations:
                unassigned_informations.append(information)
        self._short_print_resources(unassigned_informations)

    def unassigned(self, resource_type):
        if resource_type == 'all':
            self.log.info('Unassigned EC2')
            self._unassigned_ec2()
            self.log.info('Unassigned RDS')
            self._unassigned_rds()
            self.log.info('Unassigned Route53')
            self._unassigned_route53()
            self.log.info('Unassigned Services')
            self._unassigned_services()
            self.log.info('Unassigned Informations')
            self._unassigned_informations()
        elif resource_type == 'ec2':
            self._unassigned_ec2()
        elif resource_type == 'rds':
            self._unassigned_rds()
        elif resource_type == 'route53':
            self._unassigned_route53()
        elif resource_type == 'services':
            self._unassigned_services()
        elif resource_type == 'informations':
            self._unassigned_informations()

    def _list_resources(self, resource_type):
        """
        Do aggregation of data to return a sorted list of the resources of type
        resource_type.

        Parameters:
            resource_type (str): Type of clinv resource to be processed.
                It must be one of [
                    'ec2',
                    'rds',
                    'services',
                    'informations',
                    'projects',
                ]

        Returns:
            list: Resources of the selected type
        """

        return [
            resource
            for resource_id, resource
            in sorted(self.inv[resource_type].items())
        ]

    def _list_informations(self):
        """
        Do aggregation of data to print a list of the Information entries in
        the inventory.

        Returns:
            stdout: Prints the list of informations in the inventory.
        """

        self._short_print_resources(self._list_resources('informations'))

    def _list_projects(self):
        """
        Do aggregation of data to print a list of the Project entries in the
        inventory.

        Returns:
            stdout: Prints the list of projects in the inventory.
        """

        self._short_print_resources(self._list_resources('projects'))

    def _list_services(self):
        """
        Do aggregation of data to print a list of the Service entries in the
        inventory.

        Returns:
            stdout: Prints the list of non terminated services in the
            inventory.
        """

        not_terminated_service_ids = []
        for service_id, service in sorted(self.inv['services'].items()):
            if service.state != 'terminated':
                not_terminated_service_ids.append(service)
        self._short_print_resources(not_terminated_service_ids)

    def _list_ec2(self):
        """
        Do aggregation of data to print a list of the EC2 entries in the
        inventory.

        Returns:
            stdout: Prints the list of EC2 in the inventory.
        """

        self._short_print_resources(self._list_resources('ec2'))

    def _list_rds(self):
        """
        Do aggregation of data to print a list of the RDS entries in the
        inventory.

        Returns:
            stdout: Prints the list of RDS in the inventory.
        """

        self._short_print_resources(self._list_resources('rds'))

    def list(self, resource_type):
        """
        Do aggregation of data to print a list of the selected resource entries
        in the inventory.

        Parameters:
            resource_type (str): Type of clinv resource to be processed.
                It must be one of [
                    'ec2',
                    'rds',
                    'services',
                    'informations',
                    'projects',
                ]

        Returns:
            stdout: Prints the list of items of that resource in the inventory.
        """

        if resource_type == 'ec2':
            self._list_ec2()
        elif resource_type == 'rds':
            self._list_rds()
        elif resource_type == 'services':
            self._list_services()
        elif resource_type == 'informations':
            self._list_informations()
        elif resource_type == 'projects':
            self._list_projects()

    def _get_resource_names(self, resource_type, resource_ids):
        """
        Do aggregation of data to return a list with the information names.

        Parameters:
            resource_type (str): Type of resource, one of [
                'services',
                'informations',
                ].
            resource_ids (list): List of resource ids.

        Return:
            str: With the resource names separated by commas.
        """

        resource_names = []

        for resource_id in resource_ids:
            try:
                resource_names.append(
                    self.inv[resource_type][resource_id].name
                )
            except KeyError:
                pass

        if len(resource_names) == 0:
            return None
        elif len(resource_names) == 1:
            return resource_names[0]
        else:
            return ', '.join(resource_names)

    def _export_aws_resource(self, resource_type):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for an AWS type of resource.

        Parameters:
            resource_type (str): Type of AWS resource to be processed.
                It must be one of ['ec2', 'rds']

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            'ID',
            'Name',
            'Services',
            'To destroy',
            'Responsible',
            'Region',
            'Comments'
        ]

        # Fill up content
        exported_data = []
        for instance_id, instance in self.inv[resource_type].items():
            related_services = {}
            for service_id, service in self.inv['services'].items():
                try:
                    service.raw['aws'][resource_type]
                except TypeError:
                    continue
                except KeyError:
                    continue
                for service_resource_id in service.raw['aws'][resource_type]:
                    if service_resource_id == instance_id:
                        related_services[service_id] = service

            exported_data.append(
                [
                    instance_id,
                    instance.name,
                    self._get_resource_names('services', related_services),
                    instance._get_field('to_destroy'),
                    ', '.join(set(
                        [
                            service.responsible
                            for service_id, service in related_services.items()
                        ]
                    )),
                    instance.region,
                    instance.description,
                ]
            )

        # Sort by name
        exported_data = sorted(exported_data, key=itemgetter(1))
        exported_data.insert(0, exported_headers)

        return exported_data

    def _export_ec2(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the EC2 resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        return self._export_aws_resource('ec2')

    def _export_rds(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the RDS resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        return self._export_aws_resource('rds')

    def _export_route53(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the Route53 resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            'ID',
            'Name',
            'Type',
            'Value',
            'Services',
            'To destroy',
            'Access',
            'Description',
        ]

        # Fill up content
        resource_type = 'route53'

        exported_data = []
        for instance_id, instance in self.inv[resource_type].items():
            related_services = {}
            for service_id, service in self.inv['services'].items():
                try:
                    service.raw['aws'][resource_type]
                except TypeError:
                    continue
                except KeyError:
                    continue
                for service_resource_id in service.raw['aws'][resource_type]:
                    if service_resource_id == instance_id:
                        related_services[service_id] = service

            exported_data.append(
                [
                    instance.id,
                    instance.name,
                    instance.type,
                    ', '.join(instance.value),
                    self._get_resource_names('services', related_services),
                    instance._get_field('to_destroy'),
                    instance.access,
                    instance.description,
                ]
            )

        # Sort by name
        exported_data = sorted(exported_data, key=itemgetter(1))
        exported_data.insert(0, exported_headers)

        return exported_data

    def _export_projects(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the Project resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            'ID',
            'Name',
            'Services',
            'Informations',
            'State',
            'Description',
        ]

        # Fill up content
        exported_data = []
        for resource_id, resource in self.inv['projects'].items():
            exported_data.append(
                [
                    resource_id,
                    resource.name,
                    self._get_resource_names('services', resource.services),
                    self._get_resource_names(
                        'informations',
                        resource.informations
                    ),
                    resource.state,
                    resource.description,
                ]
            )

        # Sort by id
        exported_data = sorted(exported_data, key=itemgetter(0))
        exported_data.insert(0, exported_headers)

        return exported_data

    def _export_services(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the Service resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            'ID',
            'Name',
            'Access',
            'State',
            'Informations',
            'Description',
        ]

        # Fill up content
        exported_data = []
        for resource_id, resource in self.inv['services'].items():
            exported_data.append(
                [
                    resource_id,
                    resource.name,
                    resource.access,
                    resource.state,
                    self._get_resource_names(
                        'informations',
                        resource.informations
                    ),
                    resource.description,
                ]
            )

        # Sort by id
        exported_data = sorted(exported_data, key=itemgetter(0))
        exported_data.insert(0, exported_headers)

        return exported_data

    def _export_informations(self):
        """
        Do aggregation of data to return a list with the information needed to
        fill up a spreadsheet for the Information resources.

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        # Create spreadsheet headers
        exported_headers = [
            'ID',
            'Name',
            'State',
            'Responsible',
            'Personal Data',
            'Description',
        ]

        # Fill up content
        exported_data = []
        for resource_id, resource in self.inv['informations'].items():
            exported_data.append(
                [
                    resource_id,
                    resource.name,
                    resource.state,
                    resource.responsible,
                    resource.personal_data,
                    resource.description,
                ]
            )

        # Sort by id
        exported_data = sorted(exported_data, key=itemgetter(0))
        exported_data.insert(0, exported_headers)

        return exported_data

    def export(self, export_path):
        """
        Method to export the clinv inventory to ods.

        It generates the information needed to fill up a spreadsheet for a
        selected resource.

        Parameters:
            export_path (str): Path to export the inventory.
                (Default: ~/.local/share/clinv/inventory.ods)

        Returns:
            list: First row are the headers of the spreadsheet, followed
            by lines of data.
        """

        book = OrderedDict()
        book.update({'Projects': self._export_projects()})
        book.update({'Services': self._export_services()})
        book.update({'Informations': self._export_informations()})
        book.update({'EC2': self._export_ec2()})
        book.update({'RDS': self._export_rds()})
        book.update({'Route53': self._export_route53()})

        pyexcel.save_book_as(
            bookdict=book,
            dest_file_name=os.path.expanduser(export_path),
        )

    @property
    def regions(self):
        ec2 = boto3.client('ec2')
        return [
            region['RegionName']
            for region in ec2.describe_regions()['Regions']
        ]

    def print(self, input_resource_id):
        """
        Method to print the information of a clinv resource.

        Parameters:
            input_resource_id (str): id of the resource

        Returns:
            stdout: Resource information
        """

        for resource_type in self.inv:
            for resource_id, resource in self.inv[resource_type].items():
                if resource_id == input_resource_id:
                    resource.print()
