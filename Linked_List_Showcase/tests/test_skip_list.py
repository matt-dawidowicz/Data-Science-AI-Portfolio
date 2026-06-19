"""Tests for the probabilistic skip-list container.

The skip-list tests check user-facing ordered-set behavior and the internal
level invariants that make search efficient on average.
"""

import random
import unittest

from linked_list import SkipList


class TestSkipList(unittest.TestCase):
    """Unit tests for SkipList behavior and linked-level structure."""

    def assert_skip_list_integrity(
        self,
        skip_list: SkipList,
        expected: list,
    ) -> None:
        """Assert sorted values plus every active forward level."""
        self.assertEqual(skip_list.to_list(), expected)
        self.assertEqual(list(skip_list), expected)
        self.assertEqual(len(skip_list), len(expected))
        self.assertEqual(expected, self._sorted_unique(expected))
        self.assertLessEqual(skip_list.level, skip_list.max_level)

        if not expected:
            self.assertIsNone(skip_list.head)
            self.assertIsNone(skip_list.tail)
            self.assertEqual(skip_list.level, 1)
            for next_node in skip_list._head.forward:
                self.assertIsNone(next_node)
            return

        self.assertIsNotNone(skip_list.head)
        self.assertIsNotNone(skip_list.tail)
        self.assertEqual(skip_list.head.data, expected[0])
        self.assertEqual(skip_list.tail.data, expected[-1])

        bottom_nodes = []
        current = skip_list._head.forward[0]
        previous_value = None
        while current is not None:
            self.assertGreaterEqual(current.height, 1)
            self.assertLessEqual(current.height, skip_list.max_level)
            if previous_value is not None:
                self.assertLess(previous_value, current.data)
            bottom_nodes.append(current)
            previous_value = current.data
            current = current.forward[0]

        self.assertEqual([node.data for node in bottom_nodes], expected)
        self.assertIs(skip_list.tail, bottom_nodes[-1])

        for level in range(skip_list.level):
            current = skip_list._head.forward[level]
            level_values = []
            previous_value = None
            while current is not None:
                self.assertGreaterEqual(current.height, level + 1)
                if previous_value is not None:
                    self.assertLess(previous_value, current.data)
                level_values.append(current.data)
                previous_value = current.data
                current = current.forward[level]

            for value in level_values:
                self.assertIn(value, expected)

        for level in range(skip_list.level, skip_list.max_level):
            self.assertIsNone(skip_list._head.forward[level])

    def test_empty_skip_list_state_and_validation(self) -> None:
        skip_list = SkipList(max_level=6, seed=1)

        self.assertFalse(skip_list)
        self.assertTrue(skip_list.is_empty())
        self.assertEqual(str(skip_list), "[]")
        self.assertEqual(repr(skip_list), "SkipList([])")
        self.assert_skip_list_integrity(skip_list, [])

        with self.assertRaises(IndexError):
            skip_list.first()
        with self.assertRaises(IndexError):
            skip_list.last()
        with self.assertRaises(IndexError):
            skip_list.pop_first()
        with self.assertRaises(IndexError):
            skip_list.pop_last()
        with self.assertRaises(TypeError):
            SkipList(max_level=1.5)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            SkipList(max_level=True)
        with self.assertRaises(ValueError):
            SkipList(max_level=0)
        with self.assertRaises(TypeError):
            SkipList(probability="bad")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            SkipList(probability=True)
        with self.assertRaises(ValueError):
            SkipList(probability=0)
        with self.assertRaises(ValueError):
            SkipList(probability=1)

    def test_constructor_sorts_and_deduplicates_values(self) -> None:
        skip_list = SkipList([4, 1, 3, 2, 3, 1], max_level=8, seed=1)

        self.assert_skip_list_integrity(skip_list, [1, 2, 3, 4])
        self.assertEqual(skip_list.first(), 1)
        self.assertEqual(skip_list.last(), 4)
        self.assertTrue(skip_list)
        self.assertEqual(list(reversed(skip_list)), [4, 3, 2, 1])

    def test_add_contains_find_floor_and_ceiling(self) -> None:
        skip_list = SkipList(max_level=8, seed=2)

        self.assertTrue(skip_list.add(3))
        self.assertTrue(skip_list.add(1))
        self.assertTrue(skip_list.add(5))
        self.assertFalse(skip_list.add(3))
        self.assertEqual(skip_list.update([5, 7]), 1)

        self.assertIn(3, skip_list)
        self.assertNotIn(4, skip_list)
        self.assertEqual(skip_list.find(3), 3)
        self.assertIsNone(skip_list.find(4))
        self.assertEqual(skip_list.floor(4), 3)
        self.assertEqual(skip_list.ceiling(4), 5)
        self.assertEqual(skip_list.floor(3), 3)
        self.assertEqual(skip_list.ceiling(3), 3)
        self.assertEqual(skip_list.floor(0, "missing"), "missing")
        self.assertEqual(skip_list.ceiling(8, "missing"), "missing")
        self.assert_skip_list_integrity(skip_list, [1, 3, 5, 7])

    def test_remove_head_middle_tail_and_missing_values(self) -> None:
        skip_list = SkipList([1, 2, 3, 4, 5], max_level=8, seed=3)
        old_head = skip_list.head
        old_tail = skip_list.tail

        self.assertTrue(skip_list.remove(1))
        self.assertEqual(old_head.forward, [])
        self.assertTrue(skip_list.remove(5))
        self.assertEqual(old_tail.forward, [])
        self.assertTrue(skip_list.remove(3))
        self.assertFalse(skip_list.remove(99))

        self.assert_skip_list_integrity(skip_list, [2, 4])
        self.assertEqual(skip_list.first(), 2)
        self.assertEqual(skip_list.last(), 4)

        self.assertTrue(skip_list.discard(2))
        self.assertTrue(skip_list.discard(4))
        self.assertFalse(skip_list.discard(4))
        self.assert_skip_list_integrity(skip_list, [])

    def test_pop_first_and_pop_last_remove_sorted_edges(self) -> None:
        skip_list = SkipList([3, 1, 4, 2], max_level=8, seed=4)

        self.assertEqual(skip_list.pop_first(), 1)
        self.assertEqual(skip_list.pop_last(), 4)
        self.assert_skip_list_integrity(skip_list, [2, 3])

        self.assertEqual(skip_list.pop_first(), 2)
        self.assertEqual(skip_list.pop_last(), 3)
        self.assert_skip_list_integrity(skip_list, [])

    def test_extend_self_copy_and_clear(self) -> None:
        skip_list = SkipList([3, 1, 2], max_level=8, seed=4)

        self.assertEqual(skip_list.extend(skip_list), 0)
        self.assert_skip_list_integrity(skip_list, [1, 2, 3])

        self.assertEqual(skip_list.extend([3, 4, 5]), 2)
        copied = skip_list.copy()
        copied.add(6)

        self.assert_skip_list_integrity(skip_list, [1, 2, 3, 4, 5])
        self.assert_skip_list_integrity(copied, [1, 2, 3, 4, 5, 6])

        old_first = skip_list.head
        skip_list.clear()

        self.assertEqual(old_first.forward, [])
        self.assert_skip_list_integrity(skip_list, [])

    def test_extend_with_self_iterator_is_bounded(self) -> None:
        skip_list = SkipList([3, 1, 2], max_level=8, seed=4)

        self.assertEqual(skip_list.extend(iter(skip_list)), 0)

        self.assert_skip_list_integrity(skip_list, [1, 2, 3])

    def test_extend_comparison_error_is_atomic(self) -> None:
        skip_list = SkipList([1, 2, 3], max_level=8, seed=5)

        with self.assertRaises(TypeError):
            skip_list.extend([4, "bad"])

        self.assert_skip_list_integrity(skip_list, [1, 2, 3])
        self.assertNotIn(4, skip_list)

        with self.assertRaises(TypeError):
            skip_list.extend(["bad"])

        self.assert_skip_list_integrity(skip_list, [1, 2, 3])

    def test_supports_comparable_unhashable_values(self) -> None:
        skip_list = SkipList([[2], [1], [2]], max_level=8, seed=5)

        self.assertFalse(skip_list.add([1]))
        self.assertTrue(skip_list.add([3]))

        self.assertEqual(skip_list.find([2]), [2])
        self.assertEqual(skip_list.floor([2, 5]), [2])
        self.assertEqual(skip_list.ceiling([2, 5]), [3])
        self.assertTrue(skip_list.remove([1]))
        self.assert_skip_list_integrity(skip_list, [[2], [3]])

    def test_from_iterable_preserves_subclass_type(self) -> None:
        class ChildSkipList(SkipList):
            pass

        child = ChildSkipList.from_iterable(
            [2, 1, 2],
            max_level=4,
            seed=5,
        )

        self.assertIsInstance(child, ChildSkipList)
        self.assertEqual(child.max_level, 4)
        self.assert_skip_list_integrity(child, [1, 2])

    def test_equality_and_reproducible_seeded_shape(self) -> None:
        first = SkipList([5, 1, 3, 2, 4], max_level=8, seed=6)
        second = SkipList([5, 1, 3, 2, 4], max_level=8, seed=6)
        different = SkipList([1, 2, 3], max_level=8, seed=6)

        self.assertEqual(first, second)
        self.assertNotEqual(first, different)
        self.assertNotEqual(first, [1, 2, 3, 4, 5])

        first_heights = [node.height for node in self._bottom_nodes(first)]
        second_heights = [node.height for node in self._bottom_nodes(second)]
        self.assertEqual(first_heights, second_heights)

    def test_single_level_mode_behaves_like_sorted_linked_set(self) -> None:
        skip_list = SkipList(
            [5, 1, 3, 2, 4],
            max_level=1,
            probability=0.25,
            seed=7,
        )

        self.assertEqual(skip_list.level, 1)
        self.assertEqual(skip_list.probability, 0.25)
        self.assertTrue(skip_list.add(0))
        self.assertTrue(skip_list.remove(3))
        self.assert_skip_list_integrity(skip_list, [0, 1, 2, 4, 5])
        for node in self._bottom_nodes(skip_list):
            self.assertEqual(node.height, 1)

    def test_comparison_errors_leave_existing_values_unchanged(self) -> None:
        skip_list = SkipList([1, 2, 3], max_level=8, seed=7)

        with self.assertRaises(TypeError):
            skip_list.add("bad")
        self.assert_skip_list_integrity(skip_list, [1, 2, 3])

        with self.assertRaises(TypeError):
            _ = "bad" in skip_list
        self.assert_skip_list_integrity(skip_list, [1, 2, 3])

    def test_randomized_operations_match_sorted_set_behavior(self) -> None:
        for seed in range(30):
            random_source = random.Random(seed)
            skip_list = SkipList(max_level=10, seed=seed)
            expected: set[int] = set()

            for _ in range(150):
                operation = random_source.choice(
                    ["add", "remove", "extend", "clear", "floor", "ceiling"],
                )
                value = random_source.randint(-10, 10)

                if operation == "add":
                    changed = skip_list.add(value)
                    expected_changed = value not in expected
                    expected.add(value)
                    self.assertEqual(changed, expected_changed)
                elif operation == "remove":
                    changed = skip_list.remove(value)
                    expected_changed = value in expected
                    expected.discard(value)
                    self.assertEqual(changed, expected_changed)
                elif operation == "extend":
                    values = [
                        random_source.randint(-10, 10)
                        for _ in range(random_source.randint(0, 5))
                    ]
                    before_size = len(expected)
                    expected.update(values)
                    self.assertEqual(
                        skip_list.extend(values),
                        len(expected) - before_size,
                    )
                elif operation == "clear":
                    skip_list.clear()
                    expected.clear()
                elif operation == "floor":
                    floor_values = [item for item in expected if item <= value]
                    expected_floor = (
                        max(floor_values) if floor_values else None
                    )
                    self.assertEqual(skip_list.floor(value), expected_floor)
                elif operation == "ceiling":
                    ceiling_values = [
                        item for item in expected if item >= value
                    ]
                    expected_ceiling = (
                        min(ceiling_values) if ceiling_values else None
                    )
                    self.assertEqual(
                        skip_list.ceiling(value),
                        expected_ceiling,
                    )

                self.assert_skip_list_integrity(skip_list, sorted(expected))

    def _bottom_nodes(self, skip_list: SkipList) -> list:
        """Return nodes from the fully populated bottom level."""
        nodes = []
        current = skip_list._head.forward[0]
        while current is not None:
            nodes.append(current)
            current = current.forward[0]
        return nodes

    def _sorted_unique(self, values: list) -> list:
        """Return sorted unique values without requiring hashability."""
        unique_values: list = []
        for value in sorted(values):
            if not unique_values or unique_values[-1] != value:
                unique_values.append(value)
        return unique_values


if __name__ == "__main__":
    unittest.main()
