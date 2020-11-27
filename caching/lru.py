from typing import Any


class LeastRecentlyUsedCache:
    """
    Offers fix memory caching where least recently used entries are evicted.
    """
    _DEFAULT_CAPACITY = 10

    def __init__(self, capacity: int = _DEFAULT_CAPACITY):
        self._storage = {}
        self._capacity = capacity

    def get_capacity(self) -> Any:
        """

        :return: maximum number of key/value pairs the cache can hold before eviction takes place
        """
        return self._capacity

    def add(self, key: Any, value: Any) -> None:
        """ Stores the key/value pair.

        :param key: key under which the value will be stored
        :param value: value link to the given key
        :return: None
        """
        self._storage[key] = value

    def get(self, key: Any, default: Any = None) -> Any:
        """ Return the value stored for the given key or the provided default

        :param key: key associated to the value we are trying to retrieve
        :param default: value returned in case the given key isn't present in cache
        :return: value associated with key if any or the given default
        """
        return self._storage.get(key, default)
