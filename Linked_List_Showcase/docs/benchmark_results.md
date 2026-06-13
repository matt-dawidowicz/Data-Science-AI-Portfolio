# Benchmark Results

The benchmark script is a teaching aid. It compares the educational linked
structures with familiar Python containers so readers can see tradeoffs in a
concrete way.

Run it from the package directory:

```bash
python benchmarks/benchmark_structures.py
```

## Current Snapshot

Example output from the current benchmark script:

```text
case                                median_ms
-----------------------------------------------
list append                             0.047
LinkedList append                       0.518
collections.deque FIFO                  0.068
LinkedDeque FIFO                        0.685
bisect sorted insert                    0.337
SortedLinkedList insert                 0.594
set membership                          0.074
SkipList membership                     5.881
list middle insert                      0.184
UnrolledLinkedList middle insert        4.612
dense sparse-like storage               0.088
SparseMatrixLinkedList storage          0.006
```

Timings vary by machine, Python version, and background load. Treat the values
as directional, not as a formal performance claim.

## How To Read The Numbers

| Case | What the result shows |
| --- | --- |
| `list append` vs `LinkedList append` | Python's built-in `list` is highly optimized for appending. The linked version is valuable because its node allocation and pointer repair are visible. |
| `collections.deque FIFO` vs `LinkedDeque FIFO` | `collections.deque` is the production-ready tool. `LinkedDeque` demonstrates how two-ended queue behavior can be built from linked nodes. |
| `bisect sorted insert` vs `SortedLinkedList insert` | Python lists plus `bisect` are compact and optimized. The sorted linked list makes the ordering invariant explicit across every mutation method. |
| `set membership` vs `SkipList membership` | Hash lookup is faster for exact membership. The skip list is useful because it supports ordered behavior such as `floor` and `ceiling`. |
| `list middle insert` vs `UnrolledLinkedList middle insert` | Built-in lists are optimized in C. The unrolled list demonstrates block splitting, merging, and the compromise between nodes and contiguous chunks. |
| dense sparse-like storage vs `SparseMatrixLinkedList storage` | Sparse storage can avoid storing explicit zeros when the matrix is mostly empty. The linked sparse matrix makes row and column chains inspectable. |

## Portfolio Interpretation

The important lesson is not that linked structures beat Python's built-ins.
Usually they do not. The portfolio value is different:

- The data structures are implemented directly.
- The tradeoffs are measurable.
- The benchmark script is reproducible.
- The documentation explains when optimized built-ins are the better tool.
- The sparse-matrix case shows that representation choice can matter when
  the data is mostly empty.

This is the honest positioning for a portfolio project: strong implementation
and explanation, not exaggerated performance claims.

## Reproducing A Fresh Snapshot

Use these commands:

```bash
python -m pip install -e ".[dev]"
python benchmarks/benchmark_structures.py
```

When sharing benchmark results, include the Python version and machine
context if precision matters. For this repository, the benchmark is mainly
evidence that the project includes measurement and tradeoff analysis.
