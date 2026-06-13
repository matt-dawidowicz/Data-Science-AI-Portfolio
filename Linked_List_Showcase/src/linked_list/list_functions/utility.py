"""Utility helpers for linked lists.

These helpers convert between linked lists and ordinary Python collections and
perform cleanup operations that are shared by all list variants.

Conversion helpers are deliberately simple: they use normal iteration and
normal appending rather than reaching into node internals. ``clear`` is the
exception because it must detach every node so old references do not retain
stale links.
"""

from copy import deepcopy
from typing import Any


class Utility:
    """Provide conversion, copying, counting, and clearing helpers.

    The mixin keeps lifecycle operations separate from mutation algorithms so
    a reader can find "turn this into a Python list" or "empty the structure"
    without scanning insertion and deletion code.
    """

    def to_list(self) -> list[Any]:
        """Return the linked-list values as a Python list.

        This is useful for tests, debugging, and algorithms that are easier to
        express with a finite Python sequence.
        """
        return list(iter(self))

    @classmethod
    def from_list(
        cls,
        lst: list[Any],
        list_type: str = "singly",
    ) -> Any:
        """Build a linked list from a Python list.

        The new list is built through ``append`` so all normal link invariants
        are maintained for the requested list type.
        """
        new_list = cls(list_type)
        for item in lst:
            new_list.append(item)
        return new_list

    def copy(self) -> Any:
        """Return a shallow copy with the same list type.

        The node structure is new, but the stored values are the same objects.
        """
        return self.from_list(self.to_list(), self._list_type)

    def deep_copy(self) -> Any:
        """Return a deep copy with the same list type.

        Both the node structure and the stored values are copied.
        """
        return self.from_list(
            [deepcopy(item) for item in self.to_list()],
            self._list_type,
        )

    def count(self, data: Any) -> int:
        """Return the number of values equal to ``data``."""
        return sum(1 for item in self if item == data)

    def clear(self) -> None:
        """Remove every node and reset the list to an empty state.

        Circular lists are opened before traversal so the cleanup loop can stop
        naturally. The ``visited`` set is an extra guard against unexpected
        cycles if a list is already corrupted.
        """
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
