"""
Linked List Module

This module provides a versatile linked list implementation supporting both
singly-linked and doubly-linked lists. It includes a wide range of features:
appending, prepending, inserting, removing, sorting, merging, rotating,
reversing, slicing, mapping, reducing, filtering, duplicate removal, and more.
Unit and integration tests are provided at the end of the module.
"""

from copy import deepcopy
from functools import reduce as functools_reduce
from typing import Any, Optional, Iterator, Callable, Iterable

# Import node classes from nodes.py
from .nodes import SinglyLinkedNode, DoublyLinkedNode, SinglyCircularLinkedNode, DoublyCircularLinkedNode


class LinkedList:
    """
    Represents a linked list structure supporting multiple types.

    This class implements a versatile linked list that can be singly-linked, doubly-linked,
    singly_circular, or doubly_circular, determined by the `list_type` parameter during initialization.
    It provides methods for adding, removing, and retrieving elements, going forward and backward
    through the list, and supports iteration, slicing, and other Python collection-like behaviors.
    The underlying implementation adapts its behavior based on the type of linked list specified.

    Attributes:
        _list_type (str): Defines the type of the linked list as 'singly', 'doubly',
                          'singly_circular', or 'doubly_circular'.
        _is_circular (bool): Indicates whether the list is circular based on its type.
        _size (int): Tracks the number of nodes currently in the linked list.
        head: The first node in the linked list, or None if the list is empty.
        tail: The last node in the linked list, or None if the list is empty.

    Raises:
        ValueError: Raised when an invalid `list_type` is specified during initialization.
    """

    def __init__(self, list_type: str = "singly") -> None:
        """
        Initializes a list structure with a specified type and sets its initial state.

        This constructor allows the creation of a list structure with various types, such as
        singly linked, doubly linked, singly circular, or doubly circular. It normalizes the
        input type to ensure it matches the valid values and initializes additional attributes
        such as the head, tail, size, and whether the list is circular.

        Args:
            list_type (str): The type of list to construct, which must be one of
                "singly", "doubly", "singly_circular", or "doubly_circular". Defaults to "singly".

        Raises:
            ValueError: If the given list_type is not one of the valid options.
        """
        valid_types = ("singly", "doubly", "singly_circular", "doubly_circular")
        normalized_type = list_type.strip().lower()
        if normalized_type not in valid_types:
            raise ValueError(
                "list_type must be one of 'singly', 'doubly', 'singly_circular', or 'doubly_circular'"
            )
        self._list_type = normalized_type
        self.head: Optional[Any] = None
        self.tail: Optional[Any] = None
        self._size: int = 0
        # Determine circularity based on the presence of the substring "circular" in normalized_type.
        self._is_circular = "circular" in normalized_type

    def __len__(self) -> int:
        """
        Calculates and returns the number of elements in the data structure. If the size of the
        data structure is cached in the `_size` attribute, it is returned. Otherwise, the method
        iterates through the linked data structure to count the elements.

        Returns:
            int: The number of elements in the data structure.
        """
        try:
            return self._size
        except AttributeError:
            count = 0
            current = self.head
            while current:
                count += 1
                current = current.next
            return count

    def __iter__(self) -> Iterator[Any]:
        """
        Iterates over the elements of the linked list.

        Provides an iterator to traverse the linked list, yielding data from
        each node. Handles both circular and non-circular linked lists, ensuring
        the correct traversal behavior depending on the type of the list.

        Returns:
            Iterator[Any]: An iterator that yields the data contained in each
            node of the linked list during traversal.
        """
        if self._is_circular:
            if self.head is None:
                return
            current = self.head
            yield current.data
            current = current.next
            while current is not None  and current != self.head:
                yield current.data
                current = current.next
        else:
            current = self.head
            while current:
                yield current.data
                current = current.next

    def __repr__(self) -> str:
        """
        Returns a string representation of the object that provides a clear and concise
        description of the instance, including its elements and type.

        The generated string representation is primarily intended for developers to
        inspect and debug the object. It includes the class name, elements contained
        in the object, and the type of elements specified.

        Returns:
            str: A string representation of the object, including its class name, a
            comma-separated list of elements within square brackets, and the type of
            elements.

        """
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
        """
        Updates the value at the specified index in the linked list. If the index is
        negative, it is treated as an offset from the end of the list. The operation
        replaces the data of the node at the specified index with a new value.

        Args:
            index: The position of the node to update. Supports negative indexing
                to count backwards from the end of the list.
            value: The new value to assign to the node at the specified index.

        Raises:
            IndexError: If the index is out of the valid range of the linked list.
        """
        if index < 0:
            index = self._size + index
        if index < 0 or index >= self._size:
            raise IndexError("Index out of range")
        current = self.head
        for _ in range(index):
            current = current.next  # type: ignore
        current.data = value  # type: ignore

    def __eq__(self, other: object) -> bool:
        """
        Checks if this LinkedList object is equal to another object.

        The method compares the current LinkedList instance to another object.
        Two LinkedList instances are considered equal if they are of the same type,
        have the same size, and contain identical node data in the same order.

        Args:
            other (object): The object to compare with the current LinkedList instance.

        Returns:
            bool: True if the objects are of the same type, have the same size, and
            contain identical node data in the same order; otherwise, False.
        """
        if not isinstance(other, LinkedList):
            return False
        # Quickly check if sizes are different.
        if len(self) != len(other):
            return False
        # Compare node data one-by-one.
        return all(a == b for a, b in zip(self, other))

    def __reversed__(self) -> Iterator[Any]:
        """
        Returns an iterator that yields elements of the list in reverse order.

        This method provides reverse iteration functionality for doubly-linked and
        doubly circular linked lists. It determines the appropriate reverse iteration
        technique based on the type of the list and whether it is circular.

        Raises:
            NotImplementedError: If the list type is not "doubly" or "doubly_circular".

        Returns:
            Iterator[Any]: An iterator for reverse traversal of the list.
        """
        if self._list_type not in ("doubly", "doubly_circular"):
            raise NotImplementedError("Reverse iteration only supported for doubly-linked lists")
        if self._is_circular:
            yield from self._iter_reversed_circular()
        else:
            yield from self._iter_reversed_linear()

    def _iter_reversed_circular(self) -> Iterator[Any]:
        if self.tail is None:
            return
        current_node = self.tail
        yield current_node.data
        current_node = current_node.prev  # type: ignore
        while current_node != self.tail:
            yield current_node.data
            current_node = current_node.prev  # type: ignore

    def _iter_reversed_linear(self) -> Iterator[Any]:
        """
        Generates an iterator that traverses the elements of a linked list in reverse
        order, starting from the tail node.

        The method iterates through each node of the linked list by following the
        'prev' attribute of the current node until reaching the head of the list.

        Returns:
            Iterator[Any]: An iterator providing access to the elements of the linked
            list in reverse order, starting from the tail node and ending at the head.
        """
        current_node = self.tail
        while current_node:
            yield current_node.data
            current_node = current_node.prev  # type: ignore

    def _create_node(self, data: Any) -> Any:
        """
        Create a new node based on the list type.
        For circular lists, this uses the circular node classes.
        For non-circular lists, the standard node classes are used.
        """
        if self._is_circular:
            if self._list_type == "singly_circular":
                return SinglyCircularLinkedNode(data)
            elif self._list_type == "doubly_circular":
                return DoublyCircularLinkedNode(data)
        else:
            if self._list_type == "singly":
                return SinglyLinkedNode(data)
            elif self._list_type == "doubly":
                return DoublyLinkedNode(data)
        # Fallback if something unexpected happens.
        raise ValueError("Invalid list type for node creation")

    def append(self, data: Any) -> None:
        new_node = self._create_node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            if self._is_circular:
                new_node.next = new_node
                if self._list_type in ("doubly", "doubly_circular"):
                    new_node.prev = new_node
        else:
            assert self.tail is not None
            self.tail.next = new_node
            if self._list_type in ("doubly", "doubly_circular"):
                new_node.prev = self.tail  # type: ignore
            self.tail = new_node
            if self._is_circular:
                self.tail.next = self.head
                if self._list_type in ("doubly", "doubly_circular"):
                    self.head.prev = self.tail  # type: ignore
        self._size += 1

    def prepend(self, data: Any) -> None:
        new_node = self._create_node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            if self._is_circular:
                new_node.next = new_node
                if self._list_type in ("doubly", "doubly_circular"):
                    new_node.prev = new_node
        else:
            new_node.next = self.head
            if self._list_type in ("doubly", "doubly_circular"):
                self.head.prev = new_node  # type: ignore
            self.head = new_node
            if self._is_circular:
                self.tail.next = self.head
                if self._list_type in ("doubly", "doubly_circular"):
                    self.head.prev = self.tail  # type: ignore
        self._size += 1


    def insert(self, index: int, data: Any) -> None:
        """
        Inserts a new node with the given data at the specified index in the linked list.

        This method allows adding a new node at any valid position in the linked list. If the
        index is invalid, it raises an IndexError. The method supports both singly and doubly
        linked lists, as well as circular linked lists.

        Args:
            index (int): The position where the new node should be inserted. Must be between
                0 and the current size of the list (inclusive).
            data (Any): The data to be stored in the new node.

        Raises:
            IndexError: If the index is less than 0 or greater than the current size of the list.
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
        if self._list_type == "doubly":
            new_node.prev = current  # type: ignore
            if new_node.next is not None:
                new_node.next.prev = new_node  # type: ignore
        current.next = new_node  # type: ignore

        if self._is_circular:
            assert self.tail is not None
            self.tail.next = self.head
            if self._list_type == "doubly":
                self.head.prev = self.tail  # type: ignore

        self._size += 1

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

    def count(self, data: Any) -> int:
        """
        Counts the number of occurrences of a specified element in the iterable.

        This method iterates through the context in which it is called and evaluates the
        count of a given element within the iterable. It compares each element to the
        specified value using equality. The method is executed with time complexity
        proportional to the size of the iterable.

        Args:
            data: The element to count the occurrences of within the iterable.

        Returns:
            int: The count of occurrences of the specified element in the iterable.
        """
        return sum(1 for item in self if item == data)

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
        """
        Filters the elements of the LinkedList based on a given predicate function.

        This method evaluates each element of the LinkedList using the provided
        predicate function, adding only those elements that satisfy the
        predicate to a new LinkedList. The resulting LinkedList contains
        all elements for which the predicate function returns True.

        Args:
            predicate (Callable[[Any], bool]): A function that takes an element
                of the LinkedList as input and returns a boolean value. If the
                function returns True for an element, the element will be included
                in the resulting filtered LinkedList.

        Returns:
            LinkedList: A new LinkedList instance containing elements that satisfy
            the specified predicate.
        """
        filtered = LinkedList(self._list_type)
        for data in self:
            if predicate(data):
                filtered.append(data)
        return filtered

    def map(self, func: Callable[[Any], Any]) -> "LinkedList":
        mapped = LinkedList(self._list_type)
        # Convert to a list to ensure we don't run into iteration issues for circular lists
        for data in list(self):
            try:
                new_data = func(data)
            except Exception as err:
                raise RuntimeError(f"Mapping function failed on value {data}: {err}") from err
            mapped.append(new_data)
        return mapped

    def reduce(self, func: Callable[[Any, Any], Any], initializer: Optional[Any] = None) -> Any:
        if initializer is not None:
            return functools_reduce(func, self, initializer)
        return functools_reduce(func, self)

    def clear(self) -> None:
        """
        Clears the linked list by breaking all internode references,
        which is particularly important for circular or doubly-linked lists.
        """
        current = self.head

        # If the list is circular, break the circular reference by
        # setting the tail's next pointer to None.
        if self._is_circular and self.tail is not None:
            if hasattr(self.tail, "next"):
                self.tail.next = None

        # Use a set of visited node ids to avoid infinite loops (helpful for circular lists)
        visited = set()
        while current is not None and id(current) not in visited:
            visited.add(id(current))
            next_node = getattr(current, "next", None)

            # Break the node's references to its neighbors.
            if hasattr(current, "next"):
                current.next = None
            if hasattr(current, "prev"):
                current.prev = None

            current = next_node

        self.head = None
        self.tail = None
        self._size = 0

    def to_list(self) -> list:
        """
        Converts the implementing object to a list by iterating through its elements.

        This method invokes the `iter()` function on the instance to retrieve an iterator
        and converts its elements to a list. Useful for creating a list representation
        of objects that implement the iterable protocol.

        Returns:
            list: A list containing all elements of the iterable instance.
        """
        return list(iter(self))

    @classmethod
    def from_list(cls, lst: list, list_type: str = "singly") -> "LinkedList":
        """
        Creates a new LinkedList instance from a given list of elements. The method
        constructs the linked list by appending each element of the provided list to
        the newly created LinkedList. It allows specifying the type of the linked list
        to either "singly" or "doubly". The default type is "singly".

        Args:
            lst (list): A list of elements to construct the linked list from.
            list_type (str): The type of the linked list to create. It can be either
                "singly" or "doubly". Defaults to "singly".

        Returns:
            LinkedList: A new LinkedList instance populated with the elements
            from the given list.
        """
        linked_list = cls(list_type)
        for item in lst:
            linked_list.append(item)
        return linked_list

    def copy(self) -> "LinkedList":
        """
        Creates a shallow copy of the LinkedList.

        This method generates a new instance of LinkedList of the same type as the
        current instance and appends all elements of the existing list to the
        new instance. The order and the type of the elements in the copied list
        will be identical to those in the original list. It is useful for cases
        where a separate copy of the list is required without altering the original
        list's contents.

        Returns:
            LinkedList: A new LinkedList instance that contains the elements of the
                original list in the same order.
        """
        new_list = LinkedList(self._list_type)
        for item in self:
            new_list.append(item)
        return new_list

    def deep_copy(self) -> "LinkedList":
        """
        Creates a deep copy of the LinkedList instance.

        This method generates a new LinkedList instance with the same elements as the
        current list, ensuring that all elements are deep-copied. It guarantees that
        any changes made to the new copy do not affect the original list. The method
        uses the to_list() function for efficient iteration over the elements,
        particularly useful when the LinkedList contains circular references.

        Returns:
            LinkedList: A new LinkedList instance with deep-copied elements.
        """
        # Using to_list() guarantees that we iterate over each element only once,
        # which is important for circular lists.
        copied_elements = [deepcopy(item) for item in self.to_list()]
        new_list = LinkedList.from_list(copied_elements, self._list_type)

        return new_list

    def _split(self, head: Any) -> tuple[Any, Any]:
        """
        Splits a linked list into two halves.

        This method divides a linked list into two separate halves. It identifies the
        middle node of the list using a slow and fast pointer approach. The slow pointer
        progresses one node at a time while the fast pointer progresses two nodes at a
        time. Eventually, when the fast pointer reaches the end of the list, the slow
        pointer will point to the middle of the list. The list is then split into two
        segments from the middle. If the list is doubly linked, it ensures that the
        `prev` reference of the second segment's head is set to `None`.

        Args:
            head (Any): The head node of the linked list to be split.

        Returns:
            tuple[Any, Any]: A tuple containing the head nodes of the two halves of the split list.
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
        """
        Sorts the linked list using the merge sort algorithm.

        This method sorts the linked list in ascending order by default, or based on a
        custom comparator function provided by the user. It is designed for both standard
        and circular linked lists, and supports singly, doubly, and circular doubly-linked
        list types. The method ensures that the list's internal structure (circularity
        and bidirectional links) is properly maintained during and after the sorting
        process.

        Args:
            compare (Optional[Callable[[Any, Any], bool]]): A callable that takes two
                elements from the linked list and returns True if the first element
                should appear before the second in the sorted order and False otherwise.
                If not provided, the elements will be sorted in ascending order using
                their natural ordering (via comparison operators).
        """
        # If the list is circular, break the circular link temporarily.
        if self._is_circular and self.tail:
            self.tail.next = None
            # For doubly circular lists, also clear the backward link from the head.
            if self._list_type in ("doubly_circular",):
                self.head.prev = None

        def _merge_sort(node: Any) -> Any:
            """
            Represents a linked list structure.

            A data structure that consists of nodes where each node contains data and a reference
            to the next node in the sequence. This implementation supports sorting the linked list
            using the merge sort algorithm. Sorting can be customized with a compare function
            provided as an optional argument.
            """
            if not node or not node.next:
                return node
            left, right = self._split(node)
            left = _merge_sort(left)
            right = _merge_sort(right)
            return self._merge_sorted(left, right, compare)

        self.head = _merge_sort(self.head)

        # Reconnect pointers after sorting.
        current = self.head
        prev = None
        while current:
            if self._list_type in ("doubly", "doubly_circular"):
                current.prev = prev  # Update backward pointer for doubly-linked lists.
            prev = current
            if current.next is None:
                self.tail = current
            current = current.next

        # If the list should be circular, restore the circular link.
        if self._is_circular and self.head:
            self.tail.next = self.head
            if self._list_type == "doubly_circular":
                self.head.prev = self.tail

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

    def get_middle(self) -> Optional[Any]:
        """
        Returns the middle element of a singly linked list if it exists.

        This method determines the middle element by advancing two pointers,
        one at a single step (slow pointer) and the other at double steps
        (fast pointer). When the fast pointer reaches the end of the list,
        the slow pointer will be at the middle. If the list is empty, it
        returns None.

        Returns:
            Optional[Any]: The data held in the middle node of the list if
            the list is non-empty; otherwise, None.
        """
        if not self.head:
            return None
        slow = self.head
        fast = self.head
        while fast and fast.next:
            fast = fast.next.next  # type: ignore
            slow = slow.next  # type: ignore
        return slow.data if slow else None

    def insert_after(self, target_data: Any, data: Any) -> bool:
        """
        Inserts a new node with the given data immediately after the first occurrence
        of the target data in the linked list. This method supports singly, doubly,
        circular, and doubly circular linked lists, adjusting node pointers appropriately
        for each list type, including handling updates to the head and tail as needed.

        Args:
            target_data: The data value of the node after which the new node should be
                inserted. It is searched for in the list and the insertion occurs only
                when a node with this data is found.
            data: The data to be stored in the newly inserted node.

        Returns:
            bool: True if the node was successfully inserted after a node with the
            target data, False if no such node exists or the operation could not be
            completed.
        """
        current = self.head
        # For circular lists, save the start to break the loop if needed.
        start = self.head

        while current:
            if current.data == target_data:
                new_node = self._create_node(data)
                new_node.next = current.next

                # For doubly linked lists (including doubly circular), always set the prev pointer
                if self._list_type in ("doubly", "doubly_circular"):
                    new_node.prev = current
                    if new_node.next:
                        new_node.next.prev = new_node

                current.next = new_node

                # If we're inserting after the tail, update the tail pointer and handle circularity.
                if current == self.tail:
                    self.tail = new_node

                    if self._is_circular:
                        # Ensure the tail's next always points to the head.
                        self.tail.next = self.head
                        if self._list_type in ("doubly", "doubly_circular") and self.head:
                            self.head.prev = self.tail

                self._size += 1
                return True

            current = current.next
            # For circular lists, break if we've looped back at the start.
            if self._is_circular and current == start:
                break

        return False
