"""Mutation operations for linked lists.

This module contains the methods that change the shape of a linked list. These
operations are the highest-risk part of the project because each mutation has
to update the visible data order and the hidden node links at the same time.

The same methods support linear lists, circular lists, singly linked nodes, and
doubly linked nodes. The conditional logic keeps those variants consistent
without requiring four separate list classes.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from operator import lt
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .linked_list import LinkedList


class Mutation:
    """Provide mutating operations for linked lists.

    The mixin assumes that the concrete class provides ``head``, ``tail``,
    ``_size``, ``_list_type``, ``_is_circular``, and ``_create_node``. Every
    method in this class is responsible for leaving those values in a valid
    state before it returns.
    """

    def append(self, data: Any) -> None:
        """Append ``data`` to the tail of the list.

        Appending to an empty list creates the first node, so both ``head`` and
        ``tail`` must point to it. Appending to a non-empty list connects the
        current tail to the new node, then moves ``tail`` forward.
        """
        new_node = self._create_node(data)
        if not self.head:
            self.head = self.tail = new_node
            if self._is_circular:
                new_node.next = new_node
                if "doubly" in self._list_type:
                    new_node.prev = new_node
        else:
            self.tail.next = new_node  # type: ignore
            if "doubly" in self._list_type:
                new_node.prev = self.tail  # type: ignore
            self.tail = new_node
            if self._is_circular:
                self.tail.next = self.head
                if "doubly" in self._list_type:
                    self.head.prev = self.tail  # type: ignore
        self._size += 1

    def prepend(self, data: Any) -> None:
        """Insert ``data`` at the head of the list.

        Prepending mirrors ``append`` at the opposite end. For doubly linked
        lists, the old head needs a backward link to the new head.
        """
        new_node = self._create_node(data)
        if not self.head:
            self.head = self.tail = new_node
            if self._is_circular:
                new_node.next = new_node
                if "doubly" in self._list_type:
                    new_node.prev = new_node
        else:
            new_node.next = self.head
            if "doubly" in self._list_type:
                self.head.prev = new_node  # type: ignore
            self.head = new_node
            if self._is_circular:
                self.tail.next = self.head
                if "doubly" in self._list_type:
                    self.head.prev = self.tail  # type: ignore
        self._size += 1

    def insert(self, index: int, data: Any) -> None:
        """Insert ``data`` at ``index``.

        Boundary inserts delegate to ``prepend`` and ``append`` because those
        methods already know how to update head and tail correctly. Middle
        inserts locate the node before the target position and splice the new
        node between two existing nodes.
        """
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")
        if index == 0:
            return self.prepend(data)
        if index == self._size:
            return self.append(data)

        new_node = self._create_node(data)
        current = self.head
        for _ in range(index - 1):
            current = current.next  # type: ignore

        new_node.next = current.next  # type: ignore
        if "doubly" in self._list_type:
            new_node.prev = current
            if new_node.next:
                new_node.next.prev = new_node  # type: ignore
        current.next = new_node

        if self._is_circular:
            self.tail.next = self.head  # type: ignore
            if "doubly" in self._list_type:
                self.head.prev = self.tail  # type: ignore
        self._size += 1

    def remove(self, data: Any) -> bool:
        """Remove the first matching value from the list.

        The traversal is bounded by ``_size`` so circular lists cannot loop
        forever. After removal, circular lists reconnect ``tail`` to ``head``,
        and doubly linked lists repair any affected ``prev`` pointers.
        """
        current = self.head
        previous = None
        steps = 0
        while current and steps < self._size:
            next_node = current.next
            if current.data == data:
                if self._size == 1:
                    self.head = self.tail = None
                else:
                    if current == self.head:
                        self.head = next_node
                    elif previous:
                        previous.next = next_node

                    # If the removed node was the tail, the previous node
                    # becomes the new tail.
                    if current == self.tail:
                        self.tail = previous

                    if "doubly" in self._list_type and next_node:
                        next_node.prev = previous  # type: ignore

                    if self._is_circular and self.head and self.tail:
                        self.tail.next = self.head  # type: ignore
                        if "doubly" in self._list_type:
                            self.head.prev = self.tail  # type: ignore
                    elif "doubly" in self._list_type and self.head:
                        self.head.prev = None  # type: ignore

                # Detaching the removed node avoids leaving stale links behind.
                current.next = None
                if hasattr(current, "prev"):
                    current.prev = None
                self._size -= 1
                return True
            previous = current
            current = next_node  # type: ignore
            steps += 1
        return False

    def remove_all(self, data: Any) -> int:
        """Remove every matching value and return the removal count.

        This builds on ``remove`` so each individual deletion goes through the
        same link-repair path as normal single-value removal.
        """
        removed = 0
        while self.remove(data):
            removed += 1
        return removed

    def remove_at(self, index: int) -> Any:
        """Remove and return the value at ``index``.

        Positive and negative indexes follow the same rules as ``__getitem__``.
        Edge removals delegate to ``pop_front`` or ``pop`` so head and tail
        updates stay centralized. Middle removals splice one node out and then
        repair circular and doubly linked invariants.
        """
        if index < 0:
            index += self._size
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        if index == 0:
            return self.pop_front()
        if index == self._size - 1:
            return self.pop()

        previous = self.head
        for _ in range(index - 1):
            previous = previous.next  # type: ignore

        current = previous.next  # type: ignore
        next_node = current.next
        data = current.data

        previous.next = next_node  # type: ignore
        if "doubly" in self._list_type and next_node:
            next_node.prev = previous  # type: ignore

        if self._is_circular and self.head and self.tail:
            self.tail.next = self.head  # type: ignore
            if "doubly" in self._list_type:
                self.head.prev = self.tail  # type: ignore

        current.next = None
        if hasattr(current, "prev"):
            current.prev = None
        self._size -= 1
        return data

    def replace(
        self,
        old_data: Any,
        new_data: Any,
        count: int | None = None,
    ) -> int:
        """Replace matching values and return how many changed.

        Only node data changes; links are left exactly where they are. Passing
        ``count`` limits the number of replacements from left to right. A
        non-positive count performs no replacements.
        """
        if count is not None and count <= 0:
            return 0

        replaced = 0
        current = self.head
        steps = 0
        while current is not None and steps < self._size:
            if current.data == old_data:
                current.data = new_data
                replaced += 1
                if count is not None and replaced == count:
                    break
            current = current.next
            steps += 1
        return replaced

    def pop(self) -> Any:
        """Remove and return the tail value.

        Singly linked lists have no direct backward link, so popping their tail
        requires walking to the node before the tail. Doubly linked lists can
        move directly through ``prev``.
        """
        if not self.head:
            raise IndexError("Pop from empty list")
        if self._size == 1:
            old_tail = self.head
            data = old_tail.data
            self.head = None
            self.tail = None
            self._size = 0
            old_tail.next = None
            if hasattr(old_tail, "prev"):
                old_tail.prev = None
            return data
        if self._is_circular:
            old_tail = self.tail
            assert old_tail is not None
            data = old_tail.data

            # Doubly circular lists can step backward from the old tail.
            # Singly circular lists must walk forward to find the new tail.
            if "doubly" in self._list_type:
                self.tail = old_tail.prev
            else:
                self.tail = self.head
                for _ in range(self._size - 2):
                    self.tail = self.tail.next  # type: ignore

            self.tail.next = self.head  # type: ignore
            if "doubly" in self._list_type:
                self.head.prev = self.tail  # type: ignore

            old_tail.next = None
            if hasattr(old_tail, "prev"):
                old_tail.prev = None
            self._size -= 1
            return data

        current = self.head
        previous = None
        while current.next:
            previous = current
            current = current.next
        data = current.data
        if previous:
            previous.next = None
            self.tail = previous
        if hasattr(current, "prev"):
            current.prev = None
        self._size -= 1
        return data

    def pop_front(self) -> Any:
        """Remove and return the head value.

        Removing the head is simpler than removing the tail because every list
        type can move from the old head to ``old_head.next``. The extra work is
        repairing circular links and doubly linked ``prev`` pointers.
        """
        if not self.head:
            raise IndexError("Pop from empty list")
        old_head = self.head
        data = old_head.data
        if self._size == 1:
            self.head = None
            self.tail = None
            self._size = 0
            old_head.next = None
            if hasattr(old_head, "prev"):
                old_head.prev = None
            return data

        self.head = old_head.next
        if self._is_circular:
            self.tail.next = self.head  # type: ignore
            if "doubly" in self._list_type:
                self.head.prev = self.tail  # type: ignore
        elif self.head and "doubly" in self._list_type:
            self.head.prev = None  # type: ignore
        old_head.next = None
        if hasattr(old_head, "prev"):
            old_head.prev = None
        self._size -= 1
        return data

    def insert_sorted(
        self,
        data: Any,
        compare: Callable[[Any, Any], bool] | None = None,
    ) -> None:
        """Insert ``data`` into an already sorted list.

        The comparison function answers whether the first value should come
        before the second. By default, the method uses ``operator.lt``, which
        is the normal less-than ordering.
        """
        if compare is None:
            compare = lt

        new_node = self._create_node(data)

        if self.head is None:
            self.head = self.tail = new_node
            if self._is_circular:
                new_node.next = new_node
                if "doubly" in self._list_type:
                    new_node.prev = new_node
            self._size = 1
            return

        if compare(data, self.head.data):
            new_node.next = self.head
            if "doubly" in self._list_type:
                self.head.prev = new_node
            self.head = new_node
            if self._is_circular:
                self.tail.next = self.head  # type: ignore
                if "doubly" in self._list_type:
                    self.head.prev = self.tail  # type: ignore
            self._size += 1
            return

        current = self.head
        while (
            current != self.tail
            and current.next
            and compare(current.next.data, data)
        ):
            current = current.next

        new_node.next = current.next
        if "doubly" in self._list_type and new_node.next:
            new_node.next.prev = new_node

        current.next = new_node
        if "doubly" in self._list_type:
            new_node.prev = current

        if current == self.tail:
            self.tail = new_node

        if self._is_circular:
            self.tail.next = self.head  # type: ignore
            if "doubly" in self._list_type:
                self.head.prev = self.tail  # type: ignore

        self._size += 1

    def rotate(self, k: int) -> None:
        """Rotate the linked list by k positions.

        A positive ``k`` rotates the list to the right, while a negative
        ``k`` rotates to the left. Circular lists only adjust head and tail
        pointers; linear lists rearrange links.
        """
        if self._size == 0 or k % self._size == 0:
            return

        k %= self._size

        if self._is_circular:
            # Right rotation by k is equivalent to moving left by size - k.
            steps = self._size - k
            for _ in range(steps):
                assert self.head and self.tail
                self.head = self.head.next  # type: ignore
                self.tail = self.tail.next  # type: ignore
        else:
            # Linear rotation breaks one link and reconnects the old tail to
            # the old head, turning the final segment into the new front.
            new_tail = self.head
            for _ in range(self._size - k - 1):
                assert new_tail is not None
                new_tail = new_tail.next  # type: ignore
            new_head = new_tail.next  # type: ignore

            # Detach after new_tail.
            new_tail.next = None
            # Connect the old tail to the old head.
            assert self.tail is not None
            self.tail.next = self.head

            # Update the head and tail pointers.
            self.head, self.tail = new_head, new_tail

            # Fix previous pointers for doubly linked lists.
            if self._list_type == "doubly":
                # New head has no previous.
                self.head.prev = None  # type: ignore
                current, prev = self.head, None
                while current:
                    current.prev = prev  # type: ignore
                    prev, current = current, current.next

    def reverse(self) -> None:
        """Reverse the linked list in place.

        Reversal flips the direction of traversal. Circular lists stay
        circular by walking exactly ``_size`` nodes and then swapping the old
        head and tail. Linear lists stop naturally at ``None``.
        """
        if self._size <= 1:
            return

        if self._is_circular:
            old_head, old_tail = self.head, self.tail
            prev, current = self.tail, self.head
            for _ in range(self._size):
                next_node = current.next  # type: ignore
                current.next = prev  # type: ignore
                if "doubly" in self._list_type:
                    current.prev = next_node  # type: ignore
                prev, current = current, next_node
            self.head, self.tail = old_tail, old_head
            return

        prev, current = None, self.head
        self.tail = self.head  # Head will become the new tail

        while current:
            next_node = current.next
            current.next = prev
            if "doubly" in self._list_type:
                current.prev = next_node
            prev, current = current, next_node

        self.head = prev

    def merge(
        self,
        other: LinkedList,
        compare: Callable[[Any, Any], bool] | None = None,
    ) -> None:
        """Merge another sorted list into this one.

        Both lists must have the same list type. The optional comparison
        function controls ordering and defaults to less-than comparison.
        Lists are merged by value snapshots so the temporary merge process
        cannot accidentally chase circular links forever or relink nodes from
        ``other`` into this list.
        """
        if self._list_type != other._list_type:
            raise TypeError("Cannot merge lists of different types")

        if compare is None:
            compare = lt

        left_values = self.to_list()
        right_values = other.to_list()
        merged = []
        left_index = right_index = 0

        while left_index < len(left_values) and right_index < len(
            right_values
        ):
            if compare(left_values[left_index], right_values[right_index]):
                merged.append(left_values[left_index])
                left_index += 1
            else:
                merged.append(right_values[right_index])
                right_index += 1

        merged.extend(left_values[left_index:])
        merged.extend(right_values[right_index:])

        self.clear()
        for item in merged:
            self.append(item)

    def extend(self, iterable: Iterable[Any]) -> None:
        """Append all values from ``iterable`` to this list.

        Extending a list with itself needs a snapshot. Otherwise the method
        would keep appending values while also iterating over those new values.
        """
        if iterable is self:
            iterable = list(iterable)
        for item in iterable:
            self.append(item)

    def remove_duplicates(self) -> None:
        """Remove duplicate values while preserving first occurrences.

        Circular lists are temporarily opened by clearing the tail link. That
        lets the duplicate-removal loop use a normal ``while current`` pattern,
        then the circular links are restored at the end.
        """
        seen_hashable: set[Any] = set()
        seen_unhashable: list[Any] = []

        def already_seen(data: Any) -> bool:
            try:
                if data in seen_hashable:
                    return True
            except TypeError:
                pass
            return any(data == item for item in seen_unhashable)

        def remember(data: Any) -> None:
            try:
                seen_hashable.add(data)
            except TypeError:
                seen_unhashable.append(data)

        if self._is_circular and self.head:
            self.tail.next = None
            if "doubly" in self._list_type:
                self.head.prev = None

        try:
            current = self.head
            previous = None

            while current:
                next_node = current.next
                if already_seen(current.data):
                    if previous is None:
                        self.head = next_node
                        if "doubly" in self._list_type and next_node:
                            next_node.prev = None
                    else:
                        previous.next = next_node
                        if "doubly" in self._list_type and next_node:
                            next_node.prev = previous
                    if current == self.tail:
                        self.tail = previous
                    current.next = None
                    if hasattr(current, "prev"):
                        current.prev = None
                    self._size -= 1
                else:
                    remember(current.data)
                    previous = current
                current = next_node
        finally:
            if self._is_circular and self.tail:
                self.tail.next = self.head
                if "doubly" in self._list_type and self.head:
                    self.head.prev = self.tail
