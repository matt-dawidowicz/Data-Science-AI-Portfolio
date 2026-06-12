"""Positional linked-list container.

A positional list exposes stable position objects instead of making callers
repeatedly search by index. That is useful when code already has a reference
to a location and wants to insert, remove, or replace values around it.

The educational idea is the difference between an index and a position. An
index is a number that can mean a different node after insertions or removals.
A ``Position`` is a validated handle to a specific node. As long as that node
remains in the same list, the handle stays meaningful even if the node moves.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from copy import deepcopy
from functools import reduce as functools_reduce
from typing import Any, TypeVar

TPositionalLinkedList = TypeVar(
    "TPositionalLinkedList",
    bound="PositionalLinkedList",
)

_MISSING = object()


class _PositionNode:
    """Store one value plus doubly linked neighbors and owner metadata.

    ``owner`` lets the public ``Position`` object detect stale handles. When a
    node is deleted or a list is cleared, the node owner becomes ``None``.
    """

    __slots__ = ("data", "next", "owner", "prev")

    def __init__(self, data: Any, owner: PositionalLinkedList) -> None:
        """Initialize a node owned by one positional list."""
        self.data: Any = data
        self.owner: PositionalLinkedList | None = owner
        self.prev: _PositionNode | None = None
        self.next: _PositionNode | None = None

    def __repr__(self) -> str:
        """Return a compact node representation."""
        return f"_PositionNode({self.data!r})"


class Position:
    """Stable handle to a node inside a ``PositionalLinkedList``.

    Users interact with positions instead of raw nodes. That keeps the node
    implementation private while still giving callers a way to say "insert
    before this exact location" or "move this exact node to the front."
    """

    __slots__ = ("_container", "_node")

    def __init__(
        self,
        container: PositionalLinkedList | None,
        node: _PositionNode | None,
    ) -> None:
        """Initialize a handle to ``node`` inside ``container``."""
        self._container: PositionalLinkedList | None = container
        self._node: _PositionNode | None = node

    @property
    def data(self) -> Any:
        """Return the value stored at this position."""
        if self._node is None or self._node.owner is None:
            raise ValueError("Position is no longer valid")
        return self._node.data

    def is_valid(self) -> bool:
        """Return whether this position still belongs to a live list."""
        return (
            self._container is not None
            and self._node is not None
            and self._node.owner is self._container
        )

    def __eq__(self, other: object) -> bool:
        """Compare positions by node identity."""
        if not isinstance(other, Position):
            return False
        return self._node is other._node

    def __repr__(self) -> str:
        """Return a debugging representation."""
        if not self.is_valid():
            return "Position(<invalid>)"
        assert self._node is not None
        return f"Position({self._node.data!r})"


class PositionalLinkedList:
    """Doubly linked list with validated position objects.

    The list stores normal ``head`` and ``tail`` references, but public
    location-aware operations accept ``Position`` objects. Before any such
    operation mutates links, it checks that the position still belongs to this
    exact list.
    """

    def __init__(self, iterable: Iterable[Any] | None = None) -> None:
        """Initialize an empty positional list and optional values."""
        self.head: _PositionNode | None = None
        self.tail: _PositionNode | None = None
        self._size: int = 0

        if iterable is not None:
            self.extend(iterable)

    def __len__(self) -> int:
        """Return the number of stored values."""
        return self._size

    def __bool__(self) -> bool:
        """Return whether the list has at least one value."""
        return self._size > 0

    def __iter__(self) -> Iterator[Any]:
        """Yield values from head to tail."""
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            yield current.data
            current = current.next
            remaining -= 1

    def __reversed__(self) -> Iterator[Any]:
        """Yield values from tail to head."""
        current = self.tail
        remaining = self._size
        while current is not None and remaining > 0:
            yield current.data
            current = current.prev
            remaining -= 1

    def __contains__(self, value: Any) -> bool:
        """Return whether ``value`` appears in the list."""
        return any(item == value for item in self)

    def __getitem__(self, index: int | slice) -> Any:
        """Return a value or sliced positional list."""
        if isinstance(index, int):
            return self._node_at(index).data
        if isinstance(index, slice):
            return self.__class__(list(self)[index])
        raise TypeError("Index must be int or slice")

    def __setitem__(self, index: int, value: Any) -> None:
        """Replace a value by numeric index."""
        self._node_at(index).data = value

    def __eq__(self, other: object) -> bool:
        """Compare positional lists by concrete type and visible values."""
        if type(other) is not type(self):
            return False
        if len(self) != len(other):
            return False
        return all(
            left == right for left, right in zip(self, other, strict=False)
        )

    def __repr__(self) -> str:
        """Return a debugging representation."""
        return f"{self.__class__.__name__}({self.to_list()!r})"

    def __str__(self) -> str:
        """Return a readable arrow-separated representation."""
        return " <-> ".join(str(value) for value in self)

    @classmethod
    def from_iterable(
        cls: type[TPositionalLinkedList],
        iterable: Iterable[Any],
    ) -> TPositionalLinkedList:
        """Build a positional list from any iterable."""
        return cls(iterable)

    def is_empty(self) -> bool:
        """Return whether no values are stored."""
        return self._size == 0

    def to_list(self) -> list[Any]:
        """Return all values as a Python list."""
        return list(self)

    def positions(self) -> Iterator[Position]:
        """Yield stable positions from head to tail."""
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            yield Position(self, current)
            current = current.next
            remaining -= 1

    def first_position(self) -> Position | None:
        """Return the first position or ``None`` when empty."""
        if self.head is None:
            return None
        return Position(self, self.head)

    def last_position(self) -> Position | None:
        """Return the final position or ``None`` when empty."""
        if self.tail is None:
            return None
        return Position(self, self.tail)

    def position_at(self, index: int) -> Position:
        """Return the position at ``index``."""
        return Position(self, self._node_at(index))

    def before(self, position: Position) -> Position | None:
        """Return the position before ``position``."""
        node = self._validate_position(position)
        if node.prev is None:
            return None
        return Position(self, node.prev)

    def after(self, position: Position) -> Position | None:
        """Return the position after ``position``."""
        node = self._validate_position(position)
        if node.next is None:
            return None
        return Position(self, node.next)

    def add_first(self, value: Any) -> Position:
        """Insert ``value`` at the head and return its position."""
        node = _PositionNode(value, self)
        node.next = self.head
        if self.head is None:
            self.tail = node
        else:
            self.head.prev = node
        self.head = node
        self._size += 1
        return Position(self, node)

    def add_last(self, value: Any) -> Position:
        """Insert ``value`` at the tail and return its position."""
        node = _PositionNode(value, self)
        node.prev = self.tail
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self._size += 1
        return Position(self, node)

    def add_before(self, position: Position, value: Any) -> Position:
        """Insert ``value`` before ``position``."""
        target = self._validate_position(position)
        if target.prev is None:
            return self.add_first(value)
        node = _PositionNode(value, self)
        self._link_between(node, target.prev, target)
        self._size += 1
        return Position(self, node)

    def add_after(self, position: Position, value: Any) -> Position:
        """Insert ``value`` after ``position``."""
        target = self._validate_position(position)
        if target.next is None:
            return self.add_last(value)
        node = _PositionNode(value, self)
        self._link_between(node, target, target.next)
        self._size += 1
        return Position(self, node)

    def append(self, value: Any) -> Position:
        """Append ``value`` and return its position."""
        return self.add_last(value)

    def prepend(self, value: Any) -> Position:
        """Prepend ``value`` and return its position."""
        return self.add_first(value)

    def insert(self, index: int, value: Any) -> Position:
        """Insert ``value`` before ``index``."""
        if index < 0:
            index += self._size
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")
        if index == 0:
            return self.add_first(value)
        if index == self._size:
            return self.add_last(value)
        return self.add_before(self.position_at(index), value)

    def extend(self, iterable: Iterable[Any]) -> None:
        """Append every value from ``iterable``."""
        if iterable is self:
            iterable = list(iterable)
        for value in iterable:
            self.add_last(value)

    def merge(self, iterable: Iterable[Any]) -> None:
        """Append all values from another iterable."""
        self.extend(iterable)

    def delete(self, position: Position) -> Any:
        """Remove ``position`` and return its value."""
        node = self._validate_position(position)
        value = self._unlink_node(node)
        position._node = None
        position._container = None
        return value

    def replace(self, position: Position, value: Any) -> Any:
        """Replace ``position``'s value and return the old value."""
        node = self._validate_position(position)
        old_value = node.data
        node.data = value
        return old_value

    def replace_value(
        self,
        old_value: Any,
        new_value: Any,
        count: int | None = None,
    ) -> int:
        """Replace matching values and return how many changed."""
        if count is not None and count <= 0:
            return 0
        replaced = 0
        current = self.head
        while current is not None:
            if current.data == old_value:
                current.data = new_value
                replaced += 1
                if count is not None and replaced == count:
                    break
            current = current.next
        return replaced

    def remove(self, value: Any) -> bool:
        """Remove the first matching value."""
        position = self.find(value)
        if position is None:
            return False
        self.delete(position)
        return True

    def remove_all(self, value: Any) -> int:
        """Remove all matching values and return the removal count."""
        removed = 0
        current = self.head
        while current is not None:
            next_node = current.next
            if current.data == value:
                self._unlink_node(current)
                removed += 1
            current = next_node
        return removed

    def remove_at(self, index: int) -> Any:
        """Remove and return a value by index."""
        return self.delete(self.position_at(index))

    def pop_first(self) -> Any:
        """Remove and return the first value."""
        if self.head is None:
            raise IndexError("Pop from empty positional list")
        return self._unlink_node(self.head)

    def pop_last(self) -> Any:
        """Remove and return the final value."""
        if self.tail is None:
            raise IndexError("Pop from empty positional list")
        return self._unlink_node(self.tail)

    def peek_front(self) -> Any:
        """Return the first value without removing it."""
        if self.head is None:
            raise IndexError("Peek from empty positional list")
        return self.head.data

    def peek_back(self) -> Any:
        """Return the final value without removing it."""
        if self.tail is None:
            raise IndexError("Peek from empty positional list")
        return self.tail.data

    def get(self, index: int, default: Any = None) -> Any:
        """Return a value by index, or ``default`` if missing."""
        try:
            return self[index]
        except IndexError:
            return default

    def find(self, value: Any) -> Position | None:
        """Return the first position storing ``value``."""
        current = self.head
        while current is not None:
            if current.data == value:
                return Position(self, current)
            current = current.next
        return None

    def index(self, value: Any) -> int:
        """Return the numeric index of ``value``."""
        for index, item in enumerate(self):
            if item == value:
                return index
        raise ValueError(f"{value!r} is not in positional list")

    def count(self, value: Any) -> int:
        """Return how many values equal ``value``."""
        return sum(1 for item in self if item == value)

    def move_to_front(self, position: Position) -> None:
        """Move ``position``'s node to the head."""
        node = self._validate_position(position)
        if node is self.head:
            return
        self._detach_node(node)
        node.prev = None
        node.next = self.head
        assert self.head is not None
        self.head.prev = node
        self.head = node

    def move_to_back(self, position: Position) -> None:
        """Move ``position``'s node to the tail."""
        node = self._validate_position(position)
        if node is self.tail:
            return
        self._detach_node(node)
        node.prev = self.tail
        node.next = None
        assert self.tail is not None
        self.tail.next = node
        self.tail = node

    def move_before(self, position: Position, target: Position) -> None:
        """Move ``position`` so it appears before ``target``."""
        node = self._validate_position(position)
        target_node = self._validate_position(target)
        if node is target_node:
            return
        if node.next is target_node:
            return
        self._detach_node(node)
        previous = target_node.prev
        if previous is None:
            node.prev = None
            node.next = target_node
            target_node.prev = node
            self.head = node
        else:
            self._link_between(node, previous, target_node)

    def move_after(self, position: Position, target: Position) -> None:
        """Move ``position`` so it appears after ``target``."""
        node = self._validate_position(position)
        target_node = self._validate_position(target)
        if node is target_node:
            return
        if target_node.next is node:
            return
        self._detach_node(node)
        next_node = target_node.next
        if next_node is None:
            node.prev = target_node
            node.next = None
            target_node.next = node
            self.tail = node
        else:
            self._link_between(node, target_node, next_node)

    def swap(self, first: Position, second: Position) -> None:
        """Swap the values at two positions."""
        first_node = self._validate_position(first)
        second_node = self._validate_position(second)
        first_node.data, second_node.data = second_node.data, first_node.data

    def clear(self) -> None:
        """Remove every node and invalidate node ownership."""
        current = self.head
        while current is not None:
            next_node = current.next
            current.owner = None
            current.prev = None
            current.next = None
            current = next_node
        self.head = None
        self.tail = None
        self._size = 0

    def reverse(self) -> None:
        """Reverse node order in place."""
        current = self.head
        while current is not None:
            current.prev, current.next = current.next, current.prev
            current = current.prev
        self.head, self.tail = self.tail, self.head

    def rotate(self, steps: int = 1) -> None:
        """Rotate right for positive steps and left for negative steps."""
        if self._size <= 1:
            return
        steps %= self._size
        if steps == 0:
            return
        nodes = list(self._nodes())
        self._relink_nodes(nodes[-steps:] + nodes[:-steps])

    def sort(
        self,
        *,
        reverse: bool = False,
        key: Callable[[Any], Any] | None = None,
    ) -> None:
        """Sort node order after comparisons succeed."""
        nodes = list(self._nodes())
        nodes.sort(
            key=lambda node: key(node.data) if key is not None else node.data,
            reverse=reverse,
        )
        self._relink_nodes(nodes)

    def remove_duplicates(self) -> None:
        """Remove duplicate values while preserving first occurrences."""
        seen_hashable: set[Any] = set()
        seen_unhashable: list[Any] = []
        current = self.head
        while current is not None:
            next_node = current.next
            data = current.data
            try:
                if data in seen_hashable:
                    self._unlink_node(current)
                else:
                    seen_hashable.add(data)
            except TypeError:
                if any(data == item for item in seen_unhashable):
                    self._unlink_node(current)
                else:
                    seen_unhashable.append(data)
            current = next_node

    def copy(self: TPositionalLinkedList) -> TPositionalLinkedList:
        """Return a shallow copy."""
        return self.__class__(self)

    def deep_copy(self: TPositionalLinkedList) -> TPositionalLinkedList:
        """Return a deep copy of stored values."""
        return self.__class__(deepcopy(value) for value in self)

    def map(
        self: TPositionalLinkedList,
        func: Callable[[Any], Any],
    ) -> TPositionalLinkedList:
        """Return a new positional list containing mapped values."""
        return self.__class__(func(value) for value in self)

    def filter(
        self: TPositionalLinkedList,
        predicate: Callable[[Any], bool],
    ) -> TPositionalLinkedList:
        """Return a new positional list with accepted values."""
        return self.__class__(value for value in self if predicate(value))

    def reduce(
        self,
        func: Callable[[Any, Any], Any],
        initializer: Any = _MISSING,
    ) -> Any:
        """Reduce values with ``func``."""
        if initializer is _MISSING:
            return functools_reduce(func, self)
        return functools_reduce(func, self, initializer)

    def _validate_position(self, position: Position) -> _PositionNode:
        """Return the node for a live position in this list.

        This method is the safety gate for every position-based mutation. It
        rejects non-position objects, stale positions, and positions from other
        lists before any links are changed.
        """
        if not isinstance(position, Position):
            raise TypeError("position must be a Position")
        node = position._node
        if (
            position._container is not self
            or node is None
            or node.owner is not self
        ):
            raise ValueError("Position does not belong to this list")
        return node

    def _nodes(self) -> Iterator[_PositionNode]:
        """Yield nodes from head to tail."""
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            yield current
            current = current.next
            remaining -= 1

    def _node_at(self, index: int) -> _PositionNode:
        """Return the node at ``index``."""
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

    def _link_between(
        self,
        node: _PositionNode,
        previous: _PositionNode,
        next_node: _PositionNode,
    ) -> None:
        """Link ``node`` between two existing neighbors."""
        node.prev = previous
        node.next = next_node
        previous.next = node
        next_node.prev = node

    def _detach_node(self, node: _PositionNode) -> None:
        """Detach ``node`` from the chain without changing size.

        Moving a node uses this helper because the node should remain alive and
        owned by the list. Deleting uses ``_unlink_node`` instead.
        """
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

    def _unlink_node(self, node: _PositionNode) -> Any:
        """Detach ``node``, invalidate ownership, and return its value.

        Invalidating ownership is what turns old positions into stale handles.
        The public ``delete`` method also clears the specific ``Position``
        object passed by the caller.
        """
        self._detach_node(node)
        node.owner = None
        self._size -= 1
        return node.data

    def _relink_nodes(self, nodes: list[_PositionNode]) -> None:
        """Relink existing nodes in the supplied order.

        Sort and rotate preserve node identity by rearranging existing nodes
        rather than creating replacements. Live positions therefore continue
        pointing at the same values after the order changes.
        """
        if not nodes:
            self.head = None
            self.tail = None
            return

        self.head = nodes[0]
        self.tail = nodes[-1]
        for index, node in enumerate(nodes):
            node.prev = nodes[index - 1] if index > 0 else None
            node.next = nodes[index + 1] if index + 1 < len(nodes) else None
            node.owner = self

    pop = pop_last
