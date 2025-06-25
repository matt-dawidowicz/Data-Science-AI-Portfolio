from typing import Any, Callable, Optional
from functools import reduce as functools_reduce

class Functional:
    def map(self, func: Callable[[Any], Any]) -> "LinkedList":
        new_list = self.__class__(self._list_type)
        for data in list(self):
            new_list.append(func(data))
        return new_list

    def filter(self, predicate: Callable[[Any], bool]) -> "LinkedList":
        new_list = self.__class__(self._list_type)
        for data in self:
            if predicate(data):
                new_list.append(data)
        return new_list

    def reduce(self, func: Callable[[Any, Any], Any], initializer: Optional[Any] = None) -> Any:
        if initializer is not None:
            return functools_reduce(func, self, initializer)
        return functools_reduce(func, self)