from typing import Any, Iterator

class Iteration:
    def __iter__(self) -> Iterator[Any]:
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
        if self._list_type not in ("doubly", "doubly_circular"):
            raise NotImplementedError("Reverse iteration only supported for doubly-linked lists")
        if self._is_circular:
            yield from self._iter_reversed_circular()
        else:
            yield from self._iter_reversed_linear()

    def _iter_reversed_circular(self) -> Iterator[Any]:
        if self.tail is None:
            return
        current = self.tail
        yield current.data
        current = current.prev
        while current != self.tail:
            yield current.data
            current = current.prev

    def _iter_reversed_linear(self) -> Iterator[Any]:
        current = self.tail
        while current:
            yield current.data
            current = current.prev