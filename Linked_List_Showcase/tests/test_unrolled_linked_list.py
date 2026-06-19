"""Tests for the unrolled linked-list sequence container."""

import random
import unittest

from linked_list import UnrolledLinkedList


class TestUnrolledLinkedList(unittest.TestCase):
    """Behavior and block-invariant tests for UnrolledLinkedList."""

    def assert_unrolled_integrity(
        self,
        unrolled: UnrolledLinkedList,
        expected: list,
    ) -> None:
        """Assert visible values plus internal block links."""
        self.assertEqual(unrolled.to_list(), expected)
        self.assertEqual(list(unrolled), expected)
        self.assertEqual(list(reversed(unrolled)), list(reversed(expected)))
        self.assertEqual(len(unrolled), len(expected))

        blocks = unrolled.to_blocks()
        if not expected:
            self.assertIsNone(unrolled.head)
            self.assertIsNone(unrolled.tail)
            self.assertEqual(blocks, [])
            return

        self.assertIsNotNone(unrolled.head)
        self.assertIsNotNone(unrolled.tail)
        self.assertEqual(expected[0], unrolled.peek_front())
        self.assertEqual(expected[-1], unrolled.peek_back())
        self.assertEqual(
            [item for block in blocks for item in block],
            expected,
        )

        forward_blocks = []
        current = unrolled.head
        previous = None
        visited: set[int] = set()
        while current is not None:
            self.assertNotIn(id(current), visited)
            visited.add(id(current))
            self.assertIs(current.prev, previous)
            self.assertGreater(len(current.values), 0)
            self.assertLessEqual(len(current.values), unrolled.node_capacity)
            forward_blocks.append(list(current.values))
            previous = current
            current = current.next

        self.assertIs(previous, unrolled.tail)
        self.assertEqual(forward_blocks, blocks)
        self.assertIsNone(unrolled.head.prev)
        self.assertIsNone(unrolled.tail.next)

        reverse_blocks = []
        current = unrolled.tail
        next_node = None
        while current is not None:
            self.assertIs(current.next, next_node)
            reverse_blocks.append(list(current.values))
            next_node = current
            current = current.prev
        self.assertEqual(reverse_blocks, list(reversed(blocks)))

    def test_empty_state_and_configuration_validation(self) -> None:
        unrolled = UnrolledLinkedList(node_capacity=3)

        self.assertFalse(unrolled)
        self.assertTrue(unrolled.is_empty())
        self.assertEqual(
            repr(unrolled),
            "UnrolledLinkedList([], node_capacity=3)",
        )
        self.assertEqual(str(unrolled), "[]")
        self.assert_unrolled_integrity(unrolled, [])

        with self.assertRaises(IndexError):
            unrolled.peek_front()
        with self.assertRaises(IndexError):
            unrolled.peek_back()
        with self.assertRaises(IndexError):
            unrolled.pop()
        with self.assertRaises(IndexError):
            unrolled.pop_front()
        with self.assertRaises(IndexError):
            _ = unrolled[0]
        with self.assertRaises(TypeError):
            UnrolledLinkedList(node_capacity=2.5)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            UnrolledLinkedList(node_capacity=True)
        with self.assertRaises(ValueError):
            UnrolledLinkedList(node_capacity=1)

    def test_constructor_append_prepend_insert_and_block_splitting(
        self,
    ) -> None:
        unrolled = UnrolledLinkedList(range(8), node_capacity=3)

        self.assert_unrolled_integrity(unrolled, list(range(8)))
        self.assertGreater(len(unrolled.to_blocks()), 1)

        unrolled.prepend(-1)
        unrolled.append(8)
        unrolled.insert(5, 99)
        unrolled.insert(len(unrolled), 100)
        unrolled.insert(0, -2)

        self.assert_unrolled_integrity(
            unrolled,
            [-2, -1, 0, 1, 2, 3, 99, 4, 5, 6, 7, 8, 100],
        )

        with self.assertRaises(IndexError):
            unrolled.insert(-99, 0)
        with self.assertRaises(IndexError):
            unrolled.insert(len(unrolled) + 1, 0)

    def test_indexing_slicing_assignment_and_safe_get(self) -> None:
        unrolled = UnrolledLinkedList([0, 1, 2, 3, 4], node_capacity=2)

        self.assertEqual(unrolled[0], 0)
        self.assertEqual(unrolled[-1], 4)
        self.assertEqual(unrolled.get(2), 2)
        self.assertEqual(unrolled.get(99, "missing"), "missing")
        self.assertEqual(unrolled.get(-99, "missing"), "missing")

        sliced = unrolled[1:5:2]
        reversed_slice = unrolled[::-1]
        self.assertIsInstance(sliced, UnrolledLinkedList)
        self.assertEqual(sliced.node_capacity, 2)
        self.assert_unrolled_integrity(sliced, [1, 3])
        self.assert_unrolled_integrity(reversed_slice, [4, 3, 2, 1, 0])

        unrolled[2] = 20
        unrolled[-1] = 40

        self.assert_unrolled_integrity(unrolled, [0, 1, 20, 3, 40])
        with self.assertRaises(IndexError):
            _ = unrolled[99]
        with self.assertRaises(TypeError):
            _ = unrolled["bad"]  # type: ignore[index]

    def test_remove_pop_remove_at_and_rebalance(self) -> None:
        unrolled = UnrolledLinkedList(range(12), node_capacity=4)
        old_head = unrolled.head
        old_tail = unrolled.tail

        self.assertEqual(unrolled.pop_front(), 0)
        self.assertEqual(unrolled.pop(), 11)
        self.assertEqual(unrolled.remove_at(4), 5)
        self.assertTrue(unrolled.remove(7))
        self.assertFalse(unrolled.remove(99))

        self.assert_unrolled_integrity(
            unrolled,
            [1, 2, 3, 4, 6, 8, 9, 10],
        )
        self.assertIsNone(old_head.prev)
        self.assertIsNone(old_tail.next)

        while unrolled:
            unrolled.pop_front()
        self.assert_unrolled_integrity(unrolled, [])

    def test_remove_all_replace_duplicates_and_unhashable_values(self) -> None:
        unrolled = UnrolledLinkedList(
            [1, 2, 2, 3, 2, [1], [1], [2]],
            node_capacity=3,
        )

        self.assertEqual(unrolled.remove_all(2), 3)
        self.assert_unrolled_integrity(unrolled, [1, 3, [1], [1], [2]])

        self.assertEqual(unrolled.replace([1], [9], count=1), 1)
        self.assertEqual(unrolled.replace([1], [8]), 1)
        self.assertEqual(unrolled.replace([9], [9], count=0), 0)
        self.assert_unrolled_integrity(unrolled, [1, 3, [9], [8], [2]])

        unrolled.extend([[9], [2], 1])
        unrolled.remove_duplicates()

        self.assert_unrolled_integrity(unrolled, [1, 3, [9], [8], [2]])

    def test_copy_deep_copy_map_filter_reduce_and_equality(self) -> None:
        original_values = [[1], [2], [3]]
        unrolled = UnrolledLinkedList(original_values, node_capacity=2)

        shallow = unrolled.copy()
        deep = unrolled.deep_copy()
        mapped = unrolled.map(lambda value: value + [0])
        filtered = unrolled.filter(lambda value: value[0] != 2)
        reduced = unrolled.reduce(lambda left, right: left + right, [])

        self.assertEqual(unrolled, shallow)
        self.assertNotEqual(unrolled, [original_values])
        self.assert_unrolled_integrity(mapped, [[1, 0], [2, 0], [3, 0]])
        self.assert_unrolled_integrity(filtered, [[1], [3]])
        self.assertEqual(reduced, [1, 2, 3])

        shallow[0].append(99)
        self.assertEqual(unrolled[0], [1, 99])
        self.assertEqual(deep[0], [1])

    def test_reverse_rotate_sort_and_atomic_sort_errors(self) -> None:
        unrolled = UnrolledLinkedList([3, 1, 4, 2], node_capacity=3)

        unrolled.reverse()
        self.assert_unrolled_integrity(unrolled, [2, 4, 1, 3])

        unrolled.rotate(2)
        self.assert_unrolled_integrity(unrolled, [1, 3, 2, 4])

        unrolled.rotate(-1)
        self.assert_unrolled_integrity(unrolled, [3, 2, 4, 1])

        unrolled.sort()
        self.assert_unrolled_integrity(unrolled, [1, 2, 3, 4])

        unrolled.sort(reverse=True)
        self.assert_unrolled_integrity(unrolled, [4, 3, 2, 1])

        unrolled.sort(key=lambda value: value % 3)
        self.assert_unrolled_integrity(unrolled, [3, 4, 1, 2])

        mixed = UnrolledLinkedList([1, "bad", 2], node_capacity=2)
        with self.assertRaises(TypeError):
            mixed.sort()
        self.assert_unrolled_integrity(mixed, [1, "bad", 2])

    def test_extend_merge_and_self_iterator_are_bounded(self) -> None:
        unrolled = UnrolledLinkedList([1, 2, 3], node_capacity=3)

        unrolled.extend(unrolled)
        self.assert_unrolled_integrity(unrolled, [1, 2, 3, 1, 2, 3])

        unrolled.extend(iter(unrolled))
        self.assert_unrolled_integrity(
            unrolled,
            [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
        )

        unrolled.merge([4, 5])
        self.assert_unrolled_integrity(
            unrolled,
            [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 5],
        )

    def test_clear_detaches_blocks(self) -> None:
        unrolled = UnrolledLinkedList(range(7), node_capacity=3)
        old_head = unrolled.head
        old_tail = unrolled.tail

        unrolled.clear()

        self.assert_unrolled_integrity(unrolled, [])
        self.assertEqual(old_head.values, [])
        self.assertIsNone(old_head.next)
        self.assertIsNone(old_head.prev)
        self.assertEqual(old_tail.values, [])
        self.assertIsNone(old_tail.next)
        self.assertIsNone(old_tail.prev)

    def test_randomized_operations_match_python_list_behavior(self) -> None:
        for seed in range(40):
            source = random.Random(seed)
            unrolled = UnrolledLinkedList(
                node_capacity=source.randint(2, 6),
            )
            expected: list[int] = []

            for _ in range(200):
                operation = source.choice(
                    [
                        "append",
                        "prepend",
                        "insert",
                        "pop",
                        "pop_front",
                        "remove",
                        "remove_at",
                        "replace",
                        "reverse",
                        "rotate",
                    ],
                )
                value = source.randint(-8, 8)

                if operation == "append":
                    unrolled.append(value)
                    expected.append(value)
                elif operation == "prepend":
                    unrolled.prepend(value)
                    expected.insert(0, value)
                elif operation == "insert":
                    index = source.randint(-len(expected), len(expected))
                    unrolled.insert(index, value)
                    if index < 0:
                        index += len(expected)
                    expected.insert(index, value)
                elif operation == "pop":
                    if expected:
                        self.assertEqual(unrolled.pop(), expected.pop())
                    else:
                        with self.assertRaises(IndexError):
                            unrolled.pop()
                elif operation == "pop_front":
                    if expected:
                        self.assertEqual(unrolled.pop_front(), expected.pop(0))
                    else:
                        with self.assertRaises(IndexError):
                            unrolled.pop_front()
                elif operation == "remove":
                    changed = unrolled.remove(value)
                    if value in expected:
                        expected.remove(value)
                        self.assertTrue(changed)
                    else:
                        self.assertFalse(changed)
                elif operation == "remove_at":
                    if expected:
                        index = source.randrange(-len(expected), len(expected))
                        self.assertEqual(
                            unrolled.remove_at(index),
                            expected.pop(index),
                        )
                    else:
                        with self.assertRaises(IndexError):
                            unrolled.remove_at(0)
                elif operation == "replace":
                    count = source.choice([None, 0, 1, 2])
                    replacement = source.randint(-8, 8)
                    replaced = unrolled.replace(value, replacement, count)
                    expected_replaced = 0
                    limit = float("inf") if count is None else count
                    for index, item in enumerate(expected):
                        if item == value and expected_replaced < limit:
                            expected[index] = replacement
                            expected_replaced += 1
                    self.assertEqual(replaced, expected_replaced)
                elif operation == "reverse":
                    unrolled.reverse()
                    expected.reverse()
                elif operation == "rotate":
                    steps = source.randint(-20, 20)
                    unrolled.rotate(steps)
                    if expected:
                        steps %= len(expected)
                        expected[:] = expected[-steps:] + expected[:-steps]

                self.assert_unrolled_integrity(unrolled, expected)


if __name__ == "__main__":
    unittest.main()
