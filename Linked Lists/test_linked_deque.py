"""Tests for the linked deque implementation.

The deque tests check both public behavior and internal link integrity. That is
important because a linked structure can return the right values while still
having broken ``next`` or ``prev`` pointers internally.
"""

from __future__ import annotations

import unittest

from linked_list import LinkedDeque


class TestLinkedDeque(unittest.TestCase):
    """Unit tests for LinkedDeque behavior and internal links.

    Most tests finish with ``assert_deque_integrity`` so each operation is
    checked from the user's perspective and from the node-link perspective.
    """

    def assert_deque_integrity(
        self,
        linked_deque: LinkedDeque,
        expected: list,
    ) -> None:
        """Assert that values and forward/backward links are consistent.

        This helper proves three things at once: the public value order is
        correct, the head/tail pointers point to the expected ends, and every
        neighboring node agrees about its forward and backward links.
        """
        self.assertEqual(len(linked_deque), len(expected))
        self.assertEqual(linked_deque.to_list(), expected)

        if not expected:
            self.assertIsNone(linked_deque.head)
            self.assertIsNone(linked_deque.tail)
            return

        self.assertIsNotNone(linked_deque.head)
        self.assertIsNotNone(linked_deque.tail)
        self.assertIsNone(linked_deque.head.prev)
        self.assertIsNone(linked_deque.tail.next)
        self.assertEqual(linked_deque.head.data, expected[0])
        self.assertEqual(linked_deque.tail.data, expected[-1])

        current = linked_deque.head
        previous = None
        forward = []
        # Walk left-to-right and verify every node's prev pointer.
        for _ in range(len(expected)):
            self.assertIs(current.prev, previous)
            forward.append(current.data)
            previous = current
            current = current.next

        self.assertIsNone(current)
        self.assertEqual(forward, expected)

        current = linked_deque.tail
        next_node = None
        backward = []
        # Walk right-to-left and verify every node's next pointer.
        for _ in range(len(expected)):
            self.assertIs(current.next, next_node)
            backward.append(current.data)
            next_node = current
            current = current.prev

        self.assertIsNone(current)
        self.assertEqual(backward, list(reversed(expected)))

    def test_empty_deque_state(self) -> None:
        linked_deque = LinkedDeque()

        self.assertFalse(linked_deque)
        self.assertTrue(linked_deque.is_empty())
        self.assertEqual(len(linked_deque), 0)
        self.assertEqual(linked_deque.to_list(), [])
        self.assertEqual(str(linked_deque), "")
        self.assertEqual(repr(linked_deque), "LinkedDeque([])")
        self.assert_deque_integrity(linked_deque, [])

    def test_empty_pop_and_peek_raise(self) -> None:
        linked_deque = LinkedDeque()

        with self.assertRaises(IndexError):
            linked_deque.pop_left()
        with self.assertRaises(IndexError):
            linked_deque.pop_right()
        with self.assertRaises(IndexError):
            linked_deque.peek_left()
        with self.assertRaises(IndexError):
            linked_deque.peek_right()

    def test_init_from_iterable_preserves_order(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        self.assertTrue(linked_deque)
        self.assert_deque_integrity(linked_deque, [1, 2, 3])

    def test_from_iterable_constructor(self) -> None:
        linked_deque = LinkedDeque.from_iterable(range(4))

        self.assert_deque_integrity(linked_deque, [0, 1, 2, 3])

    def test_append_right_on_empty_and_non_empty(self) -> None:
        linked_deque = LinkedDeque()

        linked_deque.append_right(1)
        self.assert_deque_integrity(linked_deque, [1])

        linked_deque.append_right(2)
        linked_deque.append_right(3)
        self.assert_deque_integrity(linked_deque, [1, 2, 3])

    def test_append_left_on_empty_and_non_empty(self) -> None:
        linked_deque = LinkedDeque()

        linked_deque.append_left(3)
        self.assert_deque_integrity(linked_deque, [3])

        linked_deque.append_left(2)
        linked_deque.append_left(1)
        self.assert_deque_integrity(linked_deque, [1, 2, 3])

    def test_python_deque_style_aliases(self) -> None:
        linked_deque = LinkedDeque()

        linked_deque.append(2)
        linked_deque.appendleft(1)
        linked_deque.append(3)
        linked_deque.extendleft([-1, 0])

        self.assert_deque_integrity(linked_deque, [0, -1, 1, 2, 3])
        self.assertEqual(linked_deque.popleft(), 0)
        self.assertEqual(linked_deque.pop(), 3)
        self.assert_deque_integrity(linked_deque, [-1, 1, 2])

    def test_mixed_append_and_pop_operations(self) -> None:
        linked_deque = LinkedDeque()

        linked_deque.append_right(2)
        linked_deque.append_left(1)
        linked_deque.append_right(3)
        linked_deque.append_left(0)

        self.assert_deque_integrity(linked_deque, [0, 1, 2, 3])
        self.assertEqual(linked_deque.pop_left(), 0)
        self.assertEqual(linked_deque.pop_right(), 3)
        self.assert_deque_integrity(linked_deque, [1, 2])

    def test_pop_left_singleton_clears_deque(self) -> None:
        linked_deque = LinkedDeque(["only"])

        self.assertEqual(linked_deque.pop_left(), "only")
        self.assert_deque_integrity(linked_deque, [])

    def test_pop_right_singleton_clears_deque(self) -> None:
        linked_deque = LinkedDeque(["only"])

        self.assertEqual(linked_deque.pop_right(), "only")
        self.assert_deque_integrity(linked_deque, [])

    def test_pop_left_returns_fifo_order(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        self.assertEqual(linked_deque.pop_left(), 1)
        self.assertEqual(linked_deque.pop_left(), 2)
        self.assertEqual(linked_deque.pop_left(), 3)
        self.assert_deque_integrity(linked_deque, [])

    def test_pop_right_returns_lifo_order(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        self.assertEqual(linked_deque.pop_right(), 3)
        self.assertEqual(linked_deque.pop_right(), 2)
        self.assertEqual(linked_deque.pop_right(), 1)
        self.assert_deque_integrity(linked_deque, [])

    def test_peek_does_not_mutate(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        self.assertEqual(linked_deque.peek_left(), 1)
        self.assertEqual(linked_deque.peek_right(), 3)
        self.assertEqual(linked_deque.peek(), 3)
        self.assert_deque_integrity(linked_deque, [1, 2, 3])

    def test_indexing_and_slicing(self) -> None:
        linked_deque = LinkedDeque([0, 1, 2, 3, 4])

        self.assertEqual(linked_deque[0], 0)
        self.assertEqual(linked_deque[2], 2)
        self.assertEqual(linked_deque[-1], 4)
        self.assertEqual(linked_deque.get(3), 3)
        self.assertEqual(linked_deque.get(99, "missing"), "missing")
        self.assertEqual(linked_deque.get(-99, "missing"), "missing")
        self.assertEqual(linked_deque[::-1].to_list(), [4, 3, 2, 1, 0])
        self.assertEqual(linked_deque[1:4].to_list(), [1, 2, 3])
        self.assertIsInstance(linked_deque[1:4], LinkedDeque)

        with self.assertRaises(IndexError):
            _ = linked_deque[5]
        with self.assertRaises(TypeError):
            _ = linked_deque["bad"]

    def test_iteration_and_reversed_iteration(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3, 4])

        self.assertEqual(list(linked_deque), [1, 2, 3, 4])
        self.assertEqual(list(reversed(linked_deque)), [4, 3, 2, 1])

    def test_contains(self) -> None:
        linked_deque = LinkedDeque(["a", "b", "c"])

        self.assertIn("b", linked_deque)
        self.assertNotIn("z", linked_deque)

    def test_count_index_and_find(self) -> None:
        linked_deque = LinkedDeque(["a", "b", "a", "c", "a"])

        self.assertEqual(linked_deque.count("a"), 3)
        self.assertEqual(linked_deque.count("z"), 0)
        self.assertEqual(linked_deque.index("a"), 0)
        self.assertEqual(linked_deque.index("a", 1), 2)
        self.assertEqual(linked_deque.index("a", -2), 4)
        self.assertEqual(linked_deque.find("c"), 3)
        self.assertIsNone(linked_deque.find("missing"))

        with self.assertRaises(ValueError):
            linked_deque.index("missing")

    def test_repr_and_str(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        self.assertEqual(repr(linked_deque), "LinkedDeque([1, 2, 3])")
        self.assertEqual(str(linked_deque), "1 <-> 2 <-> 3")

    def test_equality(self) -> None:
        self.assertEqual(LinkedDeque([1, 2, 3]), LinkedDeque([1, 2, 3]))
        self.assertNotEqual(LinkedDeque([1, 2, 3]), LinkedDeque([1, 3, 2]))
        self.assertNotEqual(LinkedDeque([1, 2, 3]), [1, 2, 3])

    def test_subclass_equality_is_symmetric(self) -> None:
        class ChildDeque(LinkedDeque):
            pass

        base = LinkedDeque([1, 2, 3])
        child = ChildDeque([1, 2, 3])

        self.assertEqual(base, child)
        self.assertEqual(child, base)

    def test_repr_and_str_handle_self_reference(self) -> None:
        linked_deque = LinkedDeque()
        linked_deque.append(linked_deque)

        self.assertEqual(repr(linked_deque), "LinkedDeque([...])")
        self.assertEqual(str(linked_deque), "...")

    def test_repr_and_str_handle_mutual_references(self) -> None:
        first = LinkedDeque()
        second = LinkedDeque()
        first.append(second)
        second.append(first)

        self.assertEqual(repr(first), "LinkedDeque([LinkedDeque([...])])")
        self.assertEqual(str(first), "...")

    def test_copy_independence(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])
        copy = linked_deque.copy()

        copy.append_right(4)

        self.assert_deque_integrity(linked_deque, [1, 2, 3])
        self.assert_deque_integrity(copy, [1, 2, 3, 4])

    def test_from_iterable_and_copy_preserve_subclass_type(self) -> None:
        class ChildDeque(LinkedDeque):
            pass

        child = ChildDeque.from_iterable([1, 2])
        copy = child.copy()

        self.assertIsInstance(child, ChildDeque)
        self.assertIsInstance(copy, ChildDeque)
        self.assert_deque_integrity(copy, [1, 2])

    def test_extend_appends_to_right(self) -> None:
        linked_deque = LinkedDeque([1])

        linked_deque.extend([2, 3, 4])

        self.assert_deque_integrity(linked_deque, [1, 2, 3, 4])

    def test_extend_with_empty_iterables_are_noops(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        linked_deque.extend([])
        linked_deque.extend_left([])

        self.assert_deque_integrity(linked_deque, [1, 2, 3])

    def test_extend_with_self_uses_snapshot(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        linked_deque.extend(linked_deque)

        self.assert_deque_integrity(linked_deque, [1, 2, 3, 1, 2, 3])

    def test_extend_with_self_iterator_is_bounded(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        linked_deque.extend(iter(linked_deque))

        self.assert_deque_integrity(linked_deque, [1, 2, 3, 1, 2, 3])

    def test_extend_with_reversed_self_iterator_is_bounded(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        linked_deque.extend(reversed(linked_deque))

        self.assert_deque_integrity(linked_deque, [1, 2, 3, 3, 2, 1])

    def test_extend_left_prepends_each_item(self) -> None:
        linked_deque = LinkedDeque([4])

        linked_deque.extend_left([1, 2, 3])

        self.assert_deque_integrity(linked_deque, [3, 2, 1, 4])

    def test_extend_left_with_self_uses_snapshot(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        linked_deque.extend_left(linked_deque)

        self.assert_deque_integrity(linked_deque, [3, 2, 1, 1, 2, 3])

    def test_extend_left_with_reversed_self_iterator_is_bounded(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        linked_deque.extend_left(reversed(linked_deque))

        self.assert_deque_integrity(linked_deque, [1, 2, 3, 1, 2, 3])

    def test_extend_left_with_self_iterator_is_bounded(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])

        linked_deque.extend_left(iter(linked_deque))

        self.assert_deque_integrity(linked_deque, [3, 2, 1, 1, 2, 3])

    def test_insert_at_left_middle_right_and_clamped_edges(self) -> None:
        linked_deque = LinkedDeque([1, 3])

        linked_deque.insert(1, 2)
        self.assert_deque_integrity(linked_deque, [1, 2, 3])

        linked_deque.insert(0, 0)
        linked_deque.insert(99, 4)
        self.assert_deque_integrity(linked_deque, [0, 1, 2, 3, 4])

        linked_deque.insert(-1, "before-tail")
        linked_deque.insert(-99, "start")
        self.assert_deque_integrity(
            linked_deque,
            ["start", 0, 1, 2, 3, "before-tail", 4],
        )

    def test_insert_into_empty_deque(self) -> None:
        linked_deque = LinkedDeque()

        linked_deque.insert(25, "only")

        self.assert_deque_integrity(linked_deque, ["only"])

    def test_clear_resets_and_detaches_nodes(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3])
        old_head = linked_deque.head
        old_tail = linked_deque.tail

        linked_deque.clear()

        self.assert_deque_integrity(linked_deque, [])
        self.assertIsNone(old_head.next)
        self.assertIsNone(old_head.prev)
        self.assertIsNone(old_tail.next)
        self.assertIsNone(old_tail.prev)

    def test_clear_empty_deque_is_noop(self) -> None:
        linked_deque = LinkedDeque()

        linked_deque.clear()

        self.assert_deque_integrity(linked_deque, [])

    def test_remove_first_matching_value(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3, 2, 4])

        linked_deque.remove(2)

        self.assert_deque_integrity(linked_deque, [1, 3, 2, 4])

        linked_deque.remove(1)
        linked_deque.remove(4)
        self.assert_deque_integrity(linked_deque, [3, 2])

        with self.assertRaises(ValueError):
            linked_deque.remove(99)

    def test_remove_all_matching_values(self) -> None:
        linked_deque = LinkedDeque([1, 2, 1, 3, 1, 4])

        self.assertEqual(linked_deque.remove_all(1), 3)
        self.assert_deque_integrity(linked_deque, [2, 3, 4])
        self.assertEqual(linked_deque.remove_all(99), 0)
        self.assert_deque_integrity(linked_deque, [2, 3, 4])

    def test_replace_all_and_limited_matches(self) -> None:
        linked_deque = LinkedDeque(["a", "b", "a", "a"])

        self.assertEqual(linked_deque.replace("a", "z", count=2), 2)
        self.assert_deque_integrity(linked_deque, ["z", "b", "z", "a"])
        self.assertEqual(linked_deque.replace("a", "z"), 1)
        self.assert_deque_integrity(linked_deque, ["z", "b", "z", "z"])
        self.assertEqual(linked_deque.replace("z", "x", count=0), 0)
        self.assert_deque_integrity(linked_deque, ["z", "b", "z", "z"])

    def test_remove_and_reverse_empty_and_singleton_states(self) -> None:
        empty = LinkedDeque()
        singleton = LinkedDeque(["only"])

        empty.reverse()
        singleton.reverse()
        self.assert_deque_integrity(empty, [])
        self.assert_deque_integrity(singleton, ["only"])

        singleton.remove("only")
        self.assert_deque_integrity(singleton, [])

    def test_reverse_rewires_links_in_place(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3, 4])

        linked_deque.reverse()

        self.assert_deque_integrity(linked_deque, [4, 3, 2, 1])

        linked_deque.reverse()
        self.assert_deque_integrity(linked_deque, [1, 2, 3, 4])

    def test_rotate_right(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3, 4])

        linked_deque.rotate(1)

        self.assert_deque_integrity(linked_deque, [4, 1, 2, 3])

    def test_rotate_left(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3, 4])

        linked_deque.rotate(-1)

        self.assert_deque_integrity(linked_deque, [2, 3, 4, 1])

    def test_rotate_large_step_count(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3, 4])

        linked_deque.rotate(6)
        self.assert_deque_integrity(linked_deque, [3, 4, 1, 2])

        linked_deque.rotate(-6)
        self.assert_deque_integrity(linked_deque, [1, 2, 3, 4])

    def test_rotate_zero_and_full_step_counts_are_noops(self) -> None:
        linked_deque = LinkedDeque([1, 2, 3, 4])

        linked_deque.rotate(0)
        self.assert_deque_integrity(linked_deque, [1, 2, 3, 4])

        linked_deque.rotate(4)
        self.assert_deque_integrity(linked_deque, [1, 2, 3, 4])

        linked_deque.rotate(-4)
        self.assert_deque_integrity(linked_deque, [1, 2, 3, 4])

    def test_rotate_empty_and_singleton_are_noops(self) -> None:
        empty = LinkedDeque()
        singleton = LinkedDeque([1])

        empty.rotate(5)
        singleton.rotate(5)

        self.assert_deque_integrity(empty, [])
        self.assert_deque_integrity(singleton, [1])

    def test_supports_none_and_object_values(self) -> None:
        marker = object()
        linked_deque = LinkedDeque([None, marker, "value"])

        self.assertIs(linked_deque.peek_left(), None)
        self.assertIs(linked_deque.to_list()[1], marker)
        self.assert_deque_integrity(linked_deque, [None, marker, "value"])

    def test_repeated_alternating_operations_keep_links_consistent(
        self,
    ) -> None:
        linked_deque = LinkedDeque()

        for value in range(10):
            if value % 2 == 0:
                linked_deque.append_left(value)
            else:
                linked_deque.append_right(value)

        self.assert_deque_integrity(
            linked_deque,
            [8, 6, 4, 2, 0, 1, 3, 5, 7, 9],
        )

        for _ in range(3):
            linked_deque.pop_left()
            linked_deque.pop_right()

        self.assert_deque_integrity(linked_deque, [2, 0, 1, 3])


if __name__ == "__main__":
    unittest.main()
