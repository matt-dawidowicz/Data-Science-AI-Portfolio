

from typing import Any, Optional, Callable, Iterable

class Mutation:
    def append(self, data: Any) -> None:
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
        current = self.head
        previous = None
        while current:
            if current.data == data:
                if previous is None:
                    self.head = current.next
                    if self._list_type == "doubly" and self.head:
                        self.head.prev = None  # type: ignore
                else:
                    previous.next = current.next
                    if self._list_type == "doubly" and current.next:
                        current.next.prev = previous  # type: ignore
                if current == self.tail:
                    self.tail = previous
                self._size -= 1
                return True
            previous = current
            current = current.next  # type: ignore
        return False

    def pop(self) -> Any:
        if not self.head:
            raise IndexError("Pop from empty list")
        if self._size == 1:
            data = self.head.data
            self.head = None
            self.tail = None
            self._size = 0
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
        if not self.head:
            raise IndexError("Pop from empty list")
        data = self.head.data
        self.head = self.head.next
        if self.head and self._list_type == "doubly":
            self.head.prev = None  # type: ignore
        self._size -= 1
        if self._size == 0:
            self.tail = None
        return data
    def insert_sorted(self, data: Any, compare: Optional[Callable[[Any, Any], bool]] = None) -> None:
        if compare is None:
            compare = lambda a, b: a < b

        new_node = self._create_node(data)

        if self.head is None:
            self.head = self.tail = new_node
            self._size = 1
            return

        if compare(data, self.head.data):
            new_node.next = self.head
            if self._list_type == "doubly":
                self.head.prev = new_node
            self.head = new_node
            self._size += 1
            return

        current = self.head
        while current.next and compare(current.next.data, data):
            current = current.next

        new_node.next = current.next
        if self._list_type == "doubly" and new_node.next:
            new_node.next.prev = new_node

        current.next = new_node
        if self._list_type == "doubly":
            new_node.prev = current

        if current == self.tail:
            self.tail = new_node

        self._size += 1

    def rotate(self, k: int) -> None:
        """Rotate the linked list by k positions.

        A positive k rotates the list to the right, while a negative k rotates to the left.
        For circular lists, this operation only involves adjusting the head and tail pointers,
        while for linear lists the links are re-arranged.
        """
        if self._size == 0 or k % self._size == 0:
            return  # No need to rotate if k is 0 or a multiple of size

        k = k % self._size  # Normalize k

        if self._is_circular:
            # For circular lists, advance the head and tail pointers.
            # Rotating right by k positions is equivalent to moving left by (size - k) positions.
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
        prev, current = None, self.head
        self.tail = self.head  # Head will become the new tail

        while current:
            next_node = current.next
            current.next = prev
            if self._list_type == "doubly":
                current.prev = next_node  # Fix backward links for doubly linked list
            prev, current = current, next_node

        self.head = prev

    def merge(self, other: "LinkedList", compare: Optional[Callable[[Any, Any], bool]] = None) -> None:
        """
        Merge another LinkedList into the current LinkedList while preserving the order.

        This method combines two LinkedLists of the same type into one, using an optional
        comparison function to determine the order. If no comparison function is provided,
        a default less-than (`<`) operation is used. The resulting list will overwrite the
        current LinkedList, including its head, tail, and size. If either list is empty,
        the non-empty list will become the result or the list remains unchanged. The method
        also ensures the previous pointers (`prev`) are correctly updated for doubly linked
        lists.

        Parameters:
            other (LinkedList): The LinkedList to merge into the current one. Must be of the
                same type as the current list.
            Compare (Callable[[Any, Any], bool] | None): Optional. A function that takes two
                elements and returns `True` if the first element should precede the second
                in the merged list. If not provided, the default operation `a < b` is used.

        Raises:
            TypeError: If the current LinkedList and the `other` LinkedList are not of the
                same type.

        """
        if self._list_type != other._list_type:
            raise TypeError("Cannot merge lists of different types")

        if compare is None:
            compare = lambda a, b: a < b

        if not self.head:
            self.head, self.tail, self._size = other.head, other.tail, other._size
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
        """
        Extends the current collection with elements from another iterable.

        This method appends all elements from the given iterable to the current
        collection. If the provided iterable is the same instance as the
        current collection, it first converts the iterable into a static list
        to prevent self-iteration issues during the extension process.

        Args:
            iterable: An iterable object containing elements to
                be appended to the current collection.
        """
        # Convert self to a static list if the iterable is the same instance to avoid self-iteration issues.
        if iterable is self:
            iterable = list(iterable)
        for item in iterable:
            self.append(item)

    def remove_duplicates(self) -> None:
        """
        Removes duplicate elements from a doubly linked list while preserving the order of
        first occurrences. Ensures the linked list structure remains consistent and handles
        both circular and non-circular linked lists.

        If the linked list is circular, it temporarily breaks the circularity to perform the
        removal operation and restores the circularity afterward.

        Raises:
            No exceptions are raised by this method.
        """
        seen = set()

        # If the list is circular, break the circularity temporarily
        if self._is_circular and self.head:
            # Break the circle by setting tail.next to None
            self.tail.next = None

        current = self.head
        previous = None

        while current:
            if current.data in seen:
                # Remove duplicate
                if previous is None:
                    # Removing duplicate at the head
                    self.head = current.next
                    if current.next:
                        current.next.prev = None
                else:
                    previous.next = current.next
                    if current.next:
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
            if self.head:
                self.head.prev = self.tail