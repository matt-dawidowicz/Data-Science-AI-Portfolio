"""Functional-style helpers for linked lists.

These methods mirror common functional programming operations while preserving
the linked-list type. ``map`` and ``filter`` return new linked lists instead of
plain Python lists.

They are implemented in terms of public iteration and ``append``. That means
the same code works for singly, doubly, circular, and non-circular lists while
letting the mutation mixin handle the representation-specific pointer repair.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import reduce as functools_reduce
from typing import Any

_MISSING = object()


class Functional:
    """Provide map, filter, and reduce operations.

    These helpers are intentionally non-mutating except for ``reduce``, which
    only computes a value. This makes them safe examples of how to build new
    linked structures from existing traversal behavior.
    """

    def map(self, func: Callable[[Any], Any]) -> Any:
        """Return a new list containing ``func`` applied to each item.

        The original list is unchanged. The new list uses the same list type so
        a doubly linked list maps to another doubly linked list.
        """
        new_list = self.__class__(self._list_type)
        for data in list(self):
            new_list.append(func(data))
        return new_list

    def filter(self, predicate: Callable[[Any], bool]) -> Any:
        """Return a new list containing items accepted by ``predicate``."""
        new_list = self.__class__(self._list_type)
        for data in self:
            if predicate(data):
                new_list.append(data)
        return new_list

    def reduce(
        self,
        func: Callable[[Any, Any], Any],
        initializer: Any = _MISSING,
    ) -> Any:
        """Reduce the list with ``func`` and an optional initializer.

        This delegates to ``functools.reduce`` so it follows normal Python
        reduction behavior for empty lists and missing initializers.
        """
        if initializer is _MISSING:
            return functools_reduce(func, self)
        return functools_reduce(func, self, initializer)
