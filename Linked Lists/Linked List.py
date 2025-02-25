"""
Linked List Module

This module provides a versatile linked list implementation supporting both
singly-linked and doubly-linked lists. It includes features such as sorting,
merging, and rotating the list. The design is structured for easy extension
to additional linked list types.
"""

from __future__ import annotations
from typing import Any, Optional, Iterator, Callable


class SinglyLinkedNode:
    """Node class for a singly-linked list.

    Attributes:
        data: The data stored in the node.
        next: A reference to the next node in the list.
    """

    def __init__(self, data: Any, next: Optional[SinglyLinkedNode] = None) -> None:
        """Initialize a singly-linked node.

        Args:
            data: The data to store in the node.
            next: The next node in the list.
        """
        self.data = data
        self.next = next

    def __repr__(self) -> str:
        """Return a string representation of the node."""
        return f"SinglyLinkedNode({self.data!r})"


class DoublyLinkedNode:
    """Node class for a doubly-linked list.

    Attributes:
        data: The data stored in the node.
        prev: A reference to the previous node in the list.
        next: A reference to the next node in the list.
    """

    def __init__(
        self,
        data: Any,
        prev: Optional[DoublyLinkedNode] = None,
        next: Optional[DoublyLinkedNode] = None
    ) -> None:
        """Initialize a doubly-linked node.

        Args:
            data: The data to store in the node.
            prev: The previous node in the list.
            next: The next node in the list.
        """
        self.data = data
        self.prev = prev
        self.next = next

    def __repr__(self) -> str:
        """Return a string representation of the node."""
        return f"DoublyLinkedNode({self.data!r})"


class LinkedList:
    """A versatile linked list supporting both singly and doubly linked lists.

    This class provides methods for appending, inserting, removing, sorting
    (using merge sort), merging with another sorted list, and rotating the list.
    The type of linked list is specified at initialization, allowing the user to
    choose between 'singly' and 'doubly'. The design is extendable for other types.

    Attributes:
        head: The first node in the linked list.
        tail: The last node in the linked list.
        _size: The number of nodes in the list.
        _list_type: The type of linked list ('singly' or 'doubly').
    """

    def __init__(self, list_type: str = "singly") -> None:
        """Initialize a new linked list.

        Args:
            list_type: The type of linked list, either 'singly' or 'doubly'.

        Raises:
            ValueError: If an unsupported list type is provided.
        """
        if list_type not in ("singly", "doubly"):
            raise ValueError("list_type must be 'singly' or 'doubly'")
        self._list_type = list_type
        self.head: Optional[Any] = None
        self.tail: Optional[Any] = None
        self._size: int = 0

    def __len__(self) -> int:
        """Return the number of nodes in the linked list."""
        return self._size

    def __iter__(self) -> Iterator[Any]:
        """Iterate over the node data in the linked list."""
        current = self.head
        while current:
            yield current.data
            current = current.next  # type: ignore

    def __repr__(self) -> str:
        """Return a string representation of the linked list."""
        return (
            f"{self.__class__.__name__}([{', '.join(repr(x) for x in self)}], "
            f"type={self._list_type})"
        )

    def _create_node(self, data: Any) -> Any:
        """Create a new node based on the linked list type.

        Args:
            data: The data to store in the node.

        Returns:
            A new node instance.
        """
        if self._list_type == "singly":
            return SinglyLinkedNode(data)
        return DoublyLinkedNode(data)

    def append(self, data: Any) -> None:
        """Append data to the end of the linked list.

        Args:
            data: The data to append.
        """
        new_node = self._create_node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            assert self.tail is not None  # For type checking
            self.tail.next = new_node
            if self._list_type == "doubly":
                new_node.prev = self.tail  # type: ignore
            self.tail = new_node
        self._size += 1

    def prepend(self, data: Any) -> None:
        """Prepend data to the beginning of the linked list.

        Args:
            data: The data to prepend.
        """
        new_node = self._create_node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            if self._list_type == "doubly":
                self.head.prev = new_node  # type: ignore
            self.head = new_node
        self._size += 1

    def insert(self, index: int, data: Any) -> None:
        """Insert data at a specified index.

        Args:
            index: The position at which to insert the data.
            data: The data to insert.

        Raises:
            IndexError: If the index is out of range.
        """
        if index < 0 or index > self._size:
            raise IndexError("Index out of range")
        if index == 0:
            self.prepend(data)
            return
        if index == self._size:
            self.append(data)
            return

        new_node = self._create_node(data)
        current = self.head
        for _ in range(index - 1):
            assert current is not None
            current = current.next  # type: ignore

        new_node.next = current.next  # type: ignore
        if self._list_type == "doubly" and new_node.next is not None:
            new_node.next.prev = new_node  # type: ignore
            new_node.prev = current  # type: ignore
        current.next = new_node  # type: ignore
        self._size += 1

    def remove(self, data: Any) -> bool:
        """Remove the first occurrence of data in the linked list.

        Args:
            data: The data to remove.

        Returns:
            True if the data was found and removed, False otherwise.
        """
        current = self.head
        previous = None
        while current:
            if current.data == data:
                if previous is None:
                    # Removing the head
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

    def find(self, data: Any) -> Optional[int]:
        """Find the index of the first occurrence of data in the linked list.

        Args:
            data: The data to find.

        Returns:
            The index of the data if found, None otherwise.
        """
        current = self.head
        index = 0
        while current:
            if current.data == data:
                return index
            current = current.next  # type: ignore
            index += 1
        return None

    def clear(self) -> None:
        """Clear the linked list."""
        self.head = None
        self.tail = None
        self._size = 0

    def to_list(self) -> list:
        """Convert the linked list to a Python list.

        Returns:
            A list containing all of the linked list's data.
        """
        return list(iter(self))

    def _split(self, head: Any) -> tuple[Any, Any]:
        """Split the linked list starting from head into two halves.

        Args:
            head: The starting node of the linked list.

        Returns:
            A tuple containing the head nodes of the two halves.
        """
        slow = head
        fast = head
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
        compare: Optional[Callable[[Any, Any], bool]] = None
    ) -> Any:
        """Merge two sorted linked lists.

        Args:
            left: The head of the first sorted linked list.
            right: The head of the second sorted linked list.
            compare: A comparison function that returns True if the first
                     argument should come before the second. Defaults to <.

        Returns:
            The head of the merged sorted linked list.
        """
        if compare is None:
            compare = lambda a, b: a < b
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

    def sort(self, compare: Optional[Callable[[Any, Any], bool]] = None) -> None:
        """Sort the linked list in place using merge sort.

        Args:
            compare: A comparison function that returns True if the first
                     argument should come before the second. Defaults to <.
        """
        def _merge_sort(node: Any) -> Any:
            if not node or not node.next:
                return node
            left, right = self._split(node)
            left = _merge_sort(left)
            right = _merge_sort(right)
            return self._merge_sorted(left, right, compare)

        self.head = _merge_sort(self.head)
        # Update tail pointer after sorting.
        current = self.head
        prev = None
        while current:
            if self._list_type == "doubly":
                current.prev = prev  # type: ignore
            prev = current
            if current.next is None:
                self.tail = current
            current = current.next

    def merge(
        self,
        other: LinkedList,
        compare: Optional[Callable[[Any, Any], bool]] = None
    ) -> None:
        """Merge another sorted linked list into this sorted linked list.

        Both lists must be sorted before merging. The result is a sorted list.

        Args:
            other: Another LinkedList instance.
            compare: A comparison function that returns True if the first
                     argument should come before the second. Defaults to <.

        Raises:
            TypeError: If the list types of the two linked lists do not match.
        """
        if self._list_type != other._list_type:
            raise TypeError("Cannot merge lists of different types")
        self.head = self._merge_sorted(self.head, other.head, compare)
        # Update tail and size after merging.
        current = self.head
        self._size = 0
        prev = None
        while current:
            self._size += 1
            if self._list_type == "doubly":
                current.prev = prev  # type: ignore
            prev = current
            if current.next is None:
                self.tail = current
            current = current.next

    def rotate(self, k: int) -> None:
        """Rotate the linked list by k positions.

        A positive k rotates the list to the right, while a negative k rotates
        the list to the left.

        Args:
            k: The number of positions to rotate the list.
        """
        if self._size == 0 or k % self._size == 0:
            return
        k = k % self._size
        if k < 0:
            k = self._size + k
        # Find the new tail (node at position size - k - 1)
        new_tail = self.head
        for _ in range(self._size - k - 1):
            new_tail = new_tail.next  # type: ignore
        new_head = new_tail.next  # type: ignore
        new_tail.next = None  # type: ignore
        if self._list_type == "doubly" and new_head:
            new_head.prev = None  # type: ignore
        # Connect old tail to old head to complete rotation.
        assert self.tail is not None
        self.tail.next = self.head
        if self._list_type == "doubly":
            self.head.prev = self.tail  # type: ignore
        self.head = new_head
        # Update tail pointer.
        current = self.head
        while current and current.next:
            current = current.next
        self.tail = current


# Example usage
if __name__ == "__main__":
    # Create a doubly-linked list and populate it.
    ll = LinkedList("doubly")
    for num in [4, 2, 5, 1, 3]:
        ll.append(num)
    print("Original list:", ll)

    # Sort the list.
    ll.sort()
    print("Sorted list:", ll)

    # Rotate the list by 2 positions.
    ll.rotate(2)
    print("Rotated list:", ll)

    # Merge with another sorted doubly-linked list.
    other_ll = LinkedList("doubly")
    for num in [6, 7, 8]:
        other_ll.append(num)
    ll.merge(other_ll)
    print("Merged list:", ll)
