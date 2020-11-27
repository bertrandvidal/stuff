from typing import Any


class LeastRecentlyUsedCache:
    """
    Offers fix memory caching where least recently used entries are evicted.
    """
    _DEFAULT_CAPACITY = 10

    def __init__(self, capacity: int = _DEFAULT_CAPACITY):
        self._capacity = capacity

    def get_capacity(self) -> Any:
        """

        :return: maximum number of key/value pairs the cache can hold before eviction takes place
        """
        return self._capacity
