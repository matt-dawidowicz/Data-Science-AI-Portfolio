import unittest
from linked_list.linked_list import LinkedList


class TestLinkedListUnit(unittest.TestCase):
    """
    Unit test class for the LinkedList implementations verifying critical operations such
    as append, prepend, insert, remove and more advanced functionalities such as sorting,
    merging, and filtering.

    Attributes:
        singly: A pre-populated singly linked list containing values [0, 1, 2, 3, 4].
        doubly: A pre-populated doubly linked list containing values [0, 1, 2, 3, 4].

    Methods:
        setUp():
            Initializes the test fixture with two linked lists, one singly and the other doubly.

        test_append_and_len():
            Tests the `append` method and ensures the length of the list is updated correctly.

        test_prepend():
            Tests the `prepend` method to verify head insertion.

        test_insert():
            Tests inserting a value at a specific index using `insert`.

        test_remove():
            Tests removing an element from the list using `remove`.

        test_pop():
            Tests removing and returning the last element using `pop`.

        test_pop_front():
            Tests removing and returning the first element using `pop_front`.

        test_getitem_setitem():
            Verifies the behavior of retrieving and setting elements using index syntax.

        test_slice():
            Tests slicing functionality and extraction of sublists.

        test_equality():
            Verifies the equality check between two linked lists.

        test_extend():
            Tests extending a linked list with another iterable.

        test_count():
            Tests counting occurrences of a specific element in the list.

        test_remove_duplicates():
            Tests the removal of duplicates in the list.

        test_nth_from_end():
            Verifies the behavior of retrieving the nth element from the end of the list.

        test_filter_map_reduce():
            Tests filtering, mapping, and reducing functionalities.

        test_insert_sorted():
            Verifies inserting an element into a sorted list, maintaining order.

        test_insert_sorted_empty_list():
            Verifies inserting into an empty linked list.

        test_insert_sorted_at_head():
            Tests inserting a new smallest element which should become the head.

        test_insert_sorted_at_tail():
            Tests inserting a new largest element which should become the tail.

        test_insert_sorted_middle():
            Tests inserting a value into the middle of a sorted list.

        test_insert_sorted_duplicate():
            Tests inserting a duplicate value and checks correct placement.

        test_insert_sorted_all_same_values():
            Verifies behavior when inserting into a list with all identical values.

        test_insert_sorted_large_list():
            Tests inserting into a large sorted list and verifies correct placement.

        test_reverse_sort():
            Tests reversing and sorting operations.

        test_merge():
            Verifies merging two sorted linked lists into a single sorted list.

        test_rotate():
            Tests rotating the list by a specified number of positions.
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
        """
        Tests the `insert_sorted` method for a LinkedList when the list is initially empty.

        This method checks if the provided value is correctly inserted into
        an empty linked list. It ensures that the resultant list contains only
        the inserted value.

        Args:
            self: The instance of the test class.

        Returns:
            None
        """
        empty_list = LinkedList("singly")
        empty_list.insert_sorted(5)
        self.assertEqual(empty_list.to_list(), [5])

    def test_insert_sorted_at_head(self) -> None:
        """
        Tests the insertion of an element at the head of a singly linked list in sorted order.

        This method verifies that inserting a value smaller than all existing
        values in the linked list correctly places the value at the head of the list.

        Args:
            self: Instance reference of the test class.

        Returns:
            None
        """
        self.singly.insert_sorted(-1)
        self.assertEqual(self.singly.to_list()[0], -1)

    def test_insert_sorted_at_tail(self) -> None:
        """
        Tests the behavior of the `insert_sorted` method when inserting an element
        at the tail of the singly linked list. Validates if the inserted element
        is correctly placed at the end of the list.

        Assertions:
            Checks if the last element of the singly linked list matches the value
            that was inserted.
        """
        self.singly.insert_sorted(10)
        self.assertEqual(self.singly.to_list()[-1], 10)

    def test_insert_sorted_middle(self) -> None:
        """
        Tests the `insert_sorted` method when inserting a value
        into the middle of a singly linked list.

        This method ensures that the provided value is inserted
        in a position that maintains the sorted order of the list.
        The test verifies that the list remains sorted after the
        insertion by comparing the updated list to the expected
        result.
        """
        self.singly.insert_sorted(2.5)
        self.assertEqual(self.singly.to_list(), [0, 1, 2, 2.5, 3, 4])

    def test_insert_sorted_duplicate(self) -> None:
        """
        Tests the `insert_sorted` method of the singly linked list when a duplicate value
        is inserted into the list. The test checks whether the value is correctly inserted
        in its sorted position while maintaining the sorted order of the list.

        The insertion is tested by adding the duplicate value `2` to a pre-existing sorted
        list, and then comparing the resulting list structure to the expected list
        [0, 1, 2, 2, 3, 4].
        """
        self.singly.insert_sorted(2)
        self.assertEqual(self.singly.to_list(), [0, 1, 2, 2, 3, 4])

    def test_insert_sorted_all_same_values(self) -> None:
        """
        Tests the `insert_sorted` method of the LinkedList class when all elements
        in the list have the same value.

        Creates a singly linked list where all elements contain the value 3.
        Inserts another element with the same value (3) into this list in a
        sorted manner. Validates that the resulting list is sorted correctly
        and matches the expected output.
        """
        all_same = LinkedList("singly")
        for _ in range(5):
            all_same.append(3)
        all_same.insert_sorted(3)
        self.assertEqual(all_same.to_list(), [3, 3, 3, 3, 3, 3])

    def test_insert_sorted_large_list(self) -> None:
        """
        Tests the `insert_sorted` method for a large list to ensure it inserts an element at the correct position while maintaining the sorting. The method initializes a singly linked list and appends a range of even numbers (1000 to 1998). It then inserts an odd number (1501) in the sorted list and verifies that the inserted number is present in the list.

        Raises:
            AssertionError: If the inserted element (1501) is not found in the resulting list after insertion.
        """
        large_list = LinkedList("singly")
        for i in range(1000, 2000, 2):  # Only even numbers
            large_list.append(i)
        large_list.insert_sorted(1501)  # Insert an odd number in the middle
        self.assertIn(1501, large_list.to_list())

    def test_reverse_sort(self) -> None:
        """
        Tests the reverse and sort functionality of the list.

        This method creates a copy of the singly linked list, reverses its order,
        and verifies the reversed order. Then it sorts the reversed list and verifies
        that the elements are in ascending order.

        Assertions:
        - Asserts that the reversed list matches the expected reversed order.
        - Asserts that the sorted list matches the expected ascending order.
        """
        rev = self.singly.copy()
        rev.reverse()
        self.assertEqual(rev.to_list(), [4, 3, 2, 1, 0])
        rev.sort()
        self.assertEqual(rev.to_list(), [0, 1, 2, 3, 4])

    def test_merge(self) -> None:
        """
        Tests the merge functionality of two singly linked lists.

        The method initializes two LinkedList instances, `l1` and `l2`, as singly linked lists.
        It appends a set of predefined elements to each list, then merges `l2` into `l1`.
        Finally, the method verifies that `l1`'s elements are sorted in ascending order containing
        elements from both original lists.

        Asserts:
            Verifies that the merged list `l1` contains the elements [1, 2, 3, 4, 5, 6] in ascending order.
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
        Tests the rotate operation of a singly linked list.

        The test ensures that the `rotate` function correctly rotates the elements of a singly linked list by the specified number of places. Specifically, for a given input list [0,1,2,3,4], rotating it by 2 places should result in the list [3,4,0,1,2]. The test verifies this expected behavior by transforming the list and comparing the result with the expected output.
        """
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


if __name__ == '__main__':
    unittest.main()
