"""
Module to store the Clinv sources abstract class.

Classes:
    ClinvSourcesrc: Class to gather the common methods for the Clinv sources.
    ClinvGenericResource: Abstract class to gather common method and attributes
        for all Clinv resources.
"""

import logging
import re


class ClinvSourcesrc:
    """
    Class to gather the common methods for the Clinv sources.

    Public attributes:
        source_data (dict): Aggregated source supplied data.
        user_data (dict): Aggregated user supplied data.
        log (logging object):

    Public methods:
        prune_dictionary: Remove keys from a dictionary.
    """

    def __init__(self, source_data={}, user_data={}):
        self.source_data = source_data
        self.user_data = user_data
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

    def prune_dictionary(self, dictionary, prune_keys):
        """
        Remove keys from a dictionary.

        Parameters:
            dictionary (dict): Dictionary to modify.
            prune_keys (list): List of keys to prune.

        Returns:
            dict: dictionary without the keys specified in prune_keys.
        """
        for prune_key in prune_keys:
            try:
                dictionary.pop(prune_key)
            except KeyError:
                pass
        return dictionary


class ClinvGenericResource:
    """
    Abstract class to gather common method and attributes for all Clinv
    resources.

    Public methods:
        print: Prints information of the resource
        search: Search in the resource data if a string matches.
        short_print: Print the id and name of the resource.
        state: Returns the state of the resource.
        to_destroy: Returns if the resource must be destroyed.

    Internal methods:
        _get_field: Do aggregation of data to return the value of the
            self.raw[key].
        _get_optional_field: Similar to _get_field, but it wont raise
            exceptions on inexistent keys or if the value is None.
        _match_dict: Check if regular expression matches the contents of a
            dictionary.
        _match_list: Check if regular expression matches the contents of a
            list.
        _transform_type: input_object on the desired output_type.

    Public properties:
        description: Returns the description of the resource.
        name: Returns the name of the resource.

    Public Attributes:
        id: Stores the id of the resource.
        raw: Stores the raw_data dictionary information
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

        if output_type == "list":
            if isinstance(input_object, str):
                return [input_object]
        elif output_type == "str":
            if isinstance(input_object, list):
                return ", ".join(input_object)
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
                    "{} {} key is set to None, ".format(self.id, key)
                    + "please assign it a defined value",
                )
        except KeyError:
            raise KeyError("{} doesn't have the {} key defined".format(self.id, key))

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

        if output_type == "list":
            if isinstance(value, str):
                return [value]
            if value is None:
                return []
        elif output_type == "str":
            if isinstance(value, list):
                return ", ".join(value)

        return value

    def _match_list(self, search_term, list_to_search):
        """
        Check if regular expression matches the contents of a list.

        Parameters:
            search_term (str): Regular expression to search.
            list_to_search (list): List to perform the list

        Returns:
            bool: If it matches.
        """

        for element in list_to_search:
            if re.match(search_term, element, re.IGNORECASE):
                return True
        return False

    def _match_dict(self, search_term, dict_to_search):
        """
        Check if regular expression matches the contents of a dictionary.

        Parameters:
            search_term (str): Regular expression to search.
            dict_to_search (dict): List to perform the dictionary.

        Returns:
            bool: If it matches.
        """

        for key, value in dict_to_search.items():
            if re.match(search_term, key, re.IGNORECASE):
                return True
            if re.match(search_term, value, re.IGNORECASE):
                return True
        return False

    @property
    def description(self):
        """
        Do aggregation of data to return the description of the resource.

        Returns:
            str: Description of the resource.
        """

        return self._get_field("description", "str")

    @property
    def name(self):
        """
        Do aggregation of data to return the name of the resource.

        Returns:
            str: Name of the resource.
        """

        return self._get_field("name", "str")

    @property
    def state(self):
        """
        Do aggregation of data to return the state of the resource.

        Returns:
            str: State of the resource.
        """

        return self._get_field("state", "str")

    @property
    def to_destroy(self):
        """
        Overrides the parent method to do aggregation of data to return the
        if we want to destroy the resource.

        Returns:
            str: If we want to destroy the resource
        """

        return self._get_field("to_destroy", "str")

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
        if self.name is not None and re.match(search_string, self.name, re.IGNORECASE):
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

        print("{}: {}".format(self.id, self.name))

    def print(self):
        """
        Do aggregation of data to print information of the resource.

        It's more verbose than short_print but less than describe.

        Returns:
            stdout: Prints information of the resource.
        """

        print(self.id)
        print("  Name: {}".format(self.name))
        print("  State: {}".format(self.state))
        print("  Description: {}".format(self.description))
