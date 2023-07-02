import unittest

from replay import get_thermostat_attribute, get_thermostat_data


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


if __name__ == '__main__':
    unittest.main()
