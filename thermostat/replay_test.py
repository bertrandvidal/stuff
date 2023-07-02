import datetime
import os
import unittest
from zipfile import ZipFile

from replay import get_thermostat_attribute, get_thermostat_data, get_file_path, get_attribute_from_file


class MyTestCase(unittest.TestCase):

    def test_get_thermostat_attribute_has_attribute(self):
        thermostat_data = {"attr-1": 12}
        self.assertEqual(get_thermostat_attribute(thermostat_data, "attr-1"), 12)

    def test_get_thermostat_attribute_no_attribute(self):
        thermostat_data = {"attr-1": 12}
        self.assertEqual(get_thermostat_attribute(thermostat_data, "not-attr-1"), None)

    def test_get_thermostat_data_line_count(self):
        self.assertEqual(len(list(get_thermostat_data("thermostat-data.jsonl"))), 1068)

    def test_get_thermostat_data_jsonl_data(self):
        iterator = get_thermostat_data("thermostat-data.jsonl")
        first_element = next(iterator)
        self.assertDictEqual(first_element, {"updateTime": "2016-01-01T00:43:00.001064", "update": {"ambientTemp": 80}})
        last_element = list(iterator)[-1]
        self.assertDictEqual(last_element, {"updateTime": "2016-12-31T05:09:00.020215",
                                            "update": {"lastAlertTs": "2016-12-31T05:09:00.020215"}})

    def test_get_file_path_unzipped(self):
        self.assertEqual(get_file_path(__file__), __file__)

    def test_get_file_path_zipped(self):
        try:
            with ZipFile("test.zip", "w") as test_zip:
                test_zip.write(os.path.basename(__file__))
            path = get_file_path("test.zip")
            self.assertEqual(path, os.path.basename(__file__))
        finally:
            if os.path.exists("test.zip"):
                os.unlink("test.zip")

    def test_get_attribute_from_file_timestamp_before_file(self):
        before_file = datetime.datetime.fromisoformat("2016-01-01T00:43:00.001064") - datetime.timedelta(seconds=1)
        self.assertIsNone(get_attribute_from_file("thermostat-data.jsonl", "ambientTemp", before_file))

    def test_get_attribute_from_file_timestamp_after_file(self):
        after_file = datetime.datetime.fromisoformat("2016-01-01T00:43:00.001064") + datetime.timedelta(days=365)
        self.assertEqual(get_attribute_from_file("thermostat-data.jsonl", "ambientTemp", after_file), 84)

    def test_get_attribute_from_file_exact_timestamp(self):
        self.assertEqual(get_attribute_from_file("thermostat-data.jsonl", "ambientTemp",
                                                 datetime.datetime.fromisoformat("2016-02-27T06:16:00.057915")), 72)

    def test_get_attribute_from_file_after_timestamp(self):
        search_timestamp = datetime.datetime.fromisoformat("2016-02-27T06:16:00.057915") + datetime.timedelta(minutes=1)
        self.assertEqual(get_attribute_from_file("thermostat-data.jsonl", "ambientTemp",
                                                 search_timestamp), 72)

    def test_get_attribute_from_file_timestamp_non_such_attribute(self):
        self.assertIsNone(get_attribute_from_file("thermostat-data.jsonl", "not-an-attribute", datetime.datetime.now()))


if __name__ == '__main__':
    unittest.main()
