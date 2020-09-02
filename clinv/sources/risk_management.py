"""
Module to store the Risk management sources used by Clinv.

Classes:
    RiskManagementsrc: Class to gather common methods for the RiskManagement
        resources.
    ClinvActiveResource: Abstract class child of ClinvGenericResource to gather
        common method and attributes of the Project, Service and Information
        resources.
    Project: Extends the ClinvActiveResource class to add specific properties
        and methods for the projects stored in the inventory.
    Information: Extends the ClinvActiveResource class to add specific
        properties and methods for the information assets stored in the
        inventory.
    Service: Extends the ClinvActiveResource class to add specific properties
        and methods for the service assets stored in the inventory.
"""
from clinv.sources import ClinvSourcesrc, ClinvGenericResource

import re


class RiskManagementBasesrc(ClinvSourcesrc):
    """
    Class to gather common methods for the RiskManagement resources.

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

    def generate_source_data(self):
        """
        This source doesn't need to fetch data from source, so we return an
        empty dict.

        Returns:
            dict: content of self.source_data.
        """

        self.source_data = {}
        return self.source_data

    def generate_user_data(self):
        """
        This source doesn't need to generate default user data, so we return an
        empty dict.

        Returns:
            dict: content of self.user_data.
        """

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

        inventory = {}

        for resource_id, resource_data in self.user_data.items():
            resource = self.resource_obj({resource_id: resource_data})
            inventory[resource_id] = resource

        return inventory


class Projectsrc(RiskManagementBasesrc):
    """
    Class to gather and manipulate the Project resources.

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
        self.id = "projects"
        self.resource_obj = Project


class Servicesrc(RiskManagementBasesrc):
    """
    Class to gather and manipulate the Service resources.

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
        self.id = "services"
        self.resource_obj = Service


class Informationsrc(RiskManagementBasesrc):
    """
    Class to gather and manipulate the Information resources.

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
        self.id = "informations"
        self.resource_obj = Information


class Peoplesrc(RiskManagementBasesrc):
    """
    Class to gather and manipulate the Information resources.

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
        self.id = "people"
        self.resource_obj = People


class ClinvActiveResource(ClinvGenericResource):
    """
    Abstract class to extend ClinvGenericResource, it gathers common method and
    attributes the Project, Service and Information resources.

    Public properties:
        responsible: Returns the person responsible of the resource.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvGenericResource.
        """

        super().__init__(raw_data)

    @property
    def responsible(self):
        """
        Do aggregation of data to return the person responsible of the
        resource.

        Returns:
            str: Responsible of the resource.
        """

        return self._get_field("responsible", "str")


class Project(ClinvActiveResource):
    """
    Extends the ClinvActiveResource class to add specific properties and
    methods for the projects stored in the inventory.

    The projects represent the reason for a group of service and information
    assets to exist.

    Public methods:
        print: Print information of the resource.

    Public properties:
        aliases: Returns the aliases of the project.
        services: Returns a list of service ids used by the project.
        informations: Returns a list of information ids used by the project.
        people: Returns a list of people ids of the project.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def aliases(self):
        """
        Do aggregation of data to return the aliases of the project.

        Returns:
            list: of aliases.
        """

        return self._get_optional_field("aliases", "list")

    @property
    def services(self):
        """
        Do aggregation of data to return the Service resource ids used by
        this project.

        Returns:
            list: of service ids.
        """

        return self._get_field("services", "list")

    @property
    def informations(self):
        """
        Do aggregation of data to return the Information resource ids used
        by this project.

        Returns:
            list: of information ids.
        """

        return self._get_field("informations", "list")

    @property
    def people(self):
        """
        Do aggregation of data to return the People resource ids used
        by this project.

        Returns:
            list: of people ids.
        """

        return self._get_field("people", "list")

    def search(self, search_string):
        """
        Extend the parent search method to include project specific search.

        Extend to search by:
            aliases

        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the ClinvGenericResource searches
        if super().search(search_string):
            return True

        # Search by aliases
        if self.aliases is not None and search_string in self.aliases:
            return True

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Is more verbose than short_print but less verbose than the describe
        method.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Aliases: {}".format(", ".join(self.aliases)))
        print("  Description: {}".format(self.description))
        print("  State: {}".format(self.state))
        print("  Services: {}".format(", ".join(self.services)))
        print("  Informations: {}".format(", ".join(self.informations)))


class Information(ClinvActiveResource):
    """
    Extends the ClinvActiveResource class to add specific properties and
    methods for the information assets stored in the inventory.

    Public methods:
        print: Print information of the resource.

    Public properties:
        personal_data: Returns if the information contains personal data.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def personal_data(self):
        """
        Do aggregation of data to return if the information contains
        personal data.

        Returns:
            bool: If the information contains personal data.
        """

        return self._get_field("personal_data")

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Is more verbose than short_print but less verbose than the describe
        method.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Description: {}".format(self.description))
        print("  State: {}".format(self.state))
        print("  Personal Information: {}".format(self.personal_data))


class Service(ClinvActiveResource):
    """
    Extends the ClinvActiveResource class to add specific properties and
    methods for the service assets stored in the inventory.

    Public methods:
        print: Print information of the resource.
        search: Extends parent method to search by aws resources

    Public properties:
        access: Returns the level of exposure of the service.
        informations: Returns a list of information ids used by the service.
        aws: Returns a dict of aws resources used by the service.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def access(self):
        """
        Do aggregation of data to return the level of exposition of the
        resource.

        Returns:
            str: Access of the resource.
        """

        return self._get_field("access", "str")

    @property
    def informations(self):
        """
        Do aggregation of data to return the Information resource ids used
        by this service.

        Returns:
            list: of information ids.
        """

        return self._get_field("informations", "list")

    @property
    def aws(self):
        """
        Do aggregation of data to return the aws resource ids used
        by this service.

        Returns:
            dict: AWS resources used by the service.
        """

        return self._get_field("aws", "dict")

    @property
    def dependencies(self):
        """
        Do aggregation of data to return the dependencies of this service.

        Returns:
            list: Group of service ids.
        """

        return self._get_optional_field("dependencies", "list")

    def search(self, search_string):
        """
        Extend the parent search method to include service specific search.

        Extend to search by:
            AWS resources

        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the ClinvGenericResource searches
        if super().search(search_string):
            return True

        # Search by email
        service_aws_resources = [
            resource_id
            for resource_type in self.aws
            for resource_id in self.aws[resource_type]
        ]
        if self._match_list(search_string, service_aws_resources):
            return True

        # Search by service dependency
        if self.dependencies is not None and self._match_list(
            search_string, self.dependencies
        ):
            return True

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Is more verbose than short_print but less verbose than the describe
        method.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Description: {}".format(self.description))
        print("  State: {}".format(self.state))
        print("  Access: {}".format(self.access))
        print("  Informations: {}".format(", ".join(self.informations)))
        print("  Related resources:")
        for resource_id, resource_value in self.raw["aws"].items():
            print("    {}:".format(resource_id))
            for resource_name in resource_value:
                print("      {}".format(resource_name))


class People(ClinvActiveResource):
    """
    Extends the ClinvActiveResource class to add specific properties and
    methods for the people assets stored in the inventory.

    Public methods:
        print: Print information of the resource.
        search: Extends parent method to search by email and iam user

    Public properties:
        iam_user: Returns IAM user of the person.
        email: Returns IAM user email.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def iam_user(self):
        """
        Do aggregation of data to return the iam user of the person.

        Returns:
            str: IAM user id.
        """

        return self._get_field("iam_user", "str")

    @property
    def email(self):
        """
        Do aggregation of data to return the email of the person.

        Returns:
            str: email.
        """

        return self._get_field("email", "str")

    def search(self, search_string):
        """
        Extend the parent search method to include people specific search.

        Extend to search by:
            email
            iam_user

        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the ClinvGenericResource searches
        if super().search(search_string):
            return True

        # Search by email
        if re.match(search_string, self.email):
            return True

        # Search by iam_user
        if re.match(search_string, self.iam_user):
            return True

    def print(self):
        """
        Override parent method to do aggregation of data to print information
        of the resource.

        Is more verbose than short_print but less verbose than the describe
        method.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  Description: {}".format(self.description))
        print("  Email: {}".format(self.email))
        print("  State: {}".format(self.state))
        print("  IAM User: {}".format(self.iam_user))
