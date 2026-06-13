"""Tests for linked-list operations and structural invariants.

The linked-list tests cover normal sequence behavior, circular-list edge cases,
and the pointer invariants that are easiest to break during mutation.
"""

import unittest

from linked_list import LinkedList


class TestLinkedListUnit(unittest.TestCase):
    """Unit tests for core linked-list behavior.

    These tests focus on the operations a user would expect from the public
    ``LinkedList`` API: insertion, removal, indexing, sorting, merging, and
    functional helpers.
    """

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

    def test_truthiness_empty_check_and_peek(self) -> None:
        empty = LinkedList("singly")

        self.assertFalse(empty)
        self.assertTrue(empty.is_empty())
        self.assertTrue(self.singly)
        self.assertFalse(self.singly.is_empty())
        self.assertEqual(self.singly.peek_front(), 0)
        self.assertEqual(self.singly.peek_back(), 4)

        with self.assertRaises(IndexError):
            empty.peek_front()
        with self.assertRaises(IndexError):
            empty.peek_back()

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
        self.assertEqual(self.singly.get(2), 50)
        self.assertEqual(self.singly.get(99, "missing"), "missing")
        self.assertEqual(self.singly.get(-99, "missing"), "missing")

    def test_slice(self) -> None:
        sublist = self.singly[1:3]
        self.assertEqual(sublist.to_list(), [1, 2])
        self.assertEqual(self.singly[::2].to_list(), [0, 2, 4])
        self.assertEqual(self.singly[::-1].to_list(), [4, 3, 2, 1, 0])
        self.assertEqual(self.doubly[4:1:-1].to_list(), [4, 3, 2])

    def test_equality(self) -> None:
        another = LinkedList("singly")
        for value in range(5):
            another.append(value)
        self.assertEqual(self.singly, another)

        same_values_different_type = LinkedList("doubly")
        for value in range(5):
            same_values_different_type.append(value)
        self.assertNotEqual(self.singly, same_values_different_type)
        self.assertNotEqual(same_values_different_type, self.singly)

    def test_extend(self) -> None:
        self.singly.extend([10, 11, 12])
        self.assertEqual(self.singly.to_list()[-3:], [10, 11, 12])

    def test_extend_with_self_iterator_is_bounded(self) -> None:
        linked_list = LinkedList("doubly")
        for value in [1, 2, 3]:
            linked_list.append(value)

        linked_list.extend(iter(linked_list))

        self.assertEqual(linked_list.to_list(), [1, 2, 3, 1, 2, 3])
        self.assertEqual(len(linked_list), 6)
        self.assertIsNone(linked_list.head.prev)
        self.assertIsNone(linked_list.tail.next)

    def test_count(self) -> None:
        self.singly.append(2)
        self.assertEqual(self.singly.count(2), 2)

    def test_index_and_find(self) -> None:
        self.singly.append(2)

        self.assertEqual(self.singly.index(2), 2)
        self.assertEqual(self.singly.index(2, 3), 5)
        self.assertEqual(self.singly.index(2, -2), 5)
        self.assertEqual(self.singly.find(4), 4)
        self.assertIsNone(self.singly.find(99))

        with self.assertRaises(ValueError):
            self.singly.index(99)

    def test_remove_duplicates(self) -> None:
        dup_list = LinkedList("singly")
        for value in [1, 2, 2, 3, 3, 3]:
            dup_list.append(value)
        dup_list.remove_duplicates()
        self.assertEqual(dup_list.to_list(), [1, 2, 3])

    def test_remove_all(self) -> None:
        linked_list = LinkedList("doubly")
        for value in [1, 2, 3, 2, 4, 2]:
            linked_list.append(value)

        self.assertEqual(linked_list.remove_all(2), 3)
        self.assertEqual(linked_list.to_list(), [1, 3, 4])
        self.assertEqual(linked_list.remove_all(99), 0)

    def test_remove_at(self) -> None:
        linked_list = LinkedList("doubly")
        for value in [0, 1, 2, 3, 4]:
            linked_list.append(value)

        self.assertEqual(linked_list.remove_at(0), 0)
        self.assertEqual(linked_list.remove_at(-1), 4)
        self.assertEqual(linked_list.remove_at(1), 2)
        self.assertEqual(linked_list.to_list(), [1, 3])
        self.assertIsNone(linked_list.head.prev)
        self.assertIsNone(linked_list.tail.next)

        with self.assertRaises(IndexError):
            linked_list.remove_at(5)

    def test_replace_all_and_limited_matches(self) -> None:
        linked_list = LinkedList("singly")
        for value in [1, 2, 1, 3, 1]:
            linked_list.append(value)

        self.assertEqual(linked_list.replace(1, 9, count=2), 2)
        self.assertEqual(linked_list.to_list(), [9, 2, 9, 3, 1])
        self.assertEqual(linked_list.replace(1, 9), 1)
        self.assertEqual(linked_list.to_list(), [9, 2, 9, 3, 9])
        self.assertEqual(linked_list.replace(9, 8, count=0), 0)
        self.assertEqual(linked_list.to_list(), [9, 2, 9, 3, 9])

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

        empty = LinkedList("singly")
        self.assertIsNone(
            empty.reduce(lambda left, right: right, None),
        )

        def append_item(items: list[int] | None, item: int) -> list[int]:
            return [*items, item] if items is not None else [item]

        none_init_result = self.singly.reduce(
            append_item,
            None,
        )
        self.assertEqual(none_init_result, [0, 1, 2, 3, 4])

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

    def test_sort_preserves_nodes_and_custom_compare_order(self) -> None:
        linked_list = LinkedList("doubly")
        for value in [2, 1, 3]:
            linked_list.append(value)

        original_nodes = []
        current = linked_list.head
        while current is not None:
            original_nodes.append(current)
            current = current.next

        linked_list.sort(compare=lambda left, right: left > right)

        sorted_nodes = []
        current = linked_list.head
        while current is not None:
            sorted_nodes.append(current)
            current = current.next

        self.assertEqual(linked_list.to_list(), [3, 2, 1])
        self.assertEqual(
            {id(node) for node in sorted_nodes},
            {id(node) for node in original_nodes},
        )
        self.assertIsNone(linked_list.head.prev)
        self.assertIsNone(linked_list.tail.next)

    def test_sort_comparison_error_leaves_linear_links_unchanged(
        self,
    ) -> None:
        for list_type in ("singly", "doubly"):
            linked_list = LinkedList(list_type)
            for value in [1, "bad", 2]:
                linked_list.append(value)

            original_head = linked_list.head
            original_tail = linked_list.tail

            with self.assertRaises(TypeError):
                linked_list.sort()

            self.assertEqual(linked_list.to_list(), [1, "bad", 2])
            self.assertIs(linked_list.head, original_head)
            self.assertIs(linked_list.tail, original_tail)
            self.assertIsNone(linked_list.tail.next)
            if list_type == "doubly":
                self.assertIsNone(linked_list.head.prev)

    def test_merge(self) -> None:
        left = LinkedList("singly")
        right = LinkedList("singly")
        for value in [1, 3, 5]:
            left.append(value)
        for value in [2, 4, 6]:
            right.append(value)

        left.merge(right)

        self.assertEqual(left.to_list(), [1, 2, 3, 4, 5, 6])
        self.assertEqual(right.to_list(), [2, 4, 6])
        self.assertEqual(len(right), 3)

        right.append(8)
        self.assertEqual(left.to_list(), [1, 2, 3, 4, 5, 6])
        self.assertEqual(right.to_list(), [2, 4, 6, 8])

    def test_merge_with_empty_left_copies_other_nodes(self) -> None:
        left = LinkedList("doubly")
        right = LinkedList("doubly")
        for value in [1, 2, 3]:
            right.append(value)

        left.merge(right)
        right.append(4)

        self.assertEqual(left.to_list(), [1, 2, 3])
        self.assertEqual(right.to_list(), [1, 2, 3, 4])
        self.assertEqual(len(left), 3)
        self.assertEqual(len(right), 4)
        self.assertIsNone(left.head.prev)
        self.assertIsNone(left.tail.next)

    def test_merge_with_self_uses_snapshot(self) -> None:
        linked_list = LinkedList("singly")
        for value in [1, 3]:
            linked_list.append(value)

        linked_list.merge(linked_list)

        self.assertEqual(linked_list.to_list(), [1, 1, 3, 3])
        self.assertEqual(len(linked_list), 4)

    def test_rotate(self) -> None:
        self.singly.rotate(2)
        self.assertEqual(self.singly.to_list(), [3, 4, 0, 1, 2])


class TestLinkedListIntegration(unittest.TestCase):
    """Integration tests for multiple linked-list operations.

    This test combines operations to make sure the list still behaves correctly
    after several mutations happen in sequence.
    """

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
    """Unit tests for circular linked-list behavior.

    Circular lists need extra structural checks because traversal does not end
    at ``None``. These tests verify that head and tail remain connected after
    mutations.
    """

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

    def test_circular_slices_preserve_type_and_links(self) -> None:
        singly_reversed = self.singly_circular[::-1]
        doubly_reversed = self.doubly_circular[-1:-4:-1]

        self.assertEqual(singly_reversed.to_list(), [4, 3, 2, 1, 0])
        self.assertEqual(doubly_reversed.to_list(), [4, 3, 2])
        self.assertEqual(singly_reversed._list_type, "singly_circular")
        self.assertEqual(doubly_reversed._list_type, "doubly_circular")
        self.assert_circular_links(singly_reversed)
        self.assert_circular_links(doubly_reversed)
        self.assert_singly_nodes_have_no_prev(singly_reversed)

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

    def test_circular_sort_comparison_error_preserves_links(self) -> None:
        for list_type in ("singly_circular", "doubly_circular"):
            linked_list = LinkedList(list_type)
            for value in [1, "bad", 2]:
                linked_list.append(value)

            original_head = linked_list.head
            original_tail = linked_list.tail

            with self.assertRaises(TypeError):
                linked_list.sort()

            self.assertEqual(linked_list.to_list(), [1, "bad", 2])
            self.assertIs(linked_list.head, original_head)
            self.assertIs(linked_list.tail, original_tail)
            self.assert_circular_links(linked_list)

    def test_singleton_pop_detaches_removed_circular_node(self) -> None:
        for list_type in ("singly_circular", "doubly_circular"):
            for method_name in ("pop", "pop_front"):
                linked_list = LinkedList(list_type)
                linked_list.append("only")
                old_node = linked_list.head

                self.assertEqual(getattr(linked_list, method_name)(), "only")

                self.assertEqual(len(linked_list), 0)
                self.assertIsNone(linked_list.head)
                self.assertIsNone(linked_list.tail)
                self.assertIsNone(old_node.next)
                if list_type == "doubly_circular":
                    self.assertIsNone(old_node.prev)

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
            self.assertEqual(right.to_list(), [2, 4, 6])
            self.assertEqual(len(right), 3)
            self.assert_circular_links(right)

            right.append(8)
            self.assertEqual(left.to_list(), [1, 2, 3, 4, 5, 6])
            self.assertEqual(right.to_list(), [2, 4, 6, 8])
            self.assert_circular_links(left)
            self.assert_circular_links(right)

    def test_circular_merge_with_self_uses_snapshot(self) -> None:
        for list_type in ("singly_circular", "doubly_circular"):
            linked_list = LinkedList(list_type)
            for value in [1, 3]:
                linked_list.append(value)

            linked_list.merge(linked_list)

            self.assertEqual(linked_list.to_list(), [1, 1, 3, 3])
            self.assertEqual(len(linked_list), 4)
            self.assert_circular_links(linked_list)
            if list_type == "singly_circular":
                self.assert_singly_nodes_have_no_prev(linked_list)

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

    def test_remove_duplicates_supports_unhashable_values(self) -> None:
        for list_type in (
            "singly",
            "doubly",
            "singly_circular",
            "doubly_circular",
        ):
            linked_list = LinkedList(list_type)
            for value in [[1], [2], [1], [3], [2]]:
                linked_list.append(value)

            linked_list.remove_duplicates()

            self.assertEqual(linked_list.to_list(), [[1], [2], [3]])
            self.assertEqual(len(linked_list), 3)
            if "circular" in list_type:
                self.assert_circular_links(linked_list)
            else:
                self.assertIsNone(linked_list.tail.next)
                if "doubly" in list_type:
                    self.assertIsNone(linked_list.head.prev)
            if list_type.startswith("singly"):
                self.assert_singly_nodes_have_no_prev(linked_list)

    def test_circular_remove_all_preserves_links(self) -> None:
        singly = LinkedList("singly_circular")
        doubly = LinkedList("doubly_circular")
        for value in [1, 2, 2, 3, 2, 4]:
            singly.append(value)
            doubly.append(value)

        self.assertEqual(singly.remove_all(2), 3)
        self.assertEqual(doubly.remove_all(2), 3)
        self.assertEqual(singly.to_list(), [1, 3, 4])
        self.assertEqual(doubly.to_list(), [1, 3, 4])
        self.assert_circular_links(singly)
        self.assert_circular_links(doubly)
        self.assert_singly_nodes_have_no_prev(singly)

    def test_circular_remove_at_and_replace_preserve_links(self) -> None:
        for list_type in ("singly_circular", "doubly_circular"):
            linked_list = LinkedList(list_type)
            for value in [0, 1, 2, 3, 4]:
                linked_list.append(value)

            self.assertEqual(linked_list.remove_at(0), 0)
            self.assertEqual(linked_list.remove_at(-1), 4)
            self.assertEqual(linked_list.remove_at(1), 2)
            self.assertEqual(linked_list.replace(3, 9), 1)
            self.assertEqual(linked_list.to_list(), [1, 9])
            self.assert_circular_links(linked_list)
            if list_type == "singly_circular":
                self.assert_singly_nodes_have_no_prev(linked_list)


class TestLinkedListAdditional(unittest.TestCase):
    """Additional tests for edge cases and utility operations.

    These tests cover defensive behavior such as empty-list errors,
    out-of-bounds indexing, clear/reset behavior, copy independence, and sort
    stability.
    """

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
