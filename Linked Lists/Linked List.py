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
from copy import deepcopy

class SinglyLinkedNode:
    """
    Represents a node in a singly linked list.

    Attributes:
        data: The data stored in the node.
        next: Reference to the next node in the linked list, or None if there is no next node.
    """

    def __init__(self, data: Any, next_node: Optional["SinglyLinkedNode"] = None) -> None:
        self.data = data
        self.next = next_node

    def __repr__(self) -> str:
        return f"SinglyLinkedNode({self.data!r})"


class DoublyLinkedNode:
    """
    A class that represents a node in a doubly linked list. Each node contains data, a reference to the previous node, and a reference to the next node.

    Attributes:
        data: The value or data stored in the node.
        prev: A reference to the previous node in the doubly linked list. Defaults to None.
        next: A reference to the next node in the doubly linked list. Defaults to None.
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
    """
    A class representing a linked list data structure that supports both singly and doubly linked configurations.

    Attributes:
        _list_type (str): Defines whether the linked list is "singly" or "doubly".
        head (Optional[Any]): The first node in the list or None if the list is empty.
        tail (Optional[Any]): The last node in the list or None if the list is empty.
        _size (int): The number of elements in the linked list.

    Methods:
        __init__(list_type: str): Initializes the linked list with the specified type.
        __len__(): Returns the number of elements in the linked list.
        __iter__(): Returns an iterator to traverse the elements in the linked list.
        __repr__(): Provides a string representation of the linked list for debugging.
        __str__(): Provides a string version of the linked list for visualization.
        __contains__(data: Any): Checks if a given element exists in the list.
        __getitem__(index: int | slice): Retrieves an element or slice of elements at a specified index or range.
        __setitem__(index: int, value: Any): Replaces the value of the element at the specified index.
        __eq__(other: object): Checks if another linked list is equal to this one based on elements.
        __reversed__(): Provides reverse iteration over the list for doubly-linked lists.
        _create_node(data: Any): Creates and returns a new node, either singly or doubly linked.
        append(data: Any): Adds a new element to the end of the linked list.
        prepend(data: Any): Adds a new element to the beginning of the linked list.
        insert(index: int, data: Any): Inserts a new element at the specified index, shifting existing elements.
        insert_sorted(data: Any, compare: Optional[Callable[[Any, Any], bool]]): Inserts an element in sorted order while maintaining the sort.
        remove(data: Any): Removes the first occurrence of the specified element from the list.
        pop(): Removes and returns the last element of the linked list.
        pop_front(): Removes and returns the first element of the linked list.
        extend(iterable: Iterable[Any]): Adds all elements from an iterable to the end of the linked list.
        count(data: Any): Returns the count of occurrences of a specified element in the linked list.
        remove_duplicates(): Removes duplicate elements from the list while retaining the order of the first occurrence.
    """

    def __init__(self, list_type: str = "singly") -> None:
        """
        Initializes a linked list with a specified type.

        Args:
            list_type: The type of the linked list, either 'singly' or 'doubly'. Defaults to 'singly'.

        Raises:
            ValueError: If the list_type is not 'singly' or 'doubly'.
        """
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
        """
        Retrieves an item or a slice from the list.

        Args:
            index: An integer or a slice object specifying the position or range of items to retrieve.

        Returns:
            The data at the specified index or a new list object for the specified slice.

        Raises:
            IndexError: If the index is out of range for integer-based access.
        """
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
        """
        Inserts a new element into the list while maintaining the sorted order. Allows for custom
        comparison logic via a provided comparator function.

        Args:
            data: The data to be inserted into the list.
            compare: An optional callable that accepts two arguments and returns True if the first
                     argument should be ordered before the second. Defaults to ascending order
                     comparison if not provided.

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
        """
        Args:
            data: The data to be removed from the list.

        Returns:
            bool: True if the data was found and removed, False otherwise.
        """
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
        """
        Removes and returns the last element from the linked list.

        Raises:
            IndexError: If the linked list is empty.

        Returns:
            Any: The data from the last element of the linked list.
        """
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
        """
        Removes and returns the first element from the list.

        If the list is empty, raises an IndexError exception. Updates the head of the
        list to the next node. If the list is doubly linked (indicated by _list_type),
        the previous reference of the new head is updated to None. Decreases the size
        of the list by 1. If the size becomes zero, sets the tail to None.

        Returns:
            Any: The data stored in the previous head node.

        Raises:
            IndexError: If the list is empty.
        """
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
        """
        Extends the list by appending elements from the provided iterable.

        Args:
            iterable (Iterable[Any]): An iterable containing elements to be added to the list.
        """
        for item in iterable:
            self.append(item)

    def count(self, data: Any) -> int:
        return sum(1 for item in self if item == data)

    def remove_duplicates(self) -> None:
        """
        Removes duplicate elements from a linked list. The method ensures all duplicate nodes are removed, preserving the
        uniqueness of the elements in the list. It handles both singly and doubly linked lists appropriately and adjusts the
        tail and size of the list when necessary.

        Args:
            None

        Raises:
            None

        Returns:
            None
        """
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
        """
        Args:
            n: The position from the end of the linked list to retrieve the data from. Must be a positive integer and within the size of the list.

        Raises:
            IndexError: If n is less than or equal to 0 or greater than the size of the list.

        Returns:
            The data of the node located at the nth position from the end of the linked list.
        """
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
        """
        Filters the elements of the linked list based on a given predicate function.

        Args:
            predicate: A callable that takes an element of the linked list as input
                       and returns True if the element should be included in the
                       filtered result, False otherwise.

        Returns:
            LinkedList: A new linked list containing only the elements that satisfy
                        the predicate function.
        """
        filtered = LinkedList(self._list_type)
        for data in self:
            if predicate(data):
                filtered.append(data)
        return filtered

    def map(self, func: Callable[[Any], Any]) -> "LinkedList":
        """
        Applies the provided function to each element in the LinkedList and returns a new LinkedList containing the results.

        Args:
            func: A callable function that takes a single argument (an element from the LinkedList) and returns the transformed value.

        Returns:
            A new LinkedList containing the results of applying the function to each element of the original LinkedList.
        """
        mapped = LinkedList(self._list_type)
        for data in self:
            mapped.append(func(data))
        return mapped

    def reduce(self, func: Callable[[Any, Any], Any], initializer: Optional[Any] = None) -> Any:
        """
        Args:
            func: A callable object representing the reduction function. This function takes two arguments
                and combines them into a single result.
            initializer: Optional initial value that is placed at the beginning of the sequence prior
                to performing the reduction. If not provided, the first element of the sequence
                is used as the initial value.
        """
        if initializer is not None:
            return functools_reduce(func, self, initializer)
        return functools_reduce(func, self)

    def clear(self) -> None:
        """
        Clears all elements from the data structure.

        This method resets the data structure by setting the head and tail
        references to None and the size count to 0, effectively removing all
        elements from it.
        """
        self.head = None
        self.tail = None
        self._size = 0

    def to_list(self) -> list:
        """
        Converts the object to a list.

        Returns:
            list: A list containing all elements of the object.
        """
        return list(iter(self))

    @classmethod
    def from_list(cls, lst: list, list_type: str = "singly") -> "LinkedList":
        """
        Converts a given list into a LinkedList instance. The method constructs a new LinkedList of the specified type and appends each element from the input list to the newly created LinkedList.

        Args:
            lst: The list of elements to be converted into a LinkedList.
            list_type: The type of LinkedList to create. Defaults to "singly", but can support other configurations as implemented.

        Returns:
            A new LinkedList instance containing the elements from the input list in the same order.
        """
        linked_list = cls(list_type)
        for item in lst:
            linked_list.append(item)
        return linked_list

    def copy(self) -> "LinkedList":
        """
        Creates a shallow copy of the current LinkedList.

        Returns:
            LinkedList: A new instance of LinkedList containing the same elements as the original list, maintaining the same order.
        """
        new_list = LinkedList(self._list_type)
        for item in self:
            new_list.append(item)
        return new_list



    def deep_copy(self) -> "LinkedList":
        """
        Creates a deep copy of the current LinkedList.

        Returns:
            LinkedList: A new instance of LinkedList containing deeply copied elements of the original list, maintaining the same order.
        """
        new_list = LinkedList(self._list_type)
        for item in self:
            new_list.append(deepcopy(item))  # Ensure elements are deeply copied
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
        """Rotate the linked list by k positions.

        A positive k rotates the list to the right, while a negative k rotates to the left.

        Args:
            k: The number of positions to rotate.
        """
        if self._size == 0 or k % self._size == 0:
            return  # No need to rotate if k is 0 or a multiple of size

        k = k % self._size  # Reduce unnecessary full rotations
        if k < 0:
            k = self._size + k  # Convert negative rotations to equivalent positive rotations

        # Find new tail: (size - k - 1)th node
        new_tail = self.head
        for _ in range(self._size - k - 1):
            new_tail = new_tail.next  # Move to new tail

        new_head = new_tail.next  # New head is the next node
        new_tail.next = None  # Detach new tail

        # Update old tail to point to the old head
        self.tail.next = self.head
        if self._list_type == "doubly":
            self.head.prev = self.tail  # Fix previous pointer

        self.head, self.tail = new_head, new_tail  # Update head and tail

        # Fix prev pointers for doubly linked list
        if self._list_type == "doubly":
            self.head.prev = None  # The new head should not have a previous pointer
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
    """
    Unit tests for the LinkedList class, including various operations like appending, prepending, inserting, removing, sorting, etc.

    Methods:
        setUp: Initializes the test environment by creating pre-populated singly and doubly linked lists with values 0 to 4.
        test_append_and_len: Tests the append operation and checks the length of the list.
        test_prepend: Tests prepending a value to the list.
        test_insert: Tests inserting a value at a specific position in the list.
        test_remove: Tests removing a value from the list.
        test_pop: Tests removing and returning the last element of the list.
        test_pop_front: Tests removing and returning the first element of the list.
        test_getitem_setitem: Tests getting and setting elements using index notation.
        test_slice: Tests slicing a sublist from the list.
        test_equality: Tests equality comparison between two linked lists.
        test_extend: Tests appending multiple elements to the list at once.
        test_count: Tests counting occurrences of a specific value in the list.
        test_remove_duplicates: Tests removing duplicate values from the list.
        test_nth_from_end: Tests retrieving the nth element from the end of the list.
        test_filter_map_reduce: Tests performing filter, map, and reduce operations on the list.
        test_insert_sorted: Tests inserting a value into a sorted list while maintaining sort order.
        test_insert_sorted_empty_list: Tests inserting into an empty list.
        test_insert_sorted_at_head: Tests inserting a new smallest value, making it the head of the list.
        test_insert_sorted_at_tail: Tests inserting a new largest value, making it the tail of the list.
        test_insert_sorted_middle: Tests inserting a value in the middle of a sorted list.
        test_insert_sorted_duplicate: Tests inserting a duplicate value into a sorted list.
        test_insert_sorted_all_same_values: Tests inserting into a list where all the elements are the same.
        test_insert_sorted_large_list: Tests inserting into a large sorted list efficiently.
        test_reverse_sort: Tests reversing and sorting the list.
        test_merge: Tests merging two sorted linked lists into one sorted list.
        test_rotate: Tests rotating the list by a given number of positions.
    """

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
    """
    Integration test for the LinkedList class.

    This test validates the integration of various operations performed on a
    doubly-linked list, ensuring correctness of the final state after a sequence
    of manipulations.

    Test steps:
    1. Append a list of values to the linked list.
    2. Remove duplicate values from the list and verify the result.
    3. Reverse the list and use its sorted representation to create a new list.
    4. Insert a new value into the sorted list and verify its structure.
    5. Merge the sorted list with another linked list containing additional values.
    6. Rotate the merged list by a specified number of steps.
    7. Verify that the rotated list contains the correct elements.
    """

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
