"""Optional property-based invariant tests.

The module skips automatically when Hypothesis is not installed. Installing
the `dev` or `test` extra enables these tests locally and in CI.
"""

from __future__ import annotations

import importlib
import unittest
from typing import Any, cast

from linked_list import (
    LinkedDeque,
    LinkedList,
    SkipList,
    SortedLinkedList,
    SparseMatrixLinkedList,
    UnrolledLinkedList,
)

try:
    hypothesis = cast(Any, importlib.import_module("hypothesis"))
    st = cast(Any, importlib.import_module("hypothesis.strategies"))
except ImportError as exc:
    raise unittest.SkipTest("Hypothesis is not installed") from exc


class TestPropertyInvariants(unittest.TestCase):
    """Property-based invariants that run under pytest and unittest."""

    @hypothesis.given(st.lists(st.integers(), max_size=40))
    @hypothesis.settings(max_examples=100)
    def test_linked_list_round_trips_python_values(
        self,
        values: list[int],
    ) -> None:
        """Appending values should match Python-list snapshots."""
        linked: LinkedList[int] = LinkedList()
        linked.extend(values)

        self.assertEqual(linked.to_list(), values)
        self.assertEqual(len(linked), len(values))

        with self.assertRaises(NotImplementedError):
            list(reversed(linked))

        doubly_linked: LinkedList[int] = LinkedList("doubly")
        doubly_linked.extend(values)

        self.assertEqual(list(reversed(doubly_linked)), list(reversed(values)))

    @hypothesis.given(st.lists(st.integers(), max_size=40))
    @hypothesis.settings(max_examples=100)
    def test_linked_deque_fifo_matches_collections(
        self,
        values: list[int],
    ) -> None:
        """Deque append-right/pop-left should preserve FIFO order."""
        deque: LinkedDeque[int] = LinkedDeque()
        deque.extend(values)

        popped = [deque.pop_left() for _ in range(len(values))]

        self.assertEqual(popped, values)
        self.assertTrue(deque.is_empty())

    @hypothesis.given(st.lists(st.integers(), max_size=40))
    @hypothesis.settings(max_examples=100)
    def test_sorted_structures_match_sorted_python_values(
        self,
        values: list[int],
    ) -> None:
        """Sorted linked list and skip list should expose sorted values."""
        sorted_list: SortedLinkedList[int] = SortedLinkedList(values)
        skip_list: SkipList[int] = SkipList(values, seed=1)

        self.assertEqual(sorted_list.to_list(), sorted(values))
        self.assertEqual(skip_list.to_list(), sorted(set(values)))

    @hypothesis.given(st.lists(st.integers(), max_size=40))
    @hypothesis.settings(max_examples=100)
    def test_unrolled_list_round_trips_blocks(
        self,
        values: list[int],
    ) -> None:
        """Unrolled lists should preserve order across block layouts."""
        unrolled: UnrolledLinkedList[int] = UnrolledLinkedList(
            values,
            node_capacity=5,
        )

        self.assertEqual(unrolled.to_list(), values)
        self.assertEqual(
            [item for block in unrolled.to_blocks() for item in block],
            values,
        )

    @hypothesis.given(
        st.lists(
            st.lists(
                st.integers(min_value=-3, max_value=3),
                min_size=3,
                max_size=3,
            ),
            min_size=3,
            max_size=3,
        ),
    )
    @hypothesis.settings(max_examples=100)
    def test_sparse_matrix_round_trips_dense_values(
        self,
        values: list[list[int]],
    ) -> None:
        """Sparse matrices should round-trip rectangular dense inputs."""
        matrix: SparseMatrixLinkedList[int]
        matrix = SparseMatrixLinkedList.from_dense(values)

        self.assertEqual(matrix.to_dense(), values)
