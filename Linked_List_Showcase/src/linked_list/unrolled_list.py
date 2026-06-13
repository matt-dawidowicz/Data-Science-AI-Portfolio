"""Unrolled linked-list sequence container.

An unrolled linked list stores multiple values inside each linked node. That
keeps the pointer-based teaching value of linked lists while reducing the
number of node objects needed for larger sequences.

The structure trades a little in-block list work for fewer pointer hops. A
middle insertion first finds the block, then inserts inside that small Python
list. When a block is full, it splits into two linked blocks.
"""

from collections.abc import Callable, Iterable, Iterator
from copy import deepcopy
from functools import reduce as functools_reduce
from typing import Any, Generic, TypeVar

T = TypeVar("T")
TUnrolledLinkedList = TypeVar(
    "TUnrolledLinkedList",
    bound="UnrolledLinkedList",
)

_MISSING = object()


class _UnrolledNode:
    """Store a small block of values plus neighboring block links.

    The block values are intentionally stored in a Python list. This makes the
    unrolled-list idea visible: the chain links blocks, while each block keeps
    nearby values contiguous.
    """

    __slots__ = ("next", "prev", "values")

    def __init__(self, values: Iterable[Any] | None = None) -> None:
        """Initialize a block node with an optional value snapshot."""
        self.values: list[Any] = list(values) if values is not None else []
        self.next: _UnrolledNode | None = None
        self.prev: _UnrolledNode | None = None

    def __repr__(self) -> str:
        """Return a debugging representation for one block node."""
        return f"_UnrolledNode({self.values!r})"


class UnrolledLinkedList(Generic[T]):
    """Sequence backed by linked nodes that each store a value block.

    ``node_capacity`` controls how many values each node may hold. Insertions
    split full nodes, and removals merge or borrow from neighbors when useful
    so the structure does not degrade into one tiny node per value.

    ``to_blocks()`` is included mostly for learning and testing. It lets a
    reader see not only the public sequence but also the current block layout.
    """

    def __init__(
        self,
        iterable: Iterable[Any] | None = None,
        *,
        node_capacity: int = 8,
    ) -> None:
        """Initialize an empty unrolled list and optionally add values."""
        if not isinstance(node_capacity, int) or isinstance(
            node_capacity,
            bool,
        ):
            raise TypeError("node_capacity must be an integer")
        if node_capacity < 2:
            raise ValueError("node_capacity must be at least 2")

        self.node_capacity: int = node_capacity
        self.head: _UnrolledNode | None = None
        self.tail: _UnrolledNode | None = None
        self._size: int = 0

        if iterable is not None:
            self.extend(iterable)

    def __len__(self) -> int:
        """Return the number of stored values."""
        return self._size

    def __bool__(self) -> bool:
        """Return whether the container stores at least one value."""
        return self._size > 0

    def __iter__(self) -> Iterator[Any]:
        """Yield values from left to right.

        Iteration is bounded by the size captured at iterator creation so
        self-extension with a live iterator remains finite.
        """
        remaining = self._size
        current = self.head
        while current is not None and remaining > 0:
            index = 0
            while index < len(current.values) and remaining > 0:
                yield current.values[index]
                index += 1
                remaining -= 1
            current = current.next

    def __reversed__(self) -> Iterator[Any]:
        """Yield values from right to left."""
        remaining = self._size
        current = self.tail
        while current is not None and remaining > 0:
            index = len(current.values) - 1
            while index >= 0 and remaining > 0:
                yield current.values[index]
                index -= 1
                remaining -= 1
            current = current.prev

    def __contains__(self, value: Any) -> bool:
        """Return whether ``value`` appears in the sequence."""
        return any(item == value for item in self)

    def __getitem__(self, index: int | slice) -> Any:
        """Return a value by index or a sliced unrolled list."""
        if isinstance(index, int):
            node, offset = self._locate(index)
            return node.values[offset]

        if isinstance(index, slice):
            return self.__class__(
                list(self)[index],
                node_capacity=self.node_capacity,
            )

        raise TypeError("Index must be int or slice")

    def __setitem__(self, index: int, value: Any) -> None:
        """Replace one value without changing block links."""
        node, offset = self._locate(index)
        node.values[offset] = value

    def __eq__(self, other: object) -> bool:
        """Compare unrolled lists by concrete type and visible values."""
        if type(other) is not type(self):
            return False
        if len(self) != len(other):
            return False
        return all(
            left == right for left, right in zip(self, other, strict=False)
        )

    def __repr__(self) -> str:
        """Return a debugging representation."""
        return (
            f"{self.__class__.__name__}("
            f"{self.to_list()!r}, node_capacity={self.node_capacity})"
        )

    def __str__(self) -> str:
        """Return a readable arrow-separated representation."""
        return " -> ".join(str(value) for value in self)

    @classmethod
    def from_iterable(
        cls: type[TUnrolledLinkedList],
        iterable: Iterable[Any],
        *,
        node_capacity: int = 8,
    ) -> TUnrolledLinkedList:
        """Build an unrolled list from any iterable."""
        return cls(iterable, node_capacity=node_capacity)

    def is_empty(self) -> bool:
        """Return whether the sequence contains no values."""
        return self._size == 0

    def to_list(self) -> list[Any]:
        """Return all values as a Python list."""
        return list(self)

    def to_blocks(self) -> list[list[Any]]:
        """Return a snapshot of the internal block layout."""
        blocks = []
        current = self.head
        while current is not None:
            blocks.append(list(current.values))
            current = current.next
        return blocks

    def copy(self: TUnrolledLinkedList) -> TUnrolledLinkedList:
        """Return a shallow copy with the same block capacity."""
        return self.__class__(
            self,
            node_capacity=self.node_capacity,
        )

    def deep_copy(self: TUnrolledLinkedList) -> TUnrolledLinkedList:
        """Return a deep copy of the values and block structure."""
        return self.__class__(
            (deepcopy(value) for value in self),
            node_capacity=self.node_capacity,
        )

    def peek_front(self) -> Any:
        """Return the first value without removing it."""
        if self.head is None:
            raise IndexError("Peek from empty unrolled linked list")
        return self.head.values[0]

    def peek_back(self) -> Any:
        """Return the final value without removing it."""
        if self.tail is None:
            raise IndexError("Peek from empty unrolled linked list")
        return self.tail.values[-1]

    def get(self, index: int, default: Any = None) -> Any:
        """Return a value by index, or ``default`` if out of range."""
        try:
            return self[index]
        except IndexError:
            return default

    def count(self, value: Any) -> int:
        """Return how many stored values compare equal to ``value``."""
        return sum(1 for item in self if item == value)

    def index(
        self,
        value: Any,
        start: int = 0,
        stop: int | None = None,
    ) -> int:
        """Return the first index of ``value`` within optional bounds."""
        values = list(self)
        if stop is None:
            return values.index(value, start)
        return values.index(value, start, stop)

    def find(
        self,
        value: Any,
        start: int = 0,
        stop: int | None = None,
    ) -> int | None:
        """Return the first matching index, or ``None`` when missing."""
        try:
            return self.index(value, start, stop)
        except ValueError:
            return None

    def append(self, value: Any) -> None:
        """Append ``value`` to the right side of the sequence."""
        if self.tail is None:
            self._append_node(_UnrolledNode([value]))
        elif len(self.tail.values) < self.node_capacity:
            self.tail.values.append(value)
        else:
            self._append_node(_UnrolledNode([value]))
        self._size += 1

    def prepend(self, value: Any) -> None:
        """Insert ``value`` at the left side of the sequence."""
        if self.head is None:
            self._append_node(_UnrolledNode([value]))
        elif len(self.head.values) < self.node_capacity:
            self.head.values.insert(0, value)
        else:
            new_node = _UnrolledNode([value])
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self._size += 1

    def insert(self, index: int, value: Any) -> None:
        """Insert ``value`` before ``index`` using Python list bounds."""
        if index < 0:
            index += self._size
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")
        if index == 0:
            self.prepend(value)
            return
        if index == self._size:
            self.append(value)
            return

        node, offset = self._locate(index)
        if len(node.values) >= self.node_capacity:
            new_node = self._split_node(node)
            if offset > len(node.values):
                offset -= len(node.values)
                node = new_node

        node.values.insert(offset, value)
        self._size += 1

    def extend(self, iterable: Iterable[Any]) -> None:
        """Append every value from ``iterable``."""
        if iterable is self:
            iterable = list(iterable)
        for value in iterable:
            self.append(value)

    def merge(self, iterable: Iterable[Any]) -> None:
        """Append all values from another iterable."""
        self.extend(iterable)

    def pop(self) -> Any:
        """Remove and return the rightmost value."""
        if self.tail is None:
            raise IndexError("Pop from empty unrolled linked list")
        value = self.tail.values.pop()
        self._size -= 1
        self._rebalance_after_remove(self.tail)
        return value

    def pop_front(self) -> Any:
        """Remove and return the leftmost value."""
        if self.head is None:
            raise IndexError("Pop from empty unrolled linked list")
        value = self.head.values.pop(0)
        self._size -= 1
        self._rebalance_after_remove(self.head)
        return value

    def remove_at(self, index: int) -> Any:
        """Remove and return a value by index."""
        node, offset = self._locate(index)
        value = node.values.pop(offset)
        self._size -= 1
        self._rebalance_after_remove(node)
        return value

    def remove(self, value: Any) -> bool:
        """Remove the first matching value and return whether it existed."""
        current = self.head
        while current is not None:
            for offset, item in enumerate(current.values):
                if item == value:
                    current.values.pop(offset)
                    self._size -= 1
                    self._rebalance_after_remove(current)
                    return True
            current = current.next
        return False

    def remove_all(self, value: Any) -> int:
        """Remove every matching value and return the removal count."""
        kept = []
        removed = 0
        for item in self:
            if item == value:
                removed += 1
            else:
                kept.append(item)
        if removed:
            self._rebuild_from_values(kept)
        return removed

    def replace(
        self,
        old_value: Any,
        new_value: Any,
        count: int | None = None,
    ) -> int:
        """Replace matching values and return how many changed."""
        if count is not None and count <= 0:
            return 0

        replaced = 0
        values = []
        for item in self:
            if item == old_value and (count is None or replaced < count):
                values.append(new_value)
                replaced += 1
            else:
                values.append(item)

        if replaced:
            self._rebuild_from_values(values)
        return replaced

    def remove_duplicates(self) -> None:
        """Remove duplicate values while preserving first occurrences."""
        seen_hashable: set[Any] = set()
        seen_unhashable: list[Any] = []
        unique_values = []

        for value in self:
            try:
                if value in seen_hashable:
                    continue
            except TypeError:
                if any(value == item for item in seen_unhashable):
                    continue
                seen_unhashable.append(value)
            else:
                seen_hashable.add(value)
            unique_values.append(value)

        if len(unique_values) != self._size:
            self._rebuild_from_values(unique_values)

    def clear(self) -> None:
        """Remove every block and detach old block links."""
        current = self.head
        while current is not None:
            next_node = current.next
            current.values.clear()
            current.prev = None
            current.next = None
            current = next_node
        self.head = None
        self.tail = None
        self._size = 0

    def reverse(self) -> None:
        """Reverse the visible sequence."""
        self._rebuild_from_values(list(reversed(self.to_list())))

    def rotate(self, steps: int = 1) -> None:
        """Rotate right for positive steps and left for negative steps."""
        if self._size <= 1:
            return
        steps %= self._size
        if steps == 0:
            return
        values = self.to_list()
        self._rebuild_from_values(values[-steps:] + values[:-steps])

    def sort(
        self,
        *,
        reverse: bool = False,
        key: Callable[[Any], Any] | None = None,
    ) -> None:
        """Sort values in place and rebuild blocks after sorting succeeds."""
        sorted_values = sorted(self, key=key, reverse=reverse)
        self._rebuild_from_values(sorted_values)

    def map(
        self: TUnrolledLinkedList,
        func: Callable[[Any], Any],
    ) -> TUnrolledLinkedList:
        """Return a new unrolled list containing mapped values."""
        return self.__class__(
            (func(value) for value in self),
            node_capacity=self.node_capacity,
        )

    def filter(
        self: TUnrolledLinkedList,
        predicate: Callable[[Any], bool],
    ) -> TUnrolledLinkedList:
        """Return a new unrolled list with accepted values."""
        return self.__class__(
            (value for value in self if predicate(value)),
            node_capacity=self.node_capacity,
        )

    def reduce(
        self,
        func: Callable[[Any, Any], Any],
        initializer: Any = _MISSING,
    ) -> Any:
        """Reduce the sequence with ``func`` and an optional initializer."""
        if initializer is _MISSING:
            return functools_reduce(func, self)
        return functools_reduce(func, self, initializer)

    def _append_node(self, node: _UnrolledNode) -> None:
        """Append a block node to the right side."""
        if self.tail is None:
            self.head = self.tail = node
            return
        node.prev = self.tail
        self.tail.next = node
        self.tail = node

    def _insert_node_after(
        self,
        node: _UnrolledNode,
        new_node: _UnrolledNode,
    ) -> None:
        """Insert ``new_node`` immediately after ``node``."""
        next_node = node.next
        new_node.prev = node
        new_node.next = next_node
        node.next = new_node
        if next_node is None:
            self.tail = new_node
        else:
            next_node.prev = new_node

    def _split_node(self, node: _UnrolledNode) -> _UnrolledNode:
        """Split a full block and return the new right-side block.

        The left block keeps the first half of the values and the new block
        receives the second half. Inserting after the split then happens inside
        whichever block contains the requested offset.
        """
        midpoint = (len(node.values) + 1) // 2
        right_values = node.values[midpoint:]
        node.values = node.values[:midpoint]
        new_node = _UnrolledNode(right_values)
        self._insert_node_after(node, new_node)
        return new_node

    def _unlink_node(self, node: _UnrolledNode) -> None:
        """Detach ``node`` from the block chain."""
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
        node.values.clear()

    def _rebalance_after_remove(self, node: _UnrolledNode) -> None:
        """Merge or borrow around an underfilled block after deletion.

        Empty blocks are removed immediately. Small non-empty blocks first try
        to merge with a neighbor. If merging would overfill a block, they try
        to borrow one value from a fuller neighbor instead.
        """
        if not node.values:
            self._unlink_node(node)
            return
        if self.head is self.tail:
            return

        minimum = (self.node_capacity + 1) // 2
        if len(node.values) >= minimum:
            return

        if (
            node.next is not None
            and len(node.values) + len(node.next.values) <= self.node_capacity
        ):
            node.values.extend(node.next.values)
            self._unlink_node(node.next)
            return

        if (
            node.prev is not None
            and len(node.prev.values) + len(node.values) <= self.node_capacity
        ):
            node.prev.values.extend(node.values)
            self._unlink_node(node)
            return

        if node.next is not None and len(node.next.values) > minimum:
            node.values.append(node.next.values.pop(0))
            return

        if node.prev is not None and len(node.prev.values) > minimum:
            node.values.insert(0, node.prev.values.pop())

    def _locate(self, index: int) -> tuple[_UnrolledNode, int]:
        """Return the block and in-block offset for ``index``.

        The search starts from the closer end of the block chain. The returned
        offset is the normal Python-list index inside that block's values.
        """
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")

        if index < self._size // 2:
            current = self.head
            seen = 0
            while current is not None:
                next_seen = seen + len(current.values)
                if index < next_seen:
                    return current, index - seen
                seen = next_seen
                current = current.next
        else:
            current = self.tail
            seen = self._size
            while current is not None:
                seen -= len(current.values)
                if index >= seen:
                    return current, index - seen
                current = current.prev

        raise RuntimeError("Unrolled list index could not be located")

    def _rebuild_from_values(self, values: Iterable[Any]) -> None:
        """Replace all blocks with values from ``values``."""
        snapshot = list(values)
        self.clear()
        for value in snapshot:
            self.append(value)
