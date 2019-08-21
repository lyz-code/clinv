"""
Module to store the Risk management sources used by Clinv.

Classes:
    RiskManagementsrc: Class to gather and manipulate the AWS Route53
    resources.
"""
from clinv.resources import Information, Project, Service
from clinv.sources import ClinvSourcesrc


class RiskManagementsrc(ClinvSourcesrc):
    """
    Class to gather and manipulate the RiskManagement resources.

    Parameters:
        source_data (dict): RiskManagementsrc compatible source_data
        dictionary.
        user_data (dict): RiskManagementsrc compatible user_data dictionary.

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
        self.id = 'risk_management'

    def generate_source_data(self):
        """
        This source doesn't need to fetch data from source, so we return an
        empty dict.

        Returns:
            dict: content of self.source_data.
        """

        self.log.info('Fetching RiskManagement inventory')
        self.source_data = {}
        return self.source_data

    def generate_user_data(self):
        """
        This source doesn't need to generate default user data, so we return an
        empty dict.

        Returns:
            dict: content of self.user_data.
        """

        self.user_data = {}
        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with RiskManagement resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: RiskManagement inventory with user and source data
        """

        inventory = {
            'informations': {},
            'projects': {},
            'services': {},
        }

        for resource_type in inventory.keys():
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
                inventory[resource_type][resource_id] = resource

        return inventory
