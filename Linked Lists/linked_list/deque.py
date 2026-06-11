from typing import Any, Iterable, Iterator, Optional

from .nodes import DoublyLinkedNode


class LinkedDeque:
    """A double-ended queue backed by a doubly linked list."""

    def __init__(self, iterable: Optional[Iterable[Any]] = None) -> None:
        self.head: Optional[DoublyLinkedNode] = None
        self.tail: Optional[DoublyLinkedNode] = None
        self._size = 0

        if iterable is not None:
            self.extend(iterable)

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return self._size > 0

    def __iter__(self) -> Iterator[Any]:
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def __reversed__(self) -> Iterator[Any]:
        current = self.tail
        while current is not None:
            yield current.data
            current = current.prev

    def __contains__(self, data: Any) -> bool:
        return any(item == data for item in self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.to_list() == other.to_list()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_list()!r})"

    def __str__(self) -> str:
        return " <-> ".join(str(item) for item in self)

    @classmethod
    def from_iterable(cls, iterable: Iterable[Any]) -> "LinkedDeque":
        return cls(iterable)

    def to_list(self) -> list:
        return list(self)

    def copy(self) -> "LinkedDeque":
        return self.__class__(self)

    def append_left(self, data: Any) -> None:
        new_node = DoublyLinkedNode(data, next_node=self.head)

        if self.head is None:
            self.head = self.tail = new_node
        else:
            self.head.prev = new_node
            self.head = new_node

        self._size += 1

    def append_right(self, data: Any) -> None:
        new_node = DoublyLinkedNode(data, prev_node=self.tail)

        if self.tail is None:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

        self._size += 1

    def extend(self, iterable: Iterable[Any]) -> None:
        if iterable is self:
            iterable = list(iterable)
        for item in iterable:
            self.append_right(item)

    def extend_left(self, iterable: Iterable[Any]) -> None:
        if iterable is self:
            iterable = list(iterable)
        for item in iterable:
            self.append_left(item)

    def peek_left(self) -> Any:
        if self.head is None:
            raise IndexError("Peek from empty deque")
        return self.head.data

    def peek_right(self) -> Any:
        if self.tail is None:
            raise IndexError("Peek from empty deque")
        return self.tail.data

    def pop_left(self) -> Any:
        if self.head is None:
            raise IndexError("Pop from empty deque")

        old_head = self.head
        data = old_head.data
        self.head = old_head.next

        if self.head is None:
            self.tail = None
        else:
            self.head.prev = None

        old_head.next = None
        old_head.prev = None
        self._size -= 1
        return data

    def pop_right(self) -> Any:
        if self.tail is None:
            raise IndexError("Pop from empty deque")

        old_tail = self.tail
        data = old_tail.data
        self.tail = old_tail.prev

        if self.tail is None:
            self.head = None
        else:
            self.tail.next = None

        old_tail.next = None
        old_tail.prev = None
        self._size -= 1
        return data

    def clear(self) -> None:
        current = self.head
        while current is not None:
            next_node = current.next
            current.prev = None
            current.next = None
            current = next_node

        self.head = None
        self.tail = None
        self._size = 0

    def rotate(self, steps: int = 1) -> None:
        if self._size <= 1:
            return

        if steps > 0:
            for _ in range(steps % self._size):
                self._move_tail_to_head()
        elif steps < 0:
            for _ in range((-steps) % self._size):
                self._move_head_to_tail()

    def _move_head_to_tail(self) -> None:
        assert self.head is not None
        assert self.tail is not None
        old_head = self.head
        self.head = old_head.next
        assert self.head is not None
        self.head.prev = None

        old_head.next = None
        old_head.prev = self.tail
        self.tail.next = old_head
        self.tail = old_head

    def _move_tail_to_head(self) -> None:
        assert self.head is not None
        assert self.tail is not None
        old_tail = self.tail
        self.tail = old_tail.prev
        assert self.tail is not None
        self.tail.next = None

        old_tail.prev = None
        old_tail.next = self.head
        self.head.prev = old_tail
        self.head = old_tail

    append = append_right
    appendleft = append_left
    popleft = pop_left
    pop = pop_right
