"""Sparse matrix represented with linked row and column chains.

Only non-zero entries are stored. Each stored cell participates in two linked
lists at once: a row chain through ``right`` links and a column chain through
``down`` links.

This is a linked-structure bridge to data science. Dense matrices spend space
on every coordinate, including zeros. Sparse matrices store only meaningful
entries. The row chains make row-wise work easy, and the column chains make it
possible to inspect the same data by column without rebuilding the matrix.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from copy import deepcopy
from typing import Any, TypeVar

TSparseMatrixLinkedList = TypeVar(
    "TSparseMatrixLinkedList",
    bound="SparseMatrixLinkedList",
)

_MISSING = object()


class _SparseMatrixNode:
    """Store one non-zero matrix cell plus row/column links.

    A node is shared by two sorted chains at the same time. ``right`` moves
    across one row by increasing column, while ``down`` moves down one column
    by increasing row.
    """

    __slots__ = ("col", "down", "right", "row", "value")

    def __init__(self, row: int, col: int, value: Any) -> None:
        """Initialize one stored matrix coordinate."""
        self.row = row
        self.col = col
        self.value = value
        self.right: _SparseMatrixNode | None = None
        self.down: _SparseMatrixNode | None = None

    def __repr__(self) -> str:
        """Return a compact debugging representation."""
        return (
            "_SparseMatrixNode("
            f"row={self.row}, col={self.col}, value={self.value!r})"
        )


class SparseMatrixLinkedList:
    """Sparse matrix with row and column linked lists.

    The matrix stores dictionaries of row heads and column heads. Each stored
    cell lives in both dictionaries' linked chains through the same node
    object. Mutation methods therefore repair two chains whenever a cell is
    inserted or removed.
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        entries: Iterable[tuple[int, int, Any]] | None = None,
        *,
        zero: Any = 0,
    ) -> None:
        """Initialize an empty sparse matrix and optional entries."""
        self._validate_dimension(rows, "rows")
        self._validate_dimension(cols, "cols")
        self.rows = rows
        self.cols = cols
        self.zero = zero
        self._row_heads: dict[int, _SparseMatrixNode] = {}
        self._col_heads: dict[int, _SparseMatrixNode] = {}
        self._size = 0

        if entries is not None:
            for row, col, value in entries:
                self.set(row, col, value)

    def __len__(self) -> int:
        """Return the number of stored non-zero cells."""
        return self._size

    def __bool__(self) -> bool:
        """Return whether the matrix stores any non-zero cells."""
        return self._size > 0

    def __iter__(self) -> Iterator[tuple[int, int, Any]]:
        """Yield ``(row, col, value)`` entries in row-major order."""
        yield from self.items()

    def __contains__(self, position: object) -> bool:
        """Return whether ``(row, col)`` currently stores a non-zero value."""
        if not isinstance(position, tuple) or len(position) != 2:
            return False
        row, col = position
        if not isinstance(row, int) or not isinstance(col, int):
            return False
        if isinstance(row, bool) or isinstance(col, bool):
            return False
        if not self._in_bounds(row, col):
            return False
        return self._find_node(row, col) is not None

    def __getitem__(self, key: tuple[int, int]) -> Any:
        """Return the value at ``(row, col)`` or the configured zero."""
        row, col = self._normalize_key(key)
        return self.get(row, col)

    def __setitem__(self, key: tuple[int, int], value: Any) -> None:
        """Set the value at ``(row, col)``."""
        row, col = self._normalize_key(key)
        self.set(row, col, value)

    def __eq__(self, other: object) -> bool:
        """Compare matrix shape, zero value, and non-zero entries."""
        if type(other) is not type(self):
            return False
        return (
            self.shape == other.shape
            and self.zero == other.zero
            and self.to_entries() == other.to_entries()
        )

    def __add__(
        self: TSparseMatrixLinkedList,
        other: SparseMatrixLinkedList,
    ) -> TSparseMatrixLinkedList:
        """Return matrix addition result."""
        return self.add_matrix(other)

    def __sub__(
        self: TSparseMatrixLinkedList,
        other: SparseMatrixLinkedList,
    ) -> TSparseMatrixLinkedList:
        """Return matrix subtraction result."""
        return self.subtract_matrix(other)

    def __matmul__(
        self: TSparseMatrixLinkedList,
        other: SparseMatrixLinkedList,
    ) -> TSparseMatrixLinkedList:
        """Return sparse matrix multiplication result."""
        return self.matmul(other)

    def __repr__(self) -> str:
        """Return a debugging representation."""
        return (
            f"{self.__class__.__name__}("
            f"rows={self.rows}, cols={self.cols}, "
            f"entries={self.to_entries()!r}, zero={self.zero!r})"
        )

    @property
    def shape(self) -> tuple[int, int]:
        """Return ``(rows, cols)``."""
        return self.rows, self.cols

    @classmethod
    def from_entries(
        cls: type[TSparseMatrixLinkedList],
        rows: int,
        cols: int,
        entries: Iterable[tuple[int, int, Any]],
        *,
        zero: Any = 0,
    ) -> TSparseMatrixLinkedList:
        """Build a sparse matrix from row/column/value entries."""
        return cls(rows, cols, entries, zero=zero)

    @classmethod
    def from_dense(
        cls: type[TSparseMatrixLinkedList],
        dense: Iterable[Iterable[Any]],
        *,
        zero: Any = 0,
    ) -> TSparseMatrixLinkedList:
        """Build a sparse matrix from a rectangular dense iterable."""
        rows = [list(row) for row in dense]
        row_count = len(rows)
        col_count = len(rows[0]) if rows else 0
        for row in rows:
            if len(row) != col_count:
                raise ValueError("dense matrix rows must be rectangular")

        entries = []
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                if value != zero:
                    entries.append((row_index, col_index, value))
        return cls(row_count, col_count, entries, zero=zero)

    def is_empty(self) -> bool:
        """Return whether no non-zero values are stored."""
        return self._size == 0

    def density(self) -> float:
        """Return the fraction of cells that are explicitly stored."""
        total_cells = self.rows * self.cols
        if total_cells == 0:
            return 0.0
        return self._size / total_cells

    def get(self, row: int, col: int, default: Any = _MISSING) -> Any:
        """Return a cell value, or ``default``/zero when absent."""
        self._validate_position(row, col)
        node = self._find_node(row, col)
        if node is None:
            return self.zero if default is _MISSING else default
        return node.value

    def set(self, row: int, col: int, value: Any) -> None:
        """Set a cell value, removing entries equal to zero.

        Assigning the configured ``zero`` value removes the coordinate instead
        of storing it. That rule is what keeps the representation sparse after
        arbitrary updates.
        """
        self._validate_position(row, col)
        node = self._find_node(row, col)
        if value == self.zero:
            if node is not None:
                self.remove(row, col)
            return

        if node is not None:
            node.value = value
            return

        new_node = _SparseMatrixNode(row, col, value)
        self._insert_into_row(new_node)
        self._insert_into_column(new_node)
        self._size += 1

    def remove(self, row: int, col: int) -> bool:
        """Remove a stored cell and return whether it existed."""
        self._validate_position(row, col)
        node = self._find_node(row, col)
        if node is None:
            return False

        self._remove_from_row(row, col)
        self._remove_from_column(row, col)
        node.right = None
        node.down = None
        self._size -= 1
        return True

    def pop(self, row: int, col: int, default: Any = None) -> Any:
        """Remove and return a cell value, or ``default`` when absent."""
        self._validate_position(row, col)
        node = self._find_node(row, col)
        if node is None:
            return default
        value = node.value
        self.remove(row, col)
        return value

    def clear(self) -> None:
        """Remove all stored cells and detach links."""
        for node in list(self._nodes()):
            node.right = None
            node.down = None
        self._row_heads.clear()
        self._col_heads.clear()
        self._size = 0

    def items(self) -> Iterator[tuple[int, int, Any]]:
        """Yield entries in row-major order."""
        for row in sorted(self._row_heads):
            current: _SparseMatrixNode | None = self._row_heads[row]
            while current is not None:
                yield current.row, current.col, current.value
                current = current.right

    def values(self) -> Iterator[Any]:
        """Yield stored non-zero values in row-major order."""
        for _, _, value in self.items():
            yield value

    def row_items(self, row: int) -> list[tuple[int, Any]]:
        """Return ``(col, value)`` pairs for one row."""
        self._validate_index(row, self.rows, "row")
        items = []
        current = self._row_heads.get(row)
        while current is not None:
            items.append((current.col, current.value))
            current = current.right
        return items

    def column_items(self, col: int) -> list[tuple[int, Any]]:
        """Return ``(row, value)`` pairs for one column."""
        self._validate_index(col, self.cols, "col")
        items = []
        current = self._col_heads.get(col)
        while current is not None:
            items.append((current.row, current.value))
            current = current.down
        return items

    def to_entries(self) -> list[tuple[int, int, Any]]:
        """Return stored entries as row-major triples."""
        return list(self.items())

    def to_dense(self) -> list[list[Any]]:
        """Return a dense Python list-of-lists representation."""
        dense = [
            [deepcopy(self.zero) for _ in range(self.cols)]
            for _ in range(self.rows)
        ]
        for row, col, value in self.items():
            dense[row][col] = value
        return dense

    def copy(self: TSparseMatrixLinkedList) -> TSparseMatrixLinkedList:
        """Return a shallow sparse-matrix copy."""
        return self.__class__(
            self.rows,
            self.cols,
            self.items(),
            zero=self.zero,
        )

    def deep_copy(self: TSparseMatrixLinkedList) -> TSparseMatrixLinkedList:
        """Return a deep sparse-matrix copy."""
        return self.__class__(
            self.rows,
            self.cols,
            ((row, col, deepcopy(value)) for row, col, value in self.items()),
            zero=deepcopy(self.zero),
        )

    def transpose(self: TSparseMatrixLinkedList) -> TSparseMatrixLinkedList:
        """Return a transposed sparse matrix."""
        return self.__class__(
            self.cols,
            self.rows,
            ((col, row, value) for row, col, value in self.items()),
            zero=self.zero,
        )

    def row_sum(self, row: int) -> Any:
        """Return the sum of stored values in one row."""
        self._validate_index(row, self.rows, "row")
        return sum(value for _, value in self.row_items(row))

    def column_sum(self, col: int) -> Any:
        """Return the sum of stored values in one column."""
        self._validate_index(col, self.cols, "col")
        return sum(value for _, value in self.column_items(col))

    def trace(self) -> Any:
        """Return the matrix trace for square matrices."""
        if self.rows != self.cols:
            raise ValueError("trace requires a square matrix")
        return sum(self.get(index, index) for index in range(self.rows))

    def add_matrix(
        self: TSparseMatrixLinkedList,
        other: SparseMatrixLinkedList,
    ) -> TSparseMatrixLinkedList:
        """Return the sum of two matrices with the same shape."""
        self._validate_same_shape(other)
        result = self.copy()
        for row, col, value in other.items():
            result.set(row, col, result.get(row, col) + value)
        return result

    def subtract_matrix(
        self: TSparseMatrixLinkedList,
        other: SparseMatrixLinkedList,
    ) -> TSparseMatrixLinkedList:
        """Return the difference of two matrices with the same shape."""
        self._validate_same_shape(other)
        result = self.copy()
        for row, col, value in other.items():
            result.set(row, col, result.get(row, col) - value)
        return result

    def scalar_multiply(
        self: TSparseMatrixLinkedList,
        scalar: Any,
    ) -> TSparseMatrixLinkedList:
        """Return a matrix with every stored value multiplied by scalar."""
        return self.__class__(
            self.rows,
            self.cols,
            ((row, col, value * scalar) for row, col, value in self.items()),
            zero=self.zero,
        )

    def multiply_vector(self, vector: Iterable[Any]) -> list[Any]:
        """Return dense matrix-vector multiplication result."""
        values = list(vector)
        if len(values) != self.cols:
            raise ValueError("Vector length must match matrix columns")
        result = [0 for _ in range(self.rows)]
        for row, col, value in self.items():
            result[row] += value * values[col]
        return result

    def matmul(
        self: TSparseMatrixLinkedList,
        other: SparseMatrixLinkedList,
    ) -> TSparseMatrixLinkedList:
        """Return sparse matrix multiplication result.

        For each stored left value at ``(row, shared_col)``, only stored values
        in ``other`` row ``shared_col`` can contribute to the result. This
        skips dense zero work while still producing the same math.
        """
        if not isinstance(other, SparseMatrixLinkedList):
            raise TypeError("other must be a SparseMatrixLinkedList")
        if self.cols != other.rows:
            raise ValueError("Left columns must match right rows")

        result_entries: dict[tuple[int, int], Any] = {}
        for row, shared_col, left_value in self.items():
            for col, right_value in other.row_items(shared_col):
                key = (row, col)
                result_entries[key] = (
                    result_entries.get(key, self.zero)
                    + left_value * right_value
                )

        return self.__class__(
            self.rows,
            other.cols,
            (
                (row, col, value)
                for (row, col), value in result_entries.items()
                if value != self.zero
            ),
            zero=self.zero,
        )

    def map_values(
        self: TSparseMatrixLinkedList,
        func: Callable[[Any], Any],
    ) -> TSparseMatrixLinkedList:
        """Return a matrix with ``func`` applied to stored values."""
        return self.__class__(
            self.rows,
            self.cols,
            ((row, col, func(value)) for row, col, value in self.items()),
            zero=self.zero,
        )

    def prune(self) -> None:
        """Remove any stored entries that now equal the zero value."""
        for row, col, value in list(self.items()):
            if value == self.zero:
                self.remove(row, col)

    def _nodes(self) -> Iterator[_SparseMatrixNode]:
        """Yield all stored nodes from row chains."""
        for row in sorted(self._row_heads):
            current: _SparseMatrixNode | None = self._row_heads[row]
            while current is not None:
                yield current
                current = current.right

    def _find_node(
        self,
        row: int,
        col: int,
    ) -> _SparseMatrixNode | None:
        """Return a stored node or ``None``."""
        current = self._row_heads.get(row)
        while current is not None and current.col <= col:
            if current.col == col:
                return current
            current = current.right
        return None

    def _insert_into_row(self, node: _SparseMatrixNode) -> None:
        """Insert ``node`` into its sorted row chain.

        Row chains are ordered by column, so row iteration and dense conversion
        naturally produce row-major entries.
        """
        head = self._row_heads.get(node.row)
        if head is None or node.col < head.col:
            node.right = head
            self._row_heads[node.row] = node
            return

        previous = head
        current = head.right
        while current is not None and current.col < node.col:
            previous = current
            current = current.right
        node.right = current
        previous.right = node

    def _insert_into_column(self, node: _SparseMatrixNode) -> None:
        """Insert ``node`` into its sorted column chain.

        Column chains are ordered by row. The same node is inserted here after
        being inserted into its row chain.
        """
        head = self._col_heads.get(node.col)
        if head is None or node.row < head.row:
            node.down = head
            self._col_heads[node.col] = node
            return

        previous = head
        current = head.down
        while current is not None and current.row < node.row:
            previous = current
            current = current.down
        node.down = current
        previous.down = node

    def _remove_from_row(self, row: int, col: int) -> None:
        """Remove one cell from a row chain.

        The caller already knows the coordinate exists. This helper repairs
        only the row-side links; column-side repair happens separately.
        """
        current = self._row_heads.get(row)
        previous = None
        while current is not None:
            if current.col == col:
                if previous is None:
                    if current.right is None:
                        del self._row_heads[row]
                    else:
                        self._row_heads[row] = current.right
                else:
                    previous.right = current.right
                return
            previous = current
            current = current.right

    def _remove_from_column(self, row: int, col: int) -> None:
        """Remove one cell from a column chain.

        The caller already knows the coordinate exists. This helper repairs
        only the column-side links; row-side repair happens separately.
        """
        current = self._col_heads.get(col)
        previous = None
        while current is not None:
            if current.row == row:
                if previous is None:
                    if current.down is None:
                        del self._col_heads[col]
                    else:
                        self._col_heads[col] = current.down
                else:
                    previous.down = current.down
                return
            previous = current
            current = current.down

    def _normalize_key(self, key: tuple[int, int]) -> tuple[int, int]:
        """Validate and return a matrix key."""
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError("Matrix key must be a (row, col) tuple")
        row, col = key
        self._validate_position(row, col)
        return row, col

    def _validate_position(self, row: int, col: int) -> None:
        """Validate a row and column position."""
        self._validate_index(row, self.rows, "row")
        self._validate_index(col, self.cols, "col")

    def _validate_same_shape(self, other: SparseMatrixLinkedList) -> None:
        """Raise when two matrices cannot be combined element-wise."""
        if not isinstance(other, SparseMatrixLinkedList):
            raise TypeError("other must be a SparseMatrixLinkedList")
        if self.shape != other.shape:
            raise ValueError("Matrix shapes must match")

    def _in_bounds(self, row: int, col: int) -> bool:
        """Return whether a row/column position is valid."""
        return 0 <= row < self.rows and 0 <= col < self.cols

    @staticmethod
    def _validate_dimension(value: int, name: str) -> None:
        """Validate a matrix dimension."""
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} must be an integer")
        if value < 0:
            raise ValueError(f"{name} must be non-negative")

    @staticmethod
    def _validate_index(index: int, limit: int, name: str) -> None:
        """Validate one bounded index."""
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError(f"{name} index must be an integer")
        if index < 0 or index >= limit:
            raise IndexError(f"{name} index out of range")
