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

from clinv.resources import EC2, RDS, Project, Service, Information
from collections import OrderedDict
from operator import itemgetter
from yaml import YAMLError
import boto3
import logging
import os
import pyexcel
import yaml


class Clinv():
    def __init__(self, inventory_dir):
        self.log = logging.getLogger('main')
        self.inventory_dir = inventory_dir
        self.raw_inv_path = os.path.join(
            self.inventory_dir,
            'raw_inventory.yaml',
        )
        self.raw_data_path = os.path.join(
            self.inventory_dir,
            'raw_data.yaml',
        )
        self.raw_data = {
            'ec2': {},
        }
        self.raw_inv = {
            'ec2': {},
            'rds': {},
        }

    def _fetch_ec2_inventory(self):
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
        self._fetch_ec2_inventory()
        self._fetch_rds_inventory()

    def _update_ec2_inventory(self):
        try:
            self.raw_data['ec2']
        except KeyError:
            self.raw_data['ec2'] = {}

        for region in self.raw_inv['ec2'].keys():
            for resource in self.raw_inv['ec2'][region]:
                for instance in resource['Instances']:
                    instance_id = instance['InstanceId']
                    try:
                        self.raw_data['ec2'][instance_id]
                    except KeyError:
                        self.raw_data['ec2'][instance_id] = {
                            'description': '',
                            'to_destroy': 'tbd',
                            'environment': 'tbd',
                            'region': region,
                        }
                    for key, value in \
                            self.raw_data['ec2'][instance_id].items():
                        instance[key] = value

                    self.inv['ec2'][instance_id] = EC2(
                        {
                            instance_id: instance
                        }
                    )

    def _update_rds_inventory(self):
        try:
            self.raw_data['rds']
        except KeyError:
            self.raw_data['rds'] = {}

        for region in self.raw_inv['rds'].keys():
            for resource in self.raw_inv['rds'][region]:
                resource_id = resource['DbiResourceId']
                try:
                    self.raw_data['rds'][resource_id]
                except KeyError:
                    self.raw_data['rds'][resource_id] = {
                        'description': '',
                        'to_destroy': 'tbd',
                        'environment': 'tbd',
                        'region': region,
                    }
                for key, value in \
                        self.raw_data['rds'][resource_id].items():
                    resource[key] = value

                self.inv['rds'][resource_id] = RDS(
                    {
                        resource_id: resource
                    }
                )

    def _update_active_inventory(self, resource_type):
        try:
            self.raw_data[resource_type]
        except KeyError:
            self.raw_data[resource_type] = {}

        for resource_id, resource_data in self.raw_data[resource_type].items():
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
        self._update_active_inventory('projects')
        self._update_active_inventory('informations')
        self._update_active_inventory('services')

    def _save_yaml(self, yaml_path, dictionary):
        'Save variable to yaml'

        with open(os.path.expanduser(yaml_path), 'w+') as f:
            yaml.dump(dictionary, f, default_flow_style=False)

    def save_inventory(self):
        self._save_yaml(self.raw_inv_path, self.raw_inv)
        self._save_yaml(self.raw_data_path, self.raw_data)

    def _load_yaml(self, yaml_path):
        'Load YAML to variable'
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

    def load_inventory(self):
        self.raw_inv = self._load_yaml(self.raw_inv_path)

    def load_data(self):
        self.raw_data = self._load_yaml(self.raw_data_path)
        if self.raw_data is None:
            self.raw_data = {
                'ec2': {},
                'projects': {},
                'services': {},
                'informations': {},
            }
        self._update_inventory()

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

        if ec2_instances == [] and \
                projects == [] and \
                services == [] and \
                informations == []:
            print('I found nothing with that search_string')
            return

    def _unassigned_aws_resource(self, resource_type):
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
                    print('{}: {}'.format(instance.id, instance.name))

    def _unassigned_ec2(self):
        self._unassigned_aws_resource('ec2')

    def _unassigned_rds(self):
        self._unassigned_aws_resource('rds')

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
            self._unassigned_ec2()
            self._unassigned_rds()
            self._unassigned_services()
            self._unassigned_informations()
        elif resource_type == 'ec2':
            self._unassigned_ec2()
        elif resource_type == 'rds':
            self._unassigned_rds()
        elif resource_type == 'services':
            self._unassigned_services()
        elif resource_type == 'informations':
            self._unassigned_informations()

    def _list_resources(self, resource_type):
        return [
            resource
            for resource_id, resource
            in sorted(self.inv[resource_type].items())
        ]

    def _list_informations(self):
        self._short_print_resources(self._list_resources('informations'))

    def _list_projects(self):
        self._short_print_resources(self._list_resources('projects'))

    def _list_services(self):
        not_terminated_service_ids = []
        for service_id, service in sorted(self.inv['services'].items()):
            if service.state != 'terminated':
                not_terminated_service_ids.append(service)
        self._short_print_resources(not_terminated_service_ids)

    def _list_ec2(self):
        for instance_id, instance in self.inv['ec2'].items():
            print('{}: {}'.format(instance.id, instance.name))

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
        book.update(
            {
                'Projects': self._export_projects()
            }
        )
        book.update(
            {
                'Services': self._export_services()
            }
        )
        book.update(
            {
                'Informations': self._export_informations()
            }
        )
        book.update(
            {
                'EC2 Instances': self._export_ec2()
            }
        )
        book.update(
            {
                'RDS Instances': self._export_rds()
            }
        )

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
