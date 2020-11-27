from typing import Any, Callable


class LeastRecentlyUsedCache:
    """
    Offers fix memory caching where least recently used entries are evicted.
    """
    _DEFAULT_CAPACITY = 10

    def __init__(self, capacity: int = _DEFAULT_CAPACITY, callback: Callable = None):
        self._storage = {}
        self._callback = callback or self._storage.get
        self._capacity = capacity
        self._keys = []

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
        self._update_keys_access_order(key)
        self._evict_if_necessary()
        self._storage[key] = value

    def get(self, key: Any) -> Any:
        """ Return the value stored for the given key or the provided default

        :param key: key associated to the value we are trying to retrieve
        :return: value associated with key if any or the given default
        """
        if key in self._storage:
            self._update_keys_access_order(key)
            return self._storage.get(key)
        value = self._callback(key)
        if value:
            self._storage[key] = value
            self._evict_if_necessary()
        return value

    def _update_keys_access_order(self, key) -> None:
        """ Keep the list of keys in accessed order """
        try:
            # we remove the key from the "spot" it was last access so it can be put
            # at the head of the list
            self._keys.remove(key)
        except ValueError:
            # key is new so their is nothing to do
            pass
        # always add 'key' at the head of the list since it's the last item that was accessed
        self._keys.insert(0, key)

    def _evict_if_necessary(self):
        """ Ensure we do not store more value than 'capacity' """
        keys_length = len(self._keys)
        if keys_length > self._capacity:
            evicted = self._keys.pop(keys_length - 1)
            self._storage.pop(evicted)
