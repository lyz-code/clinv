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

import logging
import os

import yaml
from yaml import YAMLError

from clinv.sources import aws, risk_management

active_source_plugins = [
    aws.ASGsrc,
    aws.EC2src,
    aws.IAMGroupsrc,
    aws.IAMUsersrc,
    risk_management.Informationsrc,
    risk_management.Peoplesrc,
    risk_management.Projectsrc,
    aws.RDSsrc,
    aws.Route53src,
    aws.S3src,
    aws.SecurityGroupsrc,
    risk_management.Servicesrc,
    aws.VPCsrc,
]


class Inventory:
    """
    Class to gather and manipulate the inventory data.

    Parameters:
        inventory_dir (str): Path to the directory where the source_data.yml
            and user_data.yml are located.
        source_plugins (list): List of source plugins objects, for example:
            [EC2src, RDSsrc, Route53src]

    Public methods:
        generate: Build the inventory from source and user data.
        load: Load the inventory from the yaml files.
        save: Saves source and user data into the yaml files.

    Internal methods:
        _load_plugins: Initializes the source plugins.
        _load_source_data_from_file: Load the source data from the
            source_data.yaml file.
        _load_user_data_from_file: Load the user data from the
            user_data.yaml file.
        _load_yaml: Load a variable from a yaml file.
        _generate_inventory_objects: Build the inventory dictionary from the
            sources and user data.
        _generate_source_data: Build the source data dictionary from the
            sources.
        _generate_user_data: Build the user data dictionary from the
            sources.
        _save_yaml: Save a variable to a yaml file.

    Public attributes:
        source_data (dict): Aggregated source data of the different sources.
        user_data (dict): Aggregated user data of the different sources.
        sources (dict): Aggregated user data of the different sources.
    """

    def __init__(self, inventory_dir, source_plugins=active_source_plugins):
        self.inventory_dir = inventory_dir

        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)
        self._source_plugins = source_plugins
        self.source_data_path = os.path.join(self.inventory_dir, "source_data.yaml",)
        self.user_data_path = os.path.join(self.inventory_dir, "user_data.yaml",)
        self.user_data = {}
        self.source_data = {}
        self.inv = {}

    def load(self):
        """
        Loads the inventory from the saved data.

        Loads the source data from the source_data.yaml file into
        self.source_data.

        Loads the user data from the user_data.yaml file into
        self.user_data.

        Loads the source plugins into self.sources

        Loads the resource objects into self.inv

        Parameters:
            None.

        Returns:
            Nothing.
        """

        self.source_data = self._load_yaml(self.source_data_path)
        self.user_data = self._load_yaml(self.user_data_path)
        self._load_plugins()
        self._generate_inventory_objects()

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
                user_data = self.user_data[source().id]
            except KeyError:
                user_data = {}
            try:
                source_data = self.source_data[source().id]
            except KeyError:
                source_data = {}
            self.sources.append(source(source_data=source_data, user_data=user_data,))

    def _load_yaml(self, yaml_path):
        """
        Load the content of a variable from a yaml file.

        Parameters:
            yaml_path (str): Path to the file to read.

        Returns:
            (str|dict|list|set|bool): Variable with the content of the file.
        """

        try:
            with open(os.path.expanduser(yaml_path), "r") as f:
                try:
                    return yaml.safe_load(f)
                except YAMLError as e:
                    self.log.error(e)
                    raise
        except FileNotFoundError as e:
            self.log.error("Error opening yaml file {}".format(yaml_path))
            raise (e)

    def generate(self, resource_type: str = "all") -> None:
        """
        Build the inventory from source and user data.

        And saves the inventory to disk.
        """

        try:
            self.source_data = self._load_yaml(self.source_data_path)
            self.user_data = self._load_yaml(self.user_data_path)
        except FileNotFoundError:
            pass
        self._load_plugins()
        self._generate_source_data(resource_type)
        self._generate_user_data(resource_type)
        self._generate_inventory_objects(resource_type)
        self.save()

    def _generate_source_data(self, resource_type: str = "all") -> None:
        """
        Build the source data dictionary from the sources. Generates the
        self.source_data dictionary with the following structure:
        {
            'source_1_id': [
                source_1_resource_1_source_data_dict,
                source_1_resource_2_source_data_dict,
                ...
            ]
            'source_2_id': [
                source_2_resource_1_source_data_dict,
                source_2_resource_2_source_data_dict,
                ...
            ]
        }

        Needs the self.sources data, so you'll need to call first
        self._load_plugins().
        """

        for source in self.sources:
            if resource_type == "all" or source.id == resource_type:
                self.source_data[source.id] = source.generate_source_data()

    def _generate_user_data(self, resource_type: str = "all") -> None:
        """
        Build the user data dictionary from the sources. Generates the
        self.user_data dictionary with the following structure:
        {
            'source_1_id': {
                source_1_resource_1_id: source_1_resource_1_user_data_dict,
                source_1_resource_2_id: source_1_resource_2_user_data_dict,
                ...
            ]
            'source_2_id': [
                source_2_resource_1_id: source_1_resource_1_user_data_dict,
                source_2_resource_2_id: source_1_resource_2_user_data_dict,
                ...
            ]
        }

        As it needs the information of the sources, it needs to be called
        after _generate_source_data.

        Needs the self.sources data, so you'll need to call first
        self._load_plugins().
        """

        for source in self.sources:
            if resource_type == "all" or source.id == resource_type:
                self.user_data[source.id] = source.generate_user_data()

    def _generate_inventory_objects(self, resource_type: str = "all") -> None:
        """
        Build the inventory dictionary from the sources. Generates the
        self.inv dictionary with the following structure:
        {
            'source_1_id': {
                source_1_resource_1_id: source_1_resource_1_object,
                source_1_resource_2_id: source_1_resource_2_object,
                ...
            ]
            'source_2_id': [
                source_2_resource_1_id: source_1_resource_1_object,
                source_2_resource_2_id: source_1_resource_2_object,
                ...
            ]
        }

        As it needs the information of the sources and user, it needs to be
        called after _generate_source_data and _generate_user_data.

        Needs the self.sources data, so you'll need to call first
        self._load_plugins().
        """

        for source in self.sources:
            if resource_type == "all" or source.id == resource_type:
                self.inv[source.id] = source.generate_inventory()

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

    def _save_yaml(self, yaml_path, variable):
        """
        Save the content of a variable into a yaml file.

        Parameters:
            yaml_path (str): Path to the file to write.
            variable (str|dict|list|set|bool): Variable to save to the file.

        Returns:
            Nothing.
        """

        with open(os.path.expanduser(yaml_path), "w+") as f:
            yaml.dump(variable, f, default_flow_style=False)
