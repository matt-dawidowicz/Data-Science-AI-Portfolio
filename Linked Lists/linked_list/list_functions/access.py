"""Access, comparison, and display behavior for linked lists."""

from typing import Any, Union


class Access:
    """Provide indexing, membership, equality, and display helpers."""

    def __getitem__(self, index: Union[int, slice]) -> Any:
        """Return an item or sublist at the requested index or slice."""
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
            start, stop, step = index.indices(self._size)
            result = []
            current = self.head
            pos = 0
            while current and pos < stop:
                if pos >= start and (pos - start) % step == 0:
                    result.append(current.data)
                current = current.next
                pos += 1
            return self.__class__.from_list(result, self._list_type)

        raise TypeError("Index must be int or slice")

    def __setitem__(self, index: int, value: Any) -> None:
        """Assign a new value at the requested list index."""
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

    def __eq__(self, other: object) -> bool:
        """Compare two linked lists by type and stored values."""
        if not isinstance(other, self.__class__):
            return False
        if len(self) != len(other):
            return False
        return all(a == b for a, b in zip(self, other))

    def __repr__(self) -> str:
        """Return a debugging representation of the linked list."""
        return (
            f"{self.__class__.__name__}([{', '.join(repr(x) for x in self)}], "
            f"type={self._list_type})"
        )

    def __str__(self) -> str:
        """Return a readable arrow-separated representation."""
        return " -> ".join(str(x) for x in self)

    def nth_from_end(self, n: int) -> Any:
        """Return the nth value from the end using one-based indexing."""
        if n <= 0 or n > self._size:
            raise IndexError("n is out of range")
        return self[self._size - n]
