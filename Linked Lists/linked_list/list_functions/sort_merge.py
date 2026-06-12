"""Sorting helpers for linked lists.

Merge sort gives linked lists predictable O(n log n) ordering. This module
sorts a snapshot of node references first, then relinks those existing nodes
only after every comparison succeeds.

That two-phase approach is an important safety pattern. Comparisons can raise
``TypeError`` when values are not mutually comparable. By sorting a separate
node snapshot before touching links, the original list remains unchanged if
ordering fails.
"""

from __future__ import annotations

from collections.abc import Callable
from operator import lt
from typing import Any


class SortMerge:
    """Provide merge-sort behavior for linked lists.

    Sorting keeps node identity stable while avoiding partial rewires when a
    comparison raises. Circular and doubly linked invariants are restored in a
    single relinking pass after the sorted node order is known.

    The algorithm sorts node objects, not copied values. That lets external
    references to nodes remain meaningful after sorting, while still changing
    the visible order of values.
    """

    def _merge_sort_nodes(
        self,
        nodes: list[Any],
        compare: Callable[[Any, Any], bool],
    ) -> list[Any]:
        """Return nodes ordered by their data without changing links."""
        if len(nodes) <= 1:
            return nodes[:]

        midpoint = len(nodes) // 2
        left = self._merge_sort_nodes(nodes[:midpoint], compare)
        right = self._merge_sort_nodes(nodes[midpoint:], compare)
        return self._merge_node_runs(left, right, compare)

    def _merge_node_runs(
        self,
        left: list[Any],
        right: list[Any],
        compare: Callable[[Any, Any], bool],
    ) -> list[Any]:
        """Merge two sorted node lists using the configured comparator."""
        merged = []
        left_index = right_index = 0

        while left_index < len(left) and right_index < len(right):
            if compare(
                left[left_index].data,
                right[right_index].data,
            ):
                merged.append(left[left_index])
                left_index += 1
            else:
                merged.append(right[right_index])
                right_index += 1

        merged.extend(left[left_index:])
        merged.extend(right[right_index:])
        return merged

    def _relink_nodes(self, nodes: list[Any]) -> None:
        """Relink sorted nodes according to the current list variant.

        This is the point where the sorted snapshot becomes the real list.
        Linear lists end with ``None``. Circular lists wrap the first and last
        nodes back to each other. Doubly linked lists also repair ``prev``.
        """
        if not nodes:
            self.head = self.tail = None
            return

        self.head = nodes[0]
        self.tail = nodes[-1]
        for index, node in enumerate(nodes):
            previous = None
            if index > 0:
                previous = nodes[index - 1]
            elif self._is_circular:
                previous = self.tail

            next_node = None
            if index < len(nodes) - 1:
                next_node = nodes[index + 1]
            elif self._is_circular:
                next_node = self.head

            node.next = next_node
            if self._list_type in ("doubly", "doubly_circular"):
                node.prev = previous

    def sort(
        self,
        compare: Callable[[Any, Any], bool] | None = None,
    ) -> None:
        """Sort the linked list in place with merge sort.

        The sorted order is computed before links are changed. If comparison
        fails, the list remains exactly as it was before ``sort`` was called.
        """
        if self._size <= 1:
            return

        if compare is None:
            compare = lt

        nodes = []
        current = self.head
        for _ in range(self._size):
            assert current is not None
            nodes.append(current)
            current = current.next

        self._relink_nodes(self._merge_sort_nodes(nodes, compare))
