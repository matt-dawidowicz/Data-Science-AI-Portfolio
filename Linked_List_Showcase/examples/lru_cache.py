"""Tiny LRU cache using stable positions for recency order."""

import _bootstrap  # noqa: F401
from linked_list import Position, PositionalLinkedList


class TinyLRUCache:
    """Cache values and evict the least recently used key."""

    def __init__(self, capacity: int) -> None:
        """Initialize an empty fixed-capacity cache."""
        self.capacity = capacity
        self._values: dict[str, str] = {}
        self._positions: dict[str, Position[str]] = {}
        self._order: PositionalLinkedList[str] = PositionalLinkedList()

    def get(self, key: str) -> str | None:
        """Return a cached value and mark it most recently used."""
        if key not in self._values:
            return None
        self._order.move_to_front(self._positions[key])
        return self._values[key]

    def put(self, key: str, value: str) -> None:
        """Insert or update a cached value."""
        if key in self._values:
            self._values[key] = value
            self._order.move_to_front(self._positions[key])
            return

        if len(self._values) == self.capacity:
            oldest = self._order.last_position()
            assert oldest is not None
            old_key = oldest.data
            self._order.delete(oldest)
            del self._values[old_key]
            del self._positions[old_key]

        self._values[key] = value
        self._positions[key] = self._order.add_first(key)

    def keys_by_recency(self) -> list[str]:
        """Return newest keys first."""
        return self._order.to_list()


def main() -> None:
    """Show eviction order."""
    cache = TinyLRUCache(capacity=2)
    cache.put("profile:1", "Ada")
    cache.put("profile:2", "Grace")
    cache.get("profile:1")
    cache.put("profile:3", "Katherine")
    print(cache.keys_by_recency())


if __name__ == "__main__":
    main()
