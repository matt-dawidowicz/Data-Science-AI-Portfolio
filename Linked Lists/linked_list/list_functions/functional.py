"""Functional-style helpers for linked lists.

These methods mirror common functional programming operations while preserving
the linked-list type. ``map`` and ``filter`` return new linked lists instead of
plain Python lists.
"""

from functools import reduce as functools_reduce
from typing import Any, Callable, Optional


class Functional:
    """Provide map, filter, and reduce operations."""

    def map(self, func: Callable[[Any], Any]) -> "LinkedList":
        """Return a new list containing ``func`` applied to each item.

        The original list is unchanged. The new list uses the same list type so
        a doubly linked list maps to another doubly linked list.
        """
        new_list = self.__class__(self._list_type)
        for data in list(self):
            new_list.append(func(data))
        return new_list

    def filter(self, predicate: Callable[[Any], bool]) -> "LinkedList":
        """Return a new list containing items accepted by ``predicate``."""
        new_list = self.__class__(self._list_type)
        for data in self:
            if predicate(data):
                new_list.append(data)
        return new_list

    def reduce(
        self,
        func: Callable[[Any, Any], Any],
        initializer: Optional[Any] = None,
    ) -> Any:
        """Reduce the list with ``func`` and an optional initializer.

        This delegates to ``functools.reduce`` so it follows normal Python
        reduction behavior for empty lists and missing initializers.
        """
        if initializer is not None:
            return functools_reduce(func, self, initializer)
        return functools_reduce(func, self)
