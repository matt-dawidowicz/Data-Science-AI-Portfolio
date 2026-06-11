"""Sorting helpers for linked lists."""

from operator import lt
from typing import Any, Callable, Optional


class SortMerge:
    """Provide merge-sort behavior for linked lists."""

    def _split(self, head: Any) -> tuple[Any, Any]:
        """Split a linked chain into two halves."""
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
        compare: Optional[Callable[[Any, Any], bool]] = None,
    ) -> Any:
        """Merge two sorted linked chains into one sorted chain."""
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
        compare: Optional[Callable[[Any, Any], bool]] = None,
    ) -> None:
        """Sort the linked list in place with merge sort."""
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
            self.tail.next = self.head
            if self._list_type == "doubly_circular":
                self.head.prev = self.tail
