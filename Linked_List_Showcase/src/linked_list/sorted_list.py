"""Sorted linked-list container built on the core linked-list behavior.

``SortedLinkedList`` reuses the same nodes and traversal helpers as
``LinkedList``, but adds one important invariant: values are always stored in
ascending order. Methods that add or replace values either preserve that order
or reject the operation before changing the list.

This file is a useful example of how an invariant shapes an API. The node
structure is not new, but several inherited operations need narrower behavior
because arbitrary insertion, reversal, or rotation would make the name
"sorted" untrue.
"""

from collections.abc import Callable, Iterable
from operator import index as to_index
from typing import Any, Generic, SupportsIndex, TypeVar

from .list_functions.linked_list import LinkedList
from .list_functions.mutation import Mutation

T = TypeVar("T")
TSortedLinkedList = TypeVar(
    "TSortedLinkedList",
    bound="SortedLinkedList",
)


class SortedLinkedList(LinkedList[T], Generic[T]):
    """Linked list that keeps values sorted after every mutation.

    The class supports the same list variants as ``LinkedList``: singly,
    doubly, singly circular, and doubly circular. The difference is that
    insertion-style methods place values according to normal Python less-than
    ordering instead of letting callers choose arbitrary physical positions.

    The implementation often computes a sorted value snapshot before rebuilding
    links. That is intentionally conservative: if Python cannot compare two
    incoming values, the original linked structure is left untouched.
    """

    def __init__(
        self,
        list_type: str | Iterable[Any] = "singly",
        iterable: Iterable[Any] | None = None,
    ) -> None:
        """Initialize a sorted linked list.

        ``SortedLinkedList([3, 1, 2])`` builds a singly linked sorted list.
        ``SortedLinkedList("doubly", [3, 1, 2])`` selects a specific linked
        representation while still sorting the initial values.
        """
        if not isinstance(list_type, str):
            if iterable is not None:
                raise TypeError(
                    "Pass either an iterable or list_type plus iterable"
                )
            if not isinstance(list_type, Iterable):
                raise TypeError("list_type must be a string or iterable")
            iterable = list_type
            list_type = "singly"

        super().__init__(list_type)
        if iterable is not None:
            self.extend(iterable)

    @classmethod
    def from_list(
        cls: type[TSortedLinkedList],
        lst: list[Any],
        list_type: str = "singly",
    ) -> TSortedLinkedList:
        """Build a sorted linked list from a Python list."""
        return cls(list_type, lst)

    def add(self, data: Any) -> None:
        """Insert ``data`` at its sorted position.

        This is the clearest insertion method for the sorted container. It
        delegates to the base linked-list sorted insertion logic, which knows
        how to repair linear, circular, singly, and doubly linked structures.
        """
        Mutation.insert_sorted(self, data)

    def append(self, data: Any) -> None:
        """Add ``data`` while preserving sorted order.

        In a sorted list, ``append`` means "add this value to the collection,"
        not "force this value onto the physical tail." For tail-specific
        behavior, use the plain ``LinkedList`` class instead.
        """
        self.add(data)

    def prepend(self, data: Any) -> None:
        """Add ``data`` while preserving sorted order.

        The sorted invariant takes priority over physical front insertion, so
        this method behaves like ``add``.
        """
        self.add(data)

    def insert_sorted(
        self,
        data: Any,
        compare: Callable[[Any, Any], bool] | None = None,
    ) -> None:
        """Insert ``data`` using this list's fixed ascending ordering."""
        if compare is not None:
            raise ValueError(
                "SortedLinkedList uses its built-in ascending ordering"
            )
        self.add(data)

    def insert(self, index: int | SupportsIndex, data: Any) -> None:
        """Insert ``data`` at ``index`` only if order stays valid.

        This method keeps compatibility with the normal linked-list API while
        protecting the sorted invariant. If the requested position would put
        the value before a larger previous value or after a smaller next value,
        the method raises ``ValueError`` without changing the list.
        """
        index = to_index(index)
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")

        previous = self._node_at(index - 1) if index > 0 else None
        next_node = self._node_at(index) if index < self._size else None
        if not self._fits_between(data, previous, next_node):
            raise ValueError("Insertion would break sorted order")

        if index == 0:
            Mutation.prepend(self, data)
        elif index == self._size:
            Mutation.append(self, data)
        else:
            Mutation.insert(self, index, data)

    def __setitem__(self, index: int | SupportsIndex, value: Any) -> None:
        """Replace one value only if the sorted order remains valid."""
        index = to_index(index)
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")

        node = self._node_at(index)
        previous = self._node_at(index - 1) if index > 0 else None
        next_node = (
            None if index == self._size - 1 else self._node_at(index + 1)
        )

        if not self._fits_between(value, previous, next_node):
            raise ValueError("Assignment would break sorted order")

        node.data = value

    def extend(self, iterable: Iterable[Any]) -> None:
        """Add every value from ``iterable`` and keep the whole list sorted.

        Values are snapshotted and sorted before the list is rebuilt. That
        means a comparison error leaves the original list unchanged.
        """
        values = list(iterable)
        if not values:
            return
        self._rebuild_from_values([*self, *values])

    def replace(
        self,
        old_data: Any,
        new_data: Any,
        count: int | SupportsIndex | None = None,
    ) -> int:
        """Replace matching values and re-sort the result.

        Replacing a value can move it to a completely different position. The
        method therefore computes the full updated sequence first, verifies it
        can be sorted, and only then rebuilds the linked structure.
        """
        if count is not None:
            count = to_index(count)
        if count is not None and count <= 0:
            return 0

        replaced = 0
        updated = []
        for item in self:
            if item == old_data and (count is None or replaced < count):
                updated.append(new_data)
                replaced += 1
            else:
                updated.append(item)

        if replaced == 0 or old_data == new_data:
            return replaced

        self._rebuild_from_values(updated)
        return replaced

    def merge(
        self,
        other: LinkedList,
        compare: Callable[[Any, Any], bool] | None = None,
    ) -> None:
        """Merge another linked list into this sorted list.

        The other list may be sorted or unsorted, but it must use the same
        linked representation. Values are copied into this list rather than
        relinking the other list's nodes, so ``other`` remains unchanged.
        """
        if compare is not None:
            raise ValueError(
                "SortedLinkedList uses its built-in ascending ordering"
            )
        if not isinstance(other, LinkedList):
            raise TypeError("Can only merge another LinkedList")
        if self._list_type != other._list_type:
            raise TypeError("Cannot merge lists of different types")

        self.extend(list(other))

    def remove_duplicates(self) -> None:
        """Remove duplicate values while preserving one sorted occurrence.

        A sorted list only needs to compare neighboring values because equal
        values sit next to each other. That avoids the ``set`` used by the base
        linked list, so comparable but unhashable values such as nested Python
        lists are supported here.
        """
        if self._size <= 1:
            return

        if self._is_circular and self.tail:
            self.tail.next = None
            if "doubly" in self._list_type and self.head:
                self.head.prev = None

        try:
            current = self.head
            while current is not None and current.next is not None:
                duplicate = current.next
                if current.data == duplicate.data:
                    current.next = duplicate.next
                    if "doubly" in self._list_type and duplicate.next:
                        duplicate.next.prev = current
                    if duplicate is self.tail:
                        self.tail = current
                    duplicate.next = None
                    if hasattr(duplicate, "prev"):
                        duplicate.prev = None
                    self._size -= 1
                else:
                    current = current.next
        finally:
            if self._is_circular and self.head and self.tail:
                self.tail.next = self.head
                if "doubly" in self._list_type:
                    self.head.prev = self.tail

    def sort(
        self,
        compare: Callable[[Any, Any], bool] | None = None,
    ) -> None:
        """Re-sort the list with the built-in ascending ordering."""
        if compare is not None:
            raise ValueError(
                "SortedLinkedList uses its built-in ascending ordering"
            )
        self._rebuild_from_values(list(self))

    def reverse(self) -> None:
        """Reject reversal because it would break sorted order."""
        if self._size <= 1:
            return
        raise ValueError("Reverse would break sorted order")

    def rotate(self, k: int | SupportsIndex) -> None:
        """Reject non-trivial rotation because it would break sorted order."""
        k = to_index(k)
        if self._size <= 1 or k % self._size == 0:
            return
        raise ValueError("Rotate would break sorted order")

    def _node_at(self, index: int) -> Any:
        """Return the node at an already-normalized valid index."""
        current = self.head
        for _ in range(index):
            current = current.next  # type: ignore
        return current

    def _fits_between(
        self,
        data: Any,
        previous: Any | None,
        next_node: Any | None,
    ) -> bool:
        """Return whether ``data`` can sit between two neighbor nodes.

        This small helper is the local version of the sorted invariant. A value
        may be inserted or assigned only if it is not smaller than the previous
        value and not larger than the next value.
        """
        if previous is not None and data < previous.data:
            return False
        if next_node is not None and next_node.data < data:
            return False
        return True

    def _rebuild_from_values(self, values: Iterable[Any]) -> None:
        """Replace the node chain with sorted ``values``.

        Sorting happens before ``clear`` is called. If comparison fails, this
        method raises without changing the existing list.
        """
        sorted_values = sorted(values)
        self.clear()
        for item in sorted_values:
            Mutation.append(self, item)
