# Linked Structure Lab

[![CI](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![Coverage 100%](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](#testing)
[![Typed](https://img.shields.io/badge/typing-PEP%20561-informational.svg)](src/linked_list/py.typed)

Linked Structure Lab is an engineering-fundamentals and software-verification
project built around linked data structures. It began as an intentionally
thorough response to classic linked-list interview preparation, then expanded
into a package for testing structural invariants, mutation behavior, API design,
and verification strategy.

The project is not meant to argue that hand-writing linked structures is a
modern production requirement. Python already provides better production-ready
containers for normal application work. The useful signal here is how behavior
is specified and checked: pointer repair, circularity, stale-handle detection,
randomized operation sequences, property-based tests, typing, benchmarks, CI,
and reproducible examples.

Development used AI coding assistance. The project should therefore be read as
an example of technical ownership rather than a claim of manual authorship of
every line. Generated or suggested implementations still had to satisfy explicit
invariants, reference-model comparisons, regression tests, and reviewer-visible
behavior.

## What This Project Demonstrates

- Defining structural invariants before trusting implementation details.
- Testing hidden state as well as returned values.
- Comparing custom structures against simpler trusted reference models.
- Property-based and randomized testing across mutation sequences.
- Typed Python package design with a `src/` layout and PEP 561 marker.
- CI, linting, formatting, static typing, coverage, examples, and benchmarks.
- Explaining tradeoffs and failure modes instead of treating passing tests as
  sufficient evidence of correctness.

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

| Structure | Verification focus | Real product or system analogy | Demo | Primary tests |
| --- | --- | --- | --- | --- |
| `LinkedList` | Pointer variants, circularity, mutation invariants | playlists, browser history, scheduler rings | [round_robin_scheduler.py](examples/round_robin_scheduler.py) | [test_linked_list.py](tests/test_linked_list.py) |
| `LinkedDeque` | Fast left/right operations with two-sided links | job queues, BFS frontiers, sliding windows | [job_queue.py](examples/job_queue.py) | [test_linked_deque.py](tests/test_linked_deque.py) |
| `SortedLinkedList` | Maintaining sorted-order invariants through mutation | ranked waitlists, timer queues, small priority views | [leaderboard.py](examples/leaderboard.py) | [test_sorted_linked_list.py](tests/test_sorted_linked_list.py) |
| `SkipList` | Probabilistic level invariants and ordered-set behavior | leaderboard indexes, range lookup, sorted membership | [leaderboard.py](examples/leaderboard.py) | [test_skip_list.py](tests/test_skip_list.py) |
| `UnrolledLinkedList` | Block occupancy and repair across linked chunks | text buffers, log viewers, packet batches | [text_buffer_blocks.py](examples/text_buffer_blocks.py) | [test_unrolled_linked_list.py](tests/test_unrolled_linked_list.py) |
| `MultilevelLinkedList` | Child-link traversal and flattening invariants | file explorers, nested comments, document outlines | [document_outline.py](examples/document_outline.py) | [test_multilevel_linked_list.py](tests/test_multilevel_linked_list.py) |
| `PositionalLinkedList` | Stable handles, stale positions, foreign-position rejection | editor cursors, playlist editors, kanban card moves | [text_cursor.py](examples/text_cursor.py) | [test_positional_linked_list.py](tests/test_positional_linked_list.py) |
| `SelfOrganizingLinkedList` | Stateful access heuristics and behavior under repeated lookups | command palettes, contact lists, help menus | [adaptive_command_palette.py](examples/adaptive_command_palette.py) | [test_self_organizing_linked_list.py](tests/test_self_organizing_linked_list.py) |
| `SparseMatrixLinkedList` | One node participating consistently in row and column chains | recommenders, graph matrices, sparse feature matrices | [sparse_recommender.py](examples/sparse_recommender.py) | [test_sparse_matrix_linked_list.py](tests/test_sparse_matrix_linked_list.py) |

## Verification Strategy

The strongest part of the project is the test model, not the number of
containers implemented.

Tests check invariants such as:

- `head`, `tail`, and `_size` remain mutually consistent;
- forward and backward links agree after mutation;
- circular variants restore wraparound links after inserts, removals, reverse,
  and rotation;
- removed nodes do not retain invalid membership in the old structure;
- positional handles are rejected after deletion or clearing;
- skip-list levels remain ordered and consistent with bottom-level values;
- sparse-matrix row and column chains refer to the same node objects;
- randomized operations continue to match simpler Python reference models.

This matters particularly in AI-assisted development: plausible-looking code is
not evidence of correctness. The verification target has to be explicit enough
that implementation mistakes can be detected independently of who or what
produced the first draft.

## Documentation

- [Verification-focused portfolio summary](docs/portfolio_showcase.md)
- [Reviewer demo script](docs/demo_script.md)
- [API reference](docs/api_reference.md)
- [Linked structures walkthrough](docs/linked_structures_walkthrough.md)
- [Design and edge cases](docs/design_and_edge_cases.md)
- [Real-world use cases](docs/real_world_use_cases.md)
- [Complexity guide](docs/complexity.md)
- [Benchmark results](docs/benchmark_results.md)
- [Package readiness](docs/package_readiness.md)

## What Is Included

- Four linked-list variants: singly, doubly, singly circular, and doubly
  circular.
- Specialized structures: sorted list, linked deque, skip list, unrolled list,
  multilevel list, positional list, self-organizing list, and sparse matrix.
- Python container behavior: iteration, reverse iteration where appropriate,
  indexing, slicing, membership, equality, readable displays, and copying.
- Mutations: append, prepend, insert, remove, remove-all, remove-at, pop,
  pop-front, replace, clear, reverse, rotate, sort, and merge where appropriate.
- Structure-specific behavior such as skip-list floor/ceiling, sparse-matrix
  arithmetic, positional handles, multilevel flattening, adaptive-search
  strategies, and unrolled block inspection.
- Mermaid visualization helpers for small linked structures.
- Examples, benchmarks, unit tests, property tests, type hints, and packaging
  metadata.

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
- Development extras for testing, typing, linting, coverage, and property-based
  tests.

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

## Status

Feature expansion is intentionally deprioritized. The project is complete as an
engineering-fundamentals lab; future portfolio effort should go toward applied
AI, data science, evaluation, benchmarking, and production-oriented systems
rather than adding more linked-structure variants.
