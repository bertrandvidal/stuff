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

    def test_eviction_on_add_value(self):
        nb_items = 3
        lru = LeastRecentlyUsedCache(nb_items)
        [lru.add(x, x ** 2) for x in range(5)]
        self.assertIsNone(lru.get(1))
        self.assertEqual(list(reversed(range(5)))[:-2], lru._keys)
        self.assertEqual({x: x ** 2 for x in list(reversed(range(5)))[:-2]}, lru._storage)

    def test_callback_called_for_non_cached_values(self):
        nb_calls = 0

        def square(key):
            nonlocal nb_calls
            nb_calls += 1
            return key ** 2

        lru = LeastRecentlyUsedCache(callback=square)
        value = lru.get(2)
        self.assertEqual(value, 4)
        self.assertEqual(nb_calls, 1)
        value = lru.get(2)
        self.assertEqual(value, 4)
        self.assertEqual(nb_calls, 1)
