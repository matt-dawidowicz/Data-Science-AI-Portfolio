from typing import Any, Iterable, Optional
from copy import deepcopy

class Utility:
    def to_list(self) -> list:
        return list(iter(self))

    @classmethod
    def from_list(cls, lst: list, list_type: str = "singly") -> "LinkedList":
        new_list = cls(list_type)
        for item in lst:
            new_list.append(item)
        return new_list

    def copy(self) -> "LinkedList":
        return self.from_list(self.to_list(), self._list_type)

    def deep_copy(self) -> "LinkedList":
        return self.from_list([deepcopy(item) for item in self.to_list()], self._list_type)

    def count(self, data: Any) -> int:
        return sum(1 for item in self if item == data)

    def clear(self) -> None:
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