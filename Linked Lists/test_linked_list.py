"""Tests for linked-list operations and structural invariants."""

import unittest

from linked_list import LinkedList


class TestLinkedListUnit(unittest.TestCase):
    """Unit tests for core linked-list behavior."""

    def setUp(self) -> None:
        """Build populated singly and doubly linked lists for each test."""
        self.singly = LinkedList("singly")
        self.doubly = LinkedList("doubly")
        for value in range(5):
            self.singly.append(value)
            self.doubly.append(value)

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
        value = self.singly.pop()
        self.assertEqual(value, 4)
        self.assertEqual(len(self.singly), 4)

    def test_pop_front(self) -> None:
        value = self.singly.pop_front()
        self.assertEqual(value, 0)
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
        for value in range(5):
            another.append(value)
        self.assertEqual(self.singly, another)

    def test_extend(self) -> None:
        self.singly.extend([10, 11, 12])
        self.assertEqual(self.singly.to_list()[-3:], [10, 11, 12])

    def test_count(self) -> None:
        self.singly.append(2)
        self.assertEqual(self.singly.count(2), 2)

    def test_remove_duplicates(self) -> None:
        dup_list = LinkedList("singly")
        for value in [1, 2, 2, 3, 3, 3]:
            dup_list.append(value)
        dup_list.remove_duplicates()
        self.assertEqual(dup_list.to_list(), [1, 2, 3])

    def test_nth_from_end(self) -> None:
        self.assertEqual(self.singly.nth_from_end(1), 4)
        self.assertEqual(self.singly.nth_from_end(3), 2)

    def test_filter_map_reduce(self) -> None:
        filtered = self.singly.filter(lambda value: value % 2 == 0)
        self.assertEqual(filtered.to_list(), [0, 2, 4])

        mapped = self.singly.map(lambda value: value * value)
        self.assertEqual(mapped.to_list(), [0, 1, 4, 9, 16])

        result = self.singly.reduce(lambda left, right: left + right)
        self.assertEqual(result, 10)

        result_init = self.singly.reduce(
            lambda left, right: left + right,
            10,
        )
        self.assertEqual(result_init, 20)

    def test_insert_sorted(self) -> None:
        sorted_list = LinkedList("singly")
        for value in [1, 3, 5, 7]:
            sorted_list.append(value)
        sorted_list.insert_sorted(4)
        self.assertEqual(sorted_list.to_list(), [1, 3, 4, 5, 7])

    def test_insert_sorted_empty_list(self) -> None:
        empty_list = LinkedList("singly")
        empty_list.insert_sorted(5)
        self.assertEqual(empty_list.to_list(), [5])

    def test_insert_sorted_at_head(self) -> None:
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
        for value in range(1000, 2000, 2):
            large_list.append(value)
        large_list.insert_sorted(1501)
        self.assertIn(1501, large_list.to_list())

    def test_reverse_sort(self) -> None:
        reversed_list = self.singly.copy()
        reversed_list.reverse()
        self.assertEqual(reversed_list.to_list(), [4, 3, 2, 1, 0])
        reversed_list.sort()
        self.assertEqual(reversed_list.to_list(), [0, 1, 2, 3, 4])

    def test_merge(self) -> None:
        left = LinkedList("singly")
        right = LinkedList("singly")
        for value in [1, 3, 5]:
            left.append(value)
        for value in [2, 4, 6]:
            right.append(value)

        left.merge(right)

        self.assertEqual(left.to_list(), [1, 2, 3, 4, 5, 6])

    def test_rotate(self) -> None:
        self.singly.rotate(2)
        self.assertEqual(self.singly.to_list(), [3, 4, 0, 1, 2])


class TestLinkedListIntegration(unittest.TestCase):
    """Integration tests for multiple linked-list operations."""

    def test_integration(self) -> None:
        linked_list = LinkedList("doubly")
        for value in [5, 3, 1, 2, 3, 4, 5]:
            linked_list.append(value)

        linked_list.remove_duplicates()
        self.assertEqual(sorted(linked_list.to_list()), [1, 2, 3, 4, 5])

        linked_list.reverse()
        sorted_list = LinkedList("doubly")
        for value in sorted(linked_list.to_list()):
            sorted_list.append(value)

        sorted_list.insert_sorted(3)
        self.assertEqual(sorted_list.to_list(), [1, 2, 3, 3, 4, 5])

        other_list = LinkedList("doubly")
        for value in [0, 6]:
            other_list.append(value)

        sorted_list.merge(other_list)
        self.assertEqual(sorted_list.to_list(), [0, 1, 2, 3, 3, 4, 5, 6])

        sorted_list.rotate(3)
        self.assertCountEqual(
            sorted_list.to_list(),
            [0, 1, 2, 3, 3, 4, 5, 6],
        )


class TestCircularLinkedList(unittest.TestCase):
    """Unit tests for circular linked-list behavior."""

    def setUp(self) -> None:
        """Build populated singly and doubly circular lists."""
        self.singly_circular = LinkedList("singly_circular")
        self.doubly_circular = LinkedList("doubly_circular")
        for value in range(5):
            self.singly_circular.append(value)
            self.doubly_circular.append(value)

    def assert_circular_links(self, linked_list: LinkedList) -> None:
        """Assert that circular head and tail links are intact."""
        self.assertIsNotNone(linked_list.head)
        self.assertIsNotNone(linked_list.tail)
        self.assertIs(linked_list.tail.next, linked_list.head)
        if "doubly" in linked_list._list_type:
            self.assertIs(linked_list.head.prev, linked_list.tail)

    def assert_singly_nodes_have_no_prev(
        self,
        linked_list: LinkedList,
    ) -> None:
        """Assert that singly linked nodes do not have ``prev`` links."""
        current = linked_list.head
        for _ in range(len(linked_list)):
            self.assertFalse(hasattr(current, "prev"))
            current = current.next

    def test_singly_circular_integrity(self) -> None:
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
        head = self.doubly_circular.head
        tail = self.doubly_circular.tail

        self.assertIsNotNone(head)
        self.assertIsNotNone(tail)
        self.assertEqual(head.prev, tail)
        self.assertEqual(tail.next, head)

    def test_circular_operations(self) -> None:
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

    def test_circular_nth_from_end_is_bounded(self) -> None:
        self.assertEqual(self.singly_circular.nth_from_end(1), 4)
        self.assertEqual(self.singly_circular.nth_from_end(3), 2)
        self.assertEqual(self.doubly_circular.nth_from_end(1), 4)
        self.assertEqual(self.doubly_circular.nth_from_end(5), 0)

    def test_circular_insert_sorted_updates_links(self) -> None:
        singly_sorted = LinkedList("singly_circular")
        doubly_sorted = LinkedList("doubly_circular")
        for value in [1, 3, 5]:
            singly_sorted.append(value)
            doubly_sorted.append(value)

        for linked_list in (singly_sorted, doubly_sorted):
            linked_list.insert_sorted(0)
            linked_list.insert_sorted(4)
            linked_list.insert_sorted(7)
            self.assertEqual(linked_list.to_list(), [0, 1, 3, 4, 5, 7])
            self.assertEqual(linked_list.head.data, 0)
            self.assertEqual(linked_list.tail.data, 7)
            self.assert_circular_links(linked_list)

    def test_circular_reverse_preserves_orientation_and_links(self) -> None:
        self.singly_circular.reverse()
        self.assertEqual(self.singly_circular.to_list(), [4, 3, 2, 1, 0])
        self.assertEqual(self.singly_circular.head.data, 4)
        self.assertEqual(self.singly_circular.tail.data, 0)
        self.assert_circular_links(self.singly_circular)

        self.doubly_circular.reverse()
        self.assertEqual(self.doubly_circular.to_list(), [4, 3, 2, 1, 0])
        self.assertEqual(self.doubly_circular.head.data, 4)
        self.assertEqual(self.doubly_circular.tail.data, 0)
        self.assert_circular_links(self.doubly_circular)

    def test_circular_merge_preserves_sorted_order_and_links(self) -> None:
        for list_type in ("singly_circular", "doubly_circular"):
            left = LinkedList(list_type)
            right = LinkedList(list_type)
            for value in [1, 3, 5]:
                left.append(value)
            for value in [2, 4, 6]:
                right.append(value)

            left.merge(right)

            self.assertEqual(left.to_list(), [1, 2, 3, 4, 5, 6])
            self.assertEqual(left.tail.data, 6)
            self.assert_circular_links(left)

    def test_circular_remove_duplicates_preserves_links(self) -> None:
        singly = LinkedList("singly_circular")
        doubly = LinkedList("doubly_circular")
        for value in [1, 2, 2, 3, 3]:
            singly.append(value)
            doubly.append(value)

        singly.remove_duplicates()
        self.assertEqual(singly.to_list(), [1, 2, 3])
        self.assert_circular_links(singly)
        self.assert_singly_nodes_have_no_prev(singly)

        doubly.remove_duplicates()
        self.assertEqual(doubly.to_list(), [1, 2, 3])
        self.assert_circular_links(doubly)


class TestLinkedListAdditional(unittest.TestCase):
    """Additional tests for edge cases and utility operations."""

    def test_empty_list_operations(self) -> None:
        empty = LinkedList("singly")
        self.assertEqual(len(empty), 0)

        with self.assertRaises(IndexError):
            empty.pop()
        with self.assertRaises(IndexError):
            empty.pop_front()
        with self.assertRaises(IndexError):
            _ = empty[0]

    def test_out_of_bounds_getitem(self) -> None:
        linked_list = LinkedList("singly")
        for value in range(3):
            linked_list.append(value)

        with self.assertRaises(IndexError):
            _ = linked_list[3]
        with self.assertRaises(IndexError):
            _ = linked_list[-4]

    def test_iteration(self) -> None:
        linked_list = LinkedList("singly")
        expected = [10, 20, 30]
        for value in expected:
            linked_list.append(value)

        result = []
        for item in linked_list:
            result.append(item)

        self.assertEqual(result, expected)

    def test_repr_and_str(self) -> None:
        linked_list = LinkedList("doubly")
        for value in range(3):
            linked_list.append(value)

        self.assertGreater(len(repr(linked_list)), 0)
        self.assertGreater(len(str(linked_list)), 0)

    def test_contains(self) -> None:
        linked_list = LinkedList("singly")
        data = [5, 10, 15]
        for value in data:
            linked_list.append(value)

        for value in data:
            self.assertIn(value, linked_list)
        self.assertNotIn(100, linked_list)

    def test_clear_method(self) -> None:
        linked_list = LinkedList("singly")
        for value in range(10):
            linked_list.append(value)

        linked_list.clear()

        self.assertEqual(len(linked_list), 0)
        self.assertEqual(linked_list.to_list(), [])

    def test_multiple_removals(self) -> None:
        linked_list = LinkedList("singly")
        for value in [1, 2, 3, 2, 4, 2, 5]:
            linked_list.append(value)

        while 2 in linked_list.to_list():
            linked_list.remove(2)

        self.assertNotIn(2, linked_list.to_list())
        self.assertEqual(sorted(linked_list.to_list()), [1, 3, 4, 5])

    def test_copy_independence(self) -> None:
        linked_list = LinkedList("singly")
        for value in range(5):
            linked_list.append(value)

        copied_list = linked_list.copy()
        copied_list.append(100)

        self.assertNotEqual(len(linked_list), len(copied_list))
        self.assertEqual(linked_list.to_list(), [0, 1, 2, 3, 4])
        self.assertEqual(copied_list.to_list()[-1], 100)

    def test_inserting_at_boundaries(self) -> None:
        linked_list = LinkedList("singly")
        linked_list.insert(0, 10)
        self.assertEqual(linked_list.to_list(), [10])

        for value in [20, 30]:
            linked_list.insert(len(linked_list), value)
        self.assertEqual(linked_list.to_list(), [10, 20, 30])

        linked_list.insert(0, 5)
        self.assertEqual(linked_list.to_list(), [5, 10, 20, 30])

    def test_sort_stability(self) -> None:
        linked_list = LinkedList("singly")
        for value in [3, 1, 2, 1, 3]:
            linked_list.append(value)

        linked_list.sort()

        self.assertEqual(linked_list.to_list(), [1, 1, 2, 3, 3])


if __name__ == "__main__":
    unittest.main()
