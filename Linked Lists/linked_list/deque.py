"""Linked deque implementation backed by doubly linked nodes.

The deque is intentionally separate from ``LinkedList`` because it has a
different purpose. A linked list is a general sequence with many operations;
this class is focused on fast, clear operations at the left and right ends.

The important invariant is that ``head`` always points to the leftmost node,
``tail`` always points to the rightmost node, and ``_size`` always matches the
number of nodes reachable between them. Every mutation below keeps those three
pieces of state synchronized.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from reprlib import recursive_repr
from typing import Any, TypeVar

from .nodes import DoublyLinkedNode

TLinkedDeque = TypeVar("TLinkedDeque", bound="LinkedDeque")


class LinkedDeque:
    """A double-ended queue backed by a doubly linked list.

    Each node has both ``next`` and ``prev`` links, which lets the deque update
    either end without traversing from the opposite side. The public API uses
    explicit left/right method names, then exposes familiar Python-style
    aliases such as ``appendleft`` and ``popleft`` at the bottom of the class.
    """

    def __init__(self, iterable: Iterable[Any] | None = None) -> None:
        """Initialize an empty deque and optionally append initial values."""
        self.head: DoublyLinkedNode | None = None
        self.tail: DoublyLinkedNode | None = None
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
        """Yield values from left to right.

        The iterator captures the starting size so extending the same deque
        during iteration cannot make the loop walk newly appended nodes
        forever.
        """
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            yield current.data
            current = current.next
            remaining -= 1

    def __reversed__(self) -> Iterator[Any]:
        """Yield values from right to left.

        This mirrors ``__iter__`` but follows ``prev`` links from the tail. It
        is also bounded by the size captured at iterator creation time.
        """
        current = self.tail
        remaining = self._size
        while current is not None and remaining > 0:
            yield current.data
            current = current.prev
            remaining -= 1

    def __getitem__(self, index: int | slice) -> Any:
        """Return a value by index or a sliced ``LinkedDeque``.

        Integer indexes walk from the closer end. Slice indexes use Python's
        built-in slice semantics and return a new deque with the same concrete
        class.
        """
        if isinstance(index, int):
            return self._node_at(index).data

        if isinstance(index, slice):
            return self.__class__(list(self)[index])

        raise TypeError("Index must be int or slice")

    def __contains__(self, data: Any) -> bool:
        """Return whether ``data`` appears in the deque."""
        return any(item == data for item in self)

    def get(self, index: int, default: Any = None) -> Any:
        """Return a value by index, or ``default`` if out of range.

        This is a forgiving counterpart to ``deque[index]``. It still supports
        negative indexes, but it converts only missing positions into the
        caller-provided fallback.
        """
        try:
            return self[index]
        except IndexError:
            return default

    def __eq__(self, other: object) -> bool:
        """Compare deques by stored values.

        Subclasses compare as deques too, which keeps equality symmetric
        between ``LinkedDeque`` and any subclass that stores the same values.
        """
        if not isinstance(other, LinkedDeque):
            return False
        return self.to_list() == other.to_list()

    @recursive_repr()
    def __repr__(self) -> str:
        """Return a debugging representation of the deque.

        ``recursive_repr`` protects indirect cycles, while ``_repr_item`` also
        makes a direct ``deque.append(deque)`` case readable.
        """
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
        """Build a deque from an iterable while preserving subclass type."""
        return cls(iterable)

    def to_list(self) -> list[Any]:
        """Return the deque values as a Python list."""
        return list(self)

    def copy(self: TLinkedDeque) -> TLinkedDeque:
        """Return a shallow copy with the same concrete class."""
        return self.__class__(self)

    def is_empty(self) -> bool:
        """Return whether the deque currently stores no values."""
        return self._size == 0

    def count(self, data: Any) -> int:
        """Return the number of values equal to ``data``."""
        return sum(1 for item in self if item == data)

    def index(
        self,
        data: Any,
        start: int = 0,
        stop: int | None = None,
    ) -> int:
        """Return the first index of ``data`` within the optional bounds."""
        start, stop, _ = slice(start, stop, 1).indices(self._size)
        for position, item in enumerate(self):
            if position < start:
                continue
            if position >= stop:
                break
            if item == data:
                return position
        raise ValueError(f"{data!r} is not in deque")

    def find(
        self,
        data: Any,
        start: int = 0,
        stop: int | None = None,
    ) -> int | None:
        """Return the first matching index or ``None`` if not found."""
        try:
            return self.index(data, start, stop)
        except ValueError:
            return None

    def append_left(self, data: Any) -> None:
        """Insert ``data`` at the left side of the deque.

        On an empty deque, the new node is both the head and tail. Otherwise,
        the old head's ``prev`` link must point back to the new node.
        """
        new_node = DoublyLinkedNode(data, next_node=self.head)

        if self.head is None:
            self.head = self.tail = new_node
        else:
            self.head.prev = new_node
            self.head = new_node

        self._size += 1

    def append_right(self, data: Any) -> None:
        """Insert ``data`` at the right side of the deque.

        This is the mirror of ``append_left``. On a non-empty deque, the old
        tail's ``next`` link must point forward to the new node.
        """
        new_node = DoublyLinkedNode(data, prev_node=self.tail)

        if self.tail is None:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

        self._size += 1

    def insert(self, index: int, data: Any) -> None:
        """Insert ``data`` before ``index`` using deque-style bounds.

        This mirrors ``collections.deque.insert`` for an unbounded deque:
        indexes at or below the far left prepend, indexes at or beyond the far
        right append, and negative indexes count from the right.
        """
        if self._size == 0:
            self.append_left(data)
            return

        if index < 0:
            index += self._size
            if index < 0:
                index = 0

        if index <= 0:
            self.append_left(data)
            return
        if index >= self._size:
            self.append_right(data)
            return

        target = self._node_at(index)
        previous = target.prev
        assert previous is not None

        new_node = DoublyLinkedNode(
            data,
            next_node=target,
            prev_node=previous,
        )
        previous.next = new_node
        target.prev = new_node
        self._size += 1

    def extend(self, iterable: Iterable[Any]) -> None:
        """Append every item from ``iterable`` to the right.

        When the iterable is the deque itself, a list snapshot prevents the
        method from iterating over values that it is appending at the same
        time.
        """
        if iterable is self:
            iterable = list(iterable)
        for item in iterable:
            self.append_right(item)

    def extend_left(self, iterable: Iterable[Any]) -> None:
        """Prepend each item, matching ``collections.deque.extendleft``.

        Each incoming value is appended to the left as it is read, so the final
        order appears reversed relative to the input iterable.
        """
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
        """Remove and return the leftmost value.

        After the head moves right, the new head must not keep a stale
        backward link to the removed node. The removed node is also detached so
        external references cannot observe old deque links.
        """
        if self.head is None:
            raise IndexError("Pop from empty deque")

        return self._unlink_node(self.head)

    def pop_right(self) -> Any:
        """Remove and return the rightmost value.

        This mirrors ``pop_left`` from the other end. After the tail moves
        left, the new tail must not keep a stale forward link.
        """
        if self.tail is None:
            raise IndexError("Pop from empty deque")

        return self._unlink_node(self.tail)

    def remove(self, data: Any) -> None:
        """Remove the first matching value from left to right.

        This mirrors ``collections.deque.remove`` by raising ``ValueError``
        when the value is not present.
        """
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            next_node = current.next
            if current.data == data:
                self._unlink_node(current)
                return
            current = next_node
            remaining -= 1
        raise ValueError(f"{data!r} is not in deque")

    def remove_all(self, data: Any) -> int:
        """Remove every matching value and return the removal count.

        The traversal stores ``next`` before unlinking so removing the current
        node never loses the rest of the deque.
        """
        removed = 0
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            next_node = current.next
            if current.data == data:
                self._unlink_node(current)
                removed += 1
            current = next_node
            remaining -= 1
        return removed

    def replace(
        self,
        old_data: Any,
        new_data: Any,
        count: int | None = None,
    ) -> int:
        """Replace matching values and return how many changed.

        Replacement updates node data only. The deque's shape and links stay
        unchanged, which makes this safe for head, tail, and middle values.
        """
        if count is not None and count <= 0:
            return 0

        replaced = 0
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            if current.data == old_data:
                current.data = new_data
                replaced += 1
                if count is not None and replaced == count:
                    break
            current = current.next
            remaining -= 1
        return replaced

    def clear(self) -> None:
        """Remove all nodes and reset the deque to an empty state.

        The traversal detaches every node before dropping ``head`` and
        ``tail``.
        That makes the cleanup explicit and avoids stale internal links if old
        node objects are still referenced elsewhere.
        """
        current = self.head
        while current is not None:
            next_node = current.next
            current.prev = None
            current.next = None
            current = next_node

        self.head = None
        self.tail = None
        self._size = 0

    def reverse(self) -> None:
        """Reverse the deque in place by swapping every node's links."""
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            current.prev, current.next = current.next, current.prev
            current = current.prev
            remaining -= 1

        self.head, self.tail = self.tail, self.head

    def rotate(self, steps: int = 1) -> None:
        """Rotate right for positive steps and left for negative steps.

        The modulo operation avoids unnecessary full cycles. For example,
        rotating a four-item deque by six steps is the same as rotating it by
        two steps.
        """
        if self._size <= 1:
            return

        if steps > 0:
            for _ in range(steps % self._size):
                self._move_tail_to_head()
        elif steps < 0:
            for _ in range((-steps) % self._size):
                self._move_head_to_tail()

    def _node_at(self, index: int) -> DoublyLinkedNode:
        """Return the node at ``index``, walking from the closer end."""
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")

        if index <= self._size // 2:
            current = self.head
            for _ in range(index):
                assert current is not None
                current = current.next
        else:
            current = self.tail
            for _ in range(self._size - index - 1):
                assert current is not None
                current = current.prev

        assert current is not None
        return current

    def _unlink_node(self, node: DoublyLinkedNode) -> Any:
        """Detach ``node`` from the deque and return its stored value."""
        previous = node.prev
        next_node = node.next

        if previous is None:
            self.head = next_node
        else:
            previous.next = next_node

        if next_node is None:
            self.tail = previous
        else:
            next_node.prev = previous

        node.prev = None
        node.next = None
        self._size -= 1
        return node.data

    def _move_head_to_tail(self) -> None:
        """Move the current head node to the tail.

        This helper performs one left rotation step by detaching the current
        head and reattaching it after the current tail.
        """
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
        """Move the current tail node to the head.

        This helper performs one right rotation step by detaching the current
        tail and reattaching it before the current head.
        """
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

    # Python-style aliases make the class familiar to collections.deque users.
    append = append_right
    appendleft = append_left
    extendleft = extend_left
    peek = peek_right
    popleft = pop_left
    pop = pop_right
