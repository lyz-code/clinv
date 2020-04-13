# Report creation

If you want to see similar reports go to `clinv/reports/`.

## Create the report test class

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

## Create the report class

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

    def output(self, resource_id):
        """
        Method to print the report to stdout.

        Parameters:
            resource_id (str): regular expression of a resource id.

        Returns:
            stdout: Resource information
        """
```
