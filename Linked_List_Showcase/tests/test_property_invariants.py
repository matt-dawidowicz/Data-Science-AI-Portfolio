"""Property-based invariant tests for linked structures.

These tests compare public container behavior with small Python reference
models. They are intentionally heavier than the normal unit tests because
their job is to shake operation sequences, link repair, and edge cases that
are easy to miss with hand-written examples.
"""

import unittest
from collections import deque
from collections.abc import Iterable
from typing import Any

from hypothesis import given, settings
from hypothesis import strategies as st

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

LIST_TYPES = st.sampled_from(
    ("singly", "doubly", "singly_circular", "doubly_circular"),
)
SMALL_INTS = st.integers(min_value=-10, max_value=10)
OPERATIONS = st.lists(
    st.tuples(
        st.sampled_from(
            (
                "append",
                "prepend",
                "insert",
                "remove",
                "remove_all",
                "remove_at",
                "pop",
                "pop_front",
                "replace",
                "reverse",
                "rotate",
                "sort",
            ),
        ),
        SMALL_INTS,
        st.integers(min_value=-30, max_value=30),
    ),
    max_size=60,
)


def _insert_index(raw_index: int, size: int) -> int:
    """Return a valid insertion index for a sequence of ``size`` values."""
    if size == 0:
        return 0
    return raw_index % (size + 1)


def _existing_index(raw_index: int, size: int) -> int:
    """Return a valid existing-item index for a non-empty sequence."""
    return raw_index % size


def _rotate_values(values: list[int], steps: int) -> None:
    """Rotate ``values`` in place using the package's right-rotate rules."""
    if len(values) <= 1:
        return
    steps %= len(values)
    if steps:
        values[:] = values[-steps:] + values[:-steps]


def _dense_add(
    left: list[list[int]],
    right: list[list[int]],
) -> list[list[int]]:
    """Return dense matrix addition."""
    return [
        [left[row][col] + right[row][col] for col in range(len(left[0]))]
        for row in range(len(left))
    ]


def _dense_subtract(
    left: list[list[int]],
    right: list[list[int]],
) -> list[list[int]]:
    """Return dense matrix subtraction."""
    return [
        [left[row][col] - right[row][col] for col in range(len(left[0]))]
        for row in range(len(left))
    ]


def _dense_matmul(
    left: list[list[int]],
    right: list[list[int]],
) -> list[list[int]]:
    """Return dense matrix multiplication."""
    rows = len(left)
    shared = len(right)
    cols = len(right[0]) if right else 0
    return [
        [
            sum(
                left[row][inner] * right[inner][col] for inner in range(shared)
            )
            for col in range(cols)
        ]
        for row in range(rows)
    ]


def _nested_depth_first(items: Iterable[Any]) -> list[int]:
    """Return generated nested values in depth-first order."""
    values = []
    for item in items:
        if isinstance(item, tuple):
            value, children = item
            values.append(value)
            values.extend(_nested_depth_first(children))
        else:
            values.append(item)
    return values


def _nested_breadth_first(items: list[Any]) -> list[int]:
    """Return generated nested values in breadth-first order."""
    values = []
    queue: deque[list[Any]] = deque([items])
    while queue:
        level = queue.popleft()
        for item in level:
            if isinstance(item, tuple):
                value, children = item
                values.append(value)
                queue.append(children)
            else:
                values.append(item)
    return values


NESTED_ITEM = st.recursive(
    SMALL_INTS,
    lambda children: st.tuples(
        SMALL_INTS,
        st.lists(children, max_size=3),
    ),
    max_leaves=20,
)


class TestPropertyInvariants(unittest.TestCase):
    """Property-based invariants that run under pytest and unittest."""

    def assert_linked_list_links(self, linked: LinkedList[int]) -> None:
        """Assert head, tail, size, and wraparound links agree."""
        values = linked.to_list()
        self.assertEqual(len(linked), len(values))

        if not values:
            self.assertIsNone(linked.head)
            self.assertIsNone(linked.tail)
            return

        self.assertIsNotNone(linked.head)
        self.assertIsNotNone(linked.tail)

        if linked._is_circular:
            self.assertIs(linked.tail.next, linked.head)
            if "doubly" in linked._list_type:
                self.assertIs(linked.head.prev, linked.tail)
        else:
            self.assertIsNone(linked.tail.next)
            if "doubly" in linked._list_type:
                self.assertIsNone(linked.head.prev)

    @given(
        list_type=LIST_TYPES,
        values=st.lists(SMALL_INTS, max_size=20),
        operations=OPERATIONS,
    )
    @settings(max_examples=120, deadline=None)
    def test_linked_list_mutation_sequences_match_python_list(
        self,
        list_type: str,
        values: list[int],
        operations: list[tuple[str, int, int]],
    ) -> None:
        """LinkedList operation sequences should match a Python list."""
        linked: LinkedList[int] = LinkedList(list_type)
        linked.extend(values)
        model = list(values)

        for operation, value, raw_index in operations:
            if operation == "append":
                linked.append(value)
                model.append(value)
            elif operation == "prepend":
                linked.prepend(value)
                model.insert(0, value)
            elif operation == "insert":
                index = _insert_index(raw_index, len(model))
                linked.insert(index, value)
                model.insert(index, value)
            elif operation == "remove":
                removed = linked.remove(value)
                if value in model:
                    model.remove(value)
                    self.assertTrue(removed)
                else:
                    self.assertFalse(removed)
            elif operation == "remove_all":
                removed = linked.remove_all(value)
                expected_removed = model.count(value)
                model[:] = [item for item in model if item != value]
                self.assertEqual(removed, expected_removed)
            elif operation == "remove_at" and model:
                index = _existing_index(raw_index, len(model))
                self.assertEqual(linked.remove_at(index), model.pop(index))
            elif operation == "pop" and model:
                self.assertEqual(linked.pop(), model.pop())
            elif operation == "pop_front" and model:
                self.assertEqual(linked.pop_front(), model.pop(0))
            elif operation == "replace":
                replacement = raw_index % 11 - 5
                changed = linked.replace(value, replacement)
                expected_changed = model.count(value)
                model[:] = [
                    replacement if item == value else item for item in model
                ]
                self.assertEqual(changed, expected_changed)
            elif operation == "reverse":
                linked.reverse()
                model.reverse()
            elif operation == "rotate":
                linked.rotate(raw_index)
                _rotate_values(model, raw_index)
            elif operation == "sort":
                linked.sort()
                model.sort()

            self.assertEqual(linked.to_list(), model)
            self.assert_linked_list_links(linked)

    @given(
        values=st.lists(SMALL_INTS, max_size=30),
        operations=OPERATIONS,
    )
    @settings(max_examples=100, deadline=None)
    def test_linked_deque_sequences_match_python_list(
        self,
        values: list[int],
        operations: list[tuple[str, int, int]],
    ) -> None:
        """LinkedDeque end operations should match a Python-list model."""
        linked: LinkedDeque[int] = LinkedDeque(values)
        model = list(values)

        for operation, value, raw_index in operations:
            if operation == "append":
                linked.append_right(value)
                model.append(value)
            elif operation == "prepend":
                linked.append_left(value)
                model.insert(0, value)
            elif operation == "insert":
                linked.insert(raw_index, value)
                if raw_index < 0:
                    raw_index += len(model)
                    if raw_index < 0:
                        raw_index = 0
                if raw_index <= 0:
                    model.insert(0, value)
                elif raw_index >= len(model):
                    model.append(value)
                else:
                    model.insert(raw_index, value)
            elif operation == "remove":
                if value in model:
                    linked.remove(value)
                    model.remove(value)
                else:
                    with self.assertRaises(ValueError):
                        linked.remove(value)
            elif operation == "remove_all":
                removed = linked.remove_all(value)
                expected_removed = model.count(value)
                model[:] = [item for item in model if item != value]
                self.assertEqual(removed, expected_removed)
            elif operation == "remove_at" and model:
                index = _existing_index(raw_index, len(model))
                self.assertEqual(linked[index], model[index])
            elif operation == "pop" and model:
                self.assertEqual(linked.pop_right(), model.pop())
            elif operation == "pop_front" and model:
                self.assertEqual(linked.pop_left(), model.pop(0))
            elif operation == "replace":
                replacement = raw_index % 11 - 5
                changed = linked.replace(value, replacement)
                expected_changed = model.count(value)
                model[:] = [
                    replacement if item == value else item for item in model
                ]
                self.assertEqual(changed, expected_changed)
            elif operation == "reverse":
                linked.reverse()
                model.reverse()
            elif operation == "rotate":
                linked.rotate(raw_index)
                _rotate_values(model, raw_index)

            self.assertEqual(linked.to_list(), model)
            self.assertEqual(len(linked), len(model))

    @given(
        values=st.lists(SMALL_INTS, max_size=30),
        operations=OPERATIONS,
        capacity=st.integers(min_value=2, max_value=8),
    )
    @settings(max_examples=100, deadline=None)
    def test_unrolled_list_sequences_match_python_list(
        self,
        values: list[int],
        operations: list[tuple[str, int, int]],
        capacity: int,
    ) -> None:
        """Unrolled lists should preserve sequence and block bounds."""
        linked: UnrolledLinkedList[int] = UnrolledLinkedList(
            values,
            node_capacity=capacity,
        )
        model = list(values)

        for operation, value, raw_index in operations:
            if operation == "append":
                linked.append(value)
                model.append(value)
            elif operation == "prepend":
                linked.prepend(value)
                model.insert(0, value)
            elif operation == "insert":
                index = _insert_index(raw_index, len(model))
                linked.insert(index, value)
                model.insert(index, value)
            elif operation == "remove":
                removed = linked.remove(value)
                if value in model:
                    model.remove(value)
                    self.assertTrue(removed)
                else:
                    self.assertFalse(removed)
            elif operation == "remove_all":
                removed = linked.remove_all(value)
                expected_removed = model.count(value)
                model[:] = [item for item in model if item != value]
                self.assertEqual(removed, expected_removed)
            elif operation == "remove_at" and model:
                index = _existing_index(raw_index, len(model))
                self.assertEqual(linked.remove_at(index), model.pop(index))
            elif operation == "pop" and model:
                self.assertEqual(linked.pop(), model.pop())
            elif operation == "pop_front" and model:
                self.assertEqual(linked.pop_front(), model.pop(0))
            elif operation == "replace":
                replacement = raw_index % 11 - 5
                changed = linked.replace(value, replacement)
                expected_changed = model.count(value)
                model[:] = [
                    replacement if item == value else item for item in model
                ]
                self.assertEqual(changed, expected_changed)
            elif operation == "reverse":
                linked.reverse()
                model.reverse()
            elif operation == "rotate":
                linked.rotate(raw_index)
                _rotate_values(model, raw_index)
            elif operation == "sort":
                linked.sort()
                model.sort()

            blocks = linked.to_blocks()
            flattened = [item for block in blocks for item in block]
            self.assertEqual(flattened, model)
            self.assertTrue(
                all(0 < len(block) <= capacity for block in blocks)
            )
            self.assertEqual(linked.to_list(), model)

    @given(
        values=st.lists(SMALL_INTS, max_size=25),
        operations=OPERATIONS,
    )
    @settings(max_examples=100, deadline=None)
    def test_positional_list_sequences_match_python_list(
        self,
        values: list[int],
        operations: list[tuple[str, int, int]],
    ) -> None:
        """PositionalLinkedList value operations should match Python lists."""
        linked: PositionalLinkedList[int] = PositionalLinkedList(values)
        model = list(values)

        for operation, value, raw_index in operations:
            if operation == "append":
                linked.append(value)
                model.append(value)
            elif operation == "prepend":
                linked.prepend(value)
                model.insert(0, value)
            elif operation == "insert":
                index = _insert_index(raw_index, len(model))
                linked.insert(index, value)
                model.insert(index, value)
            elif operation == "remove":
                removed = linked.remove(value)
                if value in model:
                    model.remove(value)
                    self.assertTrue(removed)
                else:
                    self.assertFalse(removed)
            elif operation == "remove_all":
                removed = linked.remove_all(value)
                expected_removed = model.count(value)
                model[:] = [item for item in model if item != value]
                self.assertEqual(removed, expected_removed)
            elif operation == "remove_at" and model:
                index = _existing_index(raw_index, len(model))
                self.assertEqual(linked.remove_at(index), model.pop(index))
            elif operation == "pop" and model:
                self.assertEqual(linked.pop_last(), model.pop())
            elif operation == "pop_front" and model:
                self.assertEqual(linked.pop_first(), model.pop(0))
            elif operation == "replace" and model:
                index = _existing_index(raw_index, len(model))
                position = linked.position_at(index)
                self.assertEqual(linked.replace(position, value), model[index])
                model[index] = value
            elif operation == "reverse":
                linked.reverse()
                model.reverse()
            elif operation == "rotate":
                linked.rotate(raw_index)
                _rotate_values(model, raw_index)
            elif operation == "sort":
                linked.sort()
                model.sort()

            self.assertEqual(linked.to_list(), model)
            self.assertEqual(len(linked), len(model))
            self.assertEqual(
                [position.data for position in linked.positions()],
                model,
            )

    @given(
        values=st.lists(SMALL_INTS, min_size=1, max_size=12, unique=True),
        accesses=st.lists(st.integers(min_value=0, max_value=50), max_size=50),
        strategy=st.sampled_from(
            ("none", "move_to_front", "transpose", "frequency_count"),
        ),
    )
    @settings(max_examples=120, deadline=None)
    def test_self_organizing_access_strategies_match_reference_model(
        self,
        values: list[int],
        accesses: list[int],
        strategy: str,
    ) -> None:
        """SelfOrganizingLinkedList should apply each adaptive strategy."""
        linked: SelfOrganizingLinkedList[int] = SelfOrganizingLinkedList(
            values,
            strategy=strategy,
        )
        model = [(value, 0) for value in values]

        for raw_index in accesses:
            index = raw_index % len(model)
            value = model[index][0]

            self.assertEqual(linked.find(value), index)
            current_index = next(
                position
                for position, (item, _) in enumerate(model)
                if item == value
            )
            item, count = model[current_index]
            model[current_index] = (item, count + 1)

            if strategy == "move_to_front":
                model.insert(0, model.pop(current_index))
            elif strategy == "transpose" and current_index > 0:
                model[current_index - 1], model[current_index] = (
                    model[current_index],
                    model[current_index - 1],
                )
            elif strategy == "frequency_count":
                while (
                    current_index > 0
                    and model[current_index][1] > model[current_index - 1][1]
                ):
                    model[current_index - 1], model[current_index] = (
                        model[current_index],
                        model[current_index - 1],
                    )
                    current_index -= 1

            self.assertEqual(linked.to_access_counts(), model)

    @given(
        values=st.lists(SMALL_INTS, max_size=30),
        operations=st.lists(
            st.tuples(
                st.sampled_from(
                    ("add", "remove", "remove_all", "replace", "dedupe"),
                ),
                SMALL_INTS,
                SMALL_INTS,
            ),
            max_size=50,
        ),
    )
    @settings(max_examples=100, deadline=None)
    def test_sorted_linked_list_sequences_stay_sorted(
        self,
        values: list[int],
        operations: list[tuple[str, int, int]],
    ) -> None:
        """Sorted lists should match sorted Python values with duplicates."""
        linked: SortedLinkedList[int] = SortedLinkedList(values)
        model = sorted(values)

        for operation, value, replacement in operations:
            if operation == "add":
                linked.add(value)
                model.append(value)
                model.sort()
            elif operation == "remove":
                removed = linked.remove(value)
                if value in model:
                    model.remove(value)
                    self.assertTrue(removed)
                else:
                    self.assertFalse(removed)
            elif operation == "remove_all":
                removed = linked.remove_all(value)
                expected_removed = model.count(value)
                model[:] = [item for item in model if item != value]
                self.assertEqual(removed, expected_removed)
            elif operation == "replace":
                changed = linked.replace(value, replacement)
                expected_changed = model.count(value)
                model[:] = [
                    replacement if item == value else item for item in model
                ]
                model.sort()
                self.assertEqual(changed, expected_changed)
            elif operation == "dedupe":
                linked.remove_duplicates()
                model[:] = sorted(set(model))

            self.assertEqual(linked.to_list(), model)

    @given(
        values=st.lists(SMALL_INTS, max_size=30),
        operations=st.lists(
            st.tuples(
                st.sampled_from(("add", "remove", "discard", "pop_first")),
                SMALL_INTS,
                SMALL_INTS,
            ),
            max_size=50,
        ),
    )
    @settings(max_examples=100, deadline=None)
    def test_skip_list_sequences_match_python_set(
        self,
        values: list[int],
        operations: list[tuple[str, int, int]],
    ) -> None:
        """SkipList should match a Python set exposed in sorted order."""
        linked: SkipList[int] = SkipList(values, seed=1)
        model = set(values)

        for operation, value, _ in operations:
            if operation == "add":
                added = linked.add(value)
                expected_added = value not in model
                model.add(value)
                self.assertEqual(added, expected_added)
            elif operation == "remove":
                removed = linked.remove(value)
                expected_removed = value in model
                model.discard(value)
                self.assertEqual(removed, expected_removed)
            elif operation == "discard":
                removed = linked.discard(value)
                expected_removed = value in model
                model.discard(value)
                self.assertEqual(removed, expected_removed)
            elif operation == "pop_first" and model:
                self.assertEqual(linked.pop_first(), min(model))
                model.remove(min(model))

            self.assertEqual(linked.to_list(), sorted(model))
            self.assertEqual(len(linked), len(model))

    @given(nested=st.lists(NESTED_ITEM, max_size=5))
    @settings(max_examples=120, deadline=None)
    def test_multilevel_list_traversals_match_nested_reference(
        self,
        nested: list[Any],
    ) -> None:
        """Multilevel lists should traverse generated hierarchies correctly."""
        linked: MultilevelLinkedList[int] = MultilevelLinkedList.from_nested(
            nested,
        )
        depth_first = _nested_depth_first(nested)
        breadth_first = _nested_breadth_first(nested)

        self.assertEqual(linked.to_list(), depth_first)
        self.assertEqual(linked.to_list("breadth_first"), breadth_first)
        self.assertEqual(
            linked.copy().to_nested_list(), linked.to_nested_list()
        )
        self.assertEqual(
            linked.flattened("breadth_first").to_top_level_list(),
            breadth_first,
        )

    @given(
        rows=st.integers(min_value=0, max_value=5),
        cols=st.integers(min_value=0, max_value=5),
        data=st.data(),
    )
    @settings(max_examples=120, deadline=None)
    def test_sparse_matrix_operations_match_dense_reference(
        self,
        rows: int,
        cols: int,
        data: Any,
    ) -> None:
        """SparseMatrixLinkedList should match dense matrix math."""
        dense = data.draw(
            st.lists(
                st.lists(
                    st.integers(min_value=-3, max_value=3),
                    min_size=cols,
                    max_size=cols,
                ),
                min_size=rows,
                max_size=rows,
            ),
            label="dense",
        )
        matrix: SparseMatrixLinkedList[int]
        matrix = SparseMatrixLinkedList.from_dense(dense)

        self.assertEqual(matrix.to_dense(), dense)
        self.assertEqual(
            len(matrix),
            sum(1 for row in dense for value in row if value != 0),
        )

        if rows == 0 or cols == 0:
            return

        row = data.draw(st.integers(min_value=0, max_value=rows - 1))
        col = data.draw(st.integers(min_value=0, max_value=cols - 1))
        value = data.draw(st.integers(min_value=-3, max_value=3))
        matrix.set(row, col, value)
        dense[row][col] = value
        self.assertEqual(matrix.to_dense(), dense)

        removed_value = dense[row][col]
        self.assertEqual(matrix.pop(row, col, default=0), removed_value)
        dense[row][col] = 0
        self.assertEqual(matrix.to_dense(), dense)

        other_dense = data.draw(
            st.lists(
                st.lists(
                    st.integers(min_value=-3, max_value=3),
                    min_size=cols,
                    max_size=cols,
                ),
                min_size=rows,
                max_size=rows,
            ),
            label="other_dense",
        )
        other = SparseMatrixLinkedList.from_dense(other_dense)
        self.assertEqual(
            (matrix + other).to_dense(),
            _dense_add(dense, other_dense),
        )
        self.assertEqual(
            (matrix - other).to_dense(),
            _dense_subtract(dense, other_dense),
        )

        vector = data.draw(
            st.lists(
                st.integers(min_value=-3, max_value=3),
                min_size=cols,
                max_size=cols,
            ),
            label="vector",
        )
        expected_vector = [
            sum(dense[row][col] * vector[col] for col in range(cols))
            for row in range(rows)
        ]
        self.assertEqual(matrix.multiply_vector(vector), expected_vector)

        right_cols = data.draw(st.integers(min_value=1, max_value=5))
        right_dense = data.draw(
            st.lists(
                st.lists(
                    st.integers(min_value=-3, max_value=3),
                    min_size=right_cols,
                    max_size=right_cols,
                ),
                min_size=cols,
                max_size=cols,
            ),
            label="right_dense",
        )
        right = SparseMatrixLinkedList.from_dense(right_dense)
        self.assertEqual(
            (matrix @ right).to_dense(),
            _dense_matmul(dense, right_dense),
        )

    @given(
        dense=st.lists(
            st.lists(
                st.integers(min_value=-1, max_value=3),
                min_size=4,
                max_size=4,
            ),
            min_size=4,
            max_size=4,
        ),
    )
    @settings(max_examples=80, deadline=None)
    def test_sparse_matrix_custom_zero_round_trips(
        self,
        dense: list[list[int]],
    ) -> None:
        """Sparse matrices should respect a caller-provided zero sentinel."""
        matrix = SparseMatrixLinkedList.from_dense(dense, zero=-1)

        self.assertEqual(matrix.to_dense(), dense)
        self.assertEqual(
            len(matrix),
            sum(1 for row in dense for value in row if value != -1),
        )


if __name__ == "__main__":
    unittest.main()
