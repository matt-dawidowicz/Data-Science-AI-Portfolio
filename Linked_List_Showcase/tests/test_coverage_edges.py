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
    SkipList,
    SortedLinkedList,
    SparseMatrixLinkedList,
    UnrolledLinkedList,
)
from linked_list.list_functions.base import BaseLinkedList
from linked_list.multilevel_list import _MultilevelNode
from linked_list.nodes import (
    DoublyCircularLinkedNode,
    DoublyLinkedNode,
    SinglyCircularLinkedNode,
    SinglyLinkedNode,
)
from linked_list.nodes.base_node import BaseNode
from linked_list.self_organizing_list import _SelfOrganizingNode
from linked_list.sparse_matrix import _SparseMatrixNode
from linked_list.unrolled_list import _UnrolledNode


class _IndexLike:
    """Small integer-protocol helper for public index API tests."""

    def __init__(self, value: int) -> None:
        self.value = value

    def __index__(self) -> int:
        return self.value


class _BadIndex:
    """Object that is neither an integer nor integer-like."""


class TestCoreLinkedListCoverageEdges(unittest.TestCase):
    """Exercise linked-list guard rails and less common variants."""

    def test_invalid_list_type_and_node_factory_guards(self) -> None:
        with self.assertRaises(ValueError):
            LinkedList("sideways")
        with self.assertRaises(TypeError):
            BaseLinkedList([1, 2, 3])  # type: ignore[arg-type]

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

        linear = LinkedList("doubly")
        for value in [1, 2, 3]:
            linear.append(value)

        self.assertEqual(list(reversed(linear)), [3, 2, 1])

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

        head_removal = LinkedList("doubly")
        head_removal.extend(["remove", "keep"])
        self.assertTrue(head_removal.remove("remove"))
        self.assertEqual(head_removal.to_list(), ["keep"])
        self.assertIsNone(head_removal.head.prev)

        all_head_matches = LinkedList("doubly")
        all_head_matches.extend(["remove", "remove", "keep"])
        self.assertEqual(all_head_matches.remove_all("remove"), 2)
        self.assertEqual(all_head_matches.to_list(), ["keep"])
        self.assertIsNone(all_head_matches.head.prev)

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
        with self.assertRaises(TypeError):
            LinkedList("singly").merge([1, 2])  # type: ignore[arg-type]

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

    def test_circular_remove_all_restores_links_when_equality_raises(
        self,
    ) -> None:
        class ExplodingEquality:
            def __eq__(self, other: object) -> bool:
                raise RuntimeError("comparison exploded")

        for list_type in ("singly_circular", "doubly_circular"):
            linked_list = LinkedList(list_type)
            linked_list.append(ExplodingEquality())
            linked_list.append("survivor")

            with self.assertRaises(RuntimeError):
                linked_list.remove_all("target")

            self.assertEqual(len(linked_list), 2)
            self.assertIs(linked_list.tail.next, linked_list.head)
            if list_type == "doubly_circular":
                self.assertIs(linked_list.head.prev, linked_list.tail)

    def test_circular_sort_relinks_wraparound_neighbors(self) -> None:
        linked_list = LinkedList("doubly_circular")
        for value in [3, 1, 2]:
            linked_list.append(value)

        linked_list.sort()

        self.assertEqual(linked_list.to_list(), [1, 2, 3])
        self.assertIs(linked_list.head.prev, linked_list.tail)
        self.assertIs(linked_list.tail.next, linked_list.head)

    def test_merge_comparison_error_leaves_both_lists_unchanged(
        self,
    ) -> None:
        def exploding_compare(left: Any, right: Any) -> bool:
            raise RuntimeError(f"cannot compare {left!r} and {right!r}")

        for list_type in (
            "singly",
            "doubly",
            "singly_circular",
            "doubly_circular",
        ):
            left = LinkedList(list_type, [1, 3])
            right = LinkedList(list_type, [2, 4])

            with self.assertRaises(RuntimeError):
                left.merge(right, exploding_compare)

            self.assertEqual(left.to_list(), [1, 3])
            self.assertEqual(right.to_list(), [2, 4])

            if "circular" in list_type:
                self.assertIs(left.tail.next, left.head)
                self.assertIs(right.tail.next, right.head)
                if list_type == "doubly_circular":
                    self.assertIs(left.head.prev, left.tail)
                    self.assertIs(right.head.prev, right.tail)
            else:
                self.assertIsNone(left.tail.next)
                self.assertIsNone(right.tail.next)
                if list_type == "doubly":
                    self.assertIsNone(left.head.prev)
                    self.assertIsNone(right.head.prev)

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

    def test_deque_insert_validates_index_before_empty_shortcut(self) -> None:
        deque = LinkedDeque()

        with self.assertRaises(TypeError):
            deque.insert("bad", "value")  # type: ignore[arg-type]

        self.assertEqual(deque.to_list(), [])

    def test_deque_insert_accepts_integer_like_index(self) -> None:
        class LeftSide:
            def __index__(self) -> int:
                return 0

        deque = LinkedDeque()
        deque.insert(LeftSide(), "value")  # type: ignore[arg-type]

        self.assertEqual(deque.to_list(), ["value"])

    def test_self_referential_values_have_safe_public_displays(self) -> None:
        containers: list[Any] = [
            LinkedList("singly"),
            LinkedList("doubly_circular"),
            SortedLinkedList(),
            UnrolledLinkedList(node_capacity=3),
            PositionalLinkedList(),
            SelfOrganizingLinkedList(),
            MultilevelLinkedList(),
            SkipList(),
        ]

        for container in containers:
            if isinstance(container, SkipList):
                container.add(container)
            else:
                container.append(container)
            self.assertIn("...", repr(container))
            self.assertIn("...", str(container))

        matrix = SparseMatrixLinkedList(1, 1)
        matrix[0, 0] = matrix
        self.assertIn("...", repr(matrix))

        nested = MultilevelLinkedList(["root"])
        nested.append_child("root", nested)
        self.assertIn("...", repr(nested))


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

    def test_self_referential_position_and_node_reprs_are_safe(self) -> None:
        linked_list = PositionalLinkedList()
        position = linked_list.add_last(None)
        linked_list.replace(position, position)

        self.assertEqual(repr(position), "Position(...)")

        node = linked_list.head
        self.assertIsNotNone(node)
        assert node is not None
        node.data = node
        self.assertEqual(repr(node), "_PositionNode(...)")

        base = BaseNode(None)
        base.data = base
        self.assertEqual(repr(base), "BaseNode(...)")

        adaptive = _SelfOrganizingNode(None)
        adaptive.data = adaptive
        self.assertEqual(
            repr(adaptive),
            "_SelfOrganizingNode(data=..., access_count=0)",
        )

        nested = _MultilevelNode(None)
        nested.data = nested
        self.assertEqual(repr(nested), "_MultilevelNode(...)")

        sparse = _SparseMatrixNode(0, 0, None)
        sparse.value = sparse
        self.assertEqual(
            repr(sparse),
            "_SparseMatrixNode(row=0, col=0, value=...)",
        )

        for node_class in (
            SinglyLinkedNode,
            DoublyLinkedNode,
            SinglyCircularLinkedNode,
        ):
            public_node = node_class(None)
            public_node.data = public_node
            self.assertIn("...", repr(public_node))

        circular = DoublyCircularLinkedNode(None)
        circular.data = circular
        self.assertEqual(
            repr(circular),
            "DoublyCircularLinkedNode(data=..., prev=self, next=self)",
        )
        circular.prev = None
        circular.next = None
        self.assertEqual(
            repr(circular),
            "DoublyCircularLinkedNode(data=..., prev=None, next=None)",
        )

    def test_node_link_validation_and_circular_repr(self) -> None:
        with self.assertRaises(TypeError):
            SinglyLinkedNode("x", DoublyLinkedNode("bad"))  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            DoublyLinkedNode("x", prev_node=SinglyLinkedNode("bad"))  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            DoublyLinkedNode("x", next_node=SinglyLinkedNode("bad"))  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            SinglyCircularLinkedNode("x", DoublyLinkedNode("bad"))  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            DoublyCircularLinkedNode("x", prev=SinglyLinkedNode("bad"))  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            DoublyCircularLinkedNode("x", next_node=SinglyLinkedNode("bad"))  # type: ignore[arg-type]

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
        with self.assertRaises(TypeError):
            SortedLinkedList(42)  # type: ignore[arg-type]

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

    def test_circular_remove_duplicates_restores_links_when_equality_raises(
        self,
    ) -> None:
        class ExplodingEquality:
            def __init__(self, value: int) -> None:
                self.value = value

            def __lt__(self, other: object) -> bool:
                if not isinstance(other, ExplodingEquality):
                    return NotImplemented
                return self.value < other.value

            def __eq__(self, other: object) -> bool:
                raise RuntimeError("comparison exploded")

        first = ExplodingEquality(1)
        second = ExplodingEquality(2)

        for list_type in ("singly_circular", "doubly_circular"):
            sorted_list = SortedLinkedList(list_type, [second, first])

            with self.assertRaises(RuntimeError):
                sorted_list.remove_duplicates()

            self.assertEqual(len(sorted_list), 2)
            self.assertIs(sorted_list.head.data, first)
            self.assertIs(sorted_list.tail.data, second)
            self.assertIs(sorted_list.tail.next, sorted_list.head)
            if list_type == "doubly_circular":
                self.assertIs(sorted_list.head.prev, sorted_list.tail)


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
        self.assertEqual(first, first)

        stale_list = PositionalLinkedList([1, 2])
        stale_first = stale_list.position_at(0)
        stale_second = stale_list.position_at(1)
        stale_list.delete(stale_first)
        stale_list.delete(stale_second)

        self.assertNotEqual(stale_first, stale_second)

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


class TestIndexProtocolCoverageEdges(unittest.TestCase):
    """Cover Python's integer protocol across public positional APIs."""

    def test_core_linked_list_integer_like_indices(self) -> None:
        linked_list = LinkedList(["a", "b", "c"])

        self.assertEqual(linked_list[_IndexLike(1)], "b")
        self.assertEqual(linked_list.get(_IndexLike(-1)), "c")
        self.assertEqual(linked_list.nth_from_end(_IndexLike(2)), "b")

        linked_list[_IndexLike(-1)] = "C"
        linked_list.insert(_IndexLike(1), "inserted")
        self.assertEqual(linked_list.remove_at(_IndexLike(0)), "a")
        self.assertEqual(linked_list.to_list(), ["inserted", "b", "C"])

    def test_specialized_sequence_integer_like_indices(self) -> None:
        containers: list[Any] = [
            UnrolledLinkedList(["a", "b", "c"], node_capacity=2),
            PositionalLinkedList(["a", "b", "c"]),
            SelfOrganizingLinkedList(["a", "b", "c"], strategy="none"),
        ]

        for container in containers:
            self.assertEqual(container[_IndexLike(1)], "b")
            self.assertEqual(container.get(_IndexLike(-1)), "c")
            container[_IndexLike(1)] = "B"
            container.insert(_IndexLike(1), "inserted")
            self.assertEqual(container.remove_at(_IndexLike(-1)), "c")
            self.assertEqual(container.to_list(), ["a", "inserted", "B"])

    def test_deque_integer_like_index_and_insert(self) -> None:
        deque = LinkedDeque(["a", "b", "c"])

        self.assertEqual(deque[_IndexLike(1)], "b")
        self.assertEqual(deque.get(_IndexLike(-1)), "c")
        deque.insert(_IndexLike(1), "inserted")

        self.assertEqual(deque.to_list(), ["a", "inserted", "b", "c"])

    def test_self_organizing_access_accepts_integer_like_index(self) -> None:
        linked_list = SelfOrganizingLinkedList(
            ["a", "b", "c"],
            strategy="none",
        )

        self.assertEqual(linked_list.access(_IndexLike(1)), "b")
        self.assertEqual(linked_list.access_count("b"), 1)
        self.assertEqual(linked_list.to_list(), ["a", "b", "c"])

    def test_positional_position_at_accepts_integer_like_index(self) -> None:
        linked_list = PositionalLinkedList(["a", "b", "c"])

        position = linked_list.position_at(_IndexLike(1))

        self.assertEqual(position.data, "b")

    def test_multilevel_integer_like_indices_are_depth_first(self) -> None:
        linked_list = MultilevelLinkedList.from_nested(
            [("root", ["child"]), "tail"],
        )

        self.assertEqual(linked_list[_IndexLike(1)], "child")
        linked_list[_IndexLike(1)] = "renamed"
        self.assertEqual(linked_list.remove_at(_IndexLike(1)), "renamed")
        linked_list.insert(_IndexLike(1), "inserted")

        self.assertEqual(linked_list.to_list(), ["root", "inserted", "tail"])

    def test_sorted_list_integer_like_indices_preserve_order(self) -> None:
        linked_list = SortedLinkedList([1, 3, 5])

        self.assertEqual(linked_list[_IndexLike(1)], 3)
        linked_list[_IndexLike(1)] = 4
        linked_list.insert(_IndexLike(1), 2)
        self.assertEqual(linked_list.remove_at(_IndexLike(-1)), 5)

        self.assertEqual(linked_list.to_list(), [1, 2, 4])

    def test_bad_indices_raise_without_mutating_containers(self) -> None:
        containers: list[Any] = [
            LinkedList(["a", "b"]),
            LinkedDeque(["a", "b"]),
            UnrolledLinkedList(["a", "b"]),
            PositionalLinkedList(["a", "b"]),
            SelfOrganizingLinkedList(["a", "b"], strategy="none"),
            MultilevelLinkedList(["a", "b"]),
            SortedLinkedList([1, 2]),
        ]

        for container in containers:
            before = container.to_list()
            with self.assertRaises(TypeError):
                _ = container[_BadIndex()]  # type: ignore[index]
            with self.assertRaises(TypeError):
                container.insert(_BadIndex(), "x")  # type: ignore[arg-type]
            if hasattr(container, "remove_at"):
                with self.assertRaises(TypeError):
                    container.remove_at(_BadIndex())  # type: ignore[arg-type]
            self.assertEqual(container.to_list(), before)

        linked_list = LinkedList(["a"])
        with self.assertRaises(TypeError):
            linked_list.nth_from_end(_BadIndex())  # type: ignore[arg-type]
        self.assertEqual(linked_list.to_list(), ["a"])


class TestIntegerLikeConfigurationCoverageEdges(unittest.TestCase):
    """Cover practical integer-like inputs for configuration APIs."""

    def test_unrolled_capacity_and_skip_list_level_accept_index_protocol(
        self,
    ) -> None:
        unrolled = UnrolledLinkedList(
            ["a", "b", "c"],
            node_capacity=_IndexLike(2),
        )
        self.assertEqual(unrolled.node_capacity, 2)
        self.assertEqual(unrolled.to_blocks(), [["a", "b"], ["c"]])

        from_factory = UnrolledLinkedList.from_iterable(
            ["a", "b"],
            node_capacity=_IndexLike(2),
        )
        self.assertEqual(from_factory.node_capacity, 2)

        skip_list = SkipList([3, 1, 2], max_level=_IndexLike(4), seed=1)
        self.assertEqual(skip_list.max_level, 4)
        self.assertEqual(skip_list.to_list(), [1, 2, 3])

    def test_sparse_matrix_dimensions_and_coordinates_accept_index_protocol(
        self,
    ) -> None:
        matrix = SparseMatrixLinkedList(
            _IndexLike(3),
            _IndexLike(3),
            [(_IndexLike(0), _IndexLike(1), 5)],
        )

        self.assertEqual(matrix.shape, (3, 3))
        self.assertEqual(matrix[_IndexLike(0), _IndexLike(1)], 5)
        self.assertIn((_IndexLike(0), _IndexLike(1)), matrix)

        matrix[_IndexLike(2), _IndexLike(2)] = 9
        self.assertEqual(matrix.get(_IndexLike(2), _IndexLike(2)), 9)
        self.assertEqual(matrix.row_items(_IndexLike(2)), [(2, 9)])
        self.assertEqual(matrix.column_items(_IndexLike(2)), [(2, 9)])
        self.assertEqual(matrix.row_sum(_IndexLike(2)), 9)
        self.assertEqual(matrix.column_sum(_IndexLike(2)), 9)
        self.assertEqual(matrix.pop(_IndexLike(2), _IndexLike(2)), 9)
        self.assertFalse(matrix.remove(_IndexLike(2), _IndexLike(2)))

        from_entries = SparseMatrixLinkedList.from_entries(
            _IndexLike(2),
            _IndexLike(2),
            [(_IndexLike(1), _IndexLike(1), 7)],
        )
        self.assertEqual(from_entries.to_entries(), [(1, 1, 7)])


class TestSearchBoundsProtocolCoverageEdges(unittest.TestCase):
    """Cover integer-like bounds for index/find search APIs."""

    def test_integer_like_search_bounds_match_python_sequences(self) -> None:
        containers: list[Any] = [
            LinkedList(["a", "b", "a", "c"]),
            LinkedDeque(["a", "b", "a", "c"]),
            UnrolledLinkedList(["a", "b", "a", "c"], node_capacity=2),
        ]

        for container in containers:
            self.assertEqual(
                container.index("a", _IndexLike(1), _IndexLike(4)),
                2,
            )
            self.assertEqual(
                container.find("a", _IndexLike(1), _IndexLike(4)),
                2,
            )
            self.assertIsNone(
                container.find("a", _IndexLike(1), _IndexLike(2)),
            )

    def test_bad_search_bounds_raise_type_error(self) -> None:
        containers: list[Any] = [
            LinkedList(["a"]),
            LinkedDeque(["a"]),
            UnrolledLinkedList(["a"]),
        ]

        for container in containers:
            with self.assertRaises(TypeError):
                container.index(
                    "a",
                    _BadIndex(),  # type: ignore[arg-type]
                )
            with self.assertRaises(TypeError):
                container.find(
                    "a",
                    _BadIndex(),  # type: ignore[arg-type]
                )


class TestReplacementCountProtocolCoverageEdges(unittest.TestCase):
    """Cover integer-protocol validation for count-limited replacement."""

    def test_integer_like_replace_counts_limit_replacements(self) -> None:
        linked_list = LinkedList(["x", "x", "z"])
        self.assertEqual(linked_list.replace("x", "y", _IndexLike(1)), 1)
        self.assertEqual(linked_list.to_list(), ["y", "x", "z"])

        deque = LinkedDeque(["x", "x", "z"])
        self.assertEqual(deque.replace("x", "y", _IndexLike(1)), 1)
        self.assertEqual(deque.to_list(), ["y", "x", "z"])

        sorted_list = SortedLinkedList([1, 1, 2])
        self.assertEqual(sorted_list.replace(1, 3, _IndexLike(1)), 1)
        self.assertEqual(sorted_list.to_list(), [1, 2, 3])

        unrolled = UnrolledLinkedList(["x", "x", "z"], node_capacity=2)
        self.assertEqual(unrolled.replace("x", "y", _IndexLike(1)), 1)
        self.assertEqual(unrolled.to_list(), ["y", "x", "z"])

        positional = PositionalLinkedList(["x", "x", "z"])
        self.assertEqual(
            positional.replace_value("x", "y", _IndexLike(1)),
            1,
        )
        self.assertEqual(positional.to_list(), ["y", "x", "z"])

        self_organizing = SelfOrganizingLinkedList(
            ["x", "x", "z"],
            strategy="none",
        )
        self.assertEqual(
            self_organizing.replace("x", "y", _IndexLike(1)),
            1,
        )
        self.assertEqual(self_organizing.to_list(), ["y", "x", "z"])

        multilevel = MultilevelLinkedList.from_nested(
            [("x", ["x"]), "z"],
        )
        self.assertEqual(multilevel.replace("x", "y", _IndexLike(1)), 1)
        self.assertEqual(multilevel.to_list(), ["y", "x", "z"])

    def test_float_replace_counts_raise_without_mutating(self) -> None:
        linked_list = LinkedList(["x", "x"])
        with self.assertRaises(TypeError):
            linked_list.replace("x", "y", 1.5)  # type: ignore[arg-type]
        self.assertEqual(linked_list.to_list(), ["x", "x"])

        deque = LinkedDeque(["x", "x"])
        with self.assertRaises(TypeError):
            deque.replace("x", "y", 1.5)  # type: ignore[arg-type]
        self.assertEqual(deque.to_list(), ["x", "x"])

        sorted_list = SortedLinkedList([1, 1])
        with self.assertRaises(TypeError):
            sorted_list.replace(1, 2, 1.5)  # type: ignore[arg-type]
        self.assertEqual(sorted_list.to_list(), [1, 1])

        unrolled = UnrolledLinkedList(["x", "x"])
        with self.assertRaises(TypeError):
            unrolled.replace("x", "y", 1.5)  # type: ignore[arg-type]
        self.assertEqual(unrolled.to_list(), ["x", "x"])

        positional = PositionalLinkedList(["x", "x"])
        with self.assertRaises(TypeError):
            positional.replace_value(
                "x",
                "y",
                1.5,  # type: ignore[arg-type]
            )
        self.assertEqual(positional.to_list(), ["x", "x"])

        self_organizing = SelfOrganizingLinkedList(
            ["x", "x"],
            strategy="none",
        )
        with self.assertRaises(TypeError):
            self_organizing.replace(
                "x",
                "y",
                1.5,  # type: ignore[arg-type]
            )
        self.assertEqual(self_organizing.to_list(), ["x", "x"])

        multilevel = MultilevelLinkedList.from_nested([("x", ["x"])])
        with self.assertRaises(TypeError):
            multilevel.replace("x", "y", 1.5)  # type: ignore[arg-type]
        self.assertEqual(multilevel.to_list(), ["x", "x"])


class TestRotationInputCoverageEdges(unittest.TestCase):
    """Cover rotation-count validation across rotate-capable structures."""

    def test_empty_structures_reject_non_integer_rotation_counts(self) -> None:
        containers: list[Any] = [
            LinkedList("singly"),
            LinkedList("doubly"),
            LinkedList("singly_circular"),
            LinkedList("doubly_circular"),
            LinkedDeque(),
            SortedLinkedList(),
            UnrolledLinkedList(),
            PositionalLinkedList(),
            SelfOrganizingLinkedList(),
            MultilevelLinkedList(),
        ]

        for container in containers:
            with self.assertRaises(TypeError):
                container.rotate("bad")  # type: ignore[arg-type]

    def test_singleton_structures_reject_bad_rotation_before_noop(
        self,
    ) -> None:
        containers: list[tuple[Any, list[Any]]] = [
            (LinkedList([1]), [1]),
            (LinkedDeque([1]), [1]),
            (SortedLinkedList([1]), [1]),
            (UnrolledLinkedList([1]), [1]),
            (PositionalLinkedList([1]), [1]),
            (SelfOrganizingLinkedList([1]), [1]),
            (MultilevelLinkedList([1]), [1]),
        ]

        for container, expected in containers:
            with self.assertRaises(TypeError):
                container.rotate(1.5)  # type: ignore[arg-type]
            self.assertEqual(container.to_list(), expected)

    def test_integer_like_rotation_counts_are_supported(self) -> None:
        class OneStep:
            def __index__(self) -> int:
                return 1

        class FullTurn:
            def __index__(self) -> int:
                return 3

        containers: list[tuple[Any, list[Any]]] = [
            (LinkedList([1, 2, 3]), [3, 1, 2]),
            (LinkedDeque([1, 2, 3]), [3, 1, 2]),
            (UnrolledLinkedList([1, 2, 3]), [3, 1, 2]),
            (PositionalLinkedList([1, 2, 3]), [3, 1, 2]),
            (SelfOrganizingLinkedList([1, 2, 3]), [3, 1, 2]),
            (MultilevelLinkedList([1, 2, 3]), [3, 1, 2]),
        ]

        for container, expected in containers:
            container.rotate(OneStep())  # type: ignore[arg-type]
            self.assertEqual(container.to_list(), expected)

        sorted_list = SortedLinkedList([1, 2, 3])
        sorted_list.rotate(FullTurn())  # type: ignore[arg-type]
        self.assertEqual(sorted_list.to_list(), [1, 2, 3])


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
