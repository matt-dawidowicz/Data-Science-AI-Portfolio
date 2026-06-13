"""Tests for the adaptive self-organizing linked list."""

from __future__ import annotations

import random
import unittest

from linked_list import SelfOrganizingLinkedList


class TestSelfOrganizingLinkedList(unittest.TestCase):
    """Behavior and invariant tests for adaptive search strategies."""

    def assert_self_organizing_integrity(
        self,
        linked_list: SelfOrganizingLinkedList,
        expected_values: list,
        expected_counts: list[int] | None = None,
    ) -> None:
        """Assert values, access counts, and doubly linked structure."""
        self.assertEqual(linked_list.to_list(), expected_values)
        self.assertEqual(list(linked_list), expected_values)
        self.assertEqual(
            list(reversed(linked_list)),
            list(reversed(expected_values)),
        )
        self.assertEqual(len(linked_list), len(expected_values))

        if expected_counts is not None:
            self.assertEqual(
                [count for _, count in linked_list.to_access_counts()],
                expected_counts,
            )

        if not expected_values:
            self.assertIsNone(linked_list.head)
            self.assertIsNone(linked_list.tail)
            return

        self.assertIsNotNone(linked_list.head)
        self.assertIsNotNone(linked_list.tail)
        self.assertEqual(linked_list.peek_front(), expected_values[0])
        self.assertEqual(linked_list.peek_back(), expected_values[-1])
        self.assertIsNone(linked_list.head.prev)
        self.assertIsNone(linked_list.tail.next)

        current = linked_list.head
        previous = None
        seen = 0
        while current is not None:
            self.assertIs(current.prev, previous)
            previous = current
            current = current.next
            seen += 1

        self.assertIs(previous, linked_list.tail)
        self.assertEqual(seen, len(expected_values))

    def test_empty_state_and_strategy_validation(self) -> None:
        linked_list = SelfOrganizingLinkedList(strategy="none")

        self.assertFalse(linked_list)
        self.assertTrue(linked_list.is_empty())
        self.assertEqual(str(linked_list), "")
        self.assertEqual(
            repr(linked_list),
            "SelfOrganizingLinkedList([], strategy='none')",
        )
        self.assert_self_organizing_integrity(linked_list, [])

        with self.assertRaises(IndexError):
            linked_list.peek_front()
        with self.assertRaises(IndexError):
            linked_list.peek_back()
        with self.assertRaises(IndexError):
            linked_list.pop()
        with self.assertRaises(IndexError):
            linked_list.pop_front()
        with self.assertRaises(IndexError):
            linked_list.access(0)
        with self.assertRaises(ValueError):
            SelfOrganizingLinkedList(strategy="bad")
        with self.assertRaises(ValueError):
            linked_list.set_strategy("bad")

    def test_move_to_front_strategy(self) -> None:
        linked_list = SelfOrganizingLinkedList(
            [1, 2, 3, 4],
            strategy="move_to_front",
        )

        self.assertEqual(linked_list.find(3), 2)
        self.assert_self_organizing_integrity(
            linked_list,
            [3, 1, 2, 4],
            [1, 0, 0, 0],
        )

        self.assertEqual(linked_list.access(2), 2)
        self.assert_self_organizing_integrity(
            linked_list,
            [2, 3, 1, 4],
            [1, 1, 0, 0],
        )

        self.assertEqual(linked_list.search(9, "missing"), "missing")
        self.assert_self_organizing_integrity(
            linked_list,
            [2, 3, 1, 4],
            [1, 1, 0, 0],
        )

    def test_transpose_strategy(self) -> None:
        linked_list = SelfOrganizingLinkedList(
            [1, 2, 3, 4],
            strategy="transpose",
        )

        self.assertEqual(linked_list.search(4), 4)
        self.assert_self_organizing_integrity(
            linked_list,
            [1, 2, 4, 3],
            [0, 0, 1, 0],
        )

        self.assertEqual(linked_list.search(4), 4)
        self.assert_self_organizing_integrity(
            linked_list,
            [1, 4, 2, 3],
            [0, 2, 0, 0],
        )

    def test_frequency_count_strategy(self) -> None:
        linked_list = SelfOrganizingLinkedList(
            ["a", "b", "c", "d"],
            strategy="frequency_count",
        )

        self.assertEqual(linked_list.find("c"), 2)
        self.assert_self_organizing_integrity(
            linked_list,
            ["c", "a", "b", "d"],
            [1, 0, 0, 0],
        )

        linked_list.find("b")
        self.assert_self_organizing_integrity(
            linked_list,
            ["c", "b", "a", "d"],
            [1, 1, 0, 0],
        )

        linked_list.find("b")
        self.assert_self_organizing_integrity(
            linked_list,
            ["b", "c", "a", "d"],
            [2, 1, 0, 0],
        )

    def test_none_strategy_records_counts_without_reordering(self) -> None:
        linked_list = SelfOrganizingLinkedList(
            [1, 2, 3],
            strategy="none",
        )

        self.assertEqual(linked_list.find(3), 2)
        self.assertEqual(linked_list.find(1), 0)
        self.assertEqual(linked_list.access_count(3), 1)
        self.assert_self_organizing_integrity(
            linked_list,
            [1, 2, 3],
            [1, 0, 1],
        )

        linked_list.reset_counts()
        self.assert_self_organizing_integrity(
            linked_list,
            [1, 2, 3],
            [0, 0, 0],
        )

    def test_sequence_mutations_and_search_helpers(self) -> None:
        linked_list = SelfOrganizingLinkedList(strategy="none")

        linked_list.append(2)
        linked_list.prepend(1)
        linked_list.insert(2, 4)
        linked_list.insert(2, 3)
        linked_list.extend([4, 5])

        self.assertIn(3, linked_list)
        self.assertTrue(linked_list.contains_static(5))
        self.assertEqual(linked_list.get(2), 3)
        self.assertEqual(linked_list.get(99, "missing"), "missing")
        self.assertEqual(linked_list.count(4), 2)
        self.assertEqual(linked_list.index(4), 3)
        self.assertEqual(linked_list.access_count(4), 1)

        self.assertEqual(linked_list.remove_at(-1), 5)
        self.assertEqual(linked_list.pop_front(), 1)
        self.assertEqual(linked_list.pop(), 4)
        self.assertTrue(linked_list.remove(3))
        self.assertFalse(linked_list.remove(99))

        self.assert_self_organizing_integrity(linked_list, [2, 4], [0, 1])

        with self.assertRaises(IndexError):
            linked_list.insert(99, 0)
        with self.assertRaises(ValueError):
            linked_list.index("missing")

    def test_replace_remove_all_duplicates_and_unhashable_values(self) -> None:
        linked_list = SelfOrganizingLinkedList(
            [[1], [2], [1], [3], [2], [2]],
            strategy="none",
        )

        self.assertEqual(linked_list.replace([2], [9], count=2), 2)
        self.assertEqual(linked_list.remove_all([9]), 2)
        self.assert_self_organizing_integrity(
            linked_list,
            [[1], [1], [3], [2]],
            [0, 0, 0, 0],
        )

        linked_list.remove_duplicates()
        self.assert_self_organizing_integrity(linked_list, [[1], [3], [2]])

    def test_slice_copy_deep_copy_map_filter_reduce_and_equality(self) -> None:
        linked_list = SelfOrganizingLinkedList(
            [[1], [2], [3]],
            strategy="move_to_front",
        )
        linked_list.find([3])

        sliced = linked_list[1:]
        copied = linked_list.copy()
        deep = linked_list.deep_copy()
        mapped = linked_list.map(lambda value: value + [0])
        filtered = linked_list.filter(lambda value: value[0] != 2)
        reduced = linked_list.reduce(lambda left, right: left + right, [])

        self.assertIsInstance(sliced, SelfOrganizingLinkedList)
        self.assertEqual(sliced.strategy, "move_to_front")
        self.assertEqual(linked_list, copied)
        self.assertEqual(linked_list, deep)
        self.assert_self_organizing_integrity(mapped, [[3, 0], [1, 0], [2, 0]])
        self.assert_self_organizing_integrity(filtered, [[3], [1]])
        self.assertEqual(reduced, [3, 1, 2])

        copied[0].append(99)
        self.assertEqual(linked_list[0], [3, 99])
        self.assertEqual(deep[0], [3])

    def test_reverse_rotate_sort_and_strategy_switch(self) -> None:
        linked_list = SelfOrganizingLinkedList(
            [3, 1, 4, 2],
            strategy="none",
        )
        linked_list.find(4)
        linked_list.find(4)
        linked_list.find(1)

        linked_list.reverse()
        self.assert_self_organizing_integrity(
            linked_list,
            [2, 4, 1, 3],
            [0, 2, 1, 0],
        )

        linked_list.rotate(2)
        self.assert_self_organizing_integrity(
            linked_list,
            [1, 3, 2, 4],
            [1, 0, 0, 2],
        )

        linked_list.sort()
        self.assert_self_organizing_integrity(
            linked_list,
            [1, 2, 3, 4],
            [1, 0, 0, 2],
        )

        linked_list.set_strategy("frequency_count")
        self.assert_self_organizing_integrity(
            linked_list,
            [4, 1, 2, 3],
            [2, 1, 0, 0],
        )

        mixed = SelfOrganizingLinkedList([1, "bad", 2], strategy="none")
        with self.assertRaises(TypeError):
            mixed.sort()
        self.assert_self_organizing_integrity(mixed, [1, "bad", 2])

    def test_self_extension_is_bounded(self) -> None:
        linked_list = SelfOrganizingLinkedList([1, 2, 3], strategy="none")

        linked_list.extend(linked_list)
        linked_list.extend(iter(linked_list))
        linked_list.merge([4])

        self.assert_self_organizing_integrity(
            linked_list,
            [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 4],
        )

    def test_randomized_static_operations_match_python_list(self) -> None:
        for seed in range(40):
            source = random.Random(seed)
            linked_list = SelfOrganizingLinkedList(strategy="none")
            expected: list[int] = []

            for _ in range(180):
                operation = source.choice(
                    [
                        "append",
                        "prepend",
                        "insert",
                        "remove",
                        "remove_at",
                        "pop",
                        "pop_front",
                        "replace",
                        "reverse",
                        "rotate",
                    ],
                )
                value = source.randint(-8, 8)

                if operation == "append":
                    linked_list.append(value)
                    expected.append(value)
                elif operation == "prepend":
                    linked_list.prepend(value)
                    expected.insert(0, value)
                elif operation == "insert":
                    index = source.randint(-len(expected), len(expected))
                    linked_list.insert(index, value)
                    if index < 0:
                        index += len(expected)
                    expected.insert(index, value)
                elif operation == "remove":
                    changed = linked_list.remove(value)
                    if value in expected:
                        expected.remove(value)
                        self.assertTrue(changed)
                    else:
                        self.assertFalse(changed)
                elif operation == "remove_at":
                    if expected:
                        index = source.randrange(-len(expected), len(expected))
                        self.assertEqual(
                            linked_list.remove_at(index),
                            expected.pop(index),
                        )
                    else:
                        with self.assertRaises(IndexError):
                            linked_list.remove_at(0)
                elif operation == "pop":
                    if expected:
                        self.assertEqual(linked_list.pop(), expected.pop())
                    else:
                        with self.assertRaises(IndexError):
                            linked_list.pop()
                elif operation == "pop_front":
                    if expected:
                        self.assertEqual(
                            linked_list.pop_front(),
                            expected.pop(0),
                        )
                    else:
                        with self.assertRaises(IndexError):
                            linked_list.pop_front()
                elif operation == "replace":
                    count = source.choice([None, 0, 1, 2])
                    replacement = source.randint(-8, 8)
                    changed = linked_list.replace(value, replacement, count)
                    limit = float("inf") if count is None else count
                    expected_changed = 0
                    for index, item in enumerate(expected):
                        if item == value and expected_changed < limit:
                            expected[index] = replacement
                            expected_changed += 1
                    self.assertEqual(changed, expected_changed)
                elif operation == "reverse":
                    linked_list.reverse()
                    expected.reverse()
                elif operation == "rotate":
                    steps = source.randint(-20, 20)
                    linked_list.rotate(steps)
                    if expected:
                        steps %= len(expected)
                        expected[:] = expected[-steps:] + expected[:-steps]

                self.assert_self_organizing_integrity(linked_list, expected)


if __name__ == "__main__":
    unittest.main()
