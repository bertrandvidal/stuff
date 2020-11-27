from unittest import TestCase

from lru import LeastRecentlyUsedCache


class TestLeastRecentlyUsedCache(TestCase):

    def test_default_capacity(self):
        lru = LeastRecentlyUsedCache()
        self.assertIsNotNone(lru.get_capacity())

    def test_constructor_capacity(self):
        capacity = 12
        lru = LeastRecentlyUsedCache(capacity)
        self.assertEqual(lru.get_capacity(), capacity)

    def test_retrieve_value(self):
        key = "some-test-value"
        value = "some-test-value"
        lru = LeastRecentlyUsedCache()
        lru.add(key, value)
        self.assertEqual(value, lru.get(key))
