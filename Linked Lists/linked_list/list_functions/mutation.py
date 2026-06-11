"""Mutation operations for linked lists."""

from operator import lt
from typing import Any, Callable, Iterable, Optional


class Mutation:
    """Provide mutating operations for linked lists."""

    def append(self, data: Any) -> None:
        """Append ``data`` to the tail of the list."""
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
        """Insert ``data`` at the head of the list."""
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
        """Insert ``data`` at ``index``."""
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
        """Remove the first matching value from the list."""
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

                current.next = None
                if hasattr(current, "prev"):
                    current.prev = None
                self._size -= 1
                return True
            previous = current
            current = next_node  # type: ignore
            steps += 1
        return False

    def pop(self) -> Any:
        """Remove and return the tail value."""
        if not self.head:
            raise IndexError("Pop from empty list")
        if self._size == 1:
            data = self.head.data
            self.head = None
            self.tail = None
            self._size = 0
            return data
        if self._is_circular:
            old_tail = self.tail
            assert old_tail is not None
            data = old_tail.data

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
        self._size -= 1
        return data

    def pop_front(self) -> Any:
        """Remove and return the head value."""
        if not self.head:
            raise IndexError("Pop from empty list")
        old_head = self.head
        data = old_head.data
        if self._size == 1:
            self.head = None
            self.tail = None
            self._size = 0
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
        compare: Optional[Callable[[Any, Any], bool]] = None,
    ) -> None:
        """Insert ``data`` into an already sorted list."""
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
            # For linear lists, locate the new tail.
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
        """Reverse the linked list in place."""
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
        other: "LinkedList",
        compare: Optional[Callable[[Any, Any], bool]] = None,
    ) -> None:
        """Merge another sorted list into this one.

        Both lists must have the same list type. The optional comparison
        function controls ordering and defaults to less-than comparison.
        """
        if self._list_type != other._list_type:
            raise TypeError("Cannot merge lists of different types")

        if compare is None:
            compare = lt

        if self._is_circular:
            left_values = self.to_list()
            right_values = other.to_list()
            merged = []
            left_index = right_index = 0

            while (
                left_index < len(left_values)
                and right_index < len(right_values)
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
            return

        if not self.head:
            self.head = other.head
            self.tail = other.tail
            self._size = other._size
            return
        if not other.head:
            return

        dummy = self._create_node(None)
        tail = dummy
        left, right = self.head, other.head
        new_size = 0

        while left and right:
            if compare(left.data, right.data):
                tail.next = left
                left = left.next
            else:
                tail.next = right
                right = right.next

            tail = tail.next
            new_size += 1

        tail.next = left or right
        while tail.next:
            tail = tail.next
            new_size += 1

        self.head, self.tail, self._size = dummy.next, tail, new_size

        # Fix `prev` pointers for doubly linked lists
        if self._list_type == "doubly":
            current, prev = self.head, None
            while current:
                current.prev = prev
                prev, current = current, current.next

    def extend(self, iterable: Iterable[Any]) -> None:
        """Append all values from ``iterable`` to this list."""
        if iterable is self:
            iterable = list(iterable)
        for item in iterable:
            self.append(item)

    def remove_duplicates(self) -> None:
        """Remove duplicate values while preserving first occurrences."""
        seen = set()

        if self._is_circular and self.head:
            self.tail.next = None
            if "doubly" in self._list_type:
                self.head.prev = None

        current = self.head
        previous = None

        while current:
            if current.data in seen:
                # Remove duplicate
                if previous is None:
                    # Removing duplicate at the head
                    self.head = current.next
                    if "doubly" in self._list_type and current.next:
                        current.next.prev = None
                else:
                    previous.next = current.next
                    if "doubly" in self._list_type and current.next:
                        current.next.prev = previous
                if current == self.tail:
                    self.tail = previous
                self._size -= 1
            else:
                seen.add(current.data)
                previous = current
            current = current.next

        # If the list was circular, restore circularity
        if self._is_circular and self.tail:
            self.tail.next = self.head
            if "doubly" in self._list_type and self.head:
                self.head.prev = self.tail
