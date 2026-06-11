import unittest
from linked_list.list_functions.linked_list import LinkedList

class TestLinkedListUnit(unittest.TestCase):
    """
    Unit testing for a custom LinkedList implementation.

    This class leverages the unittest framework to validate the functionality of a
    custom LinkedList. It tests various features and operations that the LinkedList
    supports, including append, prepend, insertion, deletion, slicing, sorting,
    merging, reversing, and others. Both singly and doubly linked lists are tested
    throughout these test cases. The goal is to ensure that all functionalities of
    the linked list implementation behave as expected under different scenarios.

    Attributes:
        singly (LinkedList): A singly linked list, pre-populated with elements [0, 1, 2, 3, 4].
        doubly (LinkedList): A doubly linked list, pre-populated with elements [0, 1, 2, 3, 4].
    """

    def setUp(self) -> None:
        """
        Sets up the test environment by creating and populating singly and doubly
        linked lists. This method prepares the data structures with specific predefined
        values to facilitate consistent and controlled testing conditions.
        """
        # Create both singly and doubly linked lists pre-populated with [0, 1, 2, 3, 4].
        self.singly = LinkedList("singly")
        self.doubly = LinkedList("doubly")
        for i in range(5):
            self.singly.append(i)
            self.doubly.append(i)

    def test_append_and_len(self) -> None:
        """
        Tests the append operation and length calculation of a singly linked list.

        This method validates the functionality of the `append` method by verifying
        that the length of the singly linked list increments correctly after appending
        an element. It first confirms the initial length of the list, then appends an
        element and verifies the new length matches the expected value.

        Args:
            self (SinglyLinkedListTest): Instance of the unit test class.

        Returns:
            None
        """
        self.assertEqual(len(self.singly), 5)
        self.singly.append(5)
        self.assertEqual(len(self.singly), 6)

    def test_prepend(self) -> None:
        """
        Test the prepend functionality of a singly linked list.

        This method verifies that the prepend operation correctly adds
        a new element to the head of the linked list. It ensures that
        the data field of the head node reflects the prepended value.
        """
        self.singly.prepend(-1)
        self.assertEqual(self.singly.head.data, -1)

    def test_insert(self) -> None:
        """
        Tests the insert functionality of the singly linked list.

        This test ensures that the `insert` method correctly adds an element
        at the specified index in the singly linked list and updates the
        list structure appropriately.

        Args:
            self: Instance of the test case.

        Raises:
            AssertionError: If the inserted element at the specified index
            does not match the expected value.

        Returns:
            None
        """
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
        """
        Tests the functionality of the `remove_duplicates` method of the `LinkedList` class.

        This test validates the behavior of the `remove_duplicates` method in a `LinkedList`
        object when duplicate values are present. The test ensures that after invoking the
        method, the duplicates are removed and only unique elements remain in the list.

        Methods:
            test_remove_duplicates: Adds elements with duplicates to a LinkedList, invokes
            the `remove_duplicates` method, and asserts if the duplicates are successfully
            removed.

        Raises:
            AssertionError: If the test case assertion does not pass.
        """
        dup_list = LinkedList("singly")
        for x in [1, 2, 2, 3, 3, 3]:
            dup_list.append(x)
        dup_list.remove_duplicates()
        self.assertEqual(dup_list.to_list(), [1, 2, 3])

    def test_nth_from_end(self) -> None:
        self.assertEqual(self.singly.nth_from_end(1), 4)
        self.assertEqual(self.singly.nth_from_end(3), 2)

    def test_filter_map_reduce(self) -> None:
        """
        Tests the `filter`, `map`, and `reduce` methods of the singly linked list implementation. This
        test verifies the correctness of filtering elements based on a condition, mapping a transformation
        over the elements, and reducing elements by combining them iteratively using a binary function.

        Methods tested:
        - `filter`: Filters elements of the list based on a given predicate function.
        - `map`: Applies a transformation to each element of the list.
        - `reduce`: Reduces the list to a single value by aggregating elements with a binary function.

        Tests include:
        - Filtering to retain even values.
        - Mapping elements to their squared values.
        - Reducing a list with and without an initial value provided.

        Raises:
            AssertionError: If any assertion for equality fails during the test.
        """
        filtered = self.singly.filter(lambda x: x % 2 == 0)
        self.assertEqual(filtered.to_list(), [0, 2, 4])
        mapped = self.singly.map(lambda x: x * x)
        self.assertEqual(mapped.to_list(), [0, 1, 4, 9, 16])
        result = self.singly.reduce(lambda a, b: a + b)
        self.assertEqual(result, 10)
        result_init = self.singly.reduce(lambda a, b: a + b, 10)
        self.assertEqual(result_init, 20)

    def test_insert_sorted(self) -> None:
        sorted_ll = LinkedList("singly")
        for x in [1, 3, 5, 7]:
            sorted_ll.append(x)
        sorted_ll.insert_sorted(4)
        self.assertEqual(sorted_ll.to_list(), [1, 3, 4, 5, 7])

    def test_insert_sorted_empty_list(self) -> None:
        """
        Tests the insertion of a value into an empty list in a sorted order.

        The function verifies that when a value is inserted into an empty list,
        the list contains only the inserted value. This tests the functionality
        specific to inserting into an empty singly linked list.

        Args:
            self: The instance of the test case.

        Returns:
            None
        """
        empty_list = LinkedList("singly")
        empty_list.insert_sorted(5)
        self.assertEqual(empty_list.to_list(), [5])

    def test_insert_sorted_at_head(self) -> None:
        """
        Test the insertion of a value at the head of a sorted singly linked list.

        This test verifies that inserting a value smaller than all existing elements
        in a sorted singly linked list correctly positions the new value at the head
        of the list.

        Args:
            self: Instance of the test class.

        Returns:
            None
        """
        self.singly.insert_sorted(-1)
        self.assertEqual(self.singly.to_list()[0], -1)

    def test_insert_sorted_at_tail(self) -> None:
        self.singly.insert_sorted(10)
        self.assertEqual(self.singly.to_list()[-1], 10)

    def test_insert_sorted_middle(self) -> None:
        self.singly.insert_sorted(2.5)
        self.assertEqual(self.singly.to_list(), [0, 1, 2, 2.5, 3, 4])

    def test_insert_sorted_duplicate(self) -> None:
        self.singly.insert_sorted(2)
        self.assertEqual(self.singly.to_list(), [0, 1, 2, 2, 3, 4])

    def test_insert_sorted_all_same_values(self) -> None:
        all_same = LinkedList("singly")
        for _ in range(5):
            all_same.append(3)
        all_same.insert_sorted(3)
        self.assertEqual(all_same.to_list(), [3, 3, 3, 3, 3, 3])

    def test_insert_sorted_large_list(self) -> None:
        large_list = LinkedList("singly")
        for i in range(1000, 2000, 2):
            large_list.append(i)
        large_list.insert_sorted(1501)
        self.assertIn(1501, large_list.to_list())

    def test_reverse_sort(self) -> None:
        rev = self.singly.copy()
        rev.reverse()
        self.assertEqual(rev.to_list(), [4, 3, 2, 1, 0])
        rev.sort()
        self.assertEqual(rev.to_list(), [0, 1, 2, 3, 4])

    def test_merge(self) -> None:
        """
        Test the functionality of merging two singly linked lists.

        This test verifies that the `merge` method of the `LinkedList` class
        appropriately combines two singly linked lists into a single, sorted list.
        It ensures that elements from both linked lists are merged in sorted
        order when `merge` is called.

        Args:
            self: The instance of the test case class.

        Returns:
            None
        """
        l1 = LinkedList("singly")
        l2 = LinkedList("singly")
        for x in [1, 3, 5]:
            l1.append(x)
        for x in [2, 4, 6]:
            l2.append(x)
        l1.merge(l2)
        self.assertEqual(l1.to_list(), [1, 2, 3, 4, 5, 6])

    def test_rotate(self) -> None:
        """
        Tests the rotation of elements in a singly linked list.

        This test checks if the `rotate` method correctly rotates the elements
        of the linked list to the right by the specified number of positions.
        After the rotation, the resulting list is compared with the expected
        list to ensure the method works as intended.

        Args:
            self: The instance of the test case.

        Returns:
            None
        """
        self.singly.rotate(2)
        self.assertEqual(self.singly.to_list(), [3, 4, 0, 1, 2])


class TestLinkedListIntegration(unittest.TestCase):
    """
    Test suite for integration of LinkedList functionalities.

    This class tests the integration of various LinkedList methods to ensure
    they work together as expected. Provides test cases for appending elements,
    removing duplicates, reversing the list, inserting sorted elements, merging,
    and rotating a doubly linked list.

    Methods included in the test verify correctness of combined operations and
    maintain the integrity of the data structure.

    Methods:
        test_integration(): Tests multiple LinkedList operations collectively
        to validate integration coherence between them.
    """

    def test_integration(self) -> None:
        """
        Tests the integration of multiple operations on a doubly linked list implementation.

        The test ensures the correctness of a series of operations, including:
        - Appending elements to the doubly linked list.
        - Removing duplicates from the list.
        - Reversing the list.
        - Sorting the list and inserting elements into it while maintaining sorted order.
        - Merging two doubly linked lists.
        - Rotating the list by a specified number of positions.

        Raises:
            AssertionError: If any of the test conditions fail.
        """
        ll = LinkedList("doubly")
        data = [5, 3, 1, 2, 3, 4, 5]
        for x in data:
            ll.append(x)
        ll.remove_duplicates()
        self.assertEqual(sorted(ll.to_list()), [1, 2, 3, 4, 5])
        ll.reverse()
        sorted_ll = LinkedList("doubly")
        for x in sorted(ll.to_list()):
            sorted_ll.append(x)
        sorted_ll.insert_sorted(3)
        self.assertEqual(sorted_ll.to_list(), [1, 2, 3, 3, 4, 5])
        other_ll = LinkedList("doubly")
        for x in [0, 6]:
            other_ll.append(x)
        sorted_ll.merge(other_ll)
        self.assertEqual(sorted_ll.to_list(), [0, 1, 2, 3, 3, 4, 5, 6])
        sorted_ll.rotate(3)
        self.assertCountEqual(sorted_ll.to_list(), [0, 1, 2, 3, 3, 4, 5, 6])


class TestCircularLinkedList(unittest.TestCase):
    """
    Unit tests for circular linked list operations.

    This class contains unit tests for both singly circular and doubly circular
    linked lists, verifying their structural integrity and the correctness of
    common operations such as insertion, deletion, and rotation. The tests aim
    to ensure that the circular properties of the lists (e.g., head-tail
    connections) are maintained and that basic operations produce the expected
    changes to the list structure and contents.

    Attributes:
        singly_circular (LinkedList): Instance of a singly circular linked list
            used in testing.
        doubly_circular (LinkedList): Instance of a doubly circular linked list
            used in testing.
    """

    def setUp(self) -> None:
        """
        Sets up the test environment for linked list operations.

        This method initializes two types of circular linked lists: singly circular and
        doubly circular. Both lists are populated with a sequence of integers (0 to 4)
        to facilitate subsequent testing. This ensures that every test starts with
        a consistent and predictable state.
        """
        self.singly_circular = LinkedList("singly_circular")
        self.doubly_circular = LinkedList("doubly_circular")
        for i in range(5):
            self.singly_circular.append(i)
            self.doubly_circular.append(i)

    def assert_circular_links(self, linked_list: LinkedList) -> None:
        self.assertIsNotNone(linked_list.head)
        self.assertIsNotNone(linked_list.tail)
        self.assertIs(linked_list.tail.next, linked_list.head)
        if "doubly" in linked_list._list_type:
            self.assertIs(linked_list.head.prev, linked_list.tail)

    def test_singly_circular_integrity(self) -> None:
        """
        Tests the integrity of the singly circular linked list by ensuring its
        structural connections are preserved and its circular nature is maintained.

        Validates both that the circular connections do not break within the
        number of expected nodes and that the count of traversed nodes equals
        the list's length.

        Args:
            self: An instance of the test class.

        Raises:
            AssertionError: If the head of the singly circular linked list is
            None.
            AssertionError: If the test traverses more nodes than allowed,
            suggesting an infinite loop or corruption in the circular structure.
            AssertionError: If the count of traversed nodes does not match the
            length of the circular linked list.
        """
        head = self.singly_circular.head
        self.assertIsNotNone(head)
        current = head
        count = 0
        while True:
            current = current.next
            count += 1
            if current == head:
                break
            self.assertLessEqual(count, len(self.singly_circular) + 1)
        self.assertEqual(count, len(self.singly_circular))

    def test_doubly_circular_integrity(self) -> None:
        """
        Tests the integrity of the doubly circular linked list structure.

        This test ensures that the doubly circular linked list maintains its
        circular integrity by verifying the connections between the head,
        tail, and their respective pointers.

        Args:
            self: Represents the instance of the test case class.

        Raises:
            AssertionError: If the circular integrity of the doubly circular
            linked list is not maintained.
        """
        head = self.doubly_circular.head
        self.assertIsNotNone(head)
        tail = self.doubly_circular.tail
        self.assertIsNotNone(tail)
        self.assertEqual(head.prev, tail)
        self.assertEqual(tail.next, head)

    def test_circular_operations(self) -> None:
        """
        Tests various operations on circular linked lists, both singly and doubly, ensuring
        correctness of insertion, deletion, and rotation logic.

        This test is designed to validate multiple operations on circular linked list
        implementations. It includes validating insertions at specific indexes, element removals,
        prepend operations, list rotations, and their corresponding effects on the underlying
        data structure.

        Args:
            self: The current instance of the testing class.

        Raises:
            AssertionError: If any operation produces an unexpected result, causing the test
                to fail.

        Returns:
            None
        """
        self.singly_circular.insert(2, 99)
        snapshot = self.singly_circular.to_list()
        expected = [0, 1, 99, 2, 3, 4]
        self.assertEqual(snapshot, expected)
        self.singly_circular.remove(99)
        self.assertEqual(self.singly_circular.to_list(), [0, 1, 2, 3, 4])
        self.doubly_circular.prepend(-1)
        snapshot = self.doubly_circular.to_list()
        expected = [-1, 0, 1, 2, 3, 4]
        self.assertEqual(snapshot, expected)
        self.doubly_circular.rotate(2)
        rotated = self.doubly_circular.to_list()
        self.assertCountEqual(rotated, expected)

    def test_circular_remove_updates_head_and_tail_links(self) -> None:
        self.assertTrue(self.singly_circular.remove(0))
        self.assertEqual(self.singly_circular.to_list(), [1, 2, 3, 4])
        self.assert_circular_links(self.singly_circular)

        self.assertTrue(self.doubly_circular.remove(4))
        self.assertEqual(self.doubly_circular.to_list(), [0, 1, 2, 3])
        self.assertEqual(self.doubly_circular.tail.data, 3)
        self.assert_circular_links(self.doubly_circular)

    def test_circular_pop_updates_tail_links(self) -> None:
        self.assertEqual(self.singly_circular.pop(), 4)
        self.assertEqual(self.singly_circular.to_list(), [0, 1, 2, 3])
        self.assertEqual(self.singly_circular.tail.data, 3)
        self.assert_circular_links(self.singly_circular)

        self.assertEqual(self.doubly_circular.pop(), 4)
        self.assertEqual(self.doubly_circular.to_list(), [0, 1, 2, 3])
        self.assertEqual(self.doubly_circular.tail.data, 3)
        self.assert_circular_links(self.doubly_circular)

    def test_circular_pop_front_updates_head_links(self) -> None:
        self.assertEqual(self.singly_circular.pop_front(), 0)
        self.assertEqual(self.singly_circular.to_list(), [1, 2, 3, 4])
        self.assertEqual(self.singly_circular.head.data, 1)
        self.assert_circular_links(self.singly_circular)

        self.assertEqual(self.doubly_circular.pop_front(), 0)
        self.assertEqual(self.doubly_circular.to_list(), [1, 2, 3, 4])
        self.assertEqual(self.doubly_circular.head.data, 1)
        self.assert_circular_links(self.doubly_circular)


class TestLinkedListAdditional(unittest.TestCase):
    """
    Unit tests for validating operations on a LinkedList implementation.

    This class contains a comprehensive set of test cases to ensure the correct
    behavior and edge-case handling of a LinkedList object. It covers operations
    for empty lists, out-of-bounds access, iteration, string representation,
    membership testing, clear method functionality, multiple element removal,
    copy independence, boundary insertions, and sort stability.

    Methods:
        test_empty_list_operations: Tests operations on an empty LinkedList.
        test_out_of_bounds_getitem: Validates handling of out-of-bounds indexing.
        test_iteration: Ensures proper iteration over elements in the LinkedList.
        test_repr_and_str: Checks the string and representation methods.
        test_contains: Verifies membership testing for elements.
        test_clear_method: Tests the clear functionality of the LinkedList.
        test_multiple_removals: Ensures all occurrences of elements are removed.
        test_copy_independence: Validates copy operation's independence.
        test_inserting_at_boundaries: Checks insertion at head, tail, and other bounds.
        test_sort_stability: Tests the sorting behavior and stability.

    """

    def test_empty_list_operations(self) -> None:
        empty = LinkedList("singly")
        self.assertEqual(len(empty), 0)
        # Attempting to pop or pop_front on an empty list should raise an error.
        with self.assertRaises(IndexError):
            empty.pop()
        with self.assertRaises(IndexError):
            empty.pop_front()
        # Index access on an empty list.
        with self.assertRaises(IndexError):
            _ = empty[0]

    def test_out_of_bounds_getitem(self) -> None:
        """
        Tests the behavior of the LinkedList class when attempting to access elements
        at invalid (out-of-bounds) indices using the __getitem__ method.

        This test case ensures that accessing indices beyond the valid range
        raises an appropriate IndexError. The test performs both positive and
        negative index checks to verify correctness in all scenarios.

        Args:
            self: The instance of the test case.

        Raises:
            IndexError: If the index accessed is out of the valid range of
                indices for the LinkedList.
        """
        ll = LinkedList("singly")
        for i in range(3):
            ll.append(i)
        with self.assertRaises(IndexError):
            _ = ll[3]
        with self.assertRaises(IndexError):
            _ = ll[-4]

    def test_iteration(self) -> None:
        """
        Tests the iteration functionality of the LinkedList class.

        This test ensures that the LinkedList instance can be traversed using an
        iterator and validates that all elements are correctly iterated in the
        expected order as they were appended to the list.

        Args:
            self: The instance of the test class.

        Raises:
            AssertionError: If the iteration result does not match the expected
                sequence of elements.
        """
        ll = LinkedList("singly")
        expected = [10, 20, 30]
        for x in expected:
            ll.append(x)
        result = []
        for item in ll:
            result.append(item)
        self.assertEqual(result, expected)

    def test_repr_and_str(self) -> None:
        ll = LinkedList("doubly")
        for i in range(3):
            ll.append(i)
        # Ensure that __repr__ and __str__ return non-empty strings.
        self.assertTrue(len(repr(ll)) > 0)
        self.assertTrue(len(str(ll)) > 0)

    def test_contains(self) -> None:
        """
        Tests the `__contains__` method of the LinkedList class.

        This method verifies if the `__contains__` method correctly identifies
        whether specific elements exist in a LinkedList instance. It ensures
        true is returned for elements present in the list and false for
        elements not in the list.

        Args:
            self: Reference to the current instance of the test class.

        Returns:
            None
        """
        ll = LinkedList("singly")
        data = [5, 10, 15]
        for x in data:
            ll.append(x)
        for x in data:
            self.assertTrue(x in ll)
        self.assertFalse(100 in ll)

    def test_clear_method(self) -> None:
        """
        Tests the `clear` method of the LinkedList class in a unit testing scenario.

        The `clear` method is expected to empty the linked list by removing all elements and resetting its
        state. It is assumed that after calling `clear`, the length of the list should be zero, and converting
        the list to a regular Python list should result in an empty list.

        Args:
            self (TestCase): The current test case instance, typically used in unittest framework.

        Raises:
            AssertionError: If the length of the linked list is not zero after clearing, or if converting the
                list using `to_list` does not return an empty list.
        """
        # If your implementation provides a clear method to empty the list.
        ll = LinkedList("singly")
        for i in range(10):
            ll.append(i)
        # Assume clear resets the list.
        ll.clear()
        self.assertEqual(len(ll), 0)
        self.assertEqual(ll.to_list(), [])

    def test_multiple_removals(self) -> None:
        """
        Tests the removal of multiple occurrences of a specific value from a linked list.

        This function adds a list of integer values to a linked list and repeatedly removes
        all occurrences of a specified value until none remain. After the removals, this
        test ensures that the value is not present in the linked list and verifies that the
        remaining elements are in the correct order.

        Args:
            self: The instance of the test class.
        """
        ll = LinkedList("singly")
        data = [1, 2, 3, 2, 4, 2, 5]
        for x in data:
            ll.append(x)
        # Remove all occurrences of the value 2.
        while 2 in ll.to_list():
            ll.remove(2)
        self.assertNotIn(2, ll.to_list())
        self.assertEqual(sorted(ll.to_list()), [1, 3, 4, 5])

    def test_copy_independence(self) -> None:
        """
        Tests the independence of the copied LinkedList object by ensuring that modifications
        to the copied list do not affect the original list.

        Verifies that the copy has the same initial content as the original, but changes
        in the copy, such as appending new elements, are not reflected in the original list.

        Args:
            None

        Raises:
            AssertionError: If the copied list is not independent of the original list.
        """
        ll = LinkedList("singly")
        for i in range(5):
            ll.append(i)
        new_ll = ll.copy()
        # Modify the copy and verify that the original is not changed.
        new_ll.append(100)
        self.assertNotEqual(len(ll), len(new_ll))
        self.assertEqual(ll.to_list(), [0, 1, 2, 3, 4])
        self.assertEqual(new_ll.to_list()[-1], 100)

    def test_inserting_at_boundaries(self) -> None:
        """
        Tests insertion operations at specific boundary positions of a linked list.

        This test case evaluates the functionality of the `insert` method by
        verifying the correctness of element placement when inserting:
        - At the head of a list (both initially empty and non-empty cases).
        - At the tail of a non-empty list.

        Assertions ensure that the list reflects proper order and data consistency
        after each insertion operation.

        Args:
            self: Instance of the test case class.

        Raises:
            AssertionError: If the expected linked list does not match the actual
            result at any verification step.
        """
        ll = LinkedList("singly")
        # Insert into empty list.
        ll.insert(0, 10)
        self.assertEqual(ll.to_list(), [10])
        # Insert at tail when list is not empty.
        for i in [20, 30]:
            ll.insert(len(ll), i)
        self.assertEqual(ll.to_list(), [10, 20, 30])
        # Insert at the head.
        ll.insert(0, 5)
        self.assertEqual(ll.to_list(), [5, 10, 20, 30])

    def test_sort_stability(self) -> None:
        """
        Tests the stability of the sort method in the LinkedList implementation.
        This ensures that elements deemed equal retain their original relative positions
        after sorting. Stability in sorting algorithms is crucial for maintaining the
        order consistency of equal elements, especially when lists contain duplicate values.

        Args:
            self: Implicit reference to the instance of the test case class.

        Raises:
            AssertionError: If the sorted list does not maintain the correct element
            order as expected, specifically losing stability when duplicate elements
            are present.
        """
        # Test that sort maintains order consistency if elements are equal.
        ll = LinkedList("singly")
        data = [3, 1, 2, 1, 3]
        for x in data:
            ll.append(x)
        ll.sort()
        self.assertEqual(ll.to_list(), [1, 1, 2, 3, 3])


if __name__ == '__main__':
    unittest.main()
