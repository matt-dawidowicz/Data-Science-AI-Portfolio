"""Tests for the position-based linked-list container."""

import random
import unittest

from linked_list import Position, PositionalLinkedList


class TestPositionalLinkedList(unittest.TestCase):
    """Behavior and position-safety tests for PositionalLinkedList."""

    def assert_positional_integrity(
        self,
        linked_list: PositionalLinkedList,
        expected: list,
    ) -> None:
        """Assert values and doubly linked node invariants."""
        self.assertEqual(linked_list.to_list(), expected)
        self.assertEqual(list(linked_list), expected)
        self.assertEqual(list(reversed(linked_list)), list(reversed(expected)))
        self.assertEqual(len(linked_list), len(expected))
        self.assertEqual(
            [position.data for position in linked_list.positions()],
            expected,
        )

        if not expected:
            self.assertIsNone(linked_list.head)
            self.assertIsNone(linked_list.tail)
            self.assertIsNone(linked_list.first_position())
            self.assertIsNone(linked_list.last_position())
            return

        self.assertIsNotNone(linked_list.head)
        self.assertIsNotNone(linked_list.tail)
        self.assertEqual(linked_list.peek_front(), expected[0])
        self.assertEqual(linked_list.peek_back(), expected[-1])
        self.assertIsNone(linked_list.head.prev)
        self.assertIsNone(linked_list.tail.next)

        current = linked_list.head
        previous = None
        count = 0
        while current is not None:
            self.assertIs(current.prev, previous)
            self.assertIs(current.owner, linked_list)
            previous = current
            current = current.next
            count += 1
        self.assertIs(previous, linked_list.tail)
        self.assertEqual(count, len(expected))

    def test_empty_state_and_basic_errors(self) -> None:
        linked_list = PositionalLinkedList()

        self.assertFalse(linked_list)
        self.assertTrue(linked_list.is_empty())
        self.assertEqual(str(linked_list), "")
        self.assertEqual(repr(linked_list), "PositionalLinkedList([])")
        self.assert_positional_integrity(linked_list, [])

        with self.assertRaises(IndexError):
            linked_list.peek_front()
        with self.assertRaises(IndexError):
            linked_list.peek_back()
        with self.assertRaises(IndexError):
            linked_list.pop_first()
        with self.assertRaises(IndexError):
            linked_list.pop_last()
        with self.assertRaises(IndexError):
            linked_list.position_at(0)
        with self.assertRaises(TypeError):
            linked_list.add_after("bad", 1)  # type: ignore[arg-type]

    def test_add_before_after_and_position_navigation(self) -> None:
        linked_list = PositionalLinkedList()

        second = linked_list.add_first(2)
        first = linked_list.add_before(second, 1)
        fourth = linked_list.add_after(second, 4)
        third = linked_list.add_before(fourth, 3)

        self.assertIsInstance(first, Position)
        self.assertEqual(linked_list.before(second), first)
        self.assertEqual(linked_list.after(second), third)
        self.assertIsNone(linked_list.before(first))
        self.assertIsNone(linked_list.after(fourth))
        self.assertEqual(linked_list.first_position(), first)
        self.assertEqual(linked_list.last_position(), fourth)
        self.assert_positional_integrity(linked_list, [1, 2, 3, 4])

    def test_indexing_slicing_assignment_and_find(self) -> None:
        linked_list = PositionalLinkedList([1, 2, 3, 4, 5])

        self.assertEqual(linked_list[0], 1)
        self.assertEqual(linked_list[-1], 5)
        self.assertEqual(linked_list.get(2), 3)
        self.assertEqual(linked_list.get(99, "missing"), "missing")
        self.assertEqual(linked_list.index(3), 2)
        self.assertEqual(linked_list.count(3), 1)
        self.assertIn(4, linked_list)

        position = linked_list.find(3)
        self.assertIsNotNone(position)
        self.assertEqual(position.data, 3)

        linked_list[2] = 30
        sliced = linked_list[1:5:2]

        self.assertIsInstance(sliced, PositionalLinkedList)
        self.assert_positional_integrity(linked_list, [1, 2, 30, 4, 5])
        self.assert_positional_integrity(sliced, [2, 4])

        with self.assertRaises(ValueError):
            linked_list.index(999)
        with self.assertRaises(TypeError):
            _ = linked_list["bad"]  # type: ignore[index]

    def test_delete_replace_and_stale_position_validation(self) -> None:
        linked_list = PositionalLinkedList([1, 2, 3])
        foreign = PositionalLinkedList([9])
        position = linked_list.position_at(1)
        foreign_position = foreign.first_position()
        self.assertIsNotNone(foreign_position)
        assert foreign_position is not None

        self.assertEqual(linked_list.replace(position, 20), 2)
        self.assertEqual(linked_list.delete(position), 20)
        self.assertFalse(position.is_valid())

        self.assert_positional_integrity(linked_list, [1, 3])

        with self.assertRaises(ValueError):
            _ = position.data
        with self.assertRaises(ValueError):
            linked_list.delete(position)
        with self.assertRaises(ValueError):
            linked_list.add_after(foreign_position, 1)

    def test_move_operations_preserve_position_identity(self) -> None:
        linked_list = PositionalLinkedList([1, 2, 3, 4])
        first = linked_list.position_at(0)
        second = linked_list.position_at(1)
        third = linked_list.position_at(2)
        fourth = linked_list.position_at(3)

        linked_list.move_to_front(third)
        self.assert_positional_integrity(linked_list, [3, 1, 2, 4])
        self.assertEqual(third.data, 3)

        linked_list.move_to_back(first)
        self.assert_positional_integrity(linked_list, [3, 2, 4, 1])
        self.assertEqual(first.data, 1)

        linked_list.move_before(first, third)
        self.assert_positional_integrity(linked_list, [1, 3, 2, 4])

        linked_list.move_after(second, fourth)
        self.assert_positional_integrity(linked_list, [1, 3, 4, 2])

        linked_list.swap(first, fourth)
        self.assert_positional_integrity(linked_list, [4, 3, 1, 2])

    def test_remove_pop_replace_value_duplicates_and_unhashable(self) -> None:
        linked_list = PositionalLinkedList([[1], [2], [1], [3], [2]])

        self.assertEqual(linked_list.replace_value([2], [9], count=1), 1)
        self.assertTrue(linked_list.remove([9]))
        self.assertEqual(linked_list.remove_all([1]), 2)
        self.assertEqual(linked_list.pop_first(), [3])
        self.assertEqual(linked_list.pop_last(), [2])

        self.assert_positional_integrity(linked_list, [])

        linked_list.extend([[1], [2], [1], [3], [2]])
        linked_list.remove_duplicates()
        self.assert_positional_integrity(linked_list, [[1], [2], [3]])

    def test_reverse_rotate_sort_keep_positions_valid(self) -> None:
        linked_list = PositionalLinkedList([3, 1, 4, 2])
        positions = list(linked_list.positions())

        linked_list.reverse()
        self.assert_positional_integrity(linked_list, [2, 4, 1, 3])
        self.assertEqual(
            [position.data for position in positions],
            [3, 1, 4, 2],
        )

        linked_list.rotate(2)
        self.assert_positional_integrity(linked_list, [1, 3, 2, 4])
        self.assertEqual(
            [position.data for position in positions],
            [3, 1, 4, 2],
        )

        linked_list.sort()
        self.assert_positional_integrity(linked_list, [1, 2, 3, 4])
        self.assertEqual(
            [position.data for position in positions],
            [3, 1, 4, 2],
        )

        mixed = PositionalLinkedList([1, "bad", 2])
        with self.assertRaises(TypeError):
            mixed.sort()
        self.assert_positional_integrity(mixed, [1, "bad", 2])

    def test_copy_deep_copy_map_filter_reduce_and_self_extension(self) -> None:
        linked_list = PositionalLinkedList([[1], [2], [3]])

        linked_list.extend(linked_list)
        self.assert_positional_integrity(
            linked_list,
            [[1], [2], [3], [1], [2], [3]],
        )

        copied = linked_list.copy()
        deep = linked_list.deep_copy()
        mapped = linked_list.map(lambda value: value + [0])
        filtered = linked_list.filter(lambda value: value[0] != 2)
        reduced = PositionalLinkedList([1, 2, 3]).reduce(
            lambda left, right: left + right,
            0,
        )

        self.assertEqual(linked_list, copied)
        self.assert_positional_integrity(
            mapped,
            [[1, 0], [2, 0], [3, 0], [1, 0], [2, 0], [3, 0]],
        )
        self.assert_positional_integrity(filtered, [[1], [3], [1], [3]])
        self.assertEqual(reduced, 6)

        copied[0].append(99)
        self.assertEqual(linked_list[0], [1, 99])
        self.assertEqual(deep[0], [1])

    def test_clear_invalidates_existing_positions(self) -> None:
        linked_list = PositionalLinkedList([1, 2, 3])
        positions = list(linked_list.positions())

        linked_list.clear()

        self.assert_positional_integrity(linked_list, [])
        for position in positions:
            self.assertFalse(position.is_valid())
            with self.assertRaises(ValueError):
                _ = position.data

    def test_randomized_operations_match_python_list(self) -> None:
        for seed in range(40):
            source = random.Random(seed)
            linked_list = PositionalLinkedList()
            expected: list[int] = []

            for _ in range(180):
                operation = source.choice(
                    [
                        "append",
                        "prepend",
                        "insert",
                        "remove",
                        "remove_at",
                        "pop_first",
                        "pop_last",
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
                elif operation == "pop_first":
                    if expected:
                        self.assertEqual(
                            linked_list.pop_first(),
                            expected.pop(0),
                        )
                    else:
                        with self.assertRaises(IndexError):
                            linked_list.pop_first()
                elif operation == "pop_last":
                    if expected:
                        self.assertEqual(
                            linked_list.pop_last(),
                            expected.pop(),
                        )
                    else:
                        with self.assertRaises(IndexError):
                            linked_list.pop_last()
                elif operation == "replace":
                    count = source.choice([None, 0, 1, 2])
                    replacement = source.randint(-8, 8)
                    changed = linked_list.replace_value(
                        value,
                        replacement,
                        count,
                    )
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

                self.assert_positional_integrity(linked_list, expected)


if __name__ == "__main__":
    unittest.main()
