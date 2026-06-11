"""Utility helpers for linked lists."""

from copy import deepcopy
from typing import Any


class Utility:
    """Provide conversion, copying, counting, and clearing helpers."""

    def to_list(self) -> list[Any]:
        """Return the linked-list values as a Python list."""
        return list(iter(self))

    @classmethod
    def from_list(
        cls,
        lst: list[Any],
        list_type: str = "singly",
    ) -> "LinkedList":
        """Build a linked list from a Python list."""
        new_list = cls(list_type)
        for item in lst:
            new_list.append(item)
        return new_list

    def copy(self) -> "LinkedList":
        """Return a shallow copy with the same list type."""
        return self.from_list(self.to_list(), self._list_type)

    def deep_copy(self) -> "LinkedList":
        """Return a deep copy with the same list type."""
        return self.from_list(
            [deepcopy(item) for item in self.to_list()],
            self._list_type,
        )

    def count(self, data: Any) -> int:
        """Return the number of values equal to ``data``."""
        return sum(1 for item in self if item == data)

    def clear(self) -> None:
        """Remove every node and reset the list to an empty state."""
        current = self.head
        if self._is_circular and self.tail:
            self.tail.next = None
            if self._list_type == "doubly_circular" and self.head:
                self.head.prev = None
        visited = set()
        while current is not None and id(current) not in visited:
            visited.add(id(current))
            next_node = getattr(current, "next", None)
            if hasattr(current, "next"):
                current.next = None
            if hasattr(current, "prev"):
                current.prev = None
            current = next_node
        self.head = self.tail = None
        self._size = 0
