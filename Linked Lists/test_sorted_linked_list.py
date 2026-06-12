"""Tests for the sorted linked-list container.

These tests focus on the sorted invariant: every public mutation should either
keep values in ascending order or reject the operation before changing links.
"""

from __future__ import annotations

import unittest

from linked_list import LinkedList, SortedLinkedList


class TestSortedLinkedList(unittest.TestCase):
    """Unit tests for SortedLinkedList behavior and link integrity."""

    def assert_sorted_integrity(
        self,
        sorted_list: SortedLinkedList,
        expected: list,
    ) -> None:
        """Assert sorted values plus basic linked-structure invariants."""
        self.assertEqual(sorted_list.to_list(), expected)
        self.assertEqual(len(sorted_list), len(expected))
        self.assertEqual(expected, sorted(expected))

        if not expected:
            self.assertIsNone(sorted_list.head)
            self.assertIsNone(sorted_list.tail)
            return

        self.assertIsNotNone(sorted_list.head)
        self.assertIsNotNone(sorted_list.tail)
        self.assertEqual(sorted_list.head.data, expected[0])
        self.assertEqual(sorted_list.tail.data, expected[-1])

        if "circular" in sorted_list._list_type:
            self.assertIs(sorted_list.tail.next, sorted_list.head)
            if "doubly" in sorted_list._list_type:
                self.assertIs(sorted_list.head.prev, sorted_list.tail)
        else:
            self.assertIsNone(sorted_list.tail.next)
            if "doubly" in sorted_list._list_type:
                self.assertIsNone(sorted_list.head.prev)

    def assert_singly_nodes_have_no_prev(
        self,
        sorted_list: SortedLinkedList,
    ) -> None:
        """Assert that singly linked sorted-list nodes stay singly linked."""
        current = sorted_list.head
        for _ in range(len(sorted_list)):
            self.assertFalse(hasattr(current, "prev"))
            current = current.next

    def test_constructor_sorts_iterable_for_each_list_type(self) -> None:
        for list_type in (
            "singly",
            "doubly",
            "singly_circular",
            "doubly_circular",
        ):
            sorted_list = SortedLinkedList(list_type, [4, 1, 3, 2, 2])

            self.assert_sorted_integrity(sorted_list, [1, 2, 2, 3, 4])
            if "singly" in list_type:
                self.assert_singly_nodes_have_no_prev(sorted_list)

    def test_constructor_accepts_iterable_as_first_argument(self) -> None:
        sorted_list = SortedLinkedList([3, 1, 2])

        self.assertEqual(sorted_list._list_type, "singly")
        self.assert_sorted_integrity(sorted_list, [1, 2, 3])

    def test_add_append_prepend_and_extend_keep_order(self) -> None:
        sorted_list = SortedLinkedList("doubly")

        sorted_list.append(5)
        sorted_list.prepend(1)
        sorted_list.add(3)
        sorted_list.extend([2, 4])

        self.assert_sorted_integrity(sorted_list, [1, 2, 3, 4, 5])

    def test_extend_with_self_uses_snapshot(self) -> None:
        sorted_list = SortedLinkedList([3, 1, 2])

        sorted_list.extend(sorted_list)

        self.assert_sorted_integrity(sorted_list, [1, 1, 2, 2, 3, 3])

    def test_insert_allows_only_sorted_positions(self) -> None:
        sorted_list = SortedLinkedList([1, 3, 5])

        sorted_list.insert(1, 2)
        sorted_list.insert(4, 6)

        self.assert_sorted_integrity(sorted_list, [1, 2, 3, 5, 6])

        with self.assertRaises(ValueError):
            sorted_list.insert(0, 4)
        with self.assertRaises(IndexError):
            sorted_list.insert(-1, 0)
        with self.assertRaises(IndexError):
            sorted_list.insert(99, 7)

        self.assert_sorted_integrity(sorted_list, [1, 2, 3, 5, 6])

    def test_insert_comparison_error_leaves_list_unchanged(self) -> None:
        sorted_list = SortedLinkedList([1, 2])

        with self.assertRaises(TypeError):
            sorted_list.insert(1, "bad")

        self.assert_sorted_integrity(sorted_list, [1, 2])

    def test_setitem_allows_only_sorted_assignments(self) -> None:
        sorted_list = SortedLinkedList([1, 3, 5])

        sorted_list[1] = 4
        sorted_list[-1] = 4

        self.assert_sorted_integrity(sorted_list, [1, 4, 4])

    def test_setitem_comparison_error_leaves_list_unchanged(self) -> None:
        sorted_list = SortedLinkedList([1, 2, 3])

        with self.assertRaises(TypeError):
            sorted_list[1] = "bad"

        self.assert_sorted_integrity(sorted_list, [1, 2, 3])

        with self.assertRaises(ValueError):
            sorted_list[1] = 0
        with self.assertRaises(IndexError):
            sorted_list[5] = 9

        self.assert_sorted_integrity(sorted_list, [1, 2, 3])

    def test_replace_reorders_values_and_supports_count(self) -> None:
        sorted_list = SortedLinkedList([1, 2, 2, 3, 4])

        self.assertEqual(sorted_list.replace(2, 5, count=1), 1)
        self.assert_sorted_integrity(sorted_list, [1, 2, 3, 4, 5])

        self.assertEqual(sorted_list.replace(2, 0), 1)
        self.assert_sorted_integrity(sorted_list, [0, 1, 3, 4, 5])

        self.assertEqual(sorted_list.replace(5, 5), 1)
        self.assertEqual(sorted_list.replace(5, 9, count=0), 0)
        self.assert_sorted_integrity(sorted_list, [0, 1, 3, 4, 5])

    def test_remove_pop_and_remove_at_keep_order(self) -> None:
        sorted_list = SortedLinkedList([4, 1, 3, 2, 2])

        self.assertTrue(sorted_list.remove(2))
        self.assertEqual(sorted_list.remove_all(2), 1)
        self.assertEqual(sorted_list.remove_at(1), 3)
        self.assertEqual(sorted_list.pop_front(), 1)
        self.assertEqual(sorted_list.pop(), 4)

        self.assert_sorted_integrity(sorted_list, [])

    def test_merge_copies_values_and_preserves_other_list(self) -> None:
        sorted_list = SortedLinkedList("singly", [2, 4])
        other = LinkedList("singly")
        for value in [5, 1, 3]:
            other.append(value)

        sorted_list.merge(other)

        self.assert_sorted_integrity(sorted_list, [1, 2, 3, 4, 5])
        self.assertEqual(other.to_list(), [5, 1, 3])

        different_type = LinkedList("doubly")
        with self.assertRaises(TypeError):
            sorted_list.merge(different_type)

    def test_merge_with_self_uses_snapshot(self) -> None:
        sorted_list = SortedLinkedList([3, 1, 2])

        sorted_list.merge(sorted_list)

        self.assert_sorted_integrity(sorted_list, [1, 1, 2, 2, 3, 3])

    def test_remove_duplicates_supports_unhashable_values(self) -> None:
        sorted_list = SortedLinkedList("doubly", [[2], [1], [1], [2], [3]])

        sorted_list.remove_duplicates()

        self.assert_sorted_integrity(sorted_list, [[1], [2], [3]])
        self.assertIsNone(sorted_list.head.prev)
        self.assertIsNone(sorted_list.tail.next)

    def test_circular_remove_duplicates_supports_unhashable_values(
        self,
    ) -> None:
        for list_type in ("singly_circular", "doubly_circular"):
            sorted_list = SortedLinkedList(
                list_type,
                [[2], [1], [1], [2], [3]],
            )

            sorted_list.remove_duplicates()

            self.assert_sorted_integrity(sorted_list, [[1], [2], [3]])
            if list_type == "singly_circular":
                self.assert_singly_nodes_have_no_prev(sorted_list)

    def test_copy_deep_copy_slice_map_and_filter_return_sorted_lists(
        self,
    ) -> None:
        sorted_list = SortedLinkedList.from_list([3, 1, 2], "doubly")

        shallow = sorted_list.copy()
        deep = sorted_list.deep_copy()
        sliced = sorted_list[::-1]
        mapped = sorted_list.map(lambda value: -value)
        filtered = sorted_list.filter(lambda value: value != 2)

        for result in (shallow, deep, sliced, mapped, filtered):
            self.assertIsInstance(result, SortedLinkedList)

        self.assert_sorted_integrity(shallow, [1, 2, 3])
        self.assert_sorted_integrity(deep, [1, 2, 3])
        self.assert_sorted_integrity(sliced, [1, 2, 3])
        self.assert_sorted_integrity(mapped, [-3, -2, -1])
        self.assert_sorted_integrity(filtered, [1, 3])

    def test_sort_resorts_after_direct_internal_value_change(self) -> None:
        sorted_list = SortedLinkedList([1, 2, 3])

        sorted_list.head.data = 9
        sorted_list.sort()

        self.assert_sorted_integrity(sorted_list, [2, 3, 9])

    def test_reverse_and_rotate_are_blocked_when_not_noops(self) -> None:
        sorted_list = SortedLinkedList([1, 2, 3])
        singleton = SortedLinkedList([1])

        with self.assertRaises(ValueError):
            sorted_list.reverse()
        with self.assertRaises(ValueError):
            sorted_list.rotate(1)

        sorted_list.rotate(3)
        singleton.reverse()
        singleton.rotate(5)

        self.assert_sorted_integrity(sorted_list, [1, 2, 3])
        self.assert_sorted_integrity(singleton, [1])

    def test_custom_compare_arguments_are_rejected(self) -> None:
        sorted_list = SortedLinkedList([1, 2, 3])

        with self.assertRaises(ValueError):
            sorted_list.sort(compare=lambda left, right: left > right)
        with self.assertRaises(ValueError):
            sorted_list.insert_sorted(
                4,
                compare=lambda left, right: left > right,
            )
        with self.assertRaises(ValueError):
            sorted_list.merge(
                SortedLinkedList([4]),
                compare=lambda left, right: left > right,
            )

    def test_comparison_errors_leave_existing_list_unchanged(self) -> None:
        sorted_list = SortedLinkedList([1, 2])

        with self.assertRaises(TypeError):
            sorted_list.extend(["bad"])
        self.assert_sorted_integrity(sorted_list, [1, 2])

        with self.assertRaises(TypeError):
            sorted_list.replace(2, "bad")
        self.assert_sorted_integrity(sorted_list, [1, 2])

        with self.assertRaises(TypeError):
            sorted_list.add("bad")
        self.assert_sorted_integrity(sorted_list, [1, 2])

    def test_circular_mutations_preserve_sorted_links(self) -> None:
        for list_type in ("singly_circular", "doubly_circular"):
            sorted_list = SortedLinkedList(list_type, [4, 1, 3, 2])

            sorted_list.add(0)
            sorted_list.replace(3, 5)
            self.assertEqual(sorted_list.remove_at(1), 1)

            self.assert_sorted_integrity(sorted_list, [0, 2, 4, 5])
            if list_type == "singly_circular":
                self.assert_singly_nodes_have_no_prev(sorted_list)


if __name__ == "__main__":
    unittest.main()
