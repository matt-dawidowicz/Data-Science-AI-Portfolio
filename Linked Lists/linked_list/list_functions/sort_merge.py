"""Sorting helpers for linked lists.

Merge sort works well for linked lists because it can split and merge chains by
rewiring node links instead of repeatedly indexing into the structure.
"""

from __future__ import annotations

from collections.abc import Callable
from operator import lt
from typing import Any


class SortMerge:
    """Provide merge-sort behavior for linked lists.

    The implementation temporarily treats circular lists as linear chains,
    sorts them, repairs ``prev`` links when needed, and restores circular links
    afterward.
    """

    def _split(self, head: Any) -> tuple[Any, Any]:
        """Split a linked chain into two halves.

        The slow/fast pointer technique places ``slow`` near the midpoint while
        ``fast`` advances two nodes at a time.
        """
        slow = fast = head
        while fast.next and fast.next.next:
            slow = slow.next  # type: ignore
            fast = fast.next.next  # type: ignore
        middle = slow.next  # type: ignore
        slow.next = None  # type: ignore
        if self._list_type == "doubly" and middle:
            middle.prev = None  # type: ignore
        return head, middle

    def _merge_sorted(
        self,
        left: Any,
        right: Any,
        compare: Callable[[Any, Any], bool] | None = None,
    ) -> Any:
        """Merge two sorted linked chains into one sorted chain.

        A dummy node gives the merge a stable starting point, so the loop can
        always append to ``tail.next`` without treating the first node as a
        special case.
        """
        if compare is None:
            compare = lt

        dummy = self._create_node(None)
        tail = dummy
        while left and right:
            if compare(left.data, right.data):
                tail.next = left
                if self._list_type == "doubly":
                    left.prev = tail  # type: ignore
                left = left.next
            else:
                tail.next = right
                if self._list_type == "doubly":
                    right.prev = tail  # type: ignore
                right = right.next
            tail = tail.next  # type: ignore
        tail.next = left or right
        if self._list_type == "doubly" and tail.next:
            tail.next.prev = tail  # type: ignore
        return dummy.next

    def sort(
        self,
        compare: Callable[[Any, Any], bool] | None = None,
    ) -> None:
        """Sort the linked list in place with merge sort.

        Circular lists are opened before sorting because merge sort expects
        finite chains that end at ``None``.
        """
        if self._is_circular and self.tail:
            self.tail.next = None
            if self._list_type == "doubly_circular":
                self.head.prev = None

        def _merge_sort(node: Any) -> Any:
            if not node or not node.next:
                return node
            left, right = self._split(node)
            return self._merge_sorted(
                _merge_sort(left),
                _merge_sort(right),
                compare,
            )

        self.head = _merge_sort(self.head)

        current, prev = self.head, None
        while current:
            if self._list_type in ("doubly", "doubly_circular"):
                current.prev = prev
            prev = current
            if current.next is None:
                self.tail = current
            current = current.next

        if self._is_circular and self.tail:
            # Restore the circular invariant after the linear sort completes.
            self.tail.next = self.head
            if self._list_type == "doubly_circular":
                self.head.prev = self.tail
