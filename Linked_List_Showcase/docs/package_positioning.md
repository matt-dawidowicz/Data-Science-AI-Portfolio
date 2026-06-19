# Package Positioning

## Why This Package Exists

Linked Structure Lab is a portfolio and learning package. It is meant to show
that the author can design, document, test, type, package, and maintain a
non-trivial Python codebase.

The package is useful when someone wants to:

- Read linked data structure implementations directly.
- Learn how pointer repair changes across singly, doubly, and circular lists.
- Compare several linked structures through one consistent API.
- See examples, benchmarks, unit tests, property tests, and type hints in one
  compact project.
- Review code quality for a portfolio without needing a production service,
  cloud account, or external data source.

## Why Use This Instead Of Another Python Package

Use this package when the goal is education, demonstration, or code review.
Most existing Python packages optimize for production performance, broad
feature support, or scientific computing. This package optimizes for
readability and inspectability.

What this package offers:

- The implementation is visible and intentionally documented.
- Multiple linked structures live in one installable package.
- Tests include normal unit cases, edge cases, and Hypothesis property tests.
- The examples connect abstract structures to real product workflows.
- The docs explain both how to use the structures and why the implementation
  choices matter.

## When Not To Use It

Do not use this package as a drop-in replacement for mature production tools.

Prefer:

- `list` for most general Python sequences.
- `collections.deque` for production double-ended queues.
- `heapq`, `bisect`, a database index, or a sorted-container library for
  production ordered data.
- SciPy, NumPy, pandas, or a database/vector store for production sparse or
  numerical workloads.
- A real tree, graph, editor-buffer, or search-index library for specialized
  application domains.

The best use of this package is to show understanding. It is a readable lab
for linked structures, not a claim that hand-written linked containers beat
the highly optimized tools already available in Python.

## Portfolio Framing

For a portfolio reviewer, the strongest signals are:

- The project is installable from `pyproject.toml`.
- The code uses a `src/` layout and typed public APIs.
- The package has no runtime dependencies.
- The test suite covers normal behavior, edge behavior, and randomized
  operation sequences.
- The examples are grounded in recognizable product and systems problems.
- The README stays short and points to deeper docs instead of hiding the
  important material in one oversized file.
