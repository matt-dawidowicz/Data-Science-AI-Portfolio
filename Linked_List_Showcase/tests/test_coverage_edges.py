"""Targeted edge-case tests for full branch and line coverage.

Most tests in this file exercise public behavior. A few intentionally corrupt
private state to verify defensive guards that should never trigger through the
normal API but still exist to make invariant failures explicit.
"""

import unittest
from typing import Any
from unittest.mock import patch

from linked_list import (
    LinkedDeque,
    LinkedList,
    MultilevelLinkedList,
    PositionalLinkedList,
    SelfOrganizingLinkedList,
    SortedLinkedList,
    SparseMatrixLinkedList,
    UnrolledLinkedList,
)
from linked_list.multilevel_list import _MultilevelNode
from linked_list.nodes import (
    DoublyCircularLinkedNode,
    DoublyLinkedNode,
    SinglyLinkedNode,
)
from linked_list.nodes.base_node import BaseNode
from linked_list.self_organizing_list import _SelfOrganizingNode
from linked_list.sparse_matrix import _SparseMatrixNode
from linked_list.unrolled_list import _UnrolledNode


class TestCoreLinkedListCoverageEdges(unittest.TestCase):
    """Exercise linked-list guard rails and less common variants."""

    def test_invalid_list_type_and_node_factory_guards(self) -> None:
        with self.assertRaises(ValueError):
            LinkedList("sideways")

        linked_list = LinkedList("singly")
        linked_list._is_circular = True
        node = linked_list._create_node("value")
        self.assertEqual(node.data, "value")

        linked_list._list_type = "sideways"
        linked_list._is_circular = False
        with self.assertRaises(ValueError):
            linked_list._create_node("value")

    def test_index_assignment_and_equality_edge_cases(self) -> None:
        linked_list = LinkedList("singly")
        for value in [1, 2, 3]:
            linked_list.append(value)

        linked_list[-1] = 30
        self.assertEqual(linked_list.to_list(), [1, 2, 30])
        self.assertEqual(linked_list.index(30, 0, 3), 2)
        self.assertEqual(linked_list.find(30, 0, 2), None)
        self.assertNotEqual(linked_list, [1, 2, 30])
        self.assertNotEqual(linked_list, LinkedList.from_list([1, 2]))

        with self.assertRaises(TypeError):
            _ = linked_list["bad"]  # type: ignore[index]
        with self.assertRaises(IndexError):
            linked_list[-99] = 0
        with self.assertRaises(IndexError):
            linked_list.nth_from_end(0)
        with self.assertRaises(IndexError):
            linked_list.nth_from_end(99)

    def test_reverse_iteration_and_empty_circular_paths(self) -> None:
        singly = LinkedList("singly")
        with self.assertRaises(NotImplementedError):
            list(reversed(singly))

        empty_circular = LinkedList("doubly_circular")
        self.assertEqual(list(reversed(empty_circular)), [])

        circular = LinkedList("doubly_circular")
        for value in [1, 2, 3]:
            circular.append(value)

        self.assertEqual(list(reversed(circular)), [3, 2, 1])

    def test_mutation_edge_cases_and_circular_singletons(self) -> None:
        for list_type in ("singly_circular", "doubly_circular"):
            linked_list = LinkedList(list_type)
            linked_list.prepend("first")
            self.assertEqual(linked_list.to_list(), ["first"])
            self.assertIs(linked_list.tail.next, linked_list.head)
            if list_type == "doubly_circular":
                self.assertIs(linked_list.head.prev, linked_list.tail)
            linked_list.prepend("zero")
            self.assertEqual(linked_list.to_list(), ["zero", "first"])
            self.assertIs(linked_list.tail.next, linked_list.head)
            if list_type == "doubly_circular":
                self.assertIs(linked_list.head.prev, linked_list.tail)

            sorted_singleton = LinkedList(list_type)
            sorted_singleton.insert_sorted("first")
            self.assertEqual(sorted_singleton.to_list(), ["first"])
            self.assertIs(sorted_singleton.tail.next, sorted_singleton.head)
            if list_type == "doubly_circular":
                self.assertIs(
                    sorted_singleton.head.prev,
                    sorted_singleton.tail,
                )

        doubly = LinkedList("doubly")
        for value in [1, 3, 4]:
            doubly.append(value)
        doubly.insert(1, 2)
        self.assertEqual(doubly.to_list(), [1, 2, 3, 4])
        self.assertIs(doubly.head.next.prev, doubly.head)

        circular = LinkedList("doubly_circular")
        for value in [1, 3, 4]:
            circular.append(value)
        circular.insert(1, 2)
        self.assertEqual(circular.to_list(), [1, 2, 3, 4])
        self.assertIs(circular.tail.next, circular.head)
        self.assertIs(circular.head.prev, circular.tail)

        singleton = LinkedList("doubly")
        singleton.append("only")
        self.assertTrue(singleton.remove("only"))
        self.assertEqual(singleton.to_list(), [])

        for empty in (LinkedList("singly"), LinkedList("doubly")):
            empty.rotate(3)
            empty.reverse()
            self.assertEqual(empty.to_list(), [])

        with self.assertRaises(IndexError):
            LinkedList("singly").insert(1, "bad")

    def test_remove_at_extend_merge_and_sort_edge_cases(self) -> None:
        linked_list = LinkedList("singly")
        for value in [0, 1, 2, 3, 4]:
            linked_list.append(value)
        self.assertEqual(linked_list.remove_at(2), 2)
        self.assertEqual(linked_list.to_list(), [0, 1, 3, 4])

        self_extending = LinkedList("singly")
        for value in [1, 2]:
            self_extending.append(value)
        self_extending.extend(self_extending)
        self.assertEqual(self_extending.to_list(), [1, 2, 1, 2])

        with self.assertRaises(TypeError):
            LinkedList("singly").merge(LinkedList("doubly"))

        singleton = LinkedList("singly")
        singleton.append(1)
        singleton.sort()
        self.assertEqual(singleton.to_list(), [1])

        empty = LinkedList("singly")
        empty._relink_nodes([])
        self.assertEqual(empty.to_list(), [])

    def test_private_corruption_guards(self) -> None:
        truncated = LinkedList("doubly")
        truncated.append("head")
        truncated._size = 2
        truncated.insert(1, "tail")
        self.assertEqual(truncated.to_list(), ["head", "tail"])

        fake_sized = LinkedList("singly")
        fake_sized.append("only")
        fake_sized._size = 2
        self.assertEqual(fake_sized.pop(), "only")
        self.assertEqual(len(fake_sized), 1)
        self.assertEqual(fake_sized.head.data, "only")

        custom_sorted = LinkedList("singly")
        for value in [3, 1]:
            custom_sorted.append(value)
        custom_sorted.insert_sorted(
            2,
            compare=lambda left, right: left < right,
        )
        self.assertEqual(custom_sorted.to_list(), [2, 3, 1])

        left = LinkedList("singly")
        right = LinkedList("singly")
        left.append(3)
        right.append(1)
        left.merge(
            right,
            compare=lambda left_value, right_value: left_value < right_value,
        )
        self.assertEqual(left.to_list(), [1, 3])

    def test_defensive_remove_paths_for_broken_internal_state(self) -> None:
        class UnequalToItself:
            def __init__(self, data: Any) -> None:
                self.data = data
                self.next: Any | None = None

            def __eq__(self, other: object) -> bool:
                return False

        broken = LinkedList("singly")
        broken.head = UnequalToItself("target")
        broken.tail = object()
        broken._size = 2

        self.assertTrue(broken.remove("target"))

    def test_duplicate_at_head_defensive_cleanup_path(self) -> None:
        class AlwaysContainsSet:
            def __contains__(self, item: object) -> bool:
                return True

            def add(self, item: object) -> None:
                return None

        for list_type in ("singly", "doubly"):
            linked_list = LinkedList(list_type)
            linked_list.append("duplicate")
            linked_list.append("survivor")

            with patch(
                "linked_list.list_functions.mutation._make_seen_set",
                AlwaysContainsSet,
            ):
                linked_list.remove_duplicates()

            self.assertEqual(linked_list.to_list(), [])
            self.assertEqual(len(linked_list), 0)

    def test_circular_sort_relinks_wraparound_neighbors(self) -> None:
        linked_list = LinkedList("doubly_circular")
        for value in [3, 1, 2]:
            linked_list.append(value)

        linked_list.sort()

        self.assertEqual(linked_list.to_list(), [1, 2, 3])
        self.assertIs(linked_list.head.prev, linked_list.tail)
        self.assertIs(linked_list.tail.next, linked_list.head)

    def test_clear_tolerates_node_without_next_attribute(self) -> None:
        class PrevOnly:
            def __init__(self) -> None:
                self.prev: Any | None = object()

        linked_list = LinkedList("singly")
        linked_list.head = PrevOnly()
        linked_list.tail = linked_list.head
        linked_list._size = 1

        linked_list.clear()

        self.assertIsNone(linked_list.head)
        self.assertIsNone(linked_list.tail)
        self.assertEqual(len(linked_list), 0)

    def test_deque_index_stops_at_stop_bound(self) -> None:
        deque = LinkedDeque([1, 2, 3, 4])
        with self.assertRaises(ValueError):
            deque.index(4, 0, 3)


class TestNodeCoverageEdges(unittest.TestCase):
    """Cover small node representations and constructor validation."""

    def test_base_and_private_node_reprs(self) -> None:
        self.assertEqual(repr(BaseNode("x")), "BaseNode('x')")
        self.assertEqual(
            repr(_MultilevelNode("x")),
            "_MultilevelNode('x')",
        )
        self.assertEqual(
            repr(_SelfOrganizingNode("x")),
            "_SelfOrganizingNode(data='x', access_count=0)",
        )
        self.assertEqual(
            repr(_SparseMatrixNode(1, 2, "x")),
            "_SparseMatrixNode(row=1, col=2, value='x')",
        )
        self.assertEqual(repr(_UnrolledNode([1, 2])), "_UnrolledNode([1, 2])")

    def test_node_link_validation_and_circular_repr(self) -> None:
        with self.assertRaises(TypeError):
            SinglyLinkedNode("x", DoublyLinkedNode("bad"))  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            DoublyLinkedNode("x", prev_node=SinglyLinkedNode("bad"))  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            DoublyLinkedNode("x", next_node=SinglyLinkedNode("bad"))  # type: ignore[arg-type]

        previous = DoublyCircularLinkedNode("previous")
        following = DoublyCircularLinkedNode("following")
        node = DoublyCircularLinkedNode(
            "middle",
            prev=previous,
            next_node=following,
        )

        self.assertEqual(
            repr(node),
            "DoublyCircularLinkedNode("
            "data='middle', prev='previous', next='following')",
        )


class TestSortedLinkedListCoverageEdges(unittest.TestCase):
    """Cover sorted-list validation and no-op paths."""

    def test_constructor_direct_insert_and_empty_extension(self) -> None:
        with self.assertRaises(TypeError):
            SortedLinkedList([3, 1], [2])  # type: ignore[arg-type]

        sorted_list = SortedLinkedList("singly")
        sorted_list.insert_sorted(2)
        sorted_list.insert(0, 1)
        sorted_list.insert(len(sorted_list), 3)
        sorted_list.extend([])

        self.assertEqual(sorted_list.to_list(), [1, 2, 3])

    def test_merge_and_singleton_duplicate_noops(self) -> None:
        sorted_list = SortedLinkedList([1])
        sorted_list.remove_duplicates()
        self.assertEqual(sorted_list.to_list(), [1])

        with self.assertRaises(TypeError):
            sorted_list.merge([2, 3])  # type: ignore[arg-type]

        duplicates_at_tail = SortedLinkedList([1, 2, 2])
        duplicates_at_tail.remove_duplicates()
        self.assertEqual(duplicates_at_tail.to_list(), [1, 2])


class TestPositionalLinkedListCoverageEdges(unittest.TestCase):
    """Cover positional-list no-op moves and private defensive paths."""

    def test_position_repr_equality_and_iterable_constructor(self) -> None:
        linked_list = PositionalLinkedList.from_iterable([1, 2])
        first = linked_list.first_position()
        self.assertIsNotNone(first)
        assert first is not None

        self.assertEqual(repr(first), "Position(1)")
        self.assertNotEqual(first, object())
        self.assertEqual(repr(linked_list.head), "_PositionNode(1)")
        self.assertNotEqual(linked_list, [1, 2])
        self.assertNotEqual(linked_list, PositionalLinkedList([1, 2, 3]))

        linked_list.delete(first)
        self.assertEqual(repr(first), "Position(<invalid>)")

    def test_middle_insertions_and_move_noops(self) -> None:
        linked_list = PositionalLinkedList([1, 2, 4])
        first = linked_list.position_at(0)
        second = linked_list.position_at(1)
        third = linked_list.add_after(second, 3)
        fourth = linked_list.position_at(3)

        self.assertEqual(linked_list.to_list(), [1, 2, 3, 4])

        linked_list.move_to_front(first)
        linked_list.move_to_back(fourth)
        linked_list.move_before(third, third)
        linked_list.move_before(second, third)
        linked_list.move_after(third, third)
        linked_list.move_after(third, second)

        self.assertEqual(linked_list.to_list(), [1, 2, 3, 4])

        linked_list.move_before(fourth, second)
        self.assertEqual(linked_list.to_list(), [1, 4, 2, 3])

        linked_list.move_after(first, second)
        self.assertEqual(linked_list.to_list(), [4, 2, 1, 3])

        with self.assertRaises(IndexError):
            linked_list.insert(99, 0)

    def test_hashable_duplicate_reduce_and_empty_relink(self) -> None:
        linked_list = PositionalLinkedList([1, 2, 1, 3])
        linked_list.remove_duplicates()
        self.assertEqual(linked_list.to_list(), [1, 2, 3])
        self.assertEqual(
            linked_list.reduce(lambda left, right: left + right),
            6,
        )

        empty = PositionalLinkedList()
        empty.sort()
        self.assertEqual(empty.to_list(), [])

    def test_merge_appends_iterable_values(self) -> None:
        linked_list = PositionalLinkedList([1])
        linked_list.merge([2, 3])
        self.assertEqual(linked_list.to_list(), [1, 2, 3])


class TestSelfOrganizingCoverageEdges(unittest.TestCase):
    """Cover adaptive-list no-op strategies and static edge cases."""

    def test_indexing_equality_factory_and_access_count_edges(self) -> None:
        linked_list = SelfOrganizingLinkedList.from_iterable(
            [1, 2, 3],
            strategy="none",
        )
        linked_list[1] = 20

        self.assertEqual(linked_list.to_list(), [1, 20, 3])
        self.assertNotEqual(linked_list, [1, 20, 3])
        self.assertNotEqual(
            linked_list,
            SelfOrganizingLinkedList([1, 20, 3], strategy="move_to_front"),
        )
        self.assertIsNone(linked_list.access_count("missing"))

        with self.assertRaises(TypeError):
            _ = linked_list["bad"]  # type: ignore[index]

    def test_copy_count_options_and_strategy_switch_noop(self) -> None:
        linked_list = SelfOrganizingLinkedList([1, 2], strategy="none")
        linked_list.find(2)

        copied = linked_list.copy(preserve_counts=False)
        deep = linked_list.deep_copy(preserve_counts=False)
        linked_list.set_strategy("none")

        self.assertEqual(copied.to_access_counts(), [(1, 0), (2, 0)])
        self.assertEqual(deep.to_access_counts(), [(1, 0), (2, 0)])
        self.assertEqual(linked_list.strategy, "none")

    def test_strategy_noops_clear_and_duplicate_hashable_paths(self) -> None:
        front = SelfOrganizingLinkedList([1, 2], strategy="move_to_front")
        self.assertEqual(front.find(1), 0)
        self.assertEqual(front.to_list(), [1, 2])

        transposed = SelfOrganizingLinkedList([1, 2], strategy="transpose")
        self.assertEqual(transposed.find(1), 0)
        self.assertEqual(transposed.to_list(), [1, 2])

        duplicates = SelfOrganizingLinkedList([1, 2, 1, 3], strategy="none")
        duplicates.remove_duplicates()
        self.assertEqual(duplicates.to_list(), [1, 2, 3])
        self.assertEqual(
            duplicates.reduce(lambda left, right: left + right),
            6,
        )
        duplicates.clear()
        self.assertEqual(duplicates.to_list(), [])
        duplicates.clear()
        self.assertEqual(duplicates.to_list(), [])

        empty = SelfOrganizingLinkedList(strategy="none")
        empty.sort()
        self.assertEqual(empty.to_list(), [])


class TestMultilevelCoverageEdges(unittest.TestCase):
    """Cover multilevel traversal, child insertion, and defensive guards."""

    def test_factory_equality_count_and_self_extension(self) -> None:
        linked_list = MultilevelLinkedList.from_iterable([1, 2])
        self.assertEqual(linked_list.to_list(), [1, 2])
        self.assertNotEqual(linked_list, [1, 2])
        self.assertEqual(linked_list.count(2), 1)

        linked_list.extend(linked_list)
        self.assertEqual(linked_list.to_top_level_list(), [1, 2, 1, 2])

    def test_child_tail_flatten_reduce_and_no_duplicate_noop(self) -> None:
        linked_list = MultilevelLinkedList(["root"])
        parent = linked_list.find_node("root")
        self.assertIsNotNone(parent)
        assert parent is not None

        linked_list.append_child(parent, "child-1")
        linked_list.append_child(parent, "child-2")
        linked_list.extend_child("child-1", ["grandchild"])

        self.assertEqual(
            linked_list.to_nested_list(),
            [("root", [("child-1", ["grandchild"]), "child-2"])],
        )

        no_duplicates = linked_list.copy()
        no_duplicates.remove_duplicates()
        self.assertEqual(no_duplicates.to_list(), linked_list.to_list())

        self.assertEqual(
            linked_list.reduce(lambda left, right: f"{left}/{right}"),
            "root/child-1/grandchild/child-2",
        )

        empty = MultilevelLinkedList()
        empty.flatten()
        self.assertEqual(empty.to_list(), [])

        with self.assertRaises(ValueError):
            linked_list.flatten("sideways")

    def test_child_removal_and_corrupted_reference_guard(self) -> None:
        linked_list = MultilevelLinkedList.from_nested(
            [("root", ["child-1", "child-2"]), "tail"],
        )
        self.assertEqual(linked_list.remove_at(1), "child-1")
        self.assertEqual(
            linked_list.to_nested_list(),
            [("root", ["child-2"]), "tail"],
        )

        linked_list._size += 1
        with self.assertRaises(RuntimeError):
            linked_list._reference_at(len(linked_list.to_list()))


class TestSparseMatrixCoverageEdges(unittest.TestCase):
    """Cover sparse-matrix type guards and defensive removal helpers."""

    def test_contains_and_equality_edge_cases(self) -> None:
        matrix = SparseMatrixLinkedList(2, 2, [(0, 0, 1)])

        self.assertNotIn("not-a-position", matrix)
        self.assertNotIn((0,), matrix)
        self.assertNotIn(("0", 0), matrix)
        self.assertNotIn((True, 0), matrix)
        self.assertNotIn((3, 0), matrix)
        self.assertNotEqual(matrix, {(0, 0): 1})

    def test_defensive_shape_and_missing_link_removal_guards(self) -> None:
        matrix = SparseMatrixLinkedList(2, 2, [(0, 0, 1)])

        with self.assertRaises(TypeError):
            matrix._validate_same_shape([[1]])  # type: ignore[arg-type]

        matrix._remove_from_row(0, 1)
        matrix._remove_from_column(1, 0)

        self.assertEqual(matrix.to_entries(), [(0, 0, 1)])


class TestUnrolledCoverageEdges(unittest.TestCase):
    """Cover unrolled-list edge branches and defensive guards."""

    def test_factory_contains_equality_index_count_and_reduce_edges(
        self,
    ) -> None:
        unrolled = UnrolledLinkedList.from_iterable([1, 2, 3], node_capacity=2)

        self.assertIn(2, unrolled)
        self.assertEqual(unrolled.count(2), 1)
        self.assertEqual(unrolled.index(2), 1)
        self.assertEqual(unrolled.index(3, 1, 3), 2)
        self.assertIsNone(unrolled.find("missing"))
        self.assertEqual(unrolled.reduce(lambda left, right: left + right), 6)
        self.assertNotEqual(unrolled, [1, 2, 3])
        self.assertNotEqual(unrolled, UnrolledLinkedList([1, 2]))

    def test_noop_remove_all_and_duplicate_removal_paths(self) -> None:
        unrolled = UnrolledLinkedList([1, 2, 3], node_capacity=3)

        self.assertEqual(unrolled.remove_all(99), 0)
        unrolled.remove_duplicates()
        self.assertEqual(unrolled.to_list(), [1, 2, 3])

    def test_previous_borrow_and_corrupted_locate_guards(self) -> None:
        unrolled = UnrolledLinkedList(node_capacity=4)
        left = _UnrolledNode([1, 2, 3, 4])
        right = _UnrolledNode([5])
        unrolled._append_node(left)
        unrolled._append_node(right)
        unrolled._size = 5

        unrolled._rebalance_after_remove(right)
        self.assertEqual(left.values, [1, 2, 3])
        self.assertEqual(right.values, [4, 5])

        broken_forward = UnrolledLinkedList(node_capacity=3)
        broken_forward._size = 3
        with self.assertRaises(RuntimeError):
            broken_forward._locate(0)

        broken_backward = UnrolledLinkedList(node_capacity=3)
        broken_backward._size = 3
        with self.assertRaises(RuntimeError):
            broken_backward._locate(2)

    def test_rebalance_noop_exit_for_detached_underfilled_block(self) -> None:
        unrolled = UnrolledLinkedList(node_capacity=4)
        unrolled.head = _UnrolledNode(["head"])
        unrolled.tail = _UnrolledNode(["tail"])
        detached = _UnrolledNode(["small"])

        unrolled._rebalance_after_remove(detached)

        self.assertEqual(detached.values, ["small"])


if __name__ == "__main__":
    unittest.main()
