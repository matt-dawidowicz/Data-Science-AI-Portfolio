# Linked Structure Lab

[![CI](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Coverage 100%](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#testing)
[![Typed](https://img.shields.io/badge/typing-PEP%20561-informational.svg)](src/linked_list/py.typed)

Linked Structure Lab is an educational Python package for linked data
structures. It includes classic singly, doubly, circular, and sorted linked
lists, plus linked deques, skip lists, unrolled lists, multilevel lists,
positional lists, self-organizing lists, and sparse matrices.

This is a portfolio showcase, not a recommendation to replace Python's
production-ready built-ins. The point is to make implementation skill visible:
node design, pointer repair, invariants, type hints, documentation, examples,
benchmarks, CI, regression tests, and property-based tests are all part of the
project.

## Quick Start

From the portfolio repository root:

```powershell
cd Linked_List_Showcase
python -m pip install -e ".[dev]"
python -m pytest
```

Use the package with:

```python
from linked_list import LinkedList, LinkedDeque, SkipList

tasks = LinkedDeque(["ingest", "validate"])
tasks.append_right("publish")

ordered_ids = SkipList([42, 7, 19], seed=1)

playlist = LinkedList("doubly_circular")
playlist.extend(["intro", "main", "credits"])
playlist.rotate(1)

numbers = LinkedList([1, 2, 3])
doubly_numbers = LinkedList("doubly", [1, 2, 3])
```

If PyCharm cannot resolve `linked_list`, open this folder as the project root
or install it in the selected interpreter with `python -m pip install -e .`.
The distribution name is `linked-structure-lab`; the import package is
`linked_list`.

## Reviewer Map

| Structure | What it demonstrates | Real product or system analogy | Demo | Primary tests |
| --- | --- | --- | --- | --- |
| `LinkedList` | Pointer variants, circularity, mutation invariants | playlists, browser history, scheduler rings | [round_robin_scheduler.py](examples/round_robin_scheduler.py) | [test_linked_list.py](tests/test_linked_list.py) |
| `LinkedDeque` | Fast left/right operations with two-sided links | job queues, BFS frontiers, sliding windows | [job_queue.py](examples/job_queue.py) | [test_linked_deque.py](tests/test_linked_deque.py) |
| `SortedLinkedList` | APIs constrained by sorted-order invariants | ranked waitlists, timer queues, small priority views | [leaderboard.py](examples/leaderboard.py) | [test_sorted_linked_list.py](tests/test_sorted_linked_list.py) |
| `SkipList` | Probabilistic ordered-set search | leaderboard indexes, range lookup, sorted membership | [leaderboard.py](examples/leaderboard.py) | [test_skip_list.py](tests/test_skip_list.py) |
| `UnrolledLinkedList` | Chunked linked storage and block repair | text buffers, log viewers, packet batches | [text_buffer_blocks.py](examples/text_buffer_blocks.py) | [test_unrolled_linked_list.py](tests/test_unrolled_linked_list.py) |
| `MultilevelLinkedList` | Child links, hierarchy, flattening | file explorers, nested comments, document outlines | [document_outline.py](examples/document_outline.py) | [test_multilevel_linked_list.py](tests/test_multilevel_linked_list.py) |
| `PositionalLinkedList` | Stable handles to known nodes | editor cursors, playlist editors, kanban card moves | [text_cursor.py](examples/text_cursor.py) | [test_positional_linked_list.py](tests/test_positional_linked_list.py) |
| `SelfOrganizingLinkedList` | Adaptive search heuristics | command palettes, contact lists, help menus | [adaptive_command_palette.py](examples/adaptive_command_palette.py) | [test_self_organizing_linked_list.py](tests/test_self_organizing_linked_list.py) |
| `SparseMatrixLinkedList` | Linked row and column chains | recommenders, graph matrices, sparse feature matrices | [sparse_recommender.py](examples/sparse_recommender.py) | [test_sparse_matrix_linked_list.py](tests/test_sparse_matrix_linked_list.py) |

## Documentation

- [Portfolio showcase](docs/portfolio_showcase.md): what this project proves
  and where reviewers should look first.
- [Reviewer demo script](docs/demo_script.md): a short walkthrough for setup,
  checks, examples, and source-test pairs.
- [API reference](docs/api_reference.md): public containers and core methods.
- [Linked structures walkthrough](docs/linked_structures_walkthrough.md):
  beginner-friendly explanation of nodes, links, and invariants.
- [Design and edge cases](docs/design_and_edge_cases.md): implementation
  notes that used to make the README too large.
- [Real-world use cases](docs/real_world_use_cases.md): concrete product and
  system situations for each structure.
- [Package positioning](docs/package_positioning.md): why this package exists
  when Python already has excellent built-ins and scientific libraries.
- [Complexity guide](docs/complexity.md): time and space tradeoffs.
- [Benchmark results](docs/benchmark_results.md): current benchmark snapshot
  and interpretation.
- [Package readiness](docs/package_readiness.md): CI, coverage, typing, and
  packaging notes.

## What Is Included

- Four linked-list variants: singly, doubly, singly circular, and doubly
  circular.
- Specialized linked structures: sorted list, linked deque, skip list,
  unrolled list, multilevel list, positional list, self-organizing list, and
  sparse matrix.
- Python container behavior: iteration, reverse iteration where appropriate,
  indexing, slicing, membership, equality, readable displays, and copying.
- Mutations: append, prepend, insert, remove, remove-all, remove-at, pop,
  pop-front, replace, clear, reverse, rotate, sort, and merge where the
  operation fits the structure.
- Structure-specific behavior such as skip-list floor/ceiling, sparse matrix
  arithmetic, positional handles, multilevel flattening, adaptive search
  strategies, and unrolled block inspection.
- Mermaid visualization helpers for small linked structures.
- Examples, benchmarks, unit tests, property tests, type hints, and packaging
  metadata.

## Examples

Run a realistic multi-structure workflow:

```powershell
python examples/product_ops_demo.py
```

Other focused demos:

- `examples/job_queue.py`
- `examples/leaderboard.py`
- `examples/text_buffer_blocks.py`
- `examples/document_outline.py`
- `examples/text_cursor.py`
- `examples/adaptive_command_palette.py`
- `examples/sparse_recommender.py`

## Testing

The normal test suite can be run with either pytest or unittest:

```powershell
python -m pytest
python -m unittest discover -s tests -t . -v
```

Coverage is configured to require 100% over `src/linked_list`:

```powershell
python -m coverage run -m pytest
python -m coverage report
```

Developer checks:

```powershell
python -m ruff check .
python -m ruff format --check .
python -m mypy
```

Property-based tests use Hypothesis and are installed through the `dev` or
`test` extras. They compare linked structures with small Python reference
models across randomized operation sequences.

## Requirements

- Python 3.12 or newer.
- No runtime dependencies.
- Development extras for testing, typing, linting, coverage, and
  property-based tests.

## Project Layout

```text
Linked_List_Showcase/
  benchmarks/
  docs/
  examples/
  src/linked_list/
  tests/
  pyproject.toml
  README.md
```
