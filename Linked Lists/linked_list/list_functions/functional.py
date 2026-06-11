"""Functional-style helpers for linked lists."""

from functools import reduce as functools_reduce
from typing import Any, Callable, Optional


class Functional:
    """Provide map, filter, and reduce operations."""

    def map(self, func: Callable[[Any], Any]) -> "LinkedList":
        """Return a new list containing ``func`` applied to each item."""
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
        """Reduce the list with ``func`` and an optional initializer."""
        if initializer is not None:
            return functools_reduce(func, self, initializer)
        return functools_reduce(func, self)
