"""Self-organizing linked-list container.

Self-organizing lists adapt their order after successful searches. Frequently
accessed values drift toward the front so later linear searches can be faster
for skewed access patterns.

This structure is not about improving the worst-case O(n) bound. It is about
adapting to real access patterns. If a few values are searched often,
strategies such as move-to-front or frequency-count make those values cheaper
to find later.
"""

from collections.abc import Callable, Iterable, Iterator
from copy import deepcopy
from functools import reduce as functools_reduce
from operator import index as to_index
from reprlib import recursive_repr
from typing import Any, Generic, SupportsIndex, TypeVar

from ._display import safe_repr_item, safe_str_item

T = TypeVar("T")
TSelfOrganizingLinkedList = TypeVar(
    "TSelfOrganizingLinkedList",
    bound="SelfOrganizingLinkedList",
)

_MISSING = object()


class _SelfOrganizingNode:
    """Store one value, access count, and neighboring links."""

    __slots__ = ("access_count", "data", "next", "prev")

    def __init__(self, data: Any) -> None:
        """Initialize a node with zero recorded accesses."""
        self.data: Any = data
        self.access_count: int = 0
        self.prev: _SelfOrganizingNode | None = None
        self.next: _SelfOrganizingNode | None = None

    @recursive_repr()
    def __repr__(self) -> str:
        """Return a compact debugging representation."""
        return (
            "_SelfOrganizingNode("
            f"data={safe_repr_item(self, self.data)}, "
            f"access_count={self.access_count})"
        )


class SelfOrganizingLinkedList(Generic[T]):
    """Linked list that reorganizes itself after successful access.

    ``find``, ``search``, and ``access`` are adaptive operations: they record a
    successful access and may move a node. Static reads such as membership,
    indexing, and ``get`` intentionally do not reorganize the list.
    """

    VALID_STRATEGIES = {
        "move_to_front",
        "transpose",
        "frequency_count",
        "none",
    }

    def __init__(
        self,
        iterable: Iterable[Any] | None = None,
        *,
        strategy: str = "move_to_front",
    ) -> None:
        """Initialize an empty self-organizing list."""
        self._validate_strategy(strategy)
        self.strategy: str = strategy
        self.head: _SelfOrganizingNode | None = None
        self.tail: _SelfOrganizingNode | None = None
        self._size: int = 0

        if iterable is not None:
            self.extend(iterable)

    def __len__(self) -> int:
        """Return the number of stored values."""
        return self._size

    def __bool__(self) -> bool:
        """Return whether at least one value is stored."""
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
        """Return whether ``value`` appears without reorganizing."""
        return any(item == value for item in self)

    def __getitem__(self, index: int | SupportsIndex | slice) -> Any:
        """Return a value or sliced self-organizing list without access."""
        if isinstance(index, slice):
            return self.__class__(
                list(self)[index],
                strategy=self.strategy,
            )
        try:
            return self._node_at(index).data
        except TypeError:
            raise TypeError("Index must be int or slice") from None

    def __setitem__(self, index: int | SupportsIndex, value: Any) -> None:
        """Replace a value without reorganizing."""
        self._node_at(index).data = value

    def __eq__(self, other: object) -> bool:
        """Compare by concrete type, strategy, values, and counts."""
        if type(other) is not type(self):
            return False
        if self.strategy != other.strategy:
            return False
        return self.to_access_counts() == other.to_access_counts()

    @recursive_repr()
    def __repr__(self) -> str:
        """Return a debugging representation."""
        values = ", ".join(safe_repr_item(self, value) for value in self)
        return (
            f"{self.__class__.__name__}("
            f"[{values}], strategy={self.strategy!r})"
        )

    @recursive_repr()
    def __str__(self) -> str:
        """Return a readable arrow-separated representation."""
        if self._size == 0:
            return "[]"
        return " -> ".join(safe_str_item(self, value) for value in self)

    @classmethod
    def from_iterable(
        cls: type[TSelfOrganizingLinkedList],
        iterable: Iterable[Any],
        *,
        strategy: str = "move_to_front",
    ) -> TSelfOrganizingLinkedList:
        """Build a self-organizing list from any iterable."""
        return cls(iterable, strategy=strategy)

    def is_empty(self) -> bool:
        """Return whether no values are stored."""
        return self._size == 0

    def to_list(self) -> list[Any]:
        """Return visible values in current order."""
        return list(self)

    def to_access_counts(self) -> list[tuple[Any, int]]:
        """Return ``(value, access_count)`` pairs in current order."""
        return [(node.data, node.access_count) for node in self._nodes()]

    def copy(
        self: TSelfOrganizingLinkedList,
        *,
        preserve_counts: bool = True,
    ) -> TSelfOrganizingLinkedList:
        """Return a shallow copy, optionally preserving access counts."""
        copied = self.__class__(strategy=self.strategy)
        for node in self._nodes():
            new_node = copied.append(node.data)
            if preserve_counts:
                new_node.access_count = node.access_count
        return copied

    def deep_copy(
        self: TSelfOrganizingLinkedList,
        *,
        preserve_counts: bool = True,
    ) -> TSelfOrganizingLinkedList:
        """Return a deep copy of values and optional counts."""
        copied = self.__class__(strategy=self.strategy)
        for node in self._nodes():
            new_node = copied.append(deepcopy(node.data))
            if preserve_counts:
                new_node.access_count = node.access_count
        return copied

    def set_strategy(self, strategy: str) -> None:
        """Change the future reorganization strategy."""
        self._validate_strategy(strategy)
        self.strategy = strategy
        if strategy == "frequency_count":
            self._reorder_by_frequency()

    def append(self, value: Any) -> _SelfOrganizingNode:
        """Append a value and return the new node."""
        node = _SelfOrganizingNode(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self._size += 1
        return node

    def prepend(self, value: Any) -> _SelfOrganizingNode:
        """Prepend a value and return the new node."""
        node = _SelfOrganizingNode(value)
        if self.head is None:
            self.head = self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self._size += 1
        return node

    def insert(
        self,
        index: int | SupportsIndex,
        value: Any,
    ) -> _SelfOrganizingNode:
        """Insert ``value`` before ``index``."""
        index = to_index(index)
        if index < 0:
            index += self._size
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")
        if index == 0:
            return self.prepend(value)
        if index == self._size:
            return self.append(value)

        target = self._node_at(index)
        previous = target.prev
        assert previous is not None
        node = _SelfOrganizingNode(value)
        self._link_between(node, previous, target)
        self._size += 1
        return node

    def extend(self, iterable: Iterable[Any]) -> None:
        """Append every value from ``iterable``."""
        if iterable is self:
            iterable = list(iterable)
        for value in iterable:
            self.append(value)

    def merge(self, iterable: Iterable[Any]) -> None:
        """Append values from another iterable."""
        self.extend(iterable)

    def access(self, index: int | SupportsIndex) -> Any:
        """Read by index, increment count, and reorganize."""
        node = self._node_at(index)
        value = node.data
        self._record_access(node)
        return value

    def search(self, value: Any, default: Any = None) -> Any:
        """Return matching stored value and reorganize, or ``default``."""
        node, _ = self._find_node(value)
        if node is None:
            return default
        stored_value = node.data
        self._record_access(node)
        return stored_value

    def find(self, value: Any) -> int | None:
        """Return pre-access index of ``value`` and reorganize on success."""
        node, index = self._find_node(value)
        if node is None:
            return None
        self._record_access(node)
        return index

    def index(self, value: Any) -> int:
        """Return pre-access index of ``value`` or raise ``ValueError``."""
        index = self.find(value)
        if index is None:
            raise ValueError(f"{value!r} is not in self-organizing list")
        return index

    def contains_static(self, value: Any) -> bool:
        """Return membership without changing order or access counts."""
        return value in self

    def peek_front(self) -> Any:
        """Return the first value without reorganizing."""
        if self.head is None:
            raise IndexError("Peek from empty self-organizing list")
        return self.head.data

    def peek_back(self) -> Any:
        """Return the final value without reorganizing."""
        if self.tail is None:
            raise IndexError("Peek from empty self-organizing list")
        return self.tail.data

    def get(self, index: int | SupportsIndex, default: Any = None) -> Any:
        """Return a value by index without reorganizing."""
        try:
            return self[index]
        except IndexError:
            return default

    def count(self, value: Any) -> int:
        """Return how many stored values equal ``value``."""
        return sum(1 for item in self if item == value)

    def access_count(self, value: Any) -> int | None:
        """Return the first matching node's access count."""
        node, _ = self._find_node(value)
        if node is None:
            return None
        return node.access_count

    def reset_counts(self) -> None:
        """Reset every node's access count to zero."""
        for node in self._nodes():
            node.access_count = 0

    def remove(self, value: Any) -> bool:
        """Remove the first matching value without reorganizing."""
        node, _ = self._find_node(value)
        if node is None:
            return False
        self._unlink_node(node)
        return True

    def remove_all(self, value: Any) -> int:
        """Remove all matching values and return how many changed."""
        removed = 0
        current = self.head
        while current is not None:
            next_node = current.next
            if current.data == value:
                self._unlink_node(current)
                removed += 1
            current = next_node
        return removed

    def remove_at(self, index: int | SupportsIndex) -> Any:
        """Remove and return the value at ``index``."""
        return self._unlink_node(self._node_at(index))

    def pop_front(self) -> Any:
        """Remove and return the first value."""
        if self.head is None:
            raise IndexError("Pop from empty self-organizing list")
        return self._unlink_node(self.head)

    def pop(self) -> Any:
        """Remove and return the final value."""
        if self.tail is None:
            raise IndexError("Pop from empty self-organizing list")
        return self._unlink_node(self.tail)

    def replace(
        self,
        old_value: Any,
        new_value: Any,
        count: int | SupportsIndex | None = None,
    ) -> int:
        """Replace matching values and return how many changed."""
        if count is not None:
            count = to_index(count)
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

    def remove_duplicates(self) -> None:
        """Remove duplicate values while keeping first visible occurrences."""
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

    def clear(self) -> None:
        """Remove every node and reset state."""
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
        """Reverse node order while preserving counts."""
        current = self.head
        while current is not None:
            current.prev, current.next = current.next, current.prev
            current = current.prev
        self.head, self.tail = self.tail, self.head

    def rotate(self, steps: int | SupportsIndex = 1) -> None:
        """Rotate right for positive steps and left for negative steps."""
        steps = to_index(steps)
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
        """Sort node order by value while preserving access counts."""
        nodes = list(self._nodes())
        nodes.sort(
            key=lambda node: key(node.data) if key is not None else node.data,
            reverse=reverse,
        )
        self._relink_nodes(nodes)

    def map(
        self: TSelfOrganizingLinkedList,
        func: Callable[[Any], Any],
    ) -> TSelfOrganizingLinkedList:
        """Return a new list with mapped values and reset counts."""
        return self.__class__(
            (func(value) for value in self),
            strategy=self.strategy,
        )

    def filter(
        self: TSelfOrganizingLinkedList,
        predicate: Callable[[Any], bool],
    ) -> TSelfOrganizingLinkedList:
        """Return a new list with accepted values and reset counts."""
        return self.__class__(
            (value for value in self if predicate(value)),
            strategy=self.strategy,
        )

    def reduce(
        self,
        func: Callable[[Any, Any], Any],
        initializer: Any = _MISSING,
    ) -> Any:
        """Reduce values with ``func``."""
        if initializer is _MISSING:
            return functools_reduce(func, self)
        return functools_reduce(func, self, initializer)

    def _record_access(self, node: _SelfOrganizingNode) -> None:
        """Increment count and apply the selected strategy.

        Keeping strategy dispatch in one method makes the adaptive behavior
        easy to audit. Every successful adaptive read records the count first,
        then applies exactly one reordering rule.
        """
        node.access_count += 1
        if self.strategy == "move_to_front":
            self._move_to_front(node)
        elif self.strategy == "transpose":
            self._transpose(node)
        elif self.strategy == "frequency_count":
            self._bubble_by_frequency(node)

    def _move_to_front(self, node: _SelfOrganizingNode) -> None:
        """Move ``node`` to the head."""
        if node is self.head:
            return
        self._detach_node(node)
        node.prev = None
        node.next = self.head
        assert self.head is not None
        self.head.prev = node
        self.head = node

    def _transpose(self, node: _SelfOrganizingNode) -> None:
        """Swap ``node`` with its previous neighbor by relinking."""
        previous = node.prev
        if previous is None:
            return
        before_previous = previous.prev
        after_node = node.next

        node.prev = before_previous
        node.next = previous
        previous.prev = node
        previous.next = after_node

        if before_previous is None:
            self.head = node
        else:
            before_previous.next = node

        if after_node is None:
            self.tail = previous
        else:
            after_node.prev = previous

    def _bubble_by_frequency(self, node: _SelfOrganizingNode) -> None:
        """Move ``node`` left until frequency order is restored.

        Frequency-count ordering is local: after a node's count increases, only
        that node can be out of place, so it bubbles left past lower-frequency
        predecessors.
        """
        while (
            node.prev is not None
            and node.access_count > node.prev.access_count
        ):
            self._transpose(node)

    def _reorder_by_frequency(self) -> None:
        """Sort nodes by descending access count."""
        nodes = list(self._nodes())
        nodes.sort(key=lambda node: node.access_count, reverse=True)
        self._relink_nodes(nodes)

    def _find_node(
        self,
        value: Any,
    ) -> tuple[_SelfOrganizingNode | None, int | None]:
        """Return first matching node plus its current index."""
        current = self.head
        index = 0
        while current is not None:
            if current.data == value:
                return current, index
            current = current.next
            index += 1
        return None, None

    def _nodes(self) -> Iterator[_SelfOrganizingNode]:
        """Yield nodes from head to tail."""
        current = self.head
        remaining = self._size
        while current is not None and remaining > 0:
            yield current
            current = current.next
            remaining -= 1

    def _node_at(
        self,
        index: int | SupportsIndex,
    ) -> _SelfOrganizingNode:
        """Return the node at ``index``."""
        index = to_index(index)
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
        node: _SelfOrganizingNode,
        previous: _SelfOrganizingNode,
        next_node: _SelfOrganizingNode,
    ) -> None:
        """Link ``node`` between existing neighbors."""
        node.prev = previous
        node.next = next_node
        previous.next = node
        next_node.prev = node

    def _detach_node(self, node: _SelfOrganizingNode) -> None:
        """Detach ``node`` from the chain without changing size."""
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

    def _unlink_node(self, node: _SelfOrganizingNode) -> Any:
        """Detach ``node`` and return its value."""
        self._detach_node(node)
        self._size -= 1
        return node.data

    def _relink_nodes(self, nodes: list[_SelfOrganizingNode]) -> None:
        """Relink existing nodes in the given order.

        Sorting, rotating, and frequency reordering all preserve node objects
        and their access counts. Only the neighbor links change.
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

    @classmethod
    def _validate_strategy(cls, strategy: str) -> None:
        """Validate a reorganization strategy string."""
        if strategy not in cls.VALID_STRATEGIES:
            valid = ", ".join(sorted(cls.VALID_STRATEGIES))
            raise ValueError(f"strategy must be one of: {valid}")
