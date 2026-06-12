"""Iteration helpers for linked-list variants.

Iteration is where circular lists need special attention. Traversal is bounded
by the size captured when iteration begins, so live appends do not make
iteration chase newly added nodes forever.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any


class Iteration:
    """Provide forward and reverse iteration."""

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
