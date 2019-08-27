# Hacking

This program is developed with
[TDD](https://en.wikipedia.org/wiki/Test-driven_development), so if you want to
add code, you would most likely should add tests. If you don't know how, say so
in the pull request and we'll try to help you.

All classes, methods and modules are meant to have docstrings, so please add
them.

## Create a new source

For the purpose of this section, we'll assume that the new source we want to add
to our inventory is called `newsource`.

If you want to see similar sources go to `clinv/sources/`.

### Desired Interface

To ensure the expected behavior of the sources, the class must follow a common
interface. Don't worry if you don't understand yet what does each element mean,
you'll discover it as you read the hole doc.

Must have the following attributes:

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
        self.class_obj = {{ class_name }}src

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.class_obj(source_data, user_data)

    def tearDown(self):
        super().tearDown()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        expected_source_data = {}

        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data,
            expected_source_data,
        )
        self.assertEqual(
            generated_source_data,
            expected_source_data,
        )

    def test_generate_user_data_creates_expected_user_data_attrib(self):
        expected_user_data = {}

        generated_user_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.user_data,
            expected_user_data,
        )
        self.assertEqual(
            generated_user_data,
            expected_user_data,
        )
```

Import `{{ class_name}}src` on this file.

### Create the source class

On `clinv/sources/` create your source class from this template. Substitute
`{{ class_name }}` and `{{ class_id }}` with your values.

```python
from clinv.sources import ClinvSourcesrc


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

        self.user_data = {}

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

        return inventory
```

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

Import it in `clinv/clinv.py` and add it into the `active_source_plugins`
variable

## Create a new report

If you want to see similar reports go to `clinv/reports/`.

### Create the report test class

On `test/reports/` create your report class from this template. Substitute
`{{ class_name }}` (for example `PrintReport`) and `{{ module_path }}` (for
example `print`) with your values.

```python
from tests.reports import ClinvReportBaseTestClass
from clinv.reports.{{ module_path }} import {{ class_name }}
import unittest


class Test{{ class_name }}(ClinvReportBaseTestClass, unittest.TestCase):
    '''
    Test the {{ class_name }} implementation.
    '''

    def setUp(self):
        super().setUp()
        self.report = {{ class_name }}(self.inventory)

    def tearDown(self):
        super().tearDown()

    def test_output_method(self):
        self.report.output()
        self.assertTrue(False)
```

### Create the report class

On `clinv/sources/` create your source class from this template. Substitute
`{{ class_name }}` and `{{ class_id }}` with your values.

```python
"""
Module to store the {{ class_name }}.

Classes:
  {{ class_name }}: {{ class_description }}

"""

from clinv.reports import ClinvReport


class {{ class_name }}(ClinvReport):
    """
    {{ class_description }}

    Parameters:
        inventory (Inventory): Clinv inventory object.

    Public methods:
        output: Print the report to stdout.

    Public attributes:
        inv (Inventory): Clinv inventory.
    """

    def __init__(self, inventory):
        super().__init__(inventory)

    def output(self, regexp_id):
        """
        Method to print the report to stdout.

        Parameters:
            resource_id (str): regular expression of a resource id.

        Returns:
            stdout: Resource information
        """
```
