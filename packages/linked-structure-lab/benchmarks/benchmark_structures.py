"""Lightweight benchmarks for educational linked structures.

These timings are not formal performance claims. They are a teaching aid that
shows where Python's optimized built-ins tend to win and where the linked
structures make tradeoffs visible.
"""

from __future__ import annotations

import bisect
import statistics
import sys
from collections import deque
from collections.abc import Callable
from pathlib import Path
from time import perf_counter

PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src"
PACKAGE_ROOT_TEXT = str(PACKAGE_ROOT)
if PACKAGE_ROOT_TEXT not in sys.path:
    sys.path.insert(0, PACKAGE_ROOT_TEXT)

from linked_list import (  # noqa: E402
    LinkedDeque,
    LinkedList,
    SkipList,
    SortedLinkedList,
    SparseMatrixLinkedList,
    UnrolledLinkedList,
)

N = 2_000
REPEAT = 5


def time_case(name: str, func: Callable[[], object]) -> tuple[str, float]:
    """Return the median runtime for ``func`` in milliseconds."""
    samples = []
    for _ in range(REPEAT):
        start = perf_counter()
        func()
        samples.append((perf_counter() - start) * 1_000)
    return name, statistics.median(samples)


def built_in_list_append() -> list[int]:
    """Append integers to a built-in list."""
    values: list[int] = []
    for value in range(N):
        values.append(value)
    return values


def linked_list_append() -> list[int]:
    """Append integers to the educational linked list."""
    values: LinkedList[int] = LinkedList()
    for value in range(N):
        values.append(value)
    return values.to_list()


def collections_deque_queue() -> list[int]:
    """Use the standard-library deque as a FIFO queue."""
    values: deque[int] = deque()
    for value in range(N):
        values.append(value)
    return [values.popleft() for _ in range(N)]


def linked_deque_queue() -> list[int]:
    """Use the educational linked deque as a FIFO queue."""
    values: LinkedDeque[int] = LinkedDeque()
    for value in range(N):
        values.append_right(value)
    return [values.pop_left() for _ in range(N)]


def bisect_sorted_insert() -> list[int]:
    """Maintain sorted order with ``bisect.insort``."""
    values: list[int] = []
    for value in range(N, 0, -1):
        bisect.insort(values, value)
    return values


def sorted_linked_insert() -> list[int]:
    """Maintain sorted order with ``SortedLinkedList``."""
    values: SortedLinkedList[int] = SortedLinkedList()
    for value in range(N, 0, -1):
        values.add(value)
    return values.to_list()


def set_membership() -> int:
    """Check membership with a hash set."""
    values = set(range(N))
    return sum(1 for value in range(N) if value in values)


def skip_list_membership() -> int:
    """Check membership with a skip list."""
    values: SkipList[int] = SkipList(range(N), seed=1)
    return sum(1 for value in range(N) if value in values)


def built_in_list_middle_insert() -> list[int]:
    """Insert repeatedly near the middle of a Python list."""
    values: list[int] = []
    for value in range(N):
        values.insert(len(values) // 2, value)
    return values


def unrolled_middle_insert() -> list[int]:
    """Insert repeatedly near the middle of an unrolled linked list."""
    values: UnrolledLinkedList[int] = UnrolledLinkedList(node_capacity=16)
    for value in range(N):
        values.insert(len(values) // 2, value)
    return values.to_list()


def dense_sparse_like_storage() -> list[list[int]]:
    """Store a sparse-looking grid densely."""
    grid = [[0 for _ in range(100)] for _ in range(100)]
    for index in range(0, 100, 10):
        grid[index][index] = index
    return grid


def linked_sparse_storage() -> list[tuple[int, int, int]]:
    """Store only non-zero sparse grid entries."""
    entries = [(index, index, index) for index in range(0, 100, 10)]
    matrix: SparseMatrixLinkedList[int] = SparseMatrixLinkedList.from_entries(
        100,
        100,
        entries,
    )
    return matrix.to_entries()


def main() -> None:
    """Run benchmark cases and print a compact table."""
    cases = [
        ("list append", built_in_list_append),
        ("LinkedList append", linked_list_append),
        ("collections.deque FIFO", collections_deque_queue),
        ("LinkedDeque FIFO", linked_deque_queue),
        ("bisect sorted insert", bisect_sorted_insert),
        ("SortedLinkedList insert", sorted_linked_insert),
        ("set membership", set_membership),
        ("SkipList membership", skip_list_membership),
        ("list middle insert", built_in_list_middle_insert),
        ("UnrolledLinkedList middle insert", unrolled_middle_insert),
        ("dense sparse-like storage", dense_sparse_like_storage),
        ("SparseMatrixLinkedList storage", linked_sparse_storage),
    ]

    print(f"{'case':35} median_ms")
    print("-" * 47)
    for name, func in cases:
        case_name, milliseconds = time_case(name, func)
        print(f"{case_name:35} {milliseconds:9.3f}")


if __name__ == "__main__":
    main()
