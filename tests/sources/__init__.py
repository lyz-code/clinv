from unittest.mock import patch
import shutil
import tempfile


class ClinvSourceBaseTestClass(object):
    '''
    Abstract Base class to ensure that all the clinv sources have the same
    interface.

    Must be combined with a unittest.TestCase that defines:
        * self.class_obj the name of the source class to test
    '''

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.inventory_dir = self.tmp
        self.boto_patch = patch('clinv.sources.aws.boto3', autospect=True)
        self.boto = self.boto_patch.start()
        self.logging_patch = patch('clinv.sources.logging', autospect=True)
        self.logging = self.logging_patch.start()
        self.print_patch = patch('clinv.sources.aws.print', autospect=True)
        self.print = self.print_patch.start()

    def tearDown(self):
        self.boto_patch.stop()
        self.logging_patch.stop()
        self.print_patch.stop()
        shutil.rmtree(self.tmp)

    def test_source_data_attribute_is_initialized(self):
        self.src = self.class_obj()
        self.assertEqual(self.src.source_data, {})

    def test_user_data_attribute_is_initialized(self):
        self.src = self.class_obj()
        self.assertEqual(self.src.user_data, {})

    def test_source_data_can_be_initialized(self):
        desired_source_data = {'a': 'b'}
        self.src = self.class_obj(source_data=desired_source_data)
        self.assertEqual(
            self.src.source_data,
            desired_source_data,
        )

    def test_user_data_can_be_initialized(self):
        desired_user_data = {'a': 'b'}
        self.src = self.class_obj(user_data=desired_user_data)
        self.assertEqual(
            self.src.user_data,
            desired_user_data,
        )

    def test_id_property_works_as_expected(self):
        self.assertEqual(type(self.src.id), str)
