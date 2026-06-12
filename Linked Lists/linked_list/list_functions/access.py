"""Access, comparison, and display behavior for linked lists.

These operations read the structure without changing node links. They provide
Python container behavior such as indexing, slicing, membership checks,
equality, and readable representations.

For a beginner, the key idea is that indexing a linked list is not constant
time. The code must walk node by node from the head until it reaches the
requested position. Slicing takes a finite snapshot first so Python's normal
slice rules handle negative indexes and negative steps correctly.
"""

from __future__ import annotations

from typing import Any


class Access:
    """Provide indexing, membership, equality, and display helpers.

    The linked list does not have random access like a Python list, so index
    operations walk from ``head`` to the requested position.

    The methods in this mixin intentionally do not repair links. If one of
    these helpers ever needs link updates, that behavior belongs in the
    mutation mixin instead.
    """

    def __getitem__(self, index: int | slice) -> Any:
        """Return an item or sublist at the requested index or slice.

        Integer indexes return a single value. Slice indexes collect values
        into a new linked list of the same list type, preserving the public
        behavior of this container instead of returning a plain Python list.
        """
        if isinstance(index, int):
            if index < 0:
                index += self._size
            if index < 0 or index >= self._size:
                raise IndexError("Index out of range")
            current = self.head
            for _ in range(index):
                current = current.next
            return current.data

        if isinstance(index, slice):
            # Python already handles every slice shape correctly, including
            # negative indexes and negative steps. Rebuilding from that result
            # keeps the linked-list type while matching normal slice behavior.
            result = list(self)[index]
            return self.__class__.from_list(result, self._list_type)

        raise TypeError("Index must be int or slice")

    def __setitem__(self, index: int, value: Any) -> None:
        """Assign a new value at the requested list index.

        This changes node data only; it does not relink or replace the node.
        """
        if index < 0:
            index = self._size + index
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        current = self.head
        for _ in range(index):
            current = current.next
        current.data = value

    def __contains__(self, data: Any) -> bool:
        """Return whether the list contains the requested value."""
        return any(item == data for item in self)

    def get(self, index: int, default: Any = None) -> Any:
        """Return an item by index, or ``default`` if it is out of range.

        Normal indexing is still strict and raises ``IndexError``. This helper
        is useful when an out-of-range position is an expected possibility and
        the caller wants a fallback value instead of an exception.
        """
        try:
            return self[index]
        except IndexError:
            return default

    def index(
        self,
        data: Any,
        start: int = 0,
        stop: int | None = None,
    ) -> int:
        """Return the first index of ``data`` within the optional bounds.

        The method follows Python list semantics for ``start`` and ``stop``,
        including negative bounds. It raises ``ValueError`` when the value is
        not present inside the requested range.
        """
        values = list(self)
        if stop is None:
            return values.index(data, start)
        return values.index(data, start, stop)

    def find(
        self,
        data: Any,
        start: int = 0,
        stop: int | None = None,
    ) -> int | None:
        """Return the first matching index or ``None`` if not found."""
        try:
            return self.index(data, start, stop)
        except ValueError:
            return None

    def peek_front(self) -> Any:
        """Return the head value without removing it."""
        if self.head is None:
            raise IndexError("Peek from empty list")
        return self.head.data

    def peek_back(self) -> Any:
        """Return the tail value without removing it."""
        if self.tail is None:
            raise IndexError("Peek from empty list")
        return self.tail.data

    def __eq__(self, other: object) -> bool:
        """Compare two linked lists by type and stored values.

        The type check prevents a singly linked list and doubly linked list
        with the same values from comparing equal when their structures differ.
        """
        if type(other) is not type(self):
            return False
        if self._list_type != other._list_type:
            return False
        if len(self) != len(other):
            return False
        return all(a == b for a, b in zip(self, other, strict=False))

    def __repr__(self) -> str:
        """Return a debugging representation of the linked list.

        ``repr`` includes both values and list type because ``LinkedList`` can
        represent several pointer shapes with the same public class.
        """
        return (
            f"{self.__class__.__name__}([{', '.join(repr(x) for x in self)}], "
            f"type={self._list_type})"
        )

    def __str__(self) -> str:
        """Return a readable arrow-separated representation."""
        return " -> ".join(str(x) for x in self)

    def nth_from_end(self, n: int) -> Any:
        """Return the nth value from the end using one-based indexing.

        The method converts the request into a normal zero-based index using
        the tracked size, so it works for all list variants.
        """
        if n <= 0 or n > self._size:
            raise IndexError("n is out of range")
        return self[self._size - n]
