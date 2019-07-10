"""
Module to store the different resources used by Clinv.

Classes:
    ClinvGenericResource: Abstract class to gather common method and attributes
        for all Clinv resources.
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
    ClinvAWSResource: Abstract class to extend ClinvGenericResource, it gathers
        common method and attributes for the AWS resources.
    EC2: Abstract class to extend ClinvAWSResource, it gathers method and
        attributes for the EC2 resources.
    RDS: Abstract class to extend ClinvAWSResource, it gathers method and
        attributes for the RDS resources.
"""

import re


class ClinvGenericResource():
    """
    Abstract class to gather common method and attributes for all Clinv
    resources.

    Public methods:
        search: Search in the resource data if a string matches.
        short_print: Print the id and name of the resource.
        state: Returns the state of the resource.

    Public properties:
        description: Returns the description of the resource.
        name: Returns the name of the resource.
    """

    def __init__(self, raw_data):
        """
        Sets attributes for the object.

        Parameters:
            'raw_data (dict): Dictionary containing the data of the resource.
                It must only have one key-value, being the key the resource id
                and the value the dictionary with the information.

        Attributes:
            id: Stores the id of the resource.
            raw: Stores the raw_data dictionary information
        """

        self.id = [id for id in raw_data.keys()][0]
        self.raw = raw_data[self.id]

    def _transform_type(self, input_object, output_type=None):
        """
        Return the input_object on the desired output_type.

        Parameters:
            input_object (str or list): Object to be transformed.
            output_type (str): Type of the returned value, must be 'str' or
                'list'. By default, is set to None to return the original
                value without transformations.

        Returns:
            str or list: The input_object on the desired output_type.
        """

        if output_type == 'list':
            if isinstance(input_object, str):
                return [input_object]
        elif output_type == 'str':
            if isinstance(input_object, list):
                return ', '.join(input_object)
        return input_object

    def _get_field(self, key, output_type=None):
        """
        Do aggregation of data to return the value of the self.raw[key].

        Parameters:
            key (str): Key of the self.raw dictionary.

        Optional parameters:
            output_type (str): Type of the returned value, must be 'str' or
                'list'. By default, is set to None to return the original
                value without transformations.

        Exceptions:
            KeyError: If the key doesn't exist.
            ValueError: If the value is set to None.

        Returns:
            str or list: The value of the self.raw[key] on the desired
            output_type.
        """

        try:
            if self.raw[key] is None:
                raise ValueError(
                    "{} {} key is set to None, ".format(self.id, key) +
                    "please assign it a defined value",
                )
        except KeyError:
            raise KeyError(
                "{} doesn't have the {} key defined".format(self.id, key)
            )

        return self._transform_type(self.raw[key], output_type)

    def _get_optional_field(self, key, output_type=None):
        """
        Do aggregation of data to return the value of the self.raw[key].

        It's similar to _get_field, but it wont raise exceptions on inexistent
        keys or if the value is None

        Parameters:
            key (str): Key of the self.raw dictionary.

        Optional parameters:
            output_type (str): Type of the returned value, must be 'str' or
                'list'. By default, is set to None to return the original
                value without transformations.

        Returns:
            str or list: The value of the self.raw[key] on the desired
            output_type. Or None if it doesn't exist
        """

        try:
            self.raw[key]
        except KeyError:
            return None

        value = self.raw[key]

        if output_type == 'list':
            if isinstance(value, str):
                return [value]
        elif output_type == 'str':
            if isinstance(value, list):
                return ', '.join(value)

        return value

    @property
    def description(self):
        """
        Do aggregation of data to return the description of the resource.

        Returns:
            str: Description of the resource.
        """

        return self._get_field('description', 'str')

    @property
    def name(self):
        """
        Do aggregation of data to return the name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self._get_field('name', 'str')

    @property
    def state(self):
        """
        Do aggregation of data to return the state of the resource.

        Returns:
            str: State of the resource.
        """

        return self._get_field('state', 'str')

    def search(self, search_string):
        """
        Search in the resource data to see if the search_string matches.

        Search by:
            id
            name
            description

        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Search by id
        if re.match(search_string, self.id):
            return True

        # Search by name
        if self.name is not None and \
                re.match(search_string, self.name, re.IGNORECASE):
            return True

        # Search by description
        if re.match(search_string, self.description, re.IGNORECASE):
            return True

        return False

    def short_print(self):
        """
        Do aggregation of data to print the id and name of the resource.

        Is less verbose than print and describe methods.

        Returns:
            stdout: Prints 'id: name' of the resource.
        """

        print('{}: {}'.format(self.id, self.name))


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

        return self._get_field('responsible', 'str')


class Project(ClinvActiveResource):
    """
    Extends the ClinvActiveResource class to add specific properties and
    methods for the projects stored in the inventory.

    The projects represent the reason for a group of service and information
    assets to exist.

    Public properties:
        aliases: Returns the aliases of the project.
        services: Returns a list of service ids used by the project.
        informations: Returns a list of information ids used by the project.
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

        return self._get_optional_field('aliases', 'list')

    @property
    def services(self):
        """
        Do aggregation of data to return the Service resource ids used by
        this project.

        Returns:
            list: of service ids.
        """

        return self._get_field('services', 'list')

    @property
    def informations(self):
        """
        Do aggregation of data to return the Information resource ids used
        by this project.

        Returns:
            list: of information ids.
        """

        return self._get_field('informations', 'list')

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


class Information(ClinvActiveResource):
    """
    Extends the ClinvActiveResource class to add specific properties and
    methods for the information assets stored in the inventory.

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

        return self._get_field('personal_data')


class Service(ClinvActiveResource):
    """
    Extends the ClinvActiveResource class to add specific properties and
    methods for the service assets stored in the inventory.

    Public properties:
        access: Returns the level of exposure of the service.
        informations: Returns a list of information ids used by the service.
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

        return self._get_field('access', 'str')

    @property
    def informations(self):
        """
        Do aggregation of data to return the Information resource ids used
        by this service.

        Returns:
            list: of information ids.
        """

        return self._get_field('informations', 'list')


class ClinvAWSResource(ClinvGenericResource):
    """
    Abstract class to extend ClinvGenericResource, it gathers common method and
    attributes for the AWS resources.

    Public methods:
        search: Search in the resource data if a string matches.

    Public properties:
        region: Returns the region of the resource.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def region(self):
        """
        Do aggregation of data to return the region of the resource.

        Returns:
            str: Region of the resource.
        """

        return self._get_field('region', 'str')

    def search(self, search_string):
        """
        Extend the parent search method to include project specific search.

        Extend to search by:
            security groups
            region
            resource size


        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the ClinvGenericResource searches
        if super().search(search_string):
            return True

        # Search by security groups
        if search_string in self.security_groups:
            return True

        # Search by region
        if re.match(search_string, self.region):
            return True

        # Search by type
        if re.match(search_string, self.type):
            return True

        return False


class EC2(ClinvAWSResource):
    """
    Abstract class to extend ClinvAWSResource, it gathers method and attributes
    for the EC2 resources.

    Public methods:
        search: Search in the resource data if a string matches.
        print: Prints information of the resource

    Public properties:
        name: Returns the name of the resource.
        security_groups: Returns the security groups of the resource.
        private_ips: Returns the private ips of the resource.
        public_ips: Returns the public ips of the resource.
        state: Returns the state of the resource.
        type: Returns the type of the resource.
        state_transition: Returns the reason of the transition of the resource.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def name(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        try:
            for tag in self.raw['Tags']:
                if tag['Key'] == 'Name':
                    return tag['Value']
        except KeyError:
            pass
        except TypeError:
            pass
        return 'none'

    @property
    def security_groups(self):
        """
        Do aggregation of data to return the security groups of the resource.

        Returns:
            list: Security groups of the resource.
        """

        try:
            return [security_group['GroupId']
                    for security_group in self.raw['SecurityGroups']
                    ]
        except KeyError:
            pass

    @property
    def private_ips(self):
        """
        Do aggregation of data to return the private ips of the resource.

        Returns:
            list: Private ips of the resource.
        """

        private_ips = []
        try:
            for interface in self.raw['NetworkInterfaces']:
                for address in interface['PrivateIpAddresses']:
                    private_ips.append(address['PrivateIpAddress'])
        except KeyError:
            pass
        return private_ips

    @property
    def public_ips(self):
        """
        Do aggregation of data to return the public ips of the resource.

        Returns:
            list: Private ips of the resource.
        """

        public_ips = []
        try:
            for interface in self.raw['NetworkInterfaces']:
                for association in interface['PrivateIpAddresses']:
                    public_ips.append(association['Association']['PublicIp'])
        except KeyError:
            pass
        return public_ips

    @property
    def state(self):
        """
        Overrides the parent method to do aggregation of data to return the
        state of the resource.

        Returns:
            str: State of the resource.
        """

        try:
            return self.raw['State']['Name']
        except KeyError:
            pass

    @property
    def type(self):
        """
        Do aggregation of data to return the resource type.

        Returns:
            str: Resource type.
        """

        return self._get_field('InstanceType', 'str')

    @property
    def state_transition(self):
        """
        Do aggregation of data to return the reason of the state transition of
        the resource.

        Returns:
            str: State transition of the resource.
        """
        return self._get_field('StateTransitionReason', 'str')

    def print(self):
        """
        Do aggregation of data to print information of the resource.

        It's more verbose than short_print but less than describe.

        Returns:
            stdout: Prints information of the resource.
        """

        print('- Name: {}'.format(self.name))
        print('  ID: {}'.format(self.id))
        print('  State: {}'.format(self.state))
        if self.state != 'running':
            print('  State Reason: {}'.format(self.state_transition))
        print('  Type: {}'.format(self.type))
        print('  SecurityGroups: {}'.format(self.security_groups))
        print('  PrivateIP: {}'.format(self.private_ips))
        print('  PublicIP: {}'.format(self.public_ips))

    def search(self, search_string):
        """
        Extend the parent search method to include project specific search.

        Extend to search by:
            Public Ips
            Private Ips

        Parameters:
            search_string (str): Regular expression to match with the
                resource data.

        Returns:
            bool: If the search_string matches resource data.
        """

        # Perform the ClinvAWSResource searches
        if super().search(search_string):
            return True

        # Search by public IP
        if search_string in self.public_ips:
            return True

        # Search by private IP
        if search_string in self.private_ips:
            return True

        return False


class RDS(ClinvAWSResource):
    """
    Abstract class to extend ClinvAWSResource, it gathers method and attributes
    for the RDS resources.

    Public properties:
        name: Returns the name of the resource.
        security_groups: Returns the security groups of the resource.
        type: Returns the type of the resource.
        state: Returns the state of the resource.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)

    @property
    def name(self):
        """
        Overrides the parent method to do aggregation of data to return the
        name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self._get_field('DBInstanceIdentifier', 'str')

    @property
    def state(self):
        """
        Overrides the parent method to do aggregation of data to return the
        state of the resource.

        Returns:
            str: State of the resource.
        """

        return self._get_field('DBInstanceStatus', 'str')

    @property
    def security_groups(self):
        """
        Do aggregation of data to return the security groups of the resource.

        Returns:
            list: Security groups of the resource.
        """

        return self._get_field('DBSecurityGroups', 'list')

    @property
    def type(self):
        """
        Do aggregation of data to return the resource type.

        Returns:
            str: Resource type.
        """

        return self._get_field('DBInstanceClass', 'str')
