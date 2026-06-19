"""Tests for the multilevel linked-list container."""

import random
import unittest

from linked_list import MultilevelLinkedList


class TestMultilevelLinkedList(unittest.TestCase):
    """Behavior, hierarchy, and flattening tests."""

    def assert_multilevel_integrity(
        self,
        multilevel: MultilevelLinkedList,
        expected_flat: list,
        expected_nested: list | None = None,
        expected_top: list | None = None,
    ) -> None:
        """Assert traversal output plus top-level links."""
        self.assertEqual(multilevel.to_list(), expected_flat)
        self.assertEqual(list(multilevel), expected_flat)
        self.assertEqual(
            list(reversed(multilevel)),
            list(reversed(expected_flat)),
        )
        self.assertEqual(len(multilevel), len(expected_flat))

        if expected_nested is not None:
            self.assertEqual(multilevel.to_nested_list(), expected_nested)
        if expected_top is not None:
            self.assertEqual(multilevel.to_top_level_list(), expected_top)
            self.assertEqual(multilevel.top_level_length(), len(expected_top))

        if not expected_flat:
            self.assertIsNone(multilevel.head)
            self.assertIsNone(multilevel.tail)
            return

        self.assertIsNotNone(multilevel.head)
        self.assertIsNotNone(multilevel.tail)
        self.assertEqual(multilevel.peek_front(), expected_flat[0])
        self.assertEqual(multilevel.peek_back(), expected_flat[-1])

        visited: set[int] = set()
        for node in multilevel._iter_nodes_depth_first():
            self.assertNotIn(id(node), visited)
            visited.add(id(node))
        self.assertEqual(len(visited), len(expected_flat))

        top_nodes = []
        current = multilevel.head
        while current is not None:
            top_nodes.append(current)
            current = current.next
        self.assertIs(multilevel.tail, top_nodes[-1])

    def test_empty_state(self) -> None:
        multilevel = MultilevelLinkedList()

        self.assertFalse(multilevel)
        self.assertTrue(multilevel.is_empty())
        self.assertEqual(str(multilevel), "[]")
        self.assertEqual(repr(multilevel), "MultilevelLinkedList([])")
        self.assertEqual(multilevel.get(0, "missing"), "missing")
        self.assert_multilevel_integrity(multilevel, [])

        with self.assertRaises(IndexError):
            multilevel.peek_front()
        with self.assertRaises(IndexError):
            multilevel.peek_back()
        with self.assertRaises(IndexError):
            multilevel.pop()
        with self.assertRaises(IndexError):
            multilevel.pop_front()
        with self.assertRaises(IndexError):
            _ = multilevel[0]
        with self.assertRaises(ValueError):
            list(multilevel.iter_flat("sideways"))

    def test_from_nested_traversal_and_paths(self) -> None:
        nested = [1, (2, [3, (4, [5]), 6]), 7]
        multilevel = MultilevelLinkedList.from_nested(nested)

        self.assert_multilevel_integrity(
            multilevel,
            [1, 2, 3, 4, 5, 6, 7],
            [1, (2, [3, (4, [5]), 6]), 7],
            [1, 2, 7],
        )
        self.assertEqual(
            multilevel.to_list("breadth_first"),
            [1, 2, 7, 3, 4, 6, 5],
        )
        self.assertIn(5, multilevel)
        self.assertEqual(multilevel.index(4), 3)
        self.assertEqual(multilevel.find(99), None)
        self.assertEqual(multilevel.path_to(5), (1, 1, 0))
        self.assertEqual(multilevel.path_to(7), (2,))
        self.assertIsNone(multilevel.path_to(99))

    def test_child_operations_and_detach_children(self) -> None:
        multilevel = MultilevelLinkedList([1, 2])
        parent = multilevel.find_node(2)
        external = MultilevelLinkedList(["x"]).head

        multilevel.append_child(parent, 3)
        multilevel.prepend_child(2, 4)
        multilevel.extend_child(parent, [5, 6])

        self.assertEqual(multilevel.child_values(parent), [4, 3, 5, 6])
        self.assert_multilevel_integrity(
            multilevel,
            [1, 2, 4, 3, 5, 6],
            [1, (2, [4, 3, 5, 6])],
            [1, 2],
        )

        with self.assertRaises(ValueError):
            multilevel.append_child(external, 99)
        with self.assertRaises(ValueError):
            multilevel.child_values("missing")

        detached = multilevel.detach_children(2)

        self.assert_multilevel_integrity(multilevel, [1, 2], [1, 2], [1, 2])
        self.assert_multilevel_integrity(
            detached,
            [4, 3, 5, 6],
            [4, 3, 5, 6],
            [4, 3, 5, 6],
        )
        self.assertEqual(multilevel.detach_children(2).to_list(), [])

    def test_insert_assignment_slicing_and_merge(self) -> None:
        multilevel = MultilevelLinkedList.from_nested([1, (2, [3, 4]), 5])

        multilevel.insert(2, 99)
        multilevel.insert(0, -1)
        multilevel.insert(len(multilevel), 6)
        multilevel[-2] = 50
        multilevel.merge([7, 8])

        self.assert_multilevel_integrity(
            multilevel,
            [-1, 1, 2, 99, 3, 4, 50, 6, 7, 8],
            [-1, 1, (2, [99, 3, 4]), 50, 6, 7, 8],
            [-1, 1, 2, 50, 6, 7, 8],
        )

        sliced = multilevel[2:7:2]
        self.assertIsInstance(sliced, MultilevelLinkedList)
        self.assert_multilevel_integrity(sliced, [2, 3, 50], [2, 3, 50])

        with self.assertRaises(IndexError):
            multilevel.insert(-99, 0)
        with self.assertRaises(IndexError):
            multilevel.insert(len(multilevel) + 1, 0)
        with self.assertRaises(TypeError):
            _ = multilevel["bad"]  # type: ignore[index]

    def test_remove_subtree_and_promote_children(self) -> None:
        subtree_removed = MultilevelLinkedList.from_nested(
            [1, (2, [3, (4, [5])]), 6],
        )
        promoted = MultilevelLinkedList.from_nested(
            [1, (2, [3, (4, [5])]), 6],
        )

        self.assertTrue(subtree_removed.remove(2))
        self.assert_multilevel_integrity(
            subtree_removed,
            [1, 6],
            [1, 6],
            [1, 6],
        )

        self.assertTrue(promoted.remove(2, promote_children=True))
        self.assert_multilevel_integrity(
            promoted,
            [1, 3, 4, 5, 6],
            [1, 3, (4, [5]), 6],
            [1, 3, 4, 6],
        )
        self.assertFalse(promoted.remove(99))

    def test_remove_at_pop_pop_front_and_remove_all(self) -> None:
        multilevel = MultilevelLinkedList.from_nested(
            [(1, [2, 3]), 4, (2, [5])],
        )

        self.assertEqual(multilevel.pop_front(), 1)
        self.assert_multilevel_integrity(
            multilevel,
            [2, 3, 4, 2, 5],
            [2, 3, 4, (2, [5])],
            [2, 3, 4, 2],
        )

        self.assertEqual(multilevel.remove_at(3, promote_children=True), 2)
        self.assert_multilevel_integrity(
            multilevel,
            [2, 3, 4, 5],
            [2, 3, 4, 5],
            [2, 3, 4, 5],
        )

        self.assertEqual(multilevel.remove_all(2), 1)
        self.assertEqual(multilevel.pop(), 5)
        self.assert_multilevel_integrity(multilevel, [3, 4], [3, 4])

    def test_flatten_depth_first_and_breadth_first(self) -> None:
        depth = MultilevelLinkedList.from_nested([1, (2, [3, (4, [5])]), 6])
        breadth = depth.copy()
        original_child = depth.find_node(3)

        flat_copy = depth.flattened("breadth_first")
        self.assert_multilevel_integrity(
            flat_copy,
            [1, 2, 6, 3, 4, 5],
            [1, 2, 6, 3, 4, 5],
        )
        self.assert_multilevel_integrity(
            depth,
            [1, 2, 3, 4, 5, 6],
            [1, (2, [3, (4, [5])]), 6],
        )

        depth.flatten()
        self.assert_multilevel_integrity(
            depth,
            [1, 2, 3, 4, 5, 6],
            [1, 2, 3, 4, 5, 6],
            [1, 2, 3, 4, 5, 6],
        )
        self.assertIs(depth.find_node(3), original_child)
        for node in depth._iter_nodes_depth_first():
            self.assertIsNone(node.child)

        breadth.flatten("breadth_first")
        self.assert_multilevel_integrity(
            breadth,
            [1, 2, 6, 3, 4, 5],
            [1, 2, 6, 3, 4, 5],
            [1, 2, 6, 3, 4, 5],
        )

    def test_reverse_sort_rotate_and_duplicate_removal(self) -> None:
        multilevel = MultilevelLinkedList.from_nested([1, (2, [3, 4]), 5])

        multilevel.reverse()
        self.assert_multilevel_integrity(
            multilevel,
            [5, 2, 4, 3, 1],
            [5, (2, [4, 3]), 1],
            [5, 2, 1],
        )

        multilevel.sort(reverse=True)
        self.assert_multilevel_integrity(
            multilevel,
            [5, 4, 3, 2, 1],
            [5, 4, 3, 2, 1],
        )

        multilevel.rotate(-2)
        self.assert_multilevel_integrity(
            multilevel,
            [3, 2, 1, 5, 4],
            [3, 2, 1, 5, 4],
        )

        multilevel.extend([[3], [3], 2, [4], [4]])
        multilevel.remove_duplicates()
        self.assert_multilevel_integrity(
            multilevel,
            [3, 2, 1, 5, 4, [3], [4]],
            [3, 2, 1, 5, 4, [3], [4]],
        )

        mixed = MultilevelLinkedList.from_nested([1, ("bad", [2]), 3])
        original = mixed.to_nested_list()
        with self.assertRaises(TypeError):
            mixed.sort()
        self.assertEqual(mixed.to_nested_list(), original)

    def test_copy_deep_copy_map_filter_reduce_and_equality(self) -> None:
        multilevel = MultilevelLinkedList.from_nested(
            [([1], [([2], [])]), [3]],
        )

        shallow = multilevel.copy()
        deep = multilevel.deep_copy()

        self.assertEqual(multilevel, shallow)
        self.assertNotEqual(multilevel, MultilevelLinkedList([[1], [2], [3]]))

        shallow.head.data.append(99)
        self.assertEqual(multilevel.head.data, [1, 99])
        self.assertEqual(deep.head.data, [1])

        numbers = MultilevelLinkedList.from_nested([1, (2, [3]), 4])
        mapped = numbers.map(lambda value: value * 10)
        filtered = numbers.filter(lambda value: value % 2 == 0)
        reduced = numbers.reduce(lambda left, right: left + right, 0)

        self.assert_multilevel_integrity(
            mapped,
            [10, 20, 30, 40],
            [10, (20, [30]), 40],
        )
        self.assert_multilevel_integrity(filtered, [2, 4], [2, 4])
        self.assertEqual(reduced, 10)

    def test_clear_detaches_every_node(self) -> None:
        multilevel = MultilevelLinkedList.from_nested([1, (2, [3]), 4])
        old_head = multilevel.head
        child = multilevel.find_node(3)

        multilevel.clear()

        self.assert_multilevel_integrity(multilevel, [])
        self.assertIsNone(old_head.next)
        self.assertIsNone(old_head.child)
        self.assertIsNone(child.next)
        self.assertIsNone(child.child)

    def test_randomized_flat_operations_match_python_list_behavior(
        self,
    ) -> None:
        for seed in range(40):
            source = random.Random(seed)
            multilevel = MultilevelLinkedList()
            expected: list[int] = []

            for _ in range(180):
                operation = source.choice(
                    [
                        "append",
                        "prepend",
                        "insert",
                        "pop",
                        "pop_front",
                        "remove_at",
                        "replace",
                        "reverse",
                        "rotate",
                    ],
                )
                value = source.randint(-8, 8)

                if operation == "append":
                    multilevel.append(value)
                    expected.append(value)
                elif operation == "prepend":
                    multilevel.prepend(value)
                    expected.insert(0, value)
                elif operation == "insert":
                    index = source.randint(-len(expected), len(expected))
                    multilevel.insert(index, value)
                    if index < 0:
                        index += len(expected)
                    expected.insert(index, value)
                elif operation == "pop":
                    if expected:
                        self.assertEqual(multilevel.pop(), expected.pop())
                    else:
                        with self.assertRaises(IndexError):
                            multilevel.pop()
                elif operation == "pop_front":
                    if expected:
                        self.assertEqual(
                            multilevel.pop_front(),
                            expected.pop(0),
                        )
                    else:
                        with self.assertRaises(IndexError):
                            multilevel.pop_front()
                elif operation == "remove_at":
                    if expected:
                        index = source.randrange(-len(expected), len(expected))
                        self.assertEqual(
                            multilevel.remove_at(index),
                            expected.pop(index),
                        )
                    else:
                        with self.assertRaises(IndexError):
                            multilevel.remove_at(0)
                elif operation == "replace":
                    count = source.choice([None, 0, 1, 2])
                    replacement = source.randint(-8, 8)
                    replaced = multilevel.replace(value, replacement, count)
                    expected_replaced = 0
                    limit = float("inf") if count is None else count
                    for index, item in enumerate(expected):
                        if item == value and expected_replaced < limit:
                            expected[index] = replacement
                            expected_replaced += 1
                    self.assertEqual(replaced, expected_replaced)
                elif operation == "reverse":
                    multilevel.reverse()
                    expected.reverse()
                elif operation == "rotate":
                    steps = source.randint(-20, 20)
                    multilevel.rotate(steps)
                    if expected:
                        steps %= len(expected)
                        expected[:] = expected[-steps:] + expected[:-steps]

                self.assert_multilevel_integrity(
                    multilevel,
                    expected,
                    expected,
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
