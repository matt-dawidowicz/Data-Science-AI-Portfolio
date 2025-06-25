from typing import Any, Union

class Access:
    def __getitem__(self, index: Union[int, slice]) -> Any:
        if isinstance(index, int):
            if index < 0:
                index += self._size
            if index < 0 or index >= self._size:
                raise IndexError("Index out of range")
            current = self.head
            for _ in range(index):
                current = current.next
            return current.data

        elif isinstance(index, slice):
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

        else:
            raise TypeError("Index must be int or slice")

    def __setitem__(self, index: int, value: Any) -> None:
        if index < 0:
            index = self._size + index
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        current = self.head
        for _ in range(index):
            current = current.next
        current.data = value

    def __contains__(self, data: Any) -> bool:
        return any(item == data for item in self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if len(self) != len(other):
            return False
        return all(a == b for a, b in zip(self, other))

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}([{', '.join(repr(x) for x in self)}], "
            f"type={self._list_type})"
        )

    def __str__(self) -> str:
        return " -> ".join(str(x) for x in self)
    def nth_from_end(self, n: int) -> Any:
        if n <= 0 or n > self._size:
            raise IndexError("n is out of range")
        lead = self.head
        follow = self.head
        for _ in range(n):
            assert lead is not None
            lead = lead.next
        while lead:
            lead = lead.next
            follow = follow.next  # type: ignore
        return follow.data  # type: ignore