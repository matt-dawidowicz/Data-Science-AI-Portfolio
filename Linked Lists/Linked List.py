#!/usr/bin/env python3.12
"""
Linked List Module

This module provides a versatile linked list implementation supporting both
singly-linked and doubly-linked lists. It includes a wide range of features:
appending, prepending, inserting, removing, sorting, merging, rotating,
reversing, slicing, mapping, reducing, filtering, duplicate removal, and more.
Unit and integration tests are provided at the end of the module.

"""

from typing import Any, Optional, Iterator, Callable, Iterable
from functools import reduce as functools_reduce

class SinglyLinkedNode:
    """Node class for a singly-linked list.

    Attributes:
        data: The data stored in the node.
        next: A reference to the next node in the list.
    """

    def __init__(self, data: Any, next_node: Optional["SinglyLinkedNode"] = None) -> None:
        self.data = data
        self.next = next_node

    def __repr__(self) -> str:
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
        prev: Optional["DoublyLinkedNode"] = None,
        next_node: Optional["DoublyLinkedNode"] = None
    ) -> None:
        self.data = data
        self.prev = prev
        self.next = next_node

    def __repr__(self) -> str:
        return f"DoublyLinkedNode({self.data!r})"


class LinkedList:
    """A versatile linked list supporting both singly and doubly linked lists.

    This class provides methods for appending, prepending, inserting, removing,
    sorting, merging, rotating, reversing, slicing, mapping, reducing, filtering,
    duplicate removal, and more. The type of linked list is specified at
    initialization, allowing the user to choose between 'singly' and 'doubly'.

    Attributes:
        head: The first node in the linked list.
        tail: The last node in the linked list.
        _size: The number of nodes in the list.
        _list_type: The type of linked list ('singly' or 'doubly').
    """

    def __init__(self, list_type: str = "singly") -> None:
        if list_type not in ("singly", "doubly"):
            raise ValueError("list_type must be 'singly' or 'doubly'")
        self._list_type = list_type
        self.head: Optional[Any] = None
        self.tail: Optional[Any] = None
        self._size: int = 0

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[Any]:
        current = self.head
        while current:
            yield current.data
            current = current.next

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}([{', '.join(repr(x) for x in self)}], "
            f"type={self._list_type})"
        )

    def __str__(self) -> str:
        return " -> ".join(str(x) for x in self)

    def __contains__(self, data: Any) -> bool:
        return any(item == data for item in self)

    def __getitem__(self, index: int | slice) -> Any:
        if isinstance(index, slice):
            return self.from_list(list(self)[index], list_type=self._list_type)
        if index < 0:
            index = self._size + index
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        current = self.head
        for _ in range(index):
            current = current.next  # type: ignore
        return current.data  # type: ignore

    def __setitem__(self, index: int, value: Any) -> None:
        if index < 0:
            index = self._size + index
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        current = self.head
        for _ in range(index):
            current = current.next  # type: ignore
        current.data = value  # type: ignore

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LinkedList):
            return False
        return list(self) == list(other)

    def __reversed__(self) -> Iterator[Any]:
        if self._list_type != "doubly":
            raise NotImplementedError("Reverse iteration only supported for doubly-linked lists")
        current = self.tail
        while current:
            yield current.data
            current = current.prev  # type: ignore

    def _create_node(self, data: Any) -> Any:
        if self._list_type == "singly":
            return SinglyLinkedNode(data)
        return DoublyLinkedNode(data)

    def append(self, data: Any) -> None:
        new_node = self._create_node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            if self._list_type == "doubly":
                new_node.prev = self.tail  # type: ignore
            self.tail = new_node
        self._size += 1

    def prepend(self, data: Any) -> None:
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

    def insert_sorted(self, data: Any, compare: Optional[Callable[[Any, Any], bool]] = None) -> None:
        """Insert data into the list while maintaining sorted order.

        Args:
            data: The data to insert.
            compare: Optional comparison function (defaults to < for ascending order).
        """
        if compare is None:
            compare = lambda a, b: a < b  # Default to ascending order

        new_node = self._create_node(data)

        # 🚀 Case 1: List is empty
        if self.head is None:
            self.head = self.tail = new_node
            self._size = 1
            return

        # 🚀 Case 2: Insert at the beginning (new smallest element)
        if compare(data, self.head.data):
            new_node.next = self.head
            if self._list_type == "doubly":
                self.head.prev = new_node
            self.head = new_node
            self._size += 1
            return

        # 🚀 Case 3: Insert somewhere in the middle or at the end
        current = self.head
        while current.next and compare(current.next.data, data):
            current = current.next

        new_node.next = current.next
        if self._list_type == "doubly" and new_node.next:
            new_node.next.prev = new_node  # Fix doubly-linked list back-pointer

        current.next = new_node
        if self._list_type == "doubly":
            new_node.prev = current

        # 🚀 Case 4: Insert at the end (update tail)
        if current == self.tail:
            self.tail = new_node

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

    def extend(self, iterable: Iterable[Any]) -> None:
        for item in iterable:
            self.append(item)

    def count(self, data: Any) -> int:
        return sum(1 for item in self if item == data)

    def remove_duplicates(self) -> None:
        """Remove duplicate nodes from the list while preserving order."""
        seen = set()
        current, previous = self.head, None

        while current:
            if current.data in seen:
                previous.next = current.next
                if self._list_type == "doubly" and current.next:
                    current.next.prev = previous
                if current == self.tail:
                    self.tail = previous  # Update tail
                self._size -= 1
            else:
                seen.add(current.data)
                previous = current
            current = current.next

    def nth_from_end(self, n: int) -> Any:
        if n <= 0 or n > self._size:
            raise IndexError("n is out of range")
        lead = self.head
        follow = self.head
        for _ in range(n):
            assert lead is not None
            lead = lead.next
        while lead:
            lead = lead.next
            follow = follow.next  # type: ignore
        return follow.data  # type: ignore

    def filter(self, predicate: Callable[[Any], bool]) -> "LinkedList":
        """Return a new linked list containing only the nodes where predicate(data) is True."""
        filtered = LinkedList(self._list_type)
        for data in self:
            if predicate(data):
                filtered.append(data)
        return filtered

    def map(self, func: Callable[[Any], Any]) -> "LinkedList":
        """Return a new linked list with func applied to each node's data."""
        mapped = LinkedList(self._list_type)
        for data in self:
            mapped.append(func(data))
        return mapped

    def reduce(self, func: Callable[[Any, Any], Any], initializer: Optional[Any] = None) -> Any:
        if initializer is not None:
            return functools_reduce(func, self, initializer)
        return functools_reduce(func, self)

    def clear(self) -> None:
        self.head = None
        self.tail = None
        self._size = 0

    def to_list(self) -> list:
        return list(iter(self))

    @classmethod
    def from_list(cls, lst: list, list_type: str = "singly") -> "LinkedList":
        """Create a LinkedList from a Python list."""
        linked_list = cls(list_type)
        for item in lst:
            linked_list.append(item)
        return linked_list

    def copy(self) -> "LinkedList":
        """Return a shallow copy of the linked list."""
        new_list = LinkedList(self._list_type)
        for item in self:
            new_list.append(item)
        return new_list

    def _split(self, head: Any) -> tuple[Any, Any]:
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
        def _merge_sort(node: Any) -> Any:
            if not node or not node.next:
                return node
            left, right = self._split(node)
            left = _merge_sort(left)
            right = _merge_sort(right)
            return self._merge_sorted(left, right, compare)
        self.head = _merge_sort(self.head)
        current = self.head
        prev = None
        while current:
            if self._list_type == "doubly":
                current.prev = prev  # type: ignore
            prev = current
            if current.next is None:
                self.tail = current
            current = current.next

    def merge(self, other: "LinkedList", compare: Optional[Callable[[Any, Any], bool]] = None) -> None:
        """Merge another sorted linked list into this sorted linked list.

        Both lists must be sorted before merging.

        Args:
            other: Another LinkedList instance.
            compare: Optional comparison function (defaults to <).

        Raises:
            TypeError: If the two lists are of different types.
        """
        if self._list_type != other._list_type:
            raise TypeError("Cannot merge lists of different types")

        if compare is None:
            compare = lambda a, b: a < b

        # Handle edge cases where one of the lists is empty
        if not self.head:
            self.head, self.tail, self._size = other.head, other.tail, other._size
            return
        if not other.head:
            return

        # Merge sorted linked lists using pointer manipulation
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

        # Attach remaining elements from non-empty list
        tail.next = left or right
        while tail.next:
            tail = tail.next
            new_size += 1

        # Update head, tail, and size
        self.head, self.tail, self._size = dummy.next, tail, new_size

        # Fix `prev` pointers for doubly linked lists
        if self._list_type == "doubly":
            current, prev = self.head, None
            while current:
                current.prev = prev
                prev, current = current, current.next

    def rotate(self, k: int) -> None:
        """Rotate the list by k positions.

        A positive k rotates the list to the right, while a negative k rotates to the left.

        Args:
            k: The number of positions to rotate.
        """
        if self._size == 0 or k % self._size == 0:
            return

        k = k % self._size  # Reduce unnecessary rotations
        if k < 0:
            k = self._size + k  # Convert negative rotations to equivalent positive ones

        new_tail = self.head
        for _ in range(self._size - k - 1):
            new_tail = new_tail.next  # Move to new tail position

        new_head = new_tail.next
        new_tail.next = None
        self.tail.next = self.head  # Connect old tail to old head
        self.head, self.tail = new_head, new_tail  # Update pointers

        # Fix prev pointers for doubly linked list
        if self._list_type == "doubly":
            self.head.prev = None
            current, prev = self.head, None
            while current:
                current.prev = prev
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

    def get_middle(self) -> Optional[Any]:
        if not self.head:
            return None
        slow = self.head
        fast = self.head
        while fast and fast.next:
            fast = fast.next.next  # type: ignore
            slow = slow.next  # type: ignore
        return slow.data if slow else None

    def insert_after(self, target_data: Any, data: Any) -> bool:
        current = self.head
        while current:
            if current.data == target_data:
                new_node = self._create_node(data)
                new_node.next = current.next
                if self._list_type == "doubly" and new_node.next:
                    new_node.next.prev = new_node
                    new_node.prev = current
                current.next = new_node
                if current == self.tail:
                    self.tail = new_node
                self._size += 1
                return True
            current = current.next
        return False


# ===================== Unit and Integration Tests =====================

import unittest

class TestLinkedListUnit(unittest.TestCase):
    def setUp(self) -> None:
        # Create both singly and doubly linked lists pre-populated with 0..4.
        self.singly = LinkedList("singly")
        self.doubly = LinkedList("doubly")
        for i in range(5):
            self.singly.append(i)
            self.doubly.append(i)

    def test_append_and_len(self) -> None:
        self.assertEqual(len(self.singly), 5)
        self.singly.append(5)
        self.assertEqual(len(self.singly), 6)

    def test_prepend(self) -> None:
        self.singly.prepend(-1)
        self.assertEqual(self.singly.head.data, -1)

    def test_insert(self) -> None:
        self.singly.insert(3, 99)
        self.assertEqual(self.singly[3], 99)

    def test_remove(self) -> None:
        self.assertTrue(self.singly.remove(2))
        self.assertNotIn(2, self.singly)

    def test_pop(self) -> None:
        val = self.singly.pop()
        self.assertEqual(val, 4)
        self.assertEqual(len(self.singly), 4)

    def test_pop_front(self) -> None:
        val = self.singly.pop_front()
        self.assertEqual(val, 0)
        self.assertEqual(len(self.singly), 4)

    def test_getitem_setitem(self) -> None:
        self.singly[2] = 50
        self.assertEqual(self.singly[2], 50)
        self.assertEqual(self.singly[-1], 4)

    def test_slice(self) -> None:
        sublist = self.singly[1:3]
        self.assertEqual(sublist.to_list(), [1, 2])

    def test_equality(self) -> None:
        another = LinkedList("singly")
        for i in range(5):
            another.append(i)
        self.assertEqual(self.singly, another)

    def test_extend(self) -> None:
        self.singly.extend([10, 11, 12])
        self.assertEqual(self.singly.to_list()[-3:], [10, 11, 12])

    def test_count(self) -> None:
        self.singly.append(2)
        self.assertEqual(self.singly.count(2), 2)

    def test_remove_duplicates(self) -> None:
        dup_list = LinkedList("singly")
        for x in [1, 2, 2, 3, 3, 3]:
            dup_list.append(x)
        dup_list.remove_duplicates()
        self.assertEqual(dup_list.to_list(), [1, 2, 3])

    def test_nth_from_end(self) -> None:
        # For list [0,1,2,3,4]: nth_from_end(1)=4, nth_from_end(3)=2.
        self.assertEqual(self.singly.nth_from_end(1), 4)
        self.assertEqual(self.singly.nth_from_end(3), 2)

    def test_filter_map_reduce(self) -> None:
        # Test filter: keep even numbers.
        filtered = self.singly.filter(lambda x: x % 2 == 0)
        self.assertEqual(filtered.to_list(), [0, 2, 4])
        # Test map: square each element.
        mapped = self.singly.map(lambda x: x * x)
        self.assertEqual(mapped.to_list(), [0, 1, 4, 9, 16])
        # Test reduce: sum should be 0+1+2+3+4 = 10.
        result = self.singly.reduce(lambda a, b: a + b)
        self.assertEqual(result, 10)
        # Test reduce with initializer.
        result_init = self.singly.reduce(lambda a, b: a + b, 10)
        self.assertEqual(result_init, 20)

    def test_insert_sorted(self) -> None:
        sorted_ll = LinkedList("singly")
        for x in [1, 3, 5, 7]:
            sorted_ll.append(x)
        sorted_ll.insert_sorted(4)
        self.assertEqual(sorted_ll.to_list(), [1, 3, 4, 5, 7])

    def test_insert_sorted_empty_list(self) -> None:
        """Test inserting into an empty list"""
        empty_list = LinkedList("singly")
        empty_list.insert_sorted(5)
        self.assertEqual(empty_list.to_list(), [5])

    def test_insert_sorted_at_head(self) -> None:
        """Test inserting a new smallest element (should become head)"""
        self.singly.insert_sorted(-1)
        self.assertEqual(self.singly.to_list()[0], -1)

    def test_insert_sorted_at_tail(self) -> None:
        """Test inserting a new largest element (should become tail)"""
        self.singly.insert_sorted(10)
        self.assertEqual(self.singly.to_list()[-1], 10)

    def test_insert_sorted_middle(self) -> None:
        """Test inserting a value in the middle of a sorted list"""
        self.singly.insert_sorted(2.5)
        self.assertEqual(self.singly.to_list(), [0, 1, 2, 2.5, 3, 4])

    def test_insert_sorted_duplicate(self) -> None:
        """Test inserting a duplicate value (should be placed correctly)"""
        self.singly.insert_sorted(2)
        self.assertEqual(self.singly.to_list(), [0, 1, 2, 2, 3, 4])

    def test_insert_sorted_all_same_values(self) -> None:
        """Test inserting into a list where all elements are the same"""
        all_same = LinkedList("singly")
        for _ in range(5):
            all_same.append(3)
        all_same.insert_sorted(3)
        self.assertEqual(all_same.to_list(), [3, 3, 3, 3, 3, 3])

    def test_insert_sorted_large_list(self) -> None:
        """Test inserting into a large sorted list"""
        large_list = LinkedList("singly")
        for i in range(1000, 2000, 2):  # Only even numbers
            large_list.append(i)
        large_list.insert_sorted(1501)  # Insert an odd number in the middle
        self.assertIn(1501, large_list.to_list())

    def test_reverse_sort(self) -> None:
        rev = self.singly.copy()
        rev.reverse()
        self.assertEqual(rev.to_list(), [4, 3, 2, 1, 0])
        rev.sort()
        self.assertEqual(rev.to_list(), [0, 1, 2, 3, 4])

    def test_merge(self) -> None:
        l1 = LinkedList("singly")
        l2 = LinkedList("singly")
        for x in [1, 3, 5]:
            l1.append(x)
        for x in [2, 4, 6]:
            l2.append(x)
        l1.merge(l2)
        self.assertEqual(l1.to_list(), [1, 2, 3, 4, 5, 6])

    def test_rotate(self) -> None:
        # For list [0,1,2,3,4], rotate by 2 should yield [3,4,0,1,2].
        self.singly.rotate(2)
        self.assertEqual(self.singly.to_list(), [3, 4, 0, 1, 2])


class TestLinkedListIntegration(unittest.TestCase):
    def test_integration(self) -> None:
        # Integration test: perform a series of operations and validate final state.
        ll = LinkedList("doubly")
        data = [5, 3, 1, 2, 3, 4, 5]
        for x in data:
            ll.append(x)
        # Remove duplicates.
        ll.remove_duplicates()
        self.assertEqual(sorted(ll.to_list()), [1, 2, 3, 4, 5])
        # Reverse the list.
        ll.reverse()
        # Create a sorted list from the reversed data.
        sorted_ll = LinkedList("doubly")
        for x in sorted(ll.to_list()):
            sorted_ll.append(x)
        sorted_ll.insert_sorted(3)
        self.assertEqual(sorted_ll.to_list(), [1, 2, 3, 3, 4, 5])
        # Merge with another list.
        other_ll = LinkedList("doubly")
        for x in [0, 6]:
            other_ll.append(x)
        sorted_ll.merge(other_ll)
        self.assertEqual(sorted_ll.to_list(), [0, 1, 2, 3, 3, 4, 5, 6])
        # Rotate the merged list.
        sorted_ll.rotate(3)
        # Verify the rotated list has the correct elements.
        self.assertCountEqual(sorted_ll.to_list(), [0, 1, 2, 3, 3, 4, 5, 6])

if __name__ == "__main__":
    unittest.main()
