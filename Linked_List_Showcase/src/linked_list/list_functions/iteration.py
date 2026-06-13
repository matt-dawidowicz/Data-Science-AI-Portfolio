"""Iteration helpers for linked-list variants.

Iteration is where circular lists need special attention. A normal linear list
can stop when it reaches ``None``. A circular list never reaches ``None``
because the tail points back to the head. For that reason, iteration is
bounded by the size captured when iteration begins.

The same bound also protects live iterators on linear lists. If a caller
extends a list while iterating over it, the iterator stops after the original
number of values rather than chasing newly appended nodes forever.
"""

from collections.abc import Iterator
from typing import Any


class Iteration:
    """Provide forward and reverse iteration.

    Forward iteration works for every list type. Reverse iteration requires
    ``prev`` links, so it is available only for doubly linked variants.
    """

    def __iter__(self) -> Iterator[Any]:
        """Yield list values from head to tail.

        Iteration is bounded by the starting size. That keeps circular lists
        finite and keeps linear lists finite even if callers append during
        iteration.
        """
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            yield current.data
            current = current.next
            remaining -= 1

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
