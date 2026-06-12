"""Probabilistic ordered set implemented as a skip list.

A skip list stores values in sorted order across multiple linked levels. The
bottom level contains every value. Higher levels contain random shortcuts that
let search, insertion, and deletion skip over ranges of values on average.

The mental model is "several linked lists stacked on top of each other." A
search starts at the highest active level, moves right while the next value is
still before the target, then drops down one level. By the time the search
reaches level zero, it has skipped much of the bottom chain in typical cases.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from operator import lt
from random import Random
from typing import Any, TypeVar

TSkipList = TypeVar("TSkipList", bound="SkipList")


class _SkipListNode:
    """Store one value plus forward links for its participating levels.

    ``forward[0]`` is the normal bottom-level next pointer. Higher indexes are
    shortcut pointers used only by nodes that were randomly promoted.
    """

    __slots__ = ("data", "forward")

    def __init__(self, data: Any, height: int) -> None:
        """Initialize a node with ``height`` forward levels."""
        self.data = data
        self.forward: list[_SkipListNode | None] = [None] * height

    @property
    def height(self) -> int:
        """Return how many levels this node participates in."""
        return len(self.forward)


class SkipList:
    """Ordered set with average logarithmic search, insert, and remove.

    Values must be mutually comparable with ``<``. Duplicate insertions are
    ignored, so the container behaves like a sorted set rather than a
    duplicate-preserving linked list.

    ``max_level`` caps the number of shortcut layers. ``probability`` controls
    how likely a new node is to be promoted from one level to the next. Tests
    can pass ``seed`` to make the random tower shape reproducible.
    """

    def __init__(
        self,
        iterable: Iterable[Any] | None = None,
        *,
        max_level: int = 16,
        probability: int | float = 0.5,
        seed: int | None = None,
    ) -> None:
        """Initialize an empty skip list and optionally add initial values."""
        if not isinstance(max_level, int) or isinstance(max_level, bool):
            raise TypeError("max_level must be an integer")
        if max_level < 1:
            raise ValueError("max_level must be at least 1")
        if not isinstance(probability, int | float) or isinstance(
            probability,
            bool,
        ):
            raise TypeError("probability must be a real number")
        if not 0 < probability < 1:
            raise ValueError("probability must be between 0 and 1")

        self._max_level: int = max_level
        self._probability: float = float(probability)
        self._random: Random = Random(seed)
        self._head: _SkipListNode = _SkipListNode(None, max_level)
        self._tail: _SkipListNode | None = None
        self._level: int = 1
        self._size: int = 0

        if iterable is not None:
            self.extend(iterable)

    @property
    def max_level(self) -> int:
        """Return the maximum height nodes may reach."""
        return self._max_level

    @property
    def probability(self) -> float:
        """Return the promotion probability used for new nodes."""
        return self._probability

    @property
    def level(self) -> int:
        """Return the current highest active level count."""
        return self._level

    @property
    def head(self) -> _SkipListNode | None:
        """Return the first data node, or ``None`` when empty."""
        return self._head.forward[0]

    @property
    def tail(self) -> _SkipListNode | None:
        """Return the final data node, or ``None`` when empty."""
        return self._tail

    def __len__(self) -> int:
        """Return the number of stored values."""
        return self._size

    def __bool__(self) -> bool:
        """Return whether the skip list contains at least one value."""
        return self._size > 0

    def __iter__(self) -> Iterator[Any]:
        """Yield values in ascending order."""
        current = self._head.forward[0]
        while current is not None:
            yield current.data
            current = current.forward[0]

    def __reversed__(self) -> Iterator[Any]:
        """Yield values in descending order."""
        return reversed(self.to_list())

    def __contains__(self, value: Any) -> bool:
        """Return whether ``value`` is present."""
        return self._find_node(value) is not None

    def __eq__(self, other: object) -> bool:
        """Compare skip lists by their ordered values."""
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
        return " -> ".join(str(value) for value in self)

    @classmethod
    def from_iterable(
        cls: type[TSkipList],
        iterable: Iterable[Any],
        *,
        max_level: int = 16,
        probability: int | float = 0.5,
        seed: int | None = None,
    ) -> TSkipList:
        """Build a skip list from any iterable."""
        return cls(
            iterable,
            max_level=max_level,
            probability=probability,
            seed=seed,
        )

    def is_empty(self) -> bool:
        """Return whether no values are stored."""
        return self._size == 0

    def to_list(self) -> list[Any]:
        """Return all values as a sorted Python list."""
        return list(self)

    def copy(self: TSkipList) -> TSkipList:
        """Return a shallow copy with the same tuning parameters."""
        return self.__class__.from_iterable(
            self,
            max_level=self._max_level,
            probability=self._probability,
        )

    def first(self) -> Any:
        """Return the smallest value without removing it."""
        first_node = self._head.forward[0]
        if first_node is None:
            raise IndexError("First from empty skip list")
        return first_node.data

    def last(self) -> Any:
        """Return the largest value without removing it."""
        if self._tail is None:
            raise IndexError("Last from empty skip list")
        return self._tail.data

    def add(self, value: Any) -> bool:
        """Add ``value`` and return whether a new node was inserted.

        The ``update`` list stores the predecessor at each level. Once the new
        node height is known, insertion is just local pointer splicing on the
        levels the node participates in.
        """
        update = self._find_update(value)
        next_node = update[0].forward[0]
        if next_node is not None and next_node.data == value:
            return False

        node_level = self._random_level()
        if node_level > self._level:
            for level in range(self._level, node_level):
                update[level] = self._head
            self._level = node_level

        new_node = _SkipListNode(value, node_level)
        for level in range(node_level):
            new_node.forward[level] = update[level].forward[level]
            update[level].forward[level] = new_node

        if new_node.forward[0] is None:
            self._tail = new_node
        self._size += 1
        return True

    def extend(self, iterable: Iterable[Any]) -> int:
        """Add all values from ``iterable`` and return new insertions."""
        values = list(self) if iterable is self else list(iterable)
        if not values:
            return 0

        self._validate_values(values)

        added = 0
        for value in values:
            if self.add(value):
                added += 1
        return added

    def update(self, iterable: Iterable[Any]) -> int:
        """Alias for ``extend`` that mirrors set-style naming."""
        return self.extend(iterable)

    def remove(self, value: Any) -> bool:
        """Remove ``value`` and return whether it was present."""
        update = self._find_update(value)
        target = update[0].forward[0]
        if target is None or target.data != value:
            return False

        for level in range(self._level):
            if update[level].forward[level] is target:
                update[level].forward[level] = target.forward[level]

        while self._level > 1 and self._head.forward[self._level - 1] is None:
            self._level -= 1

        self._size -= 1
        if self._size == 0:
            self._tail = None
        elif self._tail is target:
            self._tail = update[0]

        target.forward = []
        return True

    def pop_first(self) -> Any:
        """Remove and return the smallest value."""
        value = self.first()
        self.remove(value)
        return value

    def pop_last(self) -> Any:
        """Remove and return the largest value."""
        value = self.last()
        self.remove(value)
        return value

    def discard(self, value: Any) -> bool:
        """Alias for ``remove`` that returns whether anything changed."""
        return self.remove(value)

    def clear(self) -> None:
        """Remove every value and reset the active height."""
        current = self._head.forward[0]
        while current is not None:
            next_node = current.forward[0]
            current.forward = []
            current = next_node

        self._head.forward = [None] * self._max_level
        self._tail = None
        self._level = 1
        self._size = 0

    def find(self, value: Any) -> Any | None:
        """Return the stored value equal to ``value``, or ``None``."""
        node = self._find_node(value)
        if node is None:
            return None
        return node.data

    def ceiling(self, value: Any, default: Any = None) -> Any:
        """Return the smallest stored value greater than or equal to value."""
        update = self._find_update(value)
        candidate = update[0].forward[0]
        if candidate is None:
            return default
        return candidate.data

    def floor(self, value: Any, default: Any = None) -> Any:
        """Return the largest stored value less than or equal to value."""
        update = self._find_update(value)
        candidate = update[0].forward[0]
        if candidate is not None and candidate.data == value:
            return candidate.data
        if update[0] is self._head:
            return default
        return update[0].data

    def _find_node(self, value: Any) -> _SkipListNode | None:
        """Return the node equal to ``value`` if one exists."""
        update = self._find_update(value)
        candidate = update[0].forward[0]
        if candidate is not None and candidate.data == value:
            return candidate
        return None

    def _find_update(self, value: Any) -> list[_SkipListNode]:
        """Return predecessor nodes for each level before ``value``.

        This is the core skip-list search routine. The returned list answers:
        "At each level, which node should point to a new node with this value?"
        The same predecessors are also used to find and remove existing nodes.
        """
        update = [self._head] * self._max_level
        current = self._head

        for level in range(self._level - 1, -1, -1):
            next_node = current.forward[level]
            while next_node is not None and self._is_before(
                next_node.data,
                value,
            ):
                current = next_node
                next_node = current.forward[level]
            update[level] = current

        return update

    def _random_level(self) -> int:
        """Randomly choose the height for a new node.

        Each successful promotion adds one more shortcut level. Most nodes stay
        short; a few become tall enough to speed up future searches.
        """
        level = 1
        while (
            level < self._max_level
            and self._random.random() < self._probability
        ):
            level += 1
        return level

    def _validate_values(self, values: Iterable[Any]) -> None:
        """Validate that incoming values compare with existing values."""
        for value in sorted(values):
            self._find_update(value)

    @staticmethod
    def _is_before(left: Any, right: Any) -> bool:
        """Return whether ``left`` should appear before ``right``."""
        if left == right:
            return False
        return lt(left, right)
