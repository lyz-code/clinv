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

from clinv.aws import EC2Instance
from yaml import YAMLError
import boto3
import logging
import os
import re
import yaml


class Clinv():
    def __init__(self, inventory_dir):
        self.log = logging.getLogger('main')
        self.ec2 = boto3.client('ec2')
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

    def _update_raw_inventory(self):
        self.raw_inv = {
            'ec2': [],
        }
        self.raw_inv['ec2'] = \
            self.ec2.describe_instances()['Reservations']

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

        for resource in self.raw_inv['ec2']:
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

    def _update_inventory(self):
        self.inv = {
            'ec2': {},
        }
        for resource in self.raw_inv['ec2']:
            for instance in resource['Instances']:
                instance_id = instance['InstanceId']
                try:
                    self.raw_data['ec2'][instance_id]
                except KeyError:
                    self.raw_data['ec2'][instance_id] = {
                        'description': '',
                        'to_destroy': False,
                    }
                for key, value in \
                        self.raw_data['ec2'][instance_id].items():
                    instance[key] = value

                self.inv['ec2'][instance_id] = EC2Instance(instance)

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
            }

    def _search_ec2(self, search_string):
        result = []
        for instance_id, instance in self.inv['ec2'].items():
            # Search by id
            if re.match(search_string, instance.id):
                result.append(instance)

            # Search by name
            if re.match(search_string, instance.name):
                result.append(instance)

            # Search by public IP
            if search_string in instance.public_ips:
                result.append(instance)

            # Search by private IP
            if search_string in instance.private_ips:
                result.append(instance)

            # Search by security groups
            if search_string in instance.security_groups:
                result.append(instance)
        return result

    def print_search(self, search_string):
        instances = self._search_ec2(search_string)

        if instances == []:
            print('I found nothing with that search_string')
            return

        print('Type: EC2 instances')
        for instance in instances:
            instance.print()

    def _unassigned_ec2(self):
        all_assigned_instances = []
        for service_id, service in self.raw_data['services'].items():
            for instance in service['aws']['ec2']:
                all_assigned_instances.append(instance)

        for instance_id, instance in self.inv['ec2'].items():
            if instance_id not in all_assigned_instances:
                print('{}: {}'.format(instance.id, instance.name))

    def _unassigned_services(self):
        all_assigned_services = []
        for project_id, project in self.raw_data['projects'].items():
            try:
                for service in project['services']:
                    all_assigned_services.append(service)
            except TypeError:
                pass

        for service_id, service in self.raw_data['services'].items():
            if service_id not in all_assigned_services:
                print('{}: {}'.format(service_id, service['name']))

    def _unassigned_informations(self):
        all_assigned_informations = []
        for project_id, project in self.raw_data['projects'].items():
            try:
                for information in project['informations']:
                    all_assigned_informations.append(information)
            except TypeError:
                pass

        for information_id, information in \
                self.raw_data['informations'].items():
            if information_id not in all_assigned_informations:
                print('{}: {}'.format(information_id, information['name']))

    def unassigned(self, resource_type):
        if resource_type == 'ec2':
            self._unassigned_ec2()
        elif resource_type == 'services':
            self._unassigned_services()
        elif resource_type == 'informations':
            self._unassigned_informations()
