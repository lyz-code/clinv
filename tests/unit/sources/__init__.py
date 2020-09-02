from unittest.mock import patch, call
import shutil
import tempfile


class ClinvSourceBaseTestClass(object):
    """
    Abstract Base class to ensure that all the clinv sources have the same
    interface.

    Must be combined with a unittest.TestCase that defines:
        * self.source_obj: the name of the source class to test
        * self.module_name: the name of the module file
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.inventory_dir = self.tmp
        self.print_patch = patch(
            "clinv.sources.{}.print".format(self.module_name), autospect=True,
        )
        self.print = self.print_patch.start()

    def tearDown(self):
        self.print_patch.stop()
        shutil.rmtree(self.tmp)

    def test_source_data_attribute_is_initialized(self):
        self.src = self.source_obj()
        self.assertEqual(self.src.source_data, {})

    def test_user_data_attribute_is_initialized(self):
        self.src = self.source_obj()
        self.assertEqual(self.src.user_data, {})

    def test_source_data_can_be_initialized(self):
        desired_source_data = {"a": "b"}
        self.src = self.source_obj(source_data=desired_source_data)
        self.assertEqual(
            self.src.source_data, desired_source_data,
        )

    def test_user_data_can_be_initialized(self):
        desired_user_data = {"a": "b"}
        self.src = self.source_obj(user_data=desired_user_data)
        self.assertEqual(
            self.src.user_data, desired_user_data,
        )

    def test_id_property_works_as_expected(self):
        self.assertEqual(type(self.src.id), str)

    def test_prune_dictionary_removes_keys(self):
        dictionary = {"a": "b", "c": "d"}
        self.assertEqual(self.src.prune_dictionary(dictionary, "a"), {"c": "d"})

    def test_prune_dictionary_doesnt_fail_if_key_doesnt_exist(self):
        dictionary = {"a": "b", "c": "d"}
        self.assertEqual(self.src.prune_dictionary(dictionary, "f"), dictionary)


class ClinvGenericResourceTests(object):
    """
    Must be combined with a unittest.TestCase that defines:
        * self.resource as a ClinvGenericResource subclass instance
        * self.raw as a dictionary with the data of the resource
        * self.id as a string with the resource id
        * self.module_name: the name of the module file
    """

    def setUp(self):
        # This print mock is for testing the methods of the children of
        # this class
        self.print_patch = patch(
            "clinv.sources.{}.print".format(self.module_name), autospect=True,
        )
        self.print = self.print_patch.start()

        # This print mock is for testing the methods of this class
        self.init_print_patch = patch(
            "clinv.sources.print".format(self.module_name), autospect=True,
        )
        self.init_print = self.init_print_patch.start()

    def tearDown(self):
        self.print_patch.stop()
        self.init_print_patch.stop()

    def test_raw_attribute_is_created(self):
        self.assertEqual(self.resource.raw, self.raw[self.id])

    def test_get_field_returns_expected_value(self):
        self.assertEqual(
            self.resource._get_field("description"), self.raw[self.id]["description"]
        )

    def test_get_field_returns_missing_key(self):
        with self.assertRaisesRegex(
            KeyError, "{} doesn't have the unexistent key defined".format(self.id),
        ):
            self.resource._get_field("unexistent")

    def test_get_field_raises_error_if_key_is_None(self):
        self.resource.raw["key_is_none"] = None
        with self.assertRaisesRegex(
            ValueError,
            "{} key_is_none key is set to None, ".format(self.id)
            + "please assign it a defined value",
        ):
            self.resource._get_field("key_is_none")

    def test_get_field_returns_list_when_asked_even_if_value_is_str(self):
        self.resource.raw["key"] = "value"
        self.assertEqual(self.resource._get_field("key", "list"), ["value"])

    def test_get_optional_field_returns_list_when_asked_even_if_value_is_str(self):
        self.resource.raw["key"] = "value"
        self.assertEqual(self.resource._get_optional_field("key", "list"), ["value"])

    def test_get_optional_field_returns_list_when_asked_even_if_value_is_none(self):
        self.resource.raw["key"] = None
        self.assertEqual(self.resource._get_optional_field("key", "list"), [])

    def test_get_field_returns_str_when_asked_even_if_value_is_list(self):
        self.resource.raw["key"] = ["value1", "value2"]
        self.assertEqual(self.resource._get_field("key", "str"), "value1, value2")

    def test_get_optional_field_returns_str_when_asked_even_if_value_is_list(self):
        self.resource.raw["key"] = ["value1", "value2"]
        self.assertEqual(
            self.resource._get_optional_field("key", "str"), "value1, value2"
        )

    def test_get_optional_field_returns_expected_value(self):
        self.assertEqual(
            self.resource._get_optional_field("description"),
            self.raw[self.id]["description"],
        )

    def test_get_optional_field_returns_none_on_missing_key(self):
        self.assertEqual(self.resource._get_optional_field("unexistent"), None)

    def test_id_property_works_as_expected(self):
        self.assertEqual(self.resource.id, self.id)

    def test_description_property_works_as_expected(self):
        self.assertEqual(self.resource.description, self.raw[self.id]["description"])

    def test_name_property_works_as_expected(self):
        self.assertEqual(self.resource.name, "resource_name")

    def test_search_resource_by_regexp_on_name(self):
        self.assertTrue(self.resource.search(".*name"))

    def test_search_resource_by_id(self):
        self.assertTrue(self.resource.search(self.id))

    def test_search_resource_by_description(self):
        self.assertTrue(self.resource.search(".*the description.*"))

    def test_get_resource_state(self):
        self.assertEqual(self.resource.state, "active")

    def test_short_print_resource_information(self):

        self.resource.short_print()
        print_calls = (call("{}: {}".format(self.resource.id, self.resource.name)),)

        for print_call in print_calls:
            self.assertIn(print_call, self.init_print.mock_calls)
        self.assertEqual(1, len(self.init_print.mock_calls))

    def test_print_resource_information(self):
        self.resource.print()
        print_calls = (
            call(self.resource.id),
            call("  Name: {}".format(self.resource.name)),
            call("  State: {}".format(self.resource.state)),
            call("  Description: {}".format(self.resource.description)),
        )

        for print_call in print_calls:
            self.assertIn(print_call, self.init_print.mock_calls)
        self.assertEqual(4, len(self.init_print.mock_calls))

    def test_match_list_detects_regular_expression(self):
        self.assertTrue(self.resource._match_list("a.c", ["abcd", "1"]))

    def test_match_list_is_case_insensitive(self):
        self.assertTrue(self.resource._match_list("a.c", ["AbCd", "1"]))

    def test_match_list_returns_false_if_no_match(self):
        self.assertFalse(self.resource._match_list("a.c", ["0", "1"]))

    def test_match_dict_detects_regular_expression_in_key(self):
        self.assertTrue(self.resource._match_dict("a.c", {"abcd": "1"}))

    def test_match_dict_is_case_insensitive_in_key(self):
        self.assertTrue(self.resource._match_dict("a.c", {"AbCd": "1"}))

    def test_match_dict_detects_regular_expression_in_value(self):
        self.assertTrue(self.resource._match_dict("a.c", {"1": "abcd"}))

    def test_match_dict_is_case_insensitive_in_value(self):
        self.assertTrue(self.resource._match_dict("a.c", {"1": "AbCd"}))

    def test_match_dict_returns_false_if_no_match_in_key_and_value(self):
        self.assertFalse(self.resource._match_dict("a.c", {"0": "1"}))
