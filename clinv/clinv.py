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

from yaml import YAMLError
import boto3
import logging
import os
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
        self.raw_inv = {
            'ec2': [],
        }

    def _fetch_ec2(self):
        self.raw_inv['ec2'] = self.ec2.describe_instances()['Reservations']
        for resource in self.raw_inv['ec2']:
            resource['assigned_service'] = False
            resource['exposed_services'] = []

    def _search_ec2(self, search_string):
        for ec2_resource in self.raw_inv['ec2']:
            for instance in ec2_resource['Instances']:
                # Search by id
                if instance['InstanceId'] == search_string:
                    return instance

                # Search by name
                if self._get_ec2_instance_name(instance) == search_string:
                    return instance

                # Search by public IP
                if search_string in self._get_ec2_public_ip(instance):
                    return instance

                # Search by private IP
                if search_string in self._get_ec2_private_ip(instance):
                    return instance

                # Search by security groups
                if search_string in self._get_ec2_security_groups(instance):
                    return instance

    def _save_yaml(self, yaml_path, dictionary):
        'Save variable to yaml'

        with open(os.path.expanduser(yaml_path), 'w+') as f:
            yaml.dump(dictionary, f, default_flow_style=False)

    def save_inventory(self):
        self._save_yaml(self.raw_inv_path, self.raw_inv)

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

    def _get_ec2_instance_name(self, instance):
        try:
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    return tag['Value']
        except KeyError:
            pass
        except TypeError:
            pass

    def _get_ec2_security_groups(self, instance):
        try:
            return [security_group['GroupId']
                    for security_group in instance['SecurityGroups']
                    ]
        except KeyError:
            pass

    def _get_ec2_private_ip(self, instance):
        private_ips = []
        try:
            for interface in instance['NetworkInterfaces']:
                for association in interface['PrivateIpAddresses']:
                    private_ips.append(association['PrivateIpAddress'])
        except KeyError:
            pass
        return private_ips

    def _get_ec2_state(self, instance):
        try:
            return instance['State']['Name']
        except KeyError:
            pass

    def _get_ec2_public_ip(self, instance):
        public_ips = []
        try:
            for interface in instance['NetworkInterfaces']:
                for association in interface['PrivateIpAddresses']:
                    public_ips.append(association['Association']['PublicIp'])
        except KeyError:
            pass
        return public_ips

    def print_ec2(self, search_string):
        instance = self._search_ec2(search_string)

        if instance is None:
            print('I found nothing with that search_string')
            return

        print('Type: EC2 instance')
        print('Name: {}'.format(self._get_ec2_instance_name(instance)))
        print('ID: {}'.format(instance['InstanceId']))
        print('State: {}'.format(self._get_ec2_state(instance)))
        print('SecurityGroups: {}'.format(
            ', '.join(self._get_ec2_security_groups(instance))
        ))
        print('PrivateIP: {}'.format(self._get_ec2_private_ip(instance)))
        print('PublicIP: {}'.format(self._get_ec2_public_ip(instance)))
