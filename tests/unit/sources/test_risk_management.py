from . import ClinvSourceBaseTestClass, ClinvGenericResourceTests
from clinv.sources import risk_management
from unittest.mock import patch, call

import unittest


class RiskManagementSourceBaseTestClass(ClinvSourceBaseTestClass):
    """
    Abstract Base class to ensure that all the RiskManagement sources have the
    same interface.

    Must be combined with a unittest.TestCase that defines:
        * self.module_name: the name of the module file.
        * self.source_obj: the name of the source class to test.
        * self.resource_obj: the name of the resource class to test.
        * self.resource_id: the id of the resource class to test.
        * self.resource_type: the type of the resource class to test.
    """

    def setUp(self):
        self.module_name = "risk_management"
        super().setUp()
        self.resource_patch = patch(
            "clinv.sources.risk_management.{}".format(self.resource_obj),
            autospect=True,
        )
        self.resource = self.resource_patch.start()

        # Initialize object to test
        source_data = {}
        user_data = {}
        self.src = self.source_obj(source_data, user_data)

    def tearDown(self):
        super().tearDown()
        self.resource_patch.stop()

    def test_generate_source_data_creates_expected_source_data_attrib(self):
        expected_source_data = {}

        generated_source_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.source_data, expected_source_data,
        )
        self.assertEqual(
            generated_source_data, expected_source_data,
        )

    def test_generate_user_data_creates_expected_user_data_attrib(self):
        expected_user_data = {}

        generated_user_data = self.src.generate_source_data()

        self.assertEqual(
            self.src.user_data, expected_user_data,
        )
        self.assertEqual(
            generated_user_data, expected_user_data,
        )

    def test_generate_inventory_return_empty_dict_if_no_data(self):
        self.src.user_data = {}
        self.assertEqual(self.src.generate_inventory(), {})

    def test_generate_inventory_creates_resource_objects(self):
        self.src.user_data = {self.resource_id: "tbd"}

        desired_mock_input = "tbd"

        desired_inventory = self.src.generate_inventory()
        self.assertEqual(
            self.resource.assert_called_with({self.resource_id: desired_mock_input},),
            None,
        )

        self.assertEqual(
            desired_inventory, {self.resource_id: self.resource.return_value},
        )


class TestProjectSource(RiskManagementSourceBaseTestClass, unittest.TestCase):
    """
    Test the Project implementation in the inventory.
    """

    def setUp(self):
        self.source_obj = risk_management.Projectsrc
        self.resource_obj = "Project"
        self.resource_id = "pro_01"
        self.resource_type = "projects"
        super().setUp()

    def tearDown(self):
        super().tearDown()


class TestServiceSource(RiskManagementSourceBaseTestClass, unittest.TestCase):
    """
    Test the Service implementation in the inventory.
    """

    def setUp(self):
        self.source_obj = risk_management.Servicesrc
        self.resource_obj = "Service"
        self.resource_id = "ser_01"
        self.resource_type = "services"
        super().setUp()

    def tearDown(self):
        super().tearDown()


class TestInformationSource(
    RiskManagementSourceBaseTestClass, unittest.TestCase,
):
    """
    Test the Information implementation in the inventory.
    """

    def setUp(self):
        self.source_obj = risk_management.Informationsrc
        self.resource_obj = "Information"
        self.resource_id = "inf_01"
        self.resource_type = "informations"
        super().setUp()

    def tearDown(self):
        super().tearDown()


class TestPeopleSource(RiskManagementSourceBaseTestClass, unittest.TestCase):
    """
    Test the People implementation in the inventory.
    """

    def setUp(self):
        self.source_obj = risk_management.Peoplesrc
        self.resource_obj = "People"
        self.resource_id = "peo_01"
        self.resource_type = "people"
        super().setUp()

    def tearDown(self):
        super().tearDown()


class ClinvActiveResourceTests(ClinvGenericResourceTests):
    """Must be combined with a unittest.TestCase that defines:
    * self.resource as a ClinvActiveResource subclass instance
    * self.raw as a dictionary with the data of the resource
    * self.id as a string with the resource id"""

    def setUp(self):
        self.module_name = "risk_management"
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_get_instance_responsible(self):
        self.assertEqual(self.resource.responsible, "responsible@clinv.com")


class TestProject(ClinvActiveResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = "pro_01"
        self.raw = {
            "pro_01": {
                "aliases": "Awesome Project",
                "description": "This is the description",
                "informations": ["inf_01",],
                "links": {"homepage": "www.homepage.com"},
                "responsible": "responsible@clinv.com",
                "members": {
                    "developers": ["developer_1",],
                    "devops": ["devops_1"],
                    "po": "product owner",
                    "stakeholders": ["stakeholder_1"],
                    "ux": None,
                    "qa": None,
                },
                "people": ["peo_01",],
                "name": "resource_name",
                "services": ["ser_01"],
                "state": "active",
            }
        }

        self.resource = risk_management.Project(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_services(self):
        self.assertEqual(self.resource.services, ["ser_01"])

    def test_get_informations(self):
        self.assertEqual(self.resource.informations, ["inf_01"])

    def test_get_aliases(self):
        self.assertEqual(self.resource.aliases, ["Awesome Project"])

    def test_search_by_aliases(self):
        self.assertTrue(self.resource.search("Awesome Project"))

    def test_search_by_aliases_doesn_not_work_if_alias_is_none(self):
        self.resource.raw["aliases"] = None
        self.assertFalse(self.resource.search("Awesome Project"))

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("pro_01"),
            call("  Name: resource_name"),
            call("  Aliases: Awesome Project"),
            call("  Description: This is the description"),
            call("  State: active"),
            call("  Services: ser_01"),
            call("  Informations: inf_01"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(7, len(self.print.mock_calls))


class TestInformation(ClinvActiveResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = "inf_01"
        self.raw = {
            "inf_01": {
                "description": "This is the description",
                "name": "resource_name",
                "personal_data": True,
                "responsible": "responsible@clinv.com",
                "state": "active",
            }
        }

        self.resource = risk_management.Information(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_personal_data(self):
        self.assertEqual(self.resource.personal_data, True)

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("inf_01"),
            call("  Name: resource_name"),
            call("  Description: This is the description"),
            call("  State: active"),
            call("  Personal Information: True"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(5, len(self.print.mock_calls))


class TestService(ClinvActiveResourceTests, unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.id = "ser_01"
        self.raw = {
            "ser_01": {
                "access": "public",
                "authentication": {"2fa": True, "method": "Oauth2"},
                "aws": {"ec2": ["i-01"],},
                "description": "This is the description",
                "dependencies": ["ser_02"],
                "endpoints": ["https://endpoint1.com"],
                "informations": ["inf_01",],
                "links": {
                    "docs": {
                        "internal": "https://internaldocs",
                        "external": "https://internaldocs",
                    },
                },
                "name": "resource_name",
                "responsible": "responsible@clinv.com",
                "state": "active",
            }
        }

        self.resource = risk_management.Service(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_access(self):
        self.assertEqual(self.resource.access, "public")

    def test_get_informations(self):
        self.assertEqual(self.resource.informations, ["inf_01"])

    def test_get_aws(self):
        self.assertEqual(self.resource.aws, {"ec2": ["i-01"]})

    def test_get_dependencies(self):
        self.assertEqual(self.resource.dependencies, ["ser_02"])

    def test_search_matches_aws_resources(self):
        self.assertTrue(self.resource.search("i-01"))

    def test_search_matches_service_dependencies(self):
        self.assertTrue(self.resource.search("ser_02"))

    def test_search_works_without_defined_dependencies(self):
        self.resource.raw.pop("dependencies")
        self.assertFalse(self.resource.search("ser_02"))

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("ser_01"),
            call("  Name: resource_name"),
            call("  Description: This is the description"),
            call("  State: active"),
            call("  Access: public"),
            call("  Informations: inf_01"),
            call("  Related resources:"),
            call("    ec2:"),
            call("      i-01"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(9, len(self.print.mock_calls))


class TestPeople(ClinvGenericResourceTests, unittest.TestCase):
    def setUp(self):
        self.module_name = "risk_management"
        super().setUp()

        self.id = "peo_01"
        self.raw = {
            "peo_01": {
                "description": "This is the description",
                "name": "resource_name",
                "state": "active",
                "email": "user@email.org",
                "iam_user": "iamuser_user1",
            }
        }

        self.resource = risk_management.People(self.raw)

    def tearDown(self):
        super().tearDown()

    def test_get_iam_user(self):
        self.assertEqual(self.resource.iam_user, "iamuser_user1")

    def test_get_email(self):
        self.assertEqual(self.resource.email, "user@email.org")

    def test_search_by_email(self):
        self.assertTrue(self.resource.search(".*@email.org"))

    def test_search_by_iam_user(self):
        self.assertTrue(self.resource.search("iamuser.*"))

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call("peo_01"),
            call("  Name: resource_name"),
            call("  Description: This is the description"),
            call("  Email: user@email.org"),
            call("  State: active"),
            call("  IAM User: iamuser_user1"),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.print.mock_calls)
        self.assertEqual(6, len(self.print.mock_calls))
