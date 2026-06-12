"""Iteration helpers for linked-list variants.

Iteration is where circular lists need special attention. Linear lists stop at
``None``. Circular lists stop when traversal returns to the starting node.
"""

from typing import Any, Iterator


class Iteration:
    """Provide forward and reverse iteration."""

    def __iter__(self) -> Iterator[Any]:
        """Yield list values from head to tail.

        For circular lists, the first node is yielded once and then traversal
        stops when it reaches that same node again.
        """
        if self._is_circular:
            if self.head is None:
                return
            current = self.head
            yield current.data
            current = current.next
            while current is not None and current != self.head:
                yield current.data
                current = current.next
        else:
            current = self.head
            while current:
                yield current.data
                current = current.next

    def __reversed__(self) -> Iterator[Any]:
        """Yield list values from tail to head for doubly linked lists.

        Reverse iteration requires ``prev`` links, so it is intentionally not
        supported for singly linked variants.
        """
        if self._list_type not in ("doubly", "doubly_circular"):
            raise NotImplementedError(
                "Reverse iteration only supported for doubly-linked lists"
            )
        if self._is_circular:
            yield from self._iter_reversed_circular()
        else:
            yield from self._iter_reversed_linear()

    def _iter_reversed_circular(self) -> Iterator[Any]:
        """Yield a circular list in reverse without looping forever."""
        if self.tail is None:
            return
        current = self.tail
        yield current.data
        current = current.prev
        while current != self.tail:
            yield current.data
            current = current.prev

    def _iter_reversed_linear(self) -> Iterator[Any]:
        """Yield a linear list in reverse."""
        current = self.tail
        while current:
            yield current.data
            current = current.prev
