# Source and Resource creation

## Create a new source

A source is an abstraction from where we obtain resources and index them into
our inventory.

For the purpose of this section, we'll assume that the new source we want to add
to our inventory is called `newsource`.

If you want to see similar sources go to `clinv/sources/`.

### Desired Interface

To ensure the expected behavior of the sources, the class must follow a common
interface. Don't worry if you don't understand yet what does each element mean,
you'll discover it as you read the hole document.

It must have the following attributes:

* id (str): ID of the resource.
* source_data (dict): Aggregated source supplied data.
* user_data (dict): Aggregated user supplied data.

And the following public methods:

* generate_source_data: Generates the source_data attribute and returns it.
* generate_user_data: Generates the user_data attribute and returns it.
* generate_inventory: Generates the inventory dictionary with the source
    resource.

### Create the source test class

On `test/sources/` create your source class from this template. Substitute
`{{ class_name }}` with your value.

Also fill up the `self.desired_source_data` and `self.desired_user_data` with
a representative template of the data you want to store into the inventory.

```python
from clinv.sources import {{ class_name }}src
from tests.sources import ClinvSourceBaseTestClass
import unittest

class Test{{ class_name }}Source(ClinvSourceBaseTestClass, unittest.TestCase):
    '''
    Test the {{ class_name }} implementation in the inventory.
    '''

    def setUp(self):
        super().setUp()
        self.source_obj = {{ class_name }}src

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

        # What data we want to aggregate to our inventory
        self.desired_source_data = {
        }
        self.desired_user_data = {
        }

        self.src.source_data = self.desired_source_data

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        # Mock here the call to your provider

        self.src.source_data = {}

        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data,
            self.desired_source_data,
        )
        self.assertEqual(
            generated_source_data,
            self.desired_source_data,
        )

    @unittest.skip('Not yet')
    def test_generate_user_data_creates_expected_user_data_attrib(self):
        generated_user_data = self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data,
            self.desired_user_data,
        )
        self.assertEqual(
            generated_user_data,
            self.desired_user_data,
        )

    @unittest.skip('Not yet')
    def test_generate_user_data_doesnt_loose_existing_data(self):
        user_key = [key for key in self.desired_user_data.keys()][0]
        desired_user_data = {user_key: {}}
        self.src.user_data = desired_user_data

        self.src.generate_user_data()

        self.assertEqual(
            self.src.user_data,
            desired_user_data,
        )

    @unittest.skip('Not yet')
    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.source_data = {}
        self.assertEqual(self.src.generate_inventory(), {})

    @unittest.skip('Not yet')
    @patch('clinv.sources.{{ module_name }}.{{ class_name }}')
    def test_generate_inventory_creates_expected_dictionary(
        self,
        resource_mock
    ):
        resource_id = '{{ resource_id }}'
        self.src.user_data = self.desired_user_data

        desired_mock_input = {
            **self.src.user_data[resource_id],
            **self.src.source_data[resource_id],
        }

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            resource_mock.assert_called_with(
                {
                    resource_id: desired_mock_input
                },
            ),
            None,
        )

        self.assertEqual(
            desired_inventory,
            {
                resource_id: resource_mock.return_value
            },
        )
```

### Create the source class

On `clinv/sources/` create your source class from this template. Substitute
`{{ class_name }}` and `{{ class_id }}` with your values.

```python
from clinv.sources import ClinvSourcesrc, ClinvGenericResource


class {{ class_name }}src(ClinvSourcesrc):
    """
    Class to gather and manipulate the {{ class_name }} resources.

    Parameters:
        source_data (dict): {{ class_name }}src compatible source_data
        dictionary.
        user_data (dict): {{ class_name }}src compatible user_data dictionary.

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
        self.id = '{{ class_id }}'

    def generate_source_data(self):
        """
        Do aggregation of the source data to generate the source dictionary
        into self.source_data, with the following structure:
            {
            }

        Returns:
            dict: content of self.source_data.
        """

        self.log.info('Fetching {{ class_name }} inventory')
        self.source_data = {}

        return self.source_data

    def generate_user_data(self):
        """
        Do aggregation of the user data to populate the self.user_data
        attribute with the user_data.yaml information or with default values.

        It needs the information of self.source_data, therefore it should be
        called after generate_source_data.

        Returns:
            dict: content of self.user_data.
        """

        return self.user_data

    def generate_inventory(self):
        """
        Do aggregation of the user and source data to populate the self.inv
        attribute with {{ class_name }} resources.

        It needs the information of self.source_data and self.user_data,
        therefore it should be called after generate_source_data and
        generate_user_data.

        Returns:
            dict: {{ class_name }} inventory with user and source data
        """

        inventory = {}

        for resource_id, resource in self.source_data.items():
            # Load the user_data into the source_data record
            for key, value in self.user_data[resource_id].items():
                resource[key] = value

            inventory[resource_id] = {{ class_name }}({resource_id: resource})

        return inventory
```

If you need to clean the dictionary created by your provider, use the
`self.prune_dictionary` method.

#### Create the generate_source_data method

This method is meant to extract the information from your source, for example
AWS and save it into the `self.source_data`, as well as return it.


#### Create the generate_user_data method

This method is meant to extract the information from the user, so it takes the
resources saved on `self.source_data` and generates the basic template for each
one and saves them into `self.user_data`.

#### Create the generate_inventory method

This method is meant to initiate the resource object of the source we're adding.
This object doesn't exist yet, but we'll do that later.

After initializing all the objects they are returned.

#### Add your source to the loaded sources

Import it in `clinv/inventory.py` and add it into the `active_source_plugins`
variable

### Create the resource class

On `clinv/sources/` create your source class from this template. Substitute
`{{ class_name }}` and `{{ class_id }}` with your values.

```python
class {{ class_name }}(ClinvGenericResource):
    """
    Class to extend the ClinvGenericResource abstract class. It gathers methods
    and attributes for the {{ class_name }} resources.

    Public methods:
        print: Prints information of the resource.

    Public properties:
        name: Returns the name of the record.
    """

    def __init__(self, raw_data):
        """
        Execute the __init__ of the parent class ClinvActiveResource.
        """

        super().__init__(raw_data)
```

### Create the resource test class

```python
class Test{{ class_name }}(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        self.module_name = '{{ module_name }}'
        self.id = '{{ class_id }}'

        super().setUp()

        self.raw = {
            # Example of the dictionary to initialize the object.
        }
        self.resource = {{ class_name }}(self.raw)

    def tearDown(self):
        super().tearDown()
```

Think if you can add more search filters in the object `search` method.

### Add resource to the reports

There are some reports that are generic, such as `list` or `print`, but there
are some that still aren't.

So you'll need to manually add your resource to `export` and `unassigned`.

### Add resource to the cli

For the reports that aren't generic add them in `clinv/cli.py`.

### Test that everything works

Execute the following tasks

* Generate the new inventory `clinv generate`.
* Edit the `use_data.yml`.
* Regenerate the inventory and check that no information is lost.
* Check the different reports.

### Add documentation

Complete the README.md and History.md
