"""Linked deque implementation backed by doubly linked nodes."""

from reprlib import recursive_repr
from typing import Any, Iterable, Iterator, Optional, TypeVar

from .nodes import DoublyLinkedNode


TLinkedDeque = TypeVar("TLinkedDeque", bound="LinkedDeque")


class LinkedDeque:
    """A double-ended queue backed by a doubly linked list."""

    def __init__(self, iterable: Optional[Iterable[Any]] = None) -> None:
        self.head: Optional[DoublyLinkedNode] = None
        self.tail: Optional[DoublyLinkedNode] = None
        self._size = 0

        if iterable is not None:
            self.extend(iterable)

    def __len__(self) -> int:
        """Return the number of values in the deque."""
        return self._size

    def __bool__(self) -> bool:
        """Return whether the deque contains any values."""
        return self._size > 0

    def __iter__(self) -> Iterator[Any]:
        """Yield values from left to right."""
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            yield current.data
            current = current.next
            remaining -= 1

    def __reversed__(self) -> Iterator[Any]:
        """Yield values from right to left."""
        current = self.tail
        remaining = self._size
        while current is not None and remaining > 0:
            yield current.data
            current = current.prev
            remaining -= 1

    def __contains__(self, data: Any) -> bool:
        """Return whether ``data`` appears in the deque."""
        return any(item == data for item in self)

    def __eq__(self, other: object) -> bool:
        """Compare deques by stored values."""
        if not isinstance(other, LinkedDeque):
            return False
        return self.to_list() == other.to_list()

    @recursive_repr()
    def __repr__(self) -> str:
        """Return a debugging representation of the deque."""
        items = ", ".join(self._repr_item(item) for item in self)
        return f"{self.__class__.__name__}([{items}])"

    @recursive_repr()
    def __str__(self) -> str:
        """Return a readable representation of the deque."""
        return " <-> ".join(self._str_item(item) for item in self)

    def _repr_item(self, item: Any) -> str:
        """Return a recursion-safe representation for a stored item."""
        if item is self:
            return "..."
        return repr(item)

    def _str_item(self, item: Any) -> str:
        """Return a recursion-safe string for a stored item."""
        if item is self:
            return "..."
        return str(item)

    @classmethod
    def from_iterable(
        cls: type[TLinkedDeque],
        iterable: Iterable[Any],
    ) -> TLinkedDeque:
        """Build a deque from an iterable."""
        return cls(iterable)

    def to_list(self) -> list[Any]:
        """Return the deque values as a Python list."""
        return list(self)

    def copy(self: TLinkedDeque) -> TLinkedDeque:
        """Return a shallow copy of the deque."""
        return self.__class__(self)

    def append_left(self, data: Any) -> None:
        """Insert ``data`` at the left side of the deque."""
        new_node = DoublyLinkedNode(data, next_node=self.head)

        if self.head is None:
            self.head = self.tail = new_node
        else:
            self.head.prev = new_node
            self.head = new_node

        self._size += 1

    def append_right(self, data: Any) -> None:
        """Insert ``data`` at the right side of the deque."""
        new_node = DoublyLinkedNode(data, prev_node=self.tail)

        if self.tail is None:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

        self._size += 1

    def extend(self, iterable: Iterable[Any]) -> None:
        """Append every item from ``iterable`` to the right."""
        if iterable is self:
            iterable = list(iterable)
        for item in iterable:
            self.append_right(item)

    def extend_left(self, iterable: Iterable[Any]) -> None:
        """Prepend each item, matching collections.deque.extendleft order."""
        if iterable is self:
            iterable = list(iterable)
        for item in iterable:
            self.append_left(item)

    def peek_left(self) -> Any:
        """Return the leftmost value without removing it."""
        if self.head is None:
            raise IndexError("Peek from empty deque")
        return self.head.data

    def peek_right(self) -> Any:
        """Return the rightmost value without removing it."""
        if self.tail is None:
            raise IndexError("Peek from empty deque")
        return self.tail.data

    def pop_left(self) -> Any:
        """Remove and return the leftmost value."""
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
        """Remove and return the rightmost value."""
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
        """Remove all nodes and reset the deque to an empty state."""
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
        """Rotate right for positive steps and left for negative steps."""
        if self._size <= 1:
            return

        if steps > 0:
            for _ in range(steps % self._size):
                self._move_tail_to_head()
        elif steps < 0:
            for _ in range((-steps) % self._size):
                self._move_head_to_tail()

    def _move_head_to_tail(self) -> None:
        """Move the current head node to the tail."""
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
        """Move the current tail node to the head."""
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
    extendleft = extend_left
    popleft = pop_left
    pop = pop_right
