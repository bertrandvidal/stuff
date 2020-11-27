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

    def test_add_access_order(self):
        nb_items = 5
        lru = LeastRecentlyUsedCache(nb_items + 1)
        [lru.add(x, x ** 2) for x in range(nb_items)]
        self.assertEqual(nb_items, len(lru._keys))
        self.assertEqual(list(reversed(range(nb_items))), lru._keys)

    def test_get_access_order(self):
        nb_items = 5
        lru = LeastRecentlyUsedCache(nb_items + 1)
        [lru.add(x, x ** 2) for x in range(nb_items)]
        [lru.get(x) for x in reversed(range(nb_items))]
        self.assertEqual(nb_items, len(lru._keys))
        self.assertEqual(list(range(nb_items)), lru._keys)

    def test_get_unknown_key_preserve_order(self):
        nb_items = 5
        lru = LeastRecentlyUsedCache(nb_items + 1)
        [lru.add(x, x ** 2) for x in range(nb_items)]
        self.assertEqual(nb_items, len(lru._keys))
        self.assertEqual(list(reversed(range(nb_items))), lru._keys)
        lru.get(nb_items + 1)
        self.assertEqual(list(reversed(range(nb_items))), lru._keys)

    def test_returns_default_value(self):
        lru = LeastRecentlyUsedCache()
        default = "some-default"
        value = lru.get("non-existent-value", default)
        self.assertEqual(value, default)

    def test_returns_actual_value_despite_default_value(self):
        lru = LeastRecentlyUsedCache()
        key = "non-existent-value"
        actual_value = 12
        lru.add(key, actual_value)
        default = "some-default"
        value = lru.get(key, default)
        self.assertEqual(value, actual_value)

    def test_eviction_on_add_value(self):
        nb_items = 3
        lru = LeastRecentlyUsedCache(nb_items)
        [lru.add(x, x ** 2) for x in range(5)]
        default_value = "default-value"
        value = lru.get(1, default_value)
        self.assertEqual(value, default_value)
        self.assertEqual(list(reversed(range(5)))[:-2], lru._keys)
        self.assertEqual({x: x ** 2 for x in list(reversed(range(5)))[:-2]}, lru._storage)
