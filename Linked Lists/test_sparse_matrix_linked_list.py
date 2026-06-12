"""Tests for the linked sparse-matrix container."""

from __future__ import annotations

import random
import unittest
from typing import Any

from linked_list import SparseMatrixLinkedList


class TestSparseMatrixLinkedList(unittest.TestCase):
    """Behavior and row/column-chain tests for sparse matrices."""

    def assert_sparse_integrity(
        self,
        matrix: SparseMatrixLinkedList,
        dense: list[list[Any]],
    ) -> None:
        """Assert dense values, sparse entries, and internal links."""
        expected_entries = [
            (row, col, dense[row][col])
            for row in range(matrix.rows)
            for col in range(matrix.cols)
            if dense[row][col] != matrix.zero
        ]
        expected_density = (
            0.0
            if matrix.rows * matrix.cols == 0
            else len(expected_entries) / (matrix.rows * matrix.cols)
        )

        self.assertEqual(
            matrix.shape,
            (len(dense), len(dense[0]) if dense else 0),
        )
        self.assertEqual(matrix.to_entries(), expected_entries)
        self.assertEqual(list(matrix), expected_entries)
        self.assertEqual(
            list(matrix.values()),
            [entry[2] for entry in expected_entries],
        )
        self.assertEqual(matrix.to_dense(), dense)
        self.assertEqual(len(matrix), len(expected_entries))
        self.assertEqual(bool(matrix), bool(expected_entries))
        self.assertEqual(matrix.is_empty(), not expected_entries)
        self.assertAlmostEqual(matrix.density(), expected_density)

        row_chain_nodes = []
        for row in range(matrix.rows):
            expected_row = [
                (col, dense[row][col])
                for col in range(matrix.cols)
                if dense[row][col] != matrix.zero
            ]
            self.assertEqual(matrix.row_items(row), expected_row)

            previous_col = -1
            current = matrix._row_heads.get(row)
            while current is not None:
                self.assertEqual(current.row, row)
                self.assertGreater(current.col, previous_col)
                self.assertIs(matrix._find_node(row, current.col), current)
                row_chain_nodes.append(current)
                previous_col = current.col
                current = current.right

        column_chain_nodes = []
        for col in range(matrix.cols):
            expected_column = [
                (row, dense[row][col])
                for row in range(matrix.rows)
                if dense[row][col] != matrix.zero
            ]
            self.assertEqual(matrix.column_items(col), expected_column)

            previous_row = -1
            current = matrix._col_heads.get(col)
            while current is not None:
                self.assertEqual(current.col, col)
                self.assertGreater(current.row, previous_row)
                column_chain_nodes.append(current)
                previous_row = current.row
                current = current.down

        self.assertEqual(len(row_chain_nodes), len(expected_entries))
        self.assertEqual(len(column_chain_nodes), len(expected_entries))
        self.assertEqual(set(row_chain_nodes), set(column_chain_nodes))
        for row in range(matrix.rows):
            for col in range(matrix.cols):
                self.assertEqual(matrix[row, col], dense[row][col])
                if dense[row][col] == matrix.zero:
                    self.assertNotIn((row, col), matrix)
                else:
                    self.assertIn((row, col), matrix)

    def test_empty_state_and_validation_errors(self) -> None:
        matrix = SparseMatrixLinkedList(0, 0)

        self.assert_sparse_integrity(matrix, [])
        self.assertEqual(
            repr(matrix),
            "SparseMatrixLinkedList(rows=0, cols=0, entries=[], zero=0)",
        )

        for rows, cols in [(-1, 2), (2, -1)]:
            with self.assertRaises(ValueError):
                SparseMatrixLinkedList(rows, cols)
        for rows, cols in [(True, 2), (2, False), (1.5, 2)]:
            with self.assertRaises(TypeError):
                SparseMatrixLinkedList(rows, cols)  # type: ignore[arg-type]

        with self.assertRaises(IndexError):
            matrix.get(0, 0)
        with self.assertRaises(TypeError):
            matrix.set(True, 0, 1)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            _ = matrix["bad"]  # type: ignore[index]
        with self.assertRaises(TypeError):
            _ = matrix[0, 0, 0]  # type: ignore[index]

        nonsquare = SparseMatrixLinkedList(2, 3)
        with self.assertRaises(ValueError):
            nonsquare.trace()
        with self.assertRaises(ValueError):
            nonsquare.multiply_vector([1, 2])
        with self.assertRaises(ValueError):
            nonsquare @ SparseMatrixLinkedList(4, 2)
        with self.assertRaises(TypeError):
            nonsquare.matmul("bad")  # type: ignore[arg-type]

    def test_construction_from_entries_and_dense(self) -> None:
        matrix = SparseMatrixLinkedList.from_entries(
            3,
            3,
            [
                (1, 2, 5),
                (0, 1, 3),
                (1, 2, 7),
                (2, 0, 0),
                (2, 2, -1),
            ],
        )

        self.assert_sparse_integrity(
            matrix,
            [
                [0, 3, 0],
                [0, 0, 7],
                [0, 0, -1],
            ],
        )

        dense = ((value for value in row) for row in [[0, 2], [3, 0]])
        from_dense = SparseMatrixLinkedList.from_dense(dense)
        self.assert_sparse_integrity(from_dense, [[0, 2], [3, 0]])

        with self.assertRaises(ValueError):
            SparseMatrixLinkedList.from_dense([[1, 2], [3]])
        with self.assertRaises(IndexError):
            SparseMatrixLinkedList(2, 2, [(2, 0, 1)])

    def test_set_get_remove_pop_and_zero_pruning(self) -> None:
        matrix = SparseMatrixLinkedList(3, 4)

        matrix[2, 3] = 9
        matrix.set(0, 1, 5)
        matrix.set(2, 3, 10)
        matrix.set(1, 2, -2)
        self.assertEqual(matrix.get(0, 0), 0)
        self.assertIsNone(matrix.get(0, 0, None))
        self.assertEqual(matrix.get(0, 0, "missing"), "missing")

        self.assert_sparse_integrity(
            matrix,
            [
                [0, 5, 0, 0],
                [0, 0, -2, 0],
                [0, 0, 0, 10],
            ],
        )

        self.assertTrue(matrix.remove(0, 1))
        self.assertFalse(matrix.remove(0, 1))
        self.assertEqual(matrix.pop(1, 2), -2)
        self.assertEqual(matrix.pop(1, 2, "missing"), "missing")
        matrix.set(2, 3, 0)

        self.assert_sparse_integrity(matrix, [[0, 0, 0, 0] for _ in range(3)])

        matrix.set(0, 0, 1)
        matrix.set(1, 1, 2)
        matrix.clear()
        self.assert_sparse_integrity(matrix, [[0, 0, 0, 0] for _ in range(3)])

    def test_row_column_iteration_density_and_custom_zero(self) -> None:
        matrix = SparseMatrixLinkedList.from_dense(
            [
                [None, 4, None],
                [7, None, 8],
            ],
            zero=None,
        )

        self.assert_sparse_integrity(
            matrix,
            [
                [None, 4, None],
                [7, None, 8],
            ],
        )
        self.assertEqual(matrix.row_items(1), [(0, 7), (2, 8)])
        self.assertEqual(matrix.column_items(1), [(0, 4)])
        self.assertEqual(list(matrix.values()), [4, 7, 8])
        self.assertAlmostEqual(matrix.density(), 0.5)
        self.assertIsNone(matrix[0, 0])
        self.assertEqual(matrix.get(0, 0, "empty"), "empty")
        self.assertNotIn((0, 0), matrix)
        self.assertNotIn([0, 1], matrix)
        self.assertNotIn((True, 1), matrix)

    def test_copy_deep_copy_equality_and_transpose(self) -> None:
        matrix = SparseMatrixLinkedList(2, 3)
        matrix.set(0, 1, [1])
        matrix.set(1, 2, [2])

        copied = matrix.copy()
        deep = matrix.deep_copy()
        transposed = matrix.transpose()

        self.assertEqual(matrix, copied)
        self.assertEqual(matrix, deep)
        self.assert_sparse_integrity(
            transposed,
            [
                [0, 0],
                [[1], 0],
                [0, [2]],
            ],
        )

        copied.get(0, 1).append(99)
        self.assertEqual(matrix.get(0, 1), [1, 99])
        self.assertEqual(deep.get(0, 1), [1])
        self.assertNotEqual(
            matrix,
            SparseMatrixLinkedList(2, 3, [(0, 1, [1, 99])], zero=None),
        )

    def test_arithmetic_vector_multiply_matmul_and_trace(self) -> None:
        left = SparseMatrixLinkedList.from_dense(
            [
                [1, 0, 2],
                [0, 3, 0],
            ],
        )
        right = SparseMatrixLinkedList.from_dense(
            [
                [0, 4, 0],
                [5, 0, -3],
            ],
        )
        multiplier = SparseMatrixLinkedList.from_dense(
            [
                [1, 2],
                [0, 3],
                [4, 0],
            ],
        )

        self.assert_sparse_integrity(
            left + right,
            [
                [1, 4, 2],
                [5, 3, -3],
            ],
        )
        self.assert_sparse_integrity(
            left - right,
            [
                [1, -4, 2],
                [-5, 3, 3],
            ],
        )
        self.assert_sparse_integrity(
            left.scalar_multiply(3),
            [
                [3, 0, 6],
                [0, 9, 0],
            ],
        )
        self.assert_sparse_integrity(
            left.scalar_multiply(0),
            [
                [0, 0, 0],
                [0, 0, 0],
            ],
        )
        self.assertEqual(left.multiply_vector([2, 3, 4]), [10, 9])
        self.assert_sparse_integrity(
            left @ multiplier,
            [
                [9, 2],
                [0, 9],
            ],
        )

        square = SparseMatrixLinkedList.from_dense(
            [
                [5, 0, 1],
                [0, -2, 0],
                [3, 0, 4],
            ],
        )
        self.assertEqual(square.trace(), 7)
        with self.assertRaises(ValueError):
            left + SparseMatrixLinkedList(3, 2)

    def test_map_values_and_prune(self) -> None:
        matrix = SparseMatrixLinkedList.from_dense(
            [
                [1, 0, 2],
                [0, 3, 0],
            ],
        )

        squared = matrix.map_values(lambda value: value * value)
        self.assert_sparse_integrity(
            squared,
            [
                [1, 0, 4],
                [0, 9, 0],
            ],
        )

        for node in matrix._nodes():
            if node.value == 2:
                node.value = 0
        matrix.prune()

        self.assert_sparse_integrity(
            matrix,
            [
                [1, 0, 0],
                [0, 3, 0],
            ],
        )

    def test_randomized_mutations_match_dense_matrix(self) -> None:
        for seed in range(30):
            source = random.Random(seed)
            matrix = SparseMatrixLinkedList(6, 6)
            dense = [[0 for _ in range(6)] for _ in range(6)]

            for _ in range(160):
                operation = source.choice(
                    ["set", "getitem_setitem", "remove", "pop", "clear"],
                )
                row = source.randrange(6)
                col = source.randrange(6)
                value = source.randint(-4, 4)

                if operation == "set":
                    matrix.set(row, col, value)
                    dense[row][col] = value
                elif operation == "getitem_setitem":
                    matrix[row, col] = value
                    dense[row][col] = value
                    self.assertEqual(matrix[row, col], dense[row][col])
                elif operation == "remove":
                    existed = dense[row][col] != 0
                    self.assertEqual(matrix.remove(row, col), existed)
                    dense[row][col] = 0
                elif operation == "pop":
                    expected = (
                        dense[row][col] if dense[row][col] != 0 else "missing"
                    )
                    self.assertEqual(matrix.pop(row, col, "missing"), expected)
                    dense[row][col] = 0
                elif operation == "clear":
                    matrix.clear()
                    dense = [[0 for _ in range(6)] for _ in range(6)]

                self.assert_sparse_integrity(matrix, dense)
                self.assertEqual(
                    [matrix.row_sum(row_index) for row_index in range(6)],
                    [sum(row_values) for row_values in dense],
                )
                self.assertEqual(
                    [matrix.column_sum(col_index) for col_index in range(6)],
                    [
                        sum(
                            dense[row_index][col_index]
                            for row_index in range(6)
                        )
                        for col_index in range(6)
                    ],
                )
                self.assertEqual(
                    matrix.trace(),
                    sum(dense[index][index] for index in range(6)),
                )

    def test_randomized_arithmetic_matches_dense_math(self) -> None:
        for seed in range(25):
            source = random.Random(seed)
            left_dense = [
                [source.randint(-3, 3) for _ in range(5)] for _ in range(4)
            ]
            right_dense = [
                [source.randint(-3, 3) for _ in range(5)] for _ in range(4)
            ]
            multiplier_dense = [
                [source.randint(-3, 3) for _ in range(3)] for _ in range(5)
            ]

            left = SparseMatrixLinkedList.from_dense(left_dense)
            right = SparseMatrixLinkedList.from_dense(right_dense)
            multiplier = SparseMatrixLinkedList.from_dense(multiplier_dense)

            added = [
                [
                    left_dense[row][col] + right_dense[row][col]
                    for col in range(5)
                ]
                for row in range(4)
            ]
            subtracted = [
                [
                    left_dense[row][col] - right_dense[row][col]
                    for col in range(5)
                ]
                for row in range(4)
            ]
            multiplied = [
                [
                    sum(
                        left_dense[row][shared] * multiplier_dense[shared][col]
                        for shared in range(5)
                    )
                    for col in range(3)
                ]
                for row in range(4)
            ]

            self.assert_sparse_integrity(left + right, added)
            self.assert_sparse_integrity(left - right, subtracted)
            self.assert_sparse_integrity(left @ multiplier, multiplied)


if __name__ == "__main__":
    unittest.main()
