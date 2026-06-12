"""Multilevel linked-list container with child links.

A multilevel linked list stores a normal sibling chain through ``next`` links,
and any node may also point to a child chain. This makes it useful for
teaching nested traversal, flattening, and subtree mutation.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Iterator
from copy import deepcopy
from functools import reduce as functools_reduce
from typing import Any, TypeVar

TMultilevelLinkedList = TypeVar(
    "TMultilevelLinkedList",
    bound="MultilevelLinkedList",
)

_MISSING = object()


class _MultilevelNode:
    """Store one value plus sibling and child links."""

    __slots__ = ("child", "data", "next")

    def __init__(self, data: Any) -> None:
        self.data = data
        self.next: _MultilevelNode | None = None
        self.child: _MultilevelNode | None = None

    def __repr__(self) -> str:
        """Return a compact debugging representation."""
        return f"_MultilevelNode({self.data!r})"


class MultilevelLinkedList:
    """Linked list where each node may own a nested child chain.

    Public iteration is depth-first, so ``len(container)``, indexing, and
    ``to_list()`` describe all reachable nodes rather than only the top level.
    Methods with ``child`` in their name preserve and manipulate the nested
    hierarchy directly.
    """

    def __init__(self, iterable: Iterable[Any] | None = None) -> None:
        """Initialize an empty multilevel list with optional top values."""
        self.head: _MultilevelNode | None = None
        self.tail: _MultilevelNode | None = None
        self._size: int = 0

        if iterable is not None:
            self.extend(iterable)

    def __len__(self) -> int:
        """Return the total number of reachable nodes."""
        return self._size

    def __bool__(self) -> bool:
        """Return whether the structure stores at least one node."""
        return self._size > 0

    def __iter__(self) -> Iterator[Any]:
        """Yield values in depth-first order."""
        yield from self.iter_flat()

    def __reversed__(self) -> Iterator[Any]:
        """Yield depth-first values in reverse order."""
        return reversed(self.to_list())

    def __contains__(self, value: Any) -> bool:
        """Return whether ``value`` appears anywhere in the structure."""
        return any(item == value for item in self)

    def __getitem__(self, index: int | slice) -> Any:
        """Return a depth-first value or a flat sliced multilevel list."""
        if isinstance(index, int):
            return self._node_at(index).data

        if isinstance(index, slice):
            return self.__class__(list(self)[index])

        raise TypeError("Index must be int or slice")

    def __setitem__(self, index: int, value: Any) -> None:
        """Replace one node's value by depth-first index."""
        self._node_at(index).data = value

    def __eq__(self, other: object) -> bool:
        """Compare concrete multilevel lists by nested shape and values."""
        if type(other) is not type(self):
            return False
        return self.to_nested_list() == other.to_nested_list()

    def __repr__(self) -> str:
        """Return a debugging representation."""
        return f"{self.__class__.__name__}({self.to_nested_list()!r})"

    def __str__(self) -> str:
        """Return a readable depth-first representation."""
        return " -> ".join(str(value) for value in self)

    @classmethod
    def from_iterable(
        cls: type[TMultilevelLinkedList],
        iterable: Iterable[Any],
    ) -> TMultilevelLinkedList:
        """Build a flat multilevel list from any iterable."""
        return cls(iterable)

    @classmethod
    def from_nested(
        cls: type[TMultilevelLinkedList],
        nested_values: Iterable[Any],
    ) -> TMultilevelLinkedList:
        """Build a multilevel list from ``(value, children)`` pairs.

        Plain values become normal nodes. A two-item tuple whose second item is
        an iterable is interpreted as one node plus that node's child chain.
        """
        new_list = cls()
        for item in nested_values:
            if cls._is_nested_pair(item):
                value, children = item
                node = new_list.append(value)
                child_list = cls.from_nested(children)
                node.child = child_list.head
                new_list._size += child_list._size
            else:
                new_list.append(item)
        return new_list

    def is_empty(self) -> bool:
        """Return whether no nodes are stored."""
        return self._size == 0

    def iter_flat(self, order: str = "depth_first") -> Iterator[Any]:
        """Yield all values using depth-first or breadth-first traversal."""
        if order == "depth_first":
            for node in self._iter_nodes_depth_first():
                yield node.data
            return
        if order == "breadth_first":
            for node in self._iter_nodes_breadth_first():
                yield node.data
            return
        raise ValueError("order must be 'depth_first' or 'breadth_first'")

    def iter_top_level(self) -> Iterator[Any]:
        """Yield only values stored on the top-level sibling chain."""
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def to_list(self, order: str = "depth_first") -> list[Any]:
        """Return all values in the requested traversal order."""
        return list(self.iter_flat(order))

    def to_top_level_list(self) -> list[Any]:
        """Return only the top-level values."""
        return list(self.iter_top_level())

    def to_nested_list(self) -> list[Any]:
        """Return a nested ``[(value, children)]`` style snapshot."""
        return self._nested_from_chain(self.head)

    def copy(self: TMultilevelLinkedList) -> TMultilevelLinkedList:
        """Return a shallow copy preserving hierarchy."""
        return self._clone_with_transform(lambda value: value)

    def deep_copy(self: TMultilevelLinkedList) -> TMultilevelLinkedList:
        """Return a deep copy preserving hierarchy."""
        return self._clone_with_transform(deepcopy)

    def top_level_length(self) -> int:
        """Return how many nodes live on the top-level chain."""
        return sum(1 for _ in self.iter_top_level())

    def append(self, value: Any) -> _MultilevelNode:
        """Append ``value`` to the top-level chain and return its node."""
        node = _MultilevelNode(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1
        return node

    def prepend(self, value: Any) -> _MultilevelNode:
        """Insert ``value`` at the top-level head and return its node."""
        node = _MultilevelNode(value)
        node.next = self.head
        self.head = node
        if self.tail is None:
            self.tail = node
        self._size += 1
        return node

    def extend(self, iterable: Iterable[Any]) -> None:
        """Append every value from ``iterable`` to the top level."""
        if iterable is self:
            iterable = list(iterable)
        for value in iterable:
            self.append(value)

    def merge(self, iterable: Iterable[Any]) -> None:
        """Append top-level values from another iterable."""
        self.extend(iterable)

    def insert(self, index: int, value: Any) -> _MultilevelNode:
        """Insert ``value`` before a depth-first index as a sibling."""
        if index < 0:
            index += self._size
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")
        if index == self._size:
            return self.append(value)

        target, parent, previous = self._reference_at(index)
        node = _MultilevelNode(value)
        node.next = target
        if previous is not None:
            previous.next = node
        elif parent is not None:
            parent.child = node
        else:
            self.head = node
        self._size += 1
        return node

    def append_child(self, parent: Any, value: Any) -> _MultilevelNode:
        """Append ``value`` to a parent's child chain."""
        parent_node = self._resolve_node(parent)
        node = _MultilevelNode(value)
        if parent_node.child is None:
            parent_node.child = node
        else:
            tail = self._chain_tail(parent_node.child)
            tail.next = node
        self._size += 1
        return node

    def prepend_child(self, parent: Any, value: Any) -> _MultilevelNode:
        """Prepend ``value`` to a parent's child chain."""
        parent_node = self._resolve_node(parent)
        node = _MultilevelNode(value)
        node.next = parent_node.child
        parent_node.child = node
        self._size += 1
        return node

    def extend_child(self, parent: Any, iterable: Iterable[Any]) -> None:
        """Append many values to a parent's child chain."""
        parent_node = self._resolve_node(parent)
        values = list(iterable)
        tail = None
        if parent_node.child is not None:
            tail = self._chain_tail(parent_node.child)
        for value in values:
            node = _MultilevelNode(value)
            if tail is None:
                parent_node.child = node
            else:
                tail.next = node
            tail = node
            self._size += 1

    def child_values(self, parent: Any) -> list[Any]:
        """Return direct child values for ``parent``."""
        parent_node = self._resolve_node(parent)
        values = []
        current = parent_node.child
        while current is not None:
            values.append(current.data)
            current = current.next
        return values

    def detach_children(
        self: TMultilevelLinkedList,
        parent: Any,
    ) -> TMultilevelLinkedList:
        """Move a parent's child chain into a new multilevel list."""
        parent_node = self._resolve_node(parent)
        child_head = parent_node.child
        detached = self.__class__()
        if child_head is None:
            return detached

        detached.head = child_head
        detached.tail = self._chain_tail(child_head)
        detached._size = self._chain_size(child_head)
        parent_node.child = None
        self._size -= detached._size
        return detached

    def peek_front(self) -> Any:
        """Return the first depth-first value without removing it."""
        if self.head is None:
            raise IndexError("Peek from empty multilevel linked list")
        return self.head.data

    def peek_back(self) -> Any:
        """Return the final depth-first value without removing it."""
        if self._size == 0:
            raise IndexError("Peek from empty multilevel linked list")
        return self._node_at(self._size - 1).data

    def get(self, index: int, default: Any = None) -> Any:
        """Return a depth-first value, or ``default`` if out of range."""
        try:
            return self[index]
        except IndexError:
            return default

    def count(self, value: Any) -> int:
        """Return the number of matching values."""
        return sum(1 for item in self if item == value)

    def index(self, value: Any) -> int:
        """Return the depth-first index of the first matching value."""
        for position, item in enumerate(self):
            if item == value:
                return position
        raise ValueError(f"{value!r} is not in multilevel linked list")

    def find(self, value: Any) -> int | None:
        """Return the first matching depth-first index or ``None``."""
        try:
            return self.index(value)
        except ValueError:
            return None

    def find_node(self, value: Any) -> _MultilevelNode | None:
        """Return the first node storing ``value``, or ``None``."""
        for node in self._iter_nodes_depth_first():
            if node.data == value:
                return node
        return None

    def path_to(self, value: Any) -> tuple[int, ...] | None:
        """Return sibling indexes from the top level to ``value``."""
        return self._path_from_chain(self.head, value, ())

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
        for node in self._iter_nodes_depth_first():
            if node.data == old_value:
                node.data = new_value
                replaced += 1
                if count is not None and replaced == count:
                    break
        return replaced

    def remove(
        self,
        value: Any,
        *,
        promote_children: bool = False,
    ) -> bool:
        """Remove the first matching node.

        By default, removing a node also removes its child subtree. With
        ``promote_children=True``, the removed node's child chain takes its
        place and remains reachable.
        """
        for node, parent, previous in self._iter_node_references():
            if node.data == value:
                self._remove_reference(
                    node,
                    parent,
                    previous,
                    promote_children=promote_children,
                )
                return True
        return False

    def remove_all(
        self,
        value: Any,
        *,
        promote_children: bool = False,
    ) -> int:
        """Remove every matching node and return the removal count."""
        removed = 0
        while self.remove(value, promote_children=promote_children):
            removed += 1
        return removed

    def remove_at(
        self,
        index: int,
        *,
        promote_children: bool = False,
    ) -> Any:
        """Remove a node by depth-first index and return its value."""
        node, parent, previous = self._reference_at(index)
        value = node.data
        self._remove_reference(
            node,
            parent,
            previous,
            promote_children=promote_children,
        )
        return value

    def pop(self) -> Any:
        """Remove and return the final depth-first value."""
        if self._size == 0:
            raise IndexError("Pop from empty multilevel linked list")
        return self.remove_at(self._size - 1)

    def pop_front(self) -> Any:
        """Remove and return the first depth-first value."""
        if self._size == 0:
            raise IndexError("Pop from empty multilevel linked list")
        return self.remove_at(0, promote_children=True)

    def clear(self) -> None:
        """Remove every node and detach all links."""
        self._detach_chain(self.head)
        self.head = None
        self.tail = None
        self._size = 0

    def flatten(self, order: str = "depth_first") -> None:
        """Flatten the structure in place, preserving node objects."""
        if order == "depth_first":
            nodes = list(self._iter_nodes_depth_first())
        elif order == "breadth_first":
            nodes = list(self._iter_nodes_breadth_first())
        else:
            raise ValueError("order must be 'depth_first' or 'breadth_first'")

        if not nodes:
            return

        for index, node in enumerate(nodes):
            node.child = None
            next_node = nodes[index + 1] if index + 1 < len(nodes) else None
            node.next = next_node
        self.head = nodes[0]
        self.tail = nodes[-1]

    def flattened(
        self: TMultilevelLinkedList,
        order: str = "depth_first",
    ) -> TMultilevelLinkedList:
        """Return a new flat list in the requested traversal order."""
        return self.__class__(self.to_list(order))

    def reverse(self) -> None:
        """Reverse every sibling chain while preserving hierarchy."""
        self.head, self.tail = self._reverse_chain(self.head)

    def rotate(self, steps: int = 1) -> None:
        """Flatten and rotate values right for positive steps."""
        if self._size <= 1:
            return
        steps %= self._size
        if steps == 0:
            return
        values = self.to_list()
        self._rebuild_flat(values[-steps:] + values[:-steps])

    def sort(
        self,
        *,
        reverse: bool = False,
        key: Callable[[Any], Any] | None = None,
    ) -> None:
        """Sort all values and rebuild as a flat top-level list."""
        sorted_values = sorted(self, key=key, reverse=reverse)
        self._rebuild_flat(sorted_values)

    def remove_duplicates(self) -> None:
        """Flatten while preserving the first occurrence of each value."""
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
            self._rebuild_flat(unique_values)

    def map(
        self: TMultilevelLinkedList,
        func: Callable[[Any], Any],
    ) -> TMultilevelLinkedList:
        """Return a new hierarchy with ``func`` applied to every value."""
        return self._clone_with_transform(func)

    def filter(
        self: TMultilevelLinkedList,
        predicate: Callable[[Any], bool],
    ) -> TMultilevelLinkedList:
        """Return a flat list containing values accepted by predicate."""
        return self.__class__(value for value in self if predicate(value))

    def reduce(
        self,
        func: Callable[[Any, Any], Any],
        initializer: Any = _MISSING,
    ) -> Any:
        """Reduce depth-first values with ``func``."""
        if initializer is _MISSING:
            return functools_reduce(func, self)
        return functools_reduce(func, self, initializer)

    def _node_at(self, index: int) -> _MultilevelNode:
        """Return a node by depth-first index."""
        node, _, _ = self._reference_at(index)
        return node

    def _reference_at(
        self,
        index: int,
    ) -> tuple[
        _MultilevelNode,
        _MultilevelNode | None,
        _MultilevelNode | None,
    ]:
        """Return node, parent, and previous sibling by depth-first index."""
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")

        for position, reference in enumerate(self._iter_node_references()):
            if position == index:
                return reference

        raise RuntimeError("Multilevel node index could not be located")

    def _resolve_node(self, node_or_value: Any) -> _MultilevelNode:
        """Return a node from either a node reference or a stored value."""
        if isinstance(node_or_value, _MultilevelNode):
            if self._contains_node(node_or_value):
                return node_or_value
            raise ValueError("Node does not belong to this list")

        node = self.find_node(node_or_value)
        if node is None:
            raise ValueError(f"{node_or_value!r} is not in multilevel list")
        return node

    def _contains_node(self, candidate: _MultilevelNode) -> bool:
        """Return whether ``candidate`` is reachable from ``head``."""
        return any(
            node is candidate for node in self._iter_nodes_depth_first()
        )

    def _remove_reference(
        self,
        node: _MultilevelNode,
        parent: _MultilevelNode | None,
        previous: _MultilevelNode | None,
        *,
        promote_children: bool,
    ) -> None:
        """Remove ``node`` using already-known relationship pointers."""
        next_sibling = node.next
        replacement = next_sibling
        removed_count = self._node_tree_size(node)

        if promote_children and node.child is not None:
            replacement = node.child
            child_tail = self._chain_tail(node.child)
            child_tail.next = next_sibling
            removed_count = 1

        if previous is not None:
            previous.next = replacement
        elif parent is not None:
            parent.child = replacement
        else:
            self.head = replacement

        if parent is None and node is self.tail:
            if promote_children and node.child is not None:
                self.tail = self._chain_tail(node.child)
            else:
                self.tail = previous
        if self.head is None:
            self.tail = None

        child_to_detach = None if promote_children else node.child
        node.next = None
        node.child = None
        self._detach_chain(child_to_detach)
        self._size -= removed_count

    def _rebuild_flat(self, values: Iterable[Any]) -> None:
        """Replace the whole structure with a flat top-level chain."""
        snapshot = list(values)
        self.clear()
        self.extend(snapshot)

    def _clone_with_transform(
        self: TMultilevelLinkedList,
        transform: Callable[[Any], Any],
    ) -> TMultilevelLinkedList:
        """Clone the whole hierarchy while transforming values."""
        new_list = self.__class__()
        head, tail, size = self._clone_chain(self.head, transform)
        new_list.head = head
        new_list.tail = tail
        new_list._size = size
        return new_list

    @classmethod
    def _clone_chain(
        cls,
        node: _MultilevelNode | None,
        transform: Callable[[Any], Any],
    ) -> tuple[_MultilevelNode | None, _MultilevelNode | None, int]:
        """Clone a sibling chain and all child chains."""
        new_head = None
        new_tail = None
        previous = None
        total = 0
        current = node

        while current is not None:
            cloned = _MultilevelNode(transform(current.data))
            child_head, _, child_size = cls._clone_chain(
                current.child,
                transform,
            )
            cloned.child = child_head

            if previous is None:
                new_head = cloned
            else:
                previous.next = cloned
            previous = cloned
            new_tail = cloned
            total += 1 + child_size
            current = current.next

        return new_head, new_tail, total

    def _iter_nodes_depth_first(self) -> Iterator[_MultilevelNode]:
        """Yield nodes in pre-order depth-first traversal."""
        stack: list[_MultilevelNode] = []
        current = self.head
        emitted = 0

        while (current is not None or stack) and emitted < self._size:
            if current is None:
                current = stack.pop()
                continue

            yield current
            emitted += 1
            if current.next is not None:
                stack.append(current.next)
            current = current.child

    def _iter_nodes_breadth_first(self) -> Iterator[_MultilevelNode]:
        """Yield nodes in breadth-first order."""
        queue: deque[_MultilevelNode] = deque()
        current = self.head
        while current is not None:
            queue.append(current)
            current = current.next

        emitted = 0
        while queue and emitted < self._size:
            node = queue.popleft()
            yield node
            emitted += 1

            child = node.child
            while child is not None:
                queue.append(child)
                child = child.next

    def _iter_node_references(
        self,
    ) -> Iterator[
        tuple[_MultilevelNode, _MultilevelNode | None, _MultilevelNode | None]
    ]:
        """Yield each node with its parent and previous sibling."""
        yield from self._references_from_chain(self.head, None)

    def _references_from_chain(
        self,
        node: _MultilevelNode | None,
        parent: _MultilevelNode | None,
    ) -> Iterator[
        tuple[_MultilevelNode, _MultilevelNode | None, _MultilevelNode | None]
    ]:
        """Yield relationship triples for a sibling chain."""
        previous = None
        current = node
        while current is not None:
            yield current, parent, previous
            if current.child is not None:
                yield from self._references_from_chain(current.child, current)
            previous = current
            current = current.next

    def _reverse_chain(
        self,
        node: _MultilevelNode | None,
    ) -> tuple[_MultilevelNode | None, _MultilevelNode | None]:
        """Reverse one sibling chain and all child chains."""
        previous = None
        current = node
        new_tail = node

        while current is not None:
            next_node = current.next
            if current.child is not None:
                child_head, _ = self._reverse_chain(current.child)
                current.child = child_head
            current.next = previous
            previous = current
            current = next_node

        return previous, new_tail

    def _chain_tail(self, node: _MultilevelNode) -> _MultilevelNode:
        """Return the final sibling in ``node``'s chain."""
        current = node
        while current.next is not None:
            current = current.next
        return current

    def _node_tree_size(self, node: _MultilevelNode) -> int:
        """Count ``node`` and all descendants, excluding next siblings."""
        return 1 + self._chain_size(node.child)

    def _chain_size(self, node: _MultilevelNode | None) -> int:
        """Count a sibling chain and all descendants."""
        total = 0
        current = node
        while current is not None:
            total += self._node_tree_size(current)
            current = current.next
        return total

    def _detach_chain(self, node: _MultilevelNode | None) -> None:
        """Detach a sibling chain and all descendants."""
        current = node
        while current is not None:
            next_node = current.next
            child = current.child
            current.next = None
            current.child = None
            self._detach_chain(child)
            current = next_node

    def _nested_from_chain(self, node: _MultilevelNode | None) -> list[Any]:
        """Return a nested snapshot from a sibling chain."""
        nested = []
        current = node
        while current is not None:
            if current.child is None:
                nested.append(current.data)
            else:
                nested.append(
                    (
                        current.data,
                        self._nested_from_chain(current.child),
                    ),
                )
            current = current.next
        return nested

    def _path_from_chain(
        self,
        node: _MultilevelNode | None,
        value: Any,
        prefix: tuple[int, ...],
    ) -> tuple[int, ...] | None:
        """Find ``value`` in a chain and return nested sibling indexes."""
        current = node
        sibling_index = 0
        while current is not None:
            path = (*prefix, sibling_index)
            if current.data == value:
                return path
            child_path = self._path_from_chain(current.child, value, path)
            if child_path is not None:
                return child_path
            sibling_index += 1
            current = current.next
        return None

    @staticmethod
    def _is_nested_pair(value: Any) -> bool:
        """Return whether ``value`` should be parsed as a nested pair."""
        if not isinstance(value, tuple) or len(value) != 2:
            return False
        return isinstance(value[1], Iterable) and not isinstance(
            value[1],
            str | bytes,
        )
