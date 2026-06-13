# Linked Structure Lab

[![CI](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/matt-dawidowicz/Data-Science-AI-Portfolio/actions/workflows/ci.yml)

Linked Structure Lab is an educational Python package with singly, doubly,
singly circular, and doubly circular linked-list variants, plus sorted
linked-list, linked-deque, skip-list, unrolled-list, multilevel-list,
positional-list, self-organizing-list, and sparse-matrix implementations.

This folder is intentionally self-contained so the repository root can remain
a portfolio workspace for additional projects.

## Project Layout

```text
benchmarks/
  benchmark_structures.py
docs/
  api_reference.md
  complexity.md
  linked_structures_walkthrough.md
  package_readiness.md
examples/
  adaptive_command_palette.py
  document_outline.py
  job_queue.py
  leaderboard.py
  lru_cache.py
  round_robin_scheduler.py
  sparse_recommender.py
  text_buffer_blocks.py
  text_cursor.py
src/
  linked_list/
    __init__.py
    deque.py
    multilevel_list.py
    positional_list.py
    py.typed
    self_organizing_list.py
    skip_list.py
    sorted_list.py
    sparse_matrix.py
    unrolled_list.py
    visualize.py
    list_functions/
      access.py
      base.py
      functional.py
      iteration.py
      linked_list.py
      mutation.py
      sort_merge.py
      utility.py
    nodes/
      base_node.py
      doubly.py
      mixins.py
      singly.py
tests/
  test_linked_deque.py
  test_linked_list.py
  test_multilevel_linked_list.py
  test_positional_linked_list.py
  test_property_invariants.py
  test_self_organizing_linked_list.py
  test_skip_list.py
  test_sorted_linked_list.py
  test_sparse_matrix_linked_list.py
  test_typing_and_visualization.py
  test_unrolled_linked_list.py
CHANGELOG.md
pyproject.toml
README.md
requirements-dev.txt
```

## Features

- Singly and doubly linked lists
- Singly circular and doubly circular linked lists
- Sorted linked lists that preserve ascending order after mutation
- Linked deque backed by a doubly linked list
- Skip list ordered set with probabilistic multi-level links
- Unrolled linked list with fixed-capacity value blocks
- Multilevel linked list with `next` and `child` pointers
- Positional linked list with stable validated `Position` handles
- Self-organizing linked list with adaptive search strategies
- Sparse matrix backed by linked row and column chains
- Append, prepend, insert, remove, remove-at, pop, and pop-front operations
- Deque operations: `append_left`, `append_right`, `insert`, `pop_left`,
  `pop_right`, `peek_left`, `peek_right`, `extend`, `extend_left`, `remove`,
  `remove_all`, `replace`, `reverse`, and `rotate`
- Python-style deque aliases: `append`, `appendleft`, `pop`, `popleft`, `peek`, and `extendleft`
- Indexing, slicing, membership checks, equality, and iteration
- Reverse, rotate, sort, merge, and sorted insertion
- Functional helpers: `map`, `filter`, and `reduce`
- Search and read helpers: `get`, `index`, `find`, and `count`
- Utility helpers: `is_empty`, `to_list`, `from_list`, `copy`, `deep_copy`, `remove_all`, and `clear`
- Hierarchy helpers for multilevel lists: child insertion, child detaching,
  nested snapshots, path lookup, depth-first and breadth-first flattening
- Block-layout helpers for unrolled lists, including `to_blocks()` for
  inspecting chunk boundaries
- Position-aware helpers: `positions`, `add_before`, `add_after`,
  `move_before`, `move_after`, `swap`, and stale-position validation
- Adaptive search strategies: move-to-front, transpose, frequency-count, and
  no-reorder counting
- Sparse matrix helpers: dense conversion, row/column iteration, matrix
  arithmetic, transposition, vector multiplication, and matrix multiplication
- Mermaid visualization helper for small structure diagrams
- Public generic aliases such as `LinkedDeque[int]` and `SkipList[str]`
- Real-world examples for schedulers, job queues, leaderboards, text buffers,
  nested outlines, cache eviction, command palettes, and sparse recommenders
- Standard-library benchmark runner for comparing educational structures with
  built-in containers
- PEP 561 typed-package marker and mypy configuration for static type checks
- Ruff linting and format-check configuration
- Pytest, optional Hypothesis property tests, and coverage configuration
- Local pre-commit hooks for linting, type checking, and tests
- GitHub Actions CI for Python 3.10, 3.11, and 3.12
- Installable package metadata in `pyproject.toml`
- API reference in `docs/api_reference.md`
- Dedicated complexity guide in `docs/complexity.md`
- Beginner-friendly code walkthrough in `docs/linked_structures_walkthrough.md`
- Package readiness guide in `docs/package_readiness.md`

## Install

Install the package from a local checkout:

```powershell
python -m pip install -e .
```

Install development tools, including optional property-based tests:

```powershell
python -m pip install -e ".[dev]"
```

The import package is `linked_list`:

```python
from linked_list import LinkedDeque, SkipList, SparseMatrixLinkedList

jobs: LinkedDeque[str] = LinkedDeque(["ingest", "transform", "load"])
scores: SkipList[int] = SkipList([100, 200, 150])
ratings: SparseMatrixLinkedList[float] = SparseMatrixLinkedList.from_entries(
    3,
    3,
    [(0, 2, 4.5)],
)
```

## Examples And Benchmarks

Run real-world examples from this package directory:

```powershell
python examples/job_queue.py
python examples/leaderboard.py
python examples/sparse_recommender.py
```

Run the lightweight benchmark comparison:

```powershell
python benchmarks/benchmark_structures.py
```

The benchmark is meant to teach tradeoffs. It is not a claim that these
educational structures beat Python's optimized built-ins.

## Visualization

Small structures can be exported as Mermaid diagrams:

```python
from linked_list import LinkedDeque, to_mermaid

queue = LinkedDeque(["ingest", "transform", "load"])
print(to_mermaid(queue, title="ETL queue"))
```

## Project Explanation

This project is meant to show that I understand linked data structures from the
inside out, not just how to call a built-in list or deque. I implemented the
core linked-list behavior myself, then separated the code into focused modules
so each part of the data structure is easier to explain, test, and maintain.

At the highest level, the project has nine public containers:

- `LinkedList`, which supports singly linked, doubly linked, singly circular,
  and doubly circular list variants.
- `SortedLinkedList`, which uses the same list variants but keeps values in
  ascending order at all times.
- `LinkedDeque`, which is a double-ended queue built on top of doubly linked
  nodes.
- `SkipList`, which is a probabilistic ordered set with average logarithmic
  search, insertion, and removal.
- `UnrolledLinkedList`, which stores multiple values in each linked node to
  demonstrate chunked linked storage.
- `MultilevelLinkedList`, which adds child links so nested structures can be
  traversed, flattened, copied, and mutated.
- `PositionalLinkedList`, which exposes stable position handles for direct
  insert, delete, move, and replace operations around known nodes.
- `SelfOrganizingLinkedList`, which adapts order after successful searches
  using move-to-front, transpose, frequency-count, or count-only strategies.
- `SparseMatrixLinkedList`, which stores non-zero matrix cells in linked row
  and column chains for sparse data-structure practice.

## Practical Use Cases

This package is most useful when you want to study, teach, inspect, or compare
linked structures. Each container emphasizes a different situation:

- `LinkedList("singly")`: forward-only chains, simple traversal, and the
  tradeoff of low node overhead versus slower tail-side deletion.
- `LinkedList("doubly")`: bidirectional traversal, easier local deletion, and
  cases where reverse iteration matters.
- `LinkedList("singly_circular")`: round-robin traversal, cyclic scheduling,
  and teaching why circular structures need bounded iteration.
- `LinkedList("doubly_circular")`: cyclic navigation in both directions, such
  as carousel-style movement or ring-buffer demonstrations.
- `LinkedDeque`: queue, stack, and double-ended workflows where both ends are
  the natural mutation points.
- `SortedLinkedList`: small ordered streams where preserving the sorted
  invariant is more important than arbitrary insertion positions.
- `SkipList`: ordered-set experiments, nearest-neighbor lookups with
  `floor()` and `ceiling()`, and probabilistic data-structure lessons.
- `UnrolledLinkedList`: teaching block splitting, block merging, and the
  compromise between linked nodes and contiguous value chunks.
- `MultilevelLinkedList`: outlines, menu trees, nested task lists, and
  flattening depth-first or breadth-first hierarchies.
- `PositionalLinkedList`: editor-like or playlist-like workflows where code
  keeps a handle to a known location and mutates around that handle.
- `SelfOrganizingLinkedList`: skewed search workloads, adaptive search
  demonstrations, and comparing move-to-front, transpose, and frequency
  strategies.
- `SparseMatrixLinkedList`: mostly-zero grids, sparse matrix teaching, and
  showing how one stored cell can belong to both row and column chains.

### Real-World Products, Systems, and Occasions

These examples describe where the same data-structure ideas appear in real
software. In production Python, you would often use the standard library or a
specialized package for speed, but the linked structure explains the design.

- `LinkedList("singly")`: memory free lists in allocators, simple packet
  chains in networking code, compiler token streams, and one-way processing
  pipelines where data naturally moves forward and old items are discarded.
- `LinkedList("doubly")`: browser history, media playlists, photo viewers,
  undo/redo stacks, LRU cache order tracking, and any UI where users move
  backward and forward through neighboring items.
- `LinkedList("singly_circular")`: round-robin CPU scheduling, rotating
  worker selection in service pools, multiplayer turn order, slideshow loops,
  and polling devices or sensors repeatedly without resetting to the start.
- `LinkedList("doubly_circular")`: carousel controls, circular media queues,
  previous/next navigation in gallery apps, board-game turn trackers, and
  ring menus where both directions should wrap around.
- `LinkedDeque`: job queues, breadth-first search in route planners or web
  crawlers, sliding-window analytics, task schedulers, message buffers, and
  producer-consumer systems that add and remove work at both ends.
- `SortedLinkedList`: small ordered event timelines, timer queues, ranked
  waiting rooms, simple priority queues, and audit logs that should stay
  sorted as entries arrive.
- `SkipList`: leaderboard/ranking services, ordered indexes, nearest-neighbor
  lookup, autocomplete ranges, time-series windows, and Redis-style sorted
  sets where fast ordered search matters.
- `UnrolledLinkedList`: text-buffer storage, log viewers, packet batching,
  cache-friendlier queues, and applications that benefit from grouping several
  neighboring values while still splitting and merging chunks.
- `MultilevelLinkedList`: file explorers, nested comments, menu systems,
  org charts, document outlines, course modules, and task managers where each
  item may contain another list of child items.
- `PositionalLinkedList`: text editor cursors, collaborative document ranges,
  playlist editors, timeline editors, kanban card movement, and drag-and-drop
  interfaces that keep handles to specific items.
- `SelfOrganizingLinkedList`: command palettes, contact lists, autocomplete
  candidates, small embedded lookup tables, and help menus where recently or
  frequently selected items should become easier to find.
- `SparseMatrixLinkedList`: recommender-system ratings, graph adjacency
  matrices, search-index term matrices, feature matrices in machine learning,
  scientific simulations, and any mostly-empty grid where storing every zero
  would waste memory.

## Why Use This Package Instead Of Another Python Package

Use this package when the goal is learning, teaching, portfolio review, or
experimentation with linked data structures. It gives you:

- Transparent source code instead of opaque optimized internals.
- Many linked-structure variants in one small package.
- Strong type hints throughout the implementation and tests.
- Extensive regression tests that check internal links, not only output values.
- Documentation that explains invariants, tradeoffs, and failure modes.
- No third-party runtime dependencies.

Use existing Python tools when you need production performance or mature
ecosystem integration:

- Use built-in `list` for most index-heavy sequence work.
- Use `collections.deque` for production double-ended queues.
- Use `dict` and `set` for hash-based lookup.
- Use `bisect` or a maintained sorted-collection library for production sorted
  sequences.
- Use NumPy, SciPy sparse matrices, pandas, or domain-specific graph libraries
  when you need optimized numerical or graph workloads.

In short: this package is for understanding and demonstrating linked
structures clearly. Existing optimized packages are usually the right choice
when runtime speed, memory efficiency, and ecosystem support matter most.

The linked list and deque structures are related, but they are not the same
thing. A doubly linked list is a general-purpose sequence where operations
like indexing, insertion, removal, sorting, merging, and traversal matter. A
deque is focused on efficient access at both ends. With `LinkedDeque`, the
main design goal is to make left-side and right-side operations direct and
predictable:
`append_left`, `append_right`, `pop_left`, and `pop_right` all work by updating
only the head, tail, and neighboring links.

## How the LinkedList Is Organized

The `LinkedList` class is assembled from mixins in `linked_list/list_functions`.
I used this structure so each behavior group has a clear purpose:

- `base.py` stores shared list state such as `head`, `tail`, `_size`,
  `_list_type`, and `_is_circular`.
- `access.py` handles indexing, slicing, containment checks, equality,
  string conversion, and `nth_from_end`.
- `iteration.py` handles forward iteration for every list type and reverse
  iteration for doubly linked lists.
- `mutation.py` handles operations that change the list, including append,
  prepend, insert, remove, pop, rotate, reverse, merge, extend, and duplicate
  removal.
- `sort_merge.py` implements merge sort helpers for linked lists.
- `functional.py` adds `map`, `filter`, and `reduce`.
- `utility.py` adds conversion, copying, counting, and clearing helpers.

This organization makes the class easier to reason about because each file has
one main responsibility. Instead of one large class containing every operation,
the final `LinkedList` class combines smaller behavior groups into one public
type.

## Node Design

The node classes live in `linked_list/nodes`. They are the building blocks for
all list variants:

- `BaseNode` stores the data value.
- `NextMixin` adds a `next` pointer.
- `PrevMixin` adds a `prev` pointer.
- `CircularMixin` makes missing links point back to the node itself.
- `SinglyLinkedNode` has only a forward link.
- `DoublyLinkedNode` has both forward and backward links.
- `SinglyCircularLinkedNode` starts with its `next` pointer linked to itself.
- `DoublyCircularLinkedNode` starts with both `next` and `prev` linked to
  itself.

This setup avoids repeating the same pointer fields in every node class. It
also makes the differences between singly, doubly, and circular structures
visible in the code.

## Circular List Handling

Circular lists need extra care because there is no natural `None` endpoint
during traversal. To prevent infinite loops, operations that walk a circular
list either use the list size as a boundary or stop when they return to the
starting node.

When a mutation changes a circular list, the implementation restores the
head-tail connection afterward:

- For singly circular lists, `tail.next` points back to `head`.
- For doubly circular lists, `tail.next` points to `head` and `head.prev`
  points back to `tail`.

This is especially important in operations like `remove`, `pop`, `pop_front`,
`reverse`, `merge`, `sort`, `remove_duplicates`, and `clear`, because those
operations temporarily move or detach nodes.

## SortedLinkedList Design

`SortedLinkedList` is built as a subclass of `LinkedList`. It does not need a
new node type because the pointer shapes are the same. What changes is the
rule the container must protect: every visible value must stay in ascending
order.

That invariant affects the API in a few important ways:

- `add(value)` is the clearest insertion method because it means "put this
  value where it belongs."
- `append(value)` and `prepend(value)` still exist, but they behave like
  `add(value)` so they cannot force a value onto the wrong end.
- `insert(index, value)` is allowed only when the requested position keeps the
  list sorted.
- `replace(old, new, count=None)` may move values to new positions, so it
  computes the updated values first and rebuilds only after sorting succeeds.
- `merge(other)` copies values from another linked list and re-sorts this list
  without stealing the other list's nodes.
- `remove_duplicates()` removes adjacent duplicates without using a hash set,
  which means it also works for comparable but unhashable values.
- `reverse()` and non-trivial `rotate(k)` are rejected because they would turn
  a sorted list into an unsorted list.

This is the main teaching value of the class: a data structure is not only its
nodes and pointers. It is also the set of promises every method must preserve.

## LinkedDeque Design

`LinkedDeque` is backed by `DoublyLinkedNode` objects. It keeps direct
references to both ends of the structure:

- `head` is the left side of the deque.
- `tail` is the right side of the deque.
- `_size` tracks the number of stored values.

That design makes end operations straightforward:

- `append_left` creates a new node before the current head.
- `append_right` creates a new node after the current tail.
- `pop_left` removes the head node and repairs the new head's `prev` link.
- `pop_right` removes the tail node and repairs the new tail's `next` link.
- `peek_left` and `peek_right` read values without mutating the deque.
- `clear` detaches every node so old node references do not keep stale links.

The deque also includes Python-style aliases:

- `append` maps to `append_right`.
- `appendleft` maps to `append_left`.
- `pop` maps to `pop_right`.
- `peek` maps to `peek_right`.
- `popleft` maps to `pop_left`.
- `extendleft` maps to `extend_left`.

These aliases make `LinkedDeque` feel familiar to anyone who has used
`collections.deque`, while still keeping the explicit left/right method names.

## SkipList Design

`SkipList` is an ordered set built from layered forward links. The bottom level
contains every value in sorted order. Higher levels contain random shortcuts,
so searches can skip across ranges of nodes instead of walking every value.

The implementation exposes practical ordered-set operations:

- `add(value)` inserts a comparable value and returns whether it was new.
- `extend(iterable)` and `update(iterable)` add many values atomically and
  return the number of new insertions.
- `remove(value)` and `discard(value)` remove a value and return whether it
  existed.
- `find(value)` returns the stored matching value or `None`.
- `floor(value)` returns the greatest stored value less than or equal to the
  requested value.
- `ceiling(value)` returns the smallest stored value greater than or equal to
  the requested value.
- `first()` and `last()` read the smallest and largest values.
- `pop_first()` and `pop_last()` remove the smallest and largest values.

The class accepts `max_level`, `probability`, and `seed` parameters. That keeps
the public container simple while making tests deterministic and making the
probabilistic design visible for learning purposes.

## UnrolledLinkedList Design

`UnrolledLinkedList` is a sequence container where each linked node stores a
small Python list of values instead of only one value. The `node_capacity`
setting controls the maximum block size.

This structure is useful because it shows a practical linked-list tradeoff:
fewer node objects and fewer pointer hops at the cost of small in-node array
operations. It still has linked `head` and `tail` block nodes, but values are
grouped into chunks:

- `append(value)` and `prepend(value)` add values at the ends.
- `insert(index, value)` inserts by normal sequence index and splits a full
  block when needed.
- `remove`, `remove_at`, `pop`, and `pop_front` remove values and then merge
  or borrow from neighboring blocks when a block becomes too sparse.
- `to_blocks()` exposes a snapshot of the block layout for debugging and
  teaching.
- `sort`, `reverse`, `rotate`, `remove_duplicates`, `map`, `filter`, and
  `reduce` give it the same practical sequence surface as the other containers.

The class is intentionally still a linked structure. It is not trying to beat
Python's built-in `list`; it is meant to make block splitting, block merging,
and chunked node storage easy to inspect.

## MultilevelLinkedList Design

`MultilevelLinkedList` stores a top-level sibling chain through `next` links,
and each node may also point to a child chain through `child`. Public iteration
is depth-first, so `len(multilevel)`, indexing, `to_list()`, and membership
checks see every reachable node.

The hierarchy-specific API keeps nested behavior explicit:

- `append_child(parent, value)`, `prepend_child(parent, value)`, and
  `extend_child(parent, iterable)` add child nodes below a parent node.
- `child_values(parent)` returns only a parent's direct children.
- `detach_children(parent)` moves a child chain into a new
  `MultilevelLinkedList`.
- `from_nested()` builds a hierarchy from values and `(value, children)` pairs.
- `to_nested_list()` returns the hierarchy in the same nested shape.
- `path_to(value)` returns sibling indexes from the top level to a matching
  value.
- `flatten(order="depth_first")` or `flatten(order="breadth_first")` rewires
  the existing nodes into one top-level chain.
- `flattened(order)` returns a new flat list without mutating the original.

Some sequence-style operations intentionally flatten the hierarchy. For
example, `sort`, `rotate`, `filter`, and `remove_duplicates` produce flat
top-level lists because their natural meaning is sequence-wide rather than
subtree-specific. Other operations, such as `copy`, `deep_copy`, `map`,
`reverse`, and child mutation helpers, preserve the nested shape.

## PositionalLinkedList Design

`PositionalLinkedList` is a doubly linked sequence that returns stable
`Position` objects for nodes. That mirrors the textbook positional-list API:
when client code already has a location, it can insert, delete, move, swap, or
replace around that location without searching by value or numeric index.

The implementation validates every position before mutation:

- Positions are tied to exactly one owning list.
- Deleting a position invalidates that handle.
- Clearing the list invalidates every existing handle.
- Moving, reversing, rotating, and sorting relink existing nodes while keeping
  valid position handles attached to their original values.
- Foreign positions from another list are rejected before any links change.

This is useful for teaching the difference between "a value at an index" and
"a stable handle to a node." It also highlights a common linked-list strength:
once a location is known, local insertion and deletion can be direct.

## SelfOrganizingLinkedList Design

`SelfOrganizingLinkedList` is a sequence that adapts after successful access.
Each node stores an access count, and `find`, `search`, and `access` update
the node according to the selected strategy:

- `move_to_front` moves the accessed node directly to the head.
- `transpose` swaps the accessed node one step toward the head.
- `frequency_count` keeps more frequently accessed nodes earlier.
- `none` records access counts without changing order.

The class still supports regular sequence operations such as indexing,
insertion, removal, replacement, sorting, rotation, copying, mapping,
filtering, and reducing. Membership checks and static reads do not reorganize
the list, which keeps adaptive behavior intentional and testable.

## SparseMatrixLinkedList Design

`SparseMatrixLinkedList` stores only non-zero cells. Each stored cell belongs
to two linked chains at the same time:

- A row chain through `right` pointers, sorted by column.
- A column chain through `down` pointers, sorted by row.

That dual-link representation makes it easy to inspect sparse matrix
invariants directly. Row-major iteration, row lookups, column lookups, dense
conversion, transposition, addition, subtraction, scalar multiplication,
matrix-vector multiplication, and matrix multiplication all operate on the
stored entries rather than every dense cell when possible.

Cells equal to the configured `zero` value are pruned instead of stored. This
keeps the data structure sparse after construction, assignment, arithmetic,
mapping, and explicit cleanup.

## Feature Reference

The package now exposes enough behavior to use these structures as practical
teaching containers, not only as minimal linked-list examples.

For detailed Big-O notes, see `docs/complexity.md`. That guide breaks down
time and space costs for `LinkedList`, `SortedLinkedList`, `LinkedDeque`,
`SkipList`, `UnrolledLinkedList`, `MultilevelLinkedList`,
`PositionalLinkedList`, `SelfOrganizingLinkedList`, `SparseMatrixLinkedList`,
node storage, circular-list behavior, and the tradeoffs behind snapshot-based
operations.

For a reading guide aimed at someone who has never seen the code before, see
`docs/linked_structures_walkthrough.md`. It explains the node model, pointer
invariants, each container's core tradeoff, and how to debug linked-structure
bugs by hand.

### LinkedList API

`LinkedList` supports sequence-style reading:

- `len(linked_list)` returns the number of stored values.
- `bool(linked_list)` is `False` when the list is empty.
- `is_empty()` is an explicit empty-state helper.
- `linked_list[index]` returns a value by positive or negative index.
- `linked_list[start:stop:step]` returns a new linked list of the same type.
- `get(index, default=None)` returns a fallback instead of raising
  `IndexError`.
- `peek_front()` reads the head value without removing it.
- `peek_back()` reads the tail value without removing it.
- `index(value, start=0, stop=None)` returns the first matching index.
- `find(value, start=0, stop=None)` returns the first matching index or
  `None`.
- `value in linked_list` checks membership.

It also supports mutation and algorithms:

- `append(value)` adds a value at the tail.
- `prepend(value)` adds a value at the head.
- `insert(index, value)` inserts at a specific position.
- `remove(value)` removes the first matching value and returns whether it
  found one.
- `remove_all(value)` removes every matching value and returns the count.
- `remove_at(index)` removes by position and returns the removed value.
- `replace(old, new, count=None)` changes matching values and returns the
  number replaced.
- `pop()` removes and returns the tail value.
- `pop_front()` removes and returns the head value.
- `reverse()` reverses the list in place.
- `rotate(k)` rotates right for positive `k` and left for negative `k`.
- `sort()` sorts the list in place using merge sort.
- `insert_sorted(value)` inserts into a list that is already sorted.
- `merge(other)` merges another sorted linked list of the same type.
- `remove_duplicates()` keeps the first copy of each value, including
  comparable unhashable values.
- `extend(iterable)` appends many values using bounded list iteration.
- `clear()` removes all nodes and resets the list.

For conversion and copying:

- `to_list()` converts the linked list into a Python list.
- `from_list(values, list_type)` builds a linked list from a Python list.
- `copy()` creates a shallow copy.
- `deep_copy()` recursively copies the stored values too.

### SortedLinkedList API

`SortedLinkedList` supports the same linked-list variants as `LinkedList`:

- `SortedLinkedList([3, 1, 2])` builds a sorted singly linked list.
- `SortedLinkedList("doubly", [3, 1, 2])` selects a list type and sorts the
  initial values.
- `SortedLinkedList.from_list(values, list_type)` builds a sorted list from a
  Python list.

It keeps the normal read API:

- `len(sorted_list)`, `bool(sorted_list)`, and `is_empty()` work the same way
  as they do on `LinkedList`.
- Indexing, slicing, `get`, `peek_front`, `peek_back`, `index`, `find`,
  `count`, containment checks, iteration, and reverse iteration for doubly
  linked variants are supported.
- Slices return another `SortedLinkedList`, so the selected values are sorted
  in the returned container.

It also supports sorted-safe mutation:

- `add(value)` inserts a value at its sorted position.
- `append(value)` and `prepend(value)` route to `add(value)`.
- `insert(index, value)` inserts at a specific position only if the neighbors
  still remain sorted around the new value.
- `sorted_list[index] = value` is allowed only when the replacement keeps the
  list sorted.
- `extend(iterable)` adds many values and rebuilds the list in sorted order.
- `replace(old, new, count=None)` replaces values and re-sorts afterward.
- `merge(other)` copies values from another linked list of the same list type.
- `remove`, `remove_all`, `remove_at`, `pop`, `pop_front`, `clear`,
  `remove_duplicates`, `copy`, `deep_copy`, `map`, `filter`, and `reduce` are
  available. The sorted-list version of `remove_duplicates` compares adjacent
  values, which avoids the fallback scan needed by unsorted lists.
- `sort()` can re-sort the list if internal node values were changed
  directly.

Some operations are intentionally guarded:

- `reverse()` raises `ValueError` for multi-value lists because reversing would
  break ascending order.
- `rotate(k)` raises `ValueError` unless the rotation is a no-op.
- Custom comparison callbacks are rejected on `sort`, `merge`, and
  `insert_sorted` because this class has one fixed ordering rule.

### LinkedDeque API

`LinkedDeque` focuses on double-ended operations:

- `append_left(value)` inserts at the left side.
- `append_right(value)` inserts at the right side.
- `insert(index, value)` inserts before an index, clamping far-left and
  far-right positions like `collections.deque`.
- `pop_left()` removes from the left side.
- `pop_right()` removes from the right side.
- `peek_left()` reads the leftmost value without removing it.
- `peek_right()` reads the rightmost value without removing it.
- `extend(iterable)` appends values to the right.
- `extend_left(iterable)` prepends values to the left.
- `rotate(steps)` rotates right for positive steps and left for negative
  steps.
- `reverse()` reverses the deque in place.
- `remove(value)` removes the first matching value from left to right.
- `remove_all(value)` removes every matching value and returns the count.
- `replace(old, new, count=None)` changes matching values without relinking
  nodes.
- `clear()` removes all nodes.

It also supports Python container-style helpers:

- `len(deque)` returns the number of values.
- `bool(deque)` is `False` when empty.
- `is_empty()` is an explicit empty-state helper.
- `deque[index]` returns a value by positive or negative index.
- `deque[start:stop:step]` returns a new `LinkedDeque`.
- `get(index, default=None)` returns a fallback for missing positions.
- `count(value)` returns the number of matching values.
- `index(value, start=0, stop=None)` returns the first matching index.
- `find(value, start=0, stop=None)` returns the first matching index or
  `None`.
- `value in deque` checks membership.
- `copy()` creates a shallow copy.
- `to_list()` converts the deque into a Python list.
- `from_iterable(iterable)` builds a deque from any iterable.

### SkipList API

`SkipList` focuses on sorted unique values:

- `SkipList([3, 1, 2, 2])` builds an ordered set containing `[1, 2, 3]`.
- `SkipList.from_iterable(values, max_level=16, probability=0.5, seed=None)`
  builds a skip list with explicit tuning parameters.
- `len(skip_list)`, `bool(skip_list)`, and `is_empty()` report container
  state.
- Iteration yields values in ascending order.
- Reverse iteration yields values in descending order.
- `value in skip_list` checks membership.
- `add(value)` inserts a value and returns `True` only when it was not already
  present.
- `extend(iterable)` adds many values and returns the number of new insertions.
- `update(iterable)` is an alias for `extend`.
- `remove(value)` and `discard(value)` remove a value and return whether it
  existed.
- `find(value)` returns a matching stored value or `None`.
- `floor(value, default=None)` and `ceiling(value, default=None)` support
  ordered nearest-neighbor lookups.
- `first()` and `last()` read the smallest and largest values.
- `pop_first()` and `pop_last()` remove and return the smallest and largest
  values.
- `to_list()`, `copy()`, and `clear()` provide conversion and lifecycle
  helpers.

### UnrolledLinkedList API

`UnrolledLinkedList` focuses on sequence behavior with chunked node storage:

- `UnrolledLinkedList([1, 2, 3], node_capacity=4)` builds a list whose blocks
  can hold up to four values each.
- `from_iterable(iterable, node_capacity=8)` preserves subclass construction.
- `len(unrolled)`, `bool(unrolled)`, and `is_empty()` report container state.
- Iteration yields values left to right, and reverse iteration walks blocks
  from right to left.
- Indexing, negative indexing, slicing, assignment, `get`, `index`, `find`,
  `count`, and membership checks are supported.
- `append`, `prepend`, `insert`, `extend`, and `merge` add values.
- `pop`, `pop_front`, `remove`, `remove_all`, and `remove_at` remove values.
- `replace(old, new, count=None)` changes matching values.
- `sort`, `reverse`, `rotate`, and `remove_duplicates` operate on the whole
  visible sequence.
- `map`, `filter`, and `reduce` mirror the functional helpers on `LinkedList`.
- `to_list()` returns values, while `to_blocks()` returns the internal chunk
  layout.
- `copy()`, `deep_copy()`, and `clear()` provide lifecycle helpers.

### MultilevelLinkedList API

`MultilevelLinkedList` focuses on nested linked structures:

- `MultilevelLinkedList([1, 2, 3])` builds a flat top-level chain.
- `MultilevelLinkedList.from_nested([1, (2, [3, 4])])` builds `2` with child
  nodes `3` and `4`.
- `len(multilevel)` counts every reachable node, not only top-level nodes.
- Default iteration and `to_list()` use depth-first traversal.
- `to_list("breadth_first")` returns breadth-first traversal.
- `iter_top_level()`, `to_top_level_list()`, and `top_level_length()` inspect
  only the top-level sibling chain.
- `append`, `prepend`, `extend`, `merge`, and `insert` add top-level or
  depth-indexed sibling values.
- `append_child`, `prepend_child`, and `extend_child` add nested child values.
- `child_values(parent)` returns direct children for a matching node or node
  reference.
- `detach_children(parent)` moves a child chain into a new list.
- `find(value)` returns a depth-first index, and `find_node(value)` returns
  the first matching node.
- `path_to(value)` returns nested sibling indexes such as `(1, 0, 2)`.
- `remove(value)` and `remove_at(index)` remove a node and its subtree by
  default.
- `remove(..., promote_children=True)` and
  `remove_at(..., promote_children=True)` remove only the target node and
  splice its child chain into its place.
- `pop()` removes the final depth-first node, while `pop_front()` removes the
  first node and promotes its children so the rest of the sequence remains
  reachable.
- `flatten(order)` mutates the list into one level while preserving node
  objects.
- `flattened(order)` returns a new flat list.
- `reverse()` reverses every sibling chain while preserving hierarchy.
- `sort`, `rotate`, `filter`, and `remove_duplicates` rebuild as flat lists.
- `copy`, `deep_copy`, `map`, `reduce`, `to_nested_list`, and `clear` are
  supported.

### PositionalLinkedList API

`PositionalLinkedList` focuses on stable node handles:

- `PositionalLinkedList([1, 2, 3])` builds a doubly linked positional list.
- `positions()` yields `Position` handles from head to tail.
- `first_position()`, `last_position()`, and `position_at(index)` return
  direct handles.
- `before(position)` and `after(position)` navigate around a handle.
- `add_first`, `add_last`, `add_before`, `add_after`, `append`, `prepend`,
  `insert`, `extend`, and `merge` add values and return positions where
  appropriate.
- `delete(position)` removes a specific position and invalidates that handle.
- `replace(position, value)` changes one position and returns the old value.
- `move_to_front`, `move_to_back`, `move_before`, `move_after`, and `swap`
  reorganize existing nodes without invalidating live positions.
- Indexing, slicing, assignment, `get`, `find`, `index`, `count`,
  containment checks, forward iteration, and reverse iteration are supported.
- `remove`, `remove_all`, `remove_at`, `pop_first`, `pop_last`,
  `replace_value`, `reverse`, `rotate`, `sort`, and `remove_duplicates`
  provide sequence-style mutation.
- `copy`, `deep_copy`, `map`, `filter`, `reduce`, `to_list`, and `clear`
  provide conversion, functional, and lifecycle helpers.

### SelfOrganizingLinkedList API

`SelfOrganizingLinkedList` focuses on adaptive search:

- `SelfOrganizingLinkedList(values, strategy="move_to_front")` selects the
  initial reorganization strategy.
- Supported strategies are `move_to_front`, `transpose`, `frequency_count`,
  and `none`.
- `find(value)` returns the pre-access index and reorganizes on success.
- `search(value, default=None)` returns the matching value or a fallback.
- `access(index)` reads by numeric index, increments the access count, and
  applies the selected strategy.
- `contains_static(value)`, `get(index)`, indexing, slicing, iteration, and
  membership checks read without reorganizing.
- `to_access_counts()`, `access_count(value)`, `reset_counts()`, and
  `set_strategy(strategy)` expose adaptive state.
- `append`, `prepend`, `insert`, `extend`, `merge`, `remove`, `remove_all`,
  `remove_at`, `pop_front`, `pop`, `replace`, `reverse`, `rotate`, `sort`,
  and `remove_duplicates` provide sequence mutation.
- `copy(preserve_counts=True)` and `deep_copy(preserve_counts=True)` can keep
  or reset access counts.
- `map`, `filter`, `reduce`, `to_list`, and `clear` round out the helper API.

### SparseMatrixLinkedList API

`SparseMatrixLinkedList` focuses on sparse numeric data:

- `SparseMatrixLinkedList(rows, cols, entries, zero=0)` builds a sparse
  matrix from `(row, col, value)` triples.
- `from_dense(dense, zero=0)` and `from_entries(rows, cols, entries)` provide
  alternate constructors.
- `shape`, `len(matrix)`, `bool(matrix)`, `is_empty()`, and `density()`
  describe matrix state.
- `matrix[row, col]`, `get(row, col, default)`, `set(row, col, value)`,
  `remove(row, col)`, and `pop(row, col, default)` read and mutate cells.
- `items()`, `values()`, `row_items(row)`, `column_items(col)`,
  `to_entries()`, and `to_dense()` expose sparse and dense snapshots.
- `transpose()`, `row_sum(row)`, `column_sum(col)`, and `trace()` support
  common matrix reads.
- `add_matrix`, `subtract_matrix`, `scalar_multiply`, `multiply_vector`, and
  `matmul` implement arithmetic; `+`, `-`, and `@` call the corresponding
  matrix operations.
- `map_values(func)` transforms stored cells, while `prune()` removes cells
  that became equal to the configured zero value.
- `copy`, `deep_copy`, and `clear` provide lifecycle helpers.

## Deque Edge Cases I Handled

The deque implementation intentionally handles several edge cases:

- Empty `pop` and `peek` operations raise `IndexError`.
- Popping from a one-item deque clears both `head` and `tail`.
- Appending to an empty deque sets both `head` and `tail` to the new node.
- `extend(self)` snapshots the deque before appending to avoid self-extension
  problems.
- Iterating over a deque is bounded by the size captured when iteration starts,
  which prevents `extend(iter(deque))` from walking newly appended nodes
  forever.
- `repr` and `str` handle direct and mutual self-references without infinite
  recursion.
- Equality works symmetrically between `LinkedDeque` and subclasses.
- `rotate` matches the same direction convention as `collections.deque`:
  positive values rotate right, and negative values rotate left.
- Indexing walks from the closer end so right-side indexes do not always start
  from the head.
- `insert` clamps very small indexes to the left and very large indexes to the
  right, matching the behavior of an unbounded Python deque.
- `remove` detaches the removed node and repairs both neighboring links.
- `remove_all` saves the next node before unlinking the current node so it can
  continue safely after deleting a head, middle, or tail node.
- `replace` changes node values only, which means it cannot accidentally break
  forward or backward links.
- `reverse` rewires every node in place instead of rebuilding the deque.

These cases matter because linked structures can be easy to corrupt if a method
updates one pointer but forgets the matching pointer on the neighboring node.
Most of the deque tests check both the visible values and the internal links.

## Sorted List Edge Cases I Handled

The sorted-list implementation focuses on protecting the sorted invariant:

- Initial iterables are sorted during construction.
- Every list type works: singly, doubly, singly circular, and doubly circular.
- `append` and `prepend` cannot break order because both route through
  sorted insertion.
- `insert` checks the previous and next neighbors before touching any links.
- Index assignment checks neighboring values before changing node data.
- `extend` and `replace` sort a snapshot first, so comparison errors leave the
  original list unchanged.
- `insert`, index assignment, and `add` also fail before mutation when a new
  value cannot be compared with its neighbors.
- `merge` copies values from the other list instead of relinking its nodes.
- Merging a sorted list with itself snapshots the values first, so it doubles
  the values without looping forever.
- `remove_duplicates` compares neighboring sorted values, so unhashable values
  like nested lists are handled correctly.
- Circular sorted lists restore `tail.next` and, for doubly circular lists,
  `head.prev` after mutations.
- Singly linked sorted lists never gain accidental `prev` pointers.
- Slicing, mapping, filtering, copying, and deep copying return
  `SortedLinkedList` objects instead of plain `LinkedList` objects.

These rules keep the class honest. If an operation cannot preserve sorted
order, it fails clearly instead of quietly producing a misleading container.

## Skip List Edge Cases I Handled

The skip-list implementation focuses on ordered-set behavior and level
invariants:

- Constructor input is sorted and deduplicated through normal insertion.
- Duplicate `add` calls return `False` without changing the structure.
- `extend` validates incoming values before mutation, so comparison errors do
  not partially add values.
- Removing the head, middle, tail, missing values, and the final value keeps
  all active levels consistent.
- `pop_first` and `pop_last` remove sorted edges and raise `IndexError` on an
  empty skip list.
- `clear()` detaches old nodes and resets the active level count.
- `extend(self)` snapshots first so self-extension is bounded.
- Comparable unhashable values, such as nested lists, are supported because the
  structure does not rely on hashing.
- `max_level` and `probability` are validated before any nodes are created.
- Seeded construction gives deterministic node heights for tests.
- Invalid tuning parameters fail clearly before any nodes are created.
- Comparison errors leave existing values unchanged.
- Tests walk every active level to verify that shortcut levels stay sorted and
  contain only values present on the bottom level.

## Unrolled List Edge Cases I Handled

The unrolled-list implementation focuses on keeping chunked node storage
consistent:

- `node_capacity` is validated before any nodes are created.
- Empty `peek` and `pop` operations raise `IndexError`.
- Insertions split full blocks without overfilling either block.
- Removals detach empty blocks and rebalance sparse neighboring blocks.
- Forward and backward block links are checked after mutation.
- `extend(self)` snapshots first, and live self-iterators are bounded by the
  starting size.
- Sorting computes the sorted value snapshot before rebuilding, so comparison
  errors leave the original block structure unchanged.
- `remove_duplicates()` supports unhashable values through an equality-scan
  fallback.
- `clear()` empties old block values and detaches old block links.
- Randomized tests compare append, prepend, insert, remove, pop, replace,
  reverse, and rotate behavior against Python `list`.

## Multilevel List Edge Cases I Handled

The multilevel-list implementation focuses on preserving or intentionally
flattening hierarchy:

- Empty reads and pops fail clearly.
- Nested construction handles plain values separately from `(value, children)`
  pairs.
- Depth-first and breadth-first traversal are both supported and tested.
- Child operations accept either a node reference or the first matching stored
  parent value.
- External node references are rejected so one list cannot accidentally attach
  children to another list's node.
- Removing a node can remove its full subtree or promote its children into the
  removed node's place.
- `pop_front()` promotes children so removing the first top-level node does
  not silently drop the rest of the depth-first sequence.
- `detach_children()` moves a child chain into a new list and updates both
  list sizes.
- `flatten()` preserves node objects while clearing child links.
- `copy`, `deep_copy`, and `map` preserve hierarchy.
- `sort`, `rotate`, `filter`, and `remove_duplicates` intentionally rebuild a
  flat top-level list because they operate on the whole visible sequence.
- `clear()` recursively detaches `next` and `child` links from every node.

## Positional List Edge Cases I Handled

The positional-list implementation focuses on keeping position handles honest:

- Empty peeks, pops, and position lookups raise `IndexError`.
- Non-position arguments raise `TypeError` before mutation.
- Positions from another list are rejected before any links are changed.
- Deleted positions and positions from a cleared list become invalid.
- Other live positions to moved nodes remain valid after moves, swaps,
  reversing, rotating, and sorting.
- `extend(self)` snapshots first so self-extension is bounded.
- Sorting compares nodes before relinking, so comparison errors leave the
  original order intact.
- Duplicate removal supports hashable and unhashable values.
- Tests walk forward links, backward links, owners, head, tail, and every
  yielded position after randomized list-style operations.

## Self-Organizing List Edge Cases I Handled

The self-organizing implementation keeps adaptive behavior explicit:

- Invalid strategy names fail before list state is created or changed.
- Membership checks, indexing, slicing, and static reads do not reorganize or
  increment access counts.
- `find`, `search`, and `access` report the pre-access location or value, then
  apply the selected strategy.
- Move-to-front, transpose, frequency-count, and count-only behavior are
  tested separately.
- Access counts survive in-place sequence operations such as reverse, rotate,
  sort, and strategy changes.
- Copies can preserve or reset access counts.
- Duplicate removal supports unhashable values through an equality fallback.
- Randomized tests compare non-adaptive mutations against Python `list` while
  checking every forward and backward link.

## Sparse Matrix Edge Cases I Handled

The sparse-matrix implementation protects both row and column chains:

- Matrix dimensions, row indexes, column indexes, and tuple keys are validated
  before mutation.
- Entries equal to `zero` are never stored, and assigning `zero` removes an
  existing cell.
- Duplicate constructor entries update the existing cell instead of creating
  multiple nodes for one coordinate.
- Row chains stay sorted by column, and column chains stay sorted by row.
- Removing a head, middle, or tail cell repairs both linked chains.
- Dense construction rejects ragged rows.
- Addition, subtraction, matrix multiplication, trace, and vector
  multiplication validate shape compatibility.
- Explicit `get` defaults can differ from the configured zero value.
- Tests compare every randomized mutation and arithmetic result against dense
  Python-list math, then verify that row and column chains contain the same
  node objects.

## Style and Documentation Standards

I also cleaned the Python code so it follows standard Python style more
closely, especially PEP 8 formatting and PEP 257-style documentation
conventions:

- Added module docstrings to the package, node modules, linked-list modules,
  and test modules.
- Added class and method docstrings to the implementation so each public
  behavior explains its purpose.
- Wrapped long lines to stay within a 79-character style target.
- Normalized imports and blank lines.
- Removed noisy test docstrings that repeated obvious information like
  `Args: self` or `Returns: None`.
- Replaced default comparison lambdas with `operator.lt` for clearer,
  reusable default ordering behavior.
- Preserved existing public behavior while making the code easier to read.

This cleanup is important for portfolio code because readability is part of
the implementation. The goal is not only for the data structures to work, but
also for someone reviewing the repository to understand how the design is
organized and why each piece exists.

## Complexity Overview

The detailed complexity analysis lives in `docs/complexity.md`. The
beginner-oriented source walkthrough lives in
`docs/linked_structures_walkthrough.md`. The short version is:

- `LinkedList` head and tail helpers such as `append`, `prepend`,
  `peek_front`, and `peek_back` are O(1), while indexing and searching are
  O(n).
- `LinkedList.sort()` uses merge sort, so it runs in O(n log n) time.
- `SortedLinkedList.add()` is O(n) because it walks to the correct insertion
  point, while snapshot-based operations like `extend`, `replace`, and
  `merge` are O(n log n) or O((n + m) log(n + m)).
- `LinkedDeque` end operations such as `append_left`, `append_right`,
  `pop_left`, and `pop_right` are O(1).
- `LinkedDeque` indexing is O(min(i, n - i)) because it starts from whichever
  end is closer.
- `SkipList` search, insertion, and removal are O(log n) on average with
  probabilistic shortcut levels, and O(n) in the worst case.
- `UnrolledLinkedList` end appends are O(1) while middle access and mutation
  walk block nodes and then edit a small in-block list.
- `MultilevelLinkedList` depth-first reads are O(n), and flattening or
  hierarchy-wide operations visit every reachable node.
- `PositionalLinkedList` end operations and known-position insertions are
  O(1), while numeric lookup and value search remain O(n).
- `SelfOrganizingLinkedList` keeps search O(n) in the worst case, but adaptive
  strategies can move frequently accessed values closer to the head.
- `SparseMatrixLinkedList` stores only non-zero cells, so storage is O(z) for
  `z` stored entries instead of O(rows * cols).
- All linked structures use O(n) node storage overall, while the container
  metadata itself is O(1).

Those notes matter because linked structures have different strengths from
Python's built-in `list`. This project is optimized for explaining pointer
invariants, edge cases, and data-structure behavior clearly.

## Testing Strategy

The test suite uses Python's built-in `unittest` module. It covers both
high-level behavior and low-level structural correctness.

For `LinkedList`, the tests cover:

- Appending, prepending, inserting, removing, popping, and popping from the
  front.
- Indexing, negative indexing, slicing, membership checks, and equality.
- Truthiness, explicit empty checks, safe default reads, peeking at both ends,
  and value search.
- Sorted insertion, merge sort, merging, reversing, rotating, and duplicate
  removal.
- Bulk value removal with `remove_all`, positional removal with `remove_at`,
  and value replacement with `replace`.
- Functional helpers like `map`, `filter`, and `reduce`.
- Circular-list behavior, including head-tail links and doubly circular
  `prev` links.
- Empty-list and out-of-bounds error handling.
- Copy independence and clearing behavior.

For `LinkedDeque`, the tests cover:

- Empty, singleton, and multi-node states.
- Appending and popping from both ends.
- Peeking without mutation.
- Indexing, slicing, safe default reads, counting, indexing by value, and
  finding values.
- Inserting at the left, middle, right, and clamped out-of-range positions.
- Removing the first matching value and removing every matching value.
- Replacing all matching values or only a limited number of matches.
- Reversing in place while preserving forward and backward links.
- Forward and reverse iteration.
- Python-style deque aliases.
- Copy behavior and subclass-preserving constructors.
- Self-extension and iterator-bounded extension.
- Self-referential and mutually referential string representations.
- Rotating right, rotating left, large rotations, and no-op rotations.
- Internal link integrity after repeated alternating operations.

For `SortedLinkedList`, the tests cover:

- Sorting initial values for every linked-list variant.
- Adding values through `add`, `append`, `prepend`, and `extend`.
- Self-extension through a snapshot.
- Position-aware `insert` behavior, including invalid sorted positions.
- Failed inserts and assignments leave the original list unchanged.
- Safe index assignment that accepts sorted replacements and rejects unsafe
  replacements.
- Replacing values with and without a count limit.
- Removing, popping, and removing by position while preserving sorted order.
- Merging another linked list without mutating the other list.
- Merging a sorted list with itself through a snapshot.
- Duplicate removal for comparable unhashable values.
- Copying, deep copying, slicing, mapping, and filtering.
- Re-sorting after direct internal node changes.
- Guarding `reverse`, `rotate`, and custom comparison callbacks.
- Leaving the original list unchanged when comparison errors happen.
- Preserving circular links and singly linked node shape after mutation.

For `SkipList`, the tests cover:

- Empty-state behavior and invalid configuration values.
- Constructor sorting and duplicate removal.
- Adding, duplicate insertion, membership, `find`, `floor`, and `ceiling`.
- Removing head, middle, tail, missing values, and all remaining values.
- Removing sorted edges with `pop_first` and `pop_last`.
- Self-extension, copying, clearing, and subclass-preserving construction.
- Atomic extension when an incoming value cannot be compared.
- Comparable unhashable values.
- Single-level mode, which behaves like a sorted linked set.
- Equality and reproducible seeded node heights.
- Comparison errors that leave the original list unchanged.
- Randomized add/remove/extend/clear/floor/ceiling behavior against Python
  `set` semantics.
- Internal level invariants for every active skip-list level.

For `UnrolledLinkedList`, the tests cover:

- Empty state, capacity validation, and error behavior.
- Appending, prepending, inserting, extending, and merging values.
- Block splitting and block-link integrity.
- Indexing, slicing, assignment, safe reads, search helpers, and containment.
- Removing values by value and position, plus block rebalancing after removal.
- Duplicate removal for hashable and unhashable values.
- Copying, deep copying, mapping, filtering, and reducing.
- Sorting, reversing, rotating, and atomic comparison-error behavior.
- Self-extension and live self-iterator extension.
- Clearing and detaching old block nodes.
- Randomized mutation behavior against Python `list`.

For `MultilevelLinkedList`, the tests cover:

- Empty state and traversal-order validation.
- Nested construction from `(value, children)` pairs.
- Depth-first, breadth-first, and top-level traversal.
- Child append, prepend, extension, snapshots, and detaching.
- Path lookup, node lookup, indexing, slicing, assignment, and merging.
- Subtree removal and child-promotion removal.
- Popping from both depth-first ends.
- Depth-first and breadth-first flattening.
- Reversing hierarchy, sorting, rotating, and duplicate removal.
- Copying, deep copying, mapping, filtering, reducing, and equality.
- Recursive clearing of `next` and `child` links.
- Randomized flat operations against Python `list`.

For `PositionalLinkedList`, the tests cover:

- Empty state, invalid positions, foreign positions, and stale positions.
- Adding before and after known positions.
- Position navigation with `before`, `after`, first, last, and index lookup.
- Indexing, slicing, assignment, search helpers, and containment.
- Deleting, replacing, moving, swapping, popping, and removing values.
- Preserving position identity through reverse, rotate, and sort.
- Duplicate removal for unhashable values.
- Copying, deep copying, mapping, filtering, reducing, and self-extension.
- Clearing behavior that invalidates existing positions.
- Randomized mutation behavior against Python `list` while checking node
  owners and both directions of links.

For `SelfOrganizingLinkedList`, the tests cover:

- Empty state and strategy validation.
- Move-to-front, transpose, frequency-count, and no-reorder strategies.
- Access-count increments, resets, strategy changes, and static reads.
- Adaptive `find`, `search`, and `access` behavior.
- Indexing, slicing, assignment, containment, and safe default reads.
- Removing, replacing, reversing, rotating, sorting, and duplicate removal.
- Copying and deep copying with count preservation.
- Mapping, filtering, reducing, and self-extension.
- Randomized non-adaptive mutation behavior against Python `list`.

For `SparseMatrixLinkedList`, the tests cover:

- Empty matrices, dimension validation, key validation, and shape errors.
- Construction from entries and dense rectangular iterables.
- Duplicate entries, zero pruning, assignment, removal, popping, and clearing.
- Row iteration, column iteration, values, density, and custom zero values.
- Copying, deep copying, equality, and transposition.
- Matrix addition, subtraction, scalar multiplication, vector multiplication,
  matrix multiplication, and trace.
- Value mapping and explicit pruning of cells that become zero.
- Randomized mutations against dense Python matrices.
- Randomized arithmetic against dense Python-list matrix math.
- Internal row-chain and column-chain invariants after every randomized
  operation.

The tests do more than check final lists of values. For the linked deque and
unrolled list, they also walk links in both directions to verify that
neighboring nodes agree. For the sorted list, the tests verify that public
values remain sorted and that circular head-tail links stay intact. For the
skip list, the tests verify that each shortcut level remains sorted and only
references values that exist on the bottom level. For the multilevel list, the
tests compare flat traversal, nested snapshots, top-level chains, and child
links so hierarchy bugs are visible. For positional and self-organizing lists,
the tests walk both `prev` and `next` links. For sparse matrices, the tests
verify that row chains and column chains contain the same stored node objects.

## Requirements

- Python 3.10 or newer
- No third-party runtime dependencies
- Optional development dependencies for local checks: `mypy`, `ruff`,
  `pytest`, `coverage`, and `pre-commit`

## Running Tests

From this package directory:

```bash
python -m unittest discover -s tests -t . -v
```

The GitHub Actions workflow runs the same unittest suite on pushes and pull
requests targeting `master`.

## Developer Checks

The package includes configuration for mypy, Ruff, pytest, and coverage in
`pyproject.toml`. The repository root includes the shared pre-commit config.

Install the optional development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run static type checks:

```bash
python -m mypy
```

Run Ruff linting and format checks:

```bash
python -m ruff check .
python -m ruff format --check .
```

Run the test suite with pytest:

```bash
python -m pytest
```

Run tests with coverage:

```bash
python -m coverage run -m unittest discover -s tests -t . -v
python -m coverage report
```

Run the full local pre-commit bundle:

```bash
python -m pre_commit run --all-files
```

The type configuration is intentionally practical for this educational
project. It checks typed function bodies and complete annotations while still
allowing the mixin-based linked-list internals to use `Any` where a single
class has to support singly, doubly, circular, and non-circular node shapes.

## Example

```python
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

linked_list = LinkedList("doubly_circular")
for value in [3, 1, 2]:
    linked_list.append(value)

linked_list.sort()
linked_list.insert_sorted(4)
linked_list.remove_all(2)
linked_list.replace(3, 30)
removed_tail = linked_list.remove_at(-1)

print(linked_list.peek_front())  # 1
print(linked_list.find(30))      # 1
print(removed_tail)              # 4
print(linked_list.get(99, "missing"))  # missing
print(linked_list.to_list())     # [1, 30]

linked_deque = LinkedDeque([2, 3])
linked_deque.append_left(1)
linked_deque.append_right(4)
linked_deque.insert(2, 99)
linked_deque.replace(99, 5)
linked_deque.remove_all(2)
linked_deque.rotate(1)
linked_deque.reverse()

print(linked_deque[0])        # 3
print(linked_deque.count(4))  # 1
print(linked_deque.get(99, "missing"))  # missing
print(linked_deque.to_list())  # [3, 5, 1, 4]

sorted_list = SortedLinkedList("doubly_circular", [4, 1, 3, 2])
sorted_list.add(0)
sorted_list.append(5)
sorted_list.replace(3, 30)
sorted_list.remove_at(1)

print(sorted_list.peek_front())  # 0
print(sorted_list.find(30))      # 4
print(sorted_list.to_list())     # [0, 2, 4, 5, 30]

skip_list = SkipList([4, 1, 3, 2, 2], seed=1)
skip_list.add(5)
skip_list.remove(1)

print(skip_list.first())       # 2
print(skip_list.ceiling(3))    # 3
print(skip_list.floor(6))      # 5
print(skip_list.to_list())     # [2, 3, 4, 5]

unrolled = UnrolledLinkedList([1, 2, 3, 4], node_capacity=3)
unrolled.insert(2, 99)
unrolled.remove(3)

print(unrolled.to_list())    # [1, 2, 99, 4]
print(unrolled.to_blocks())  # block layout, for example [[1, 2], [99, 4]]

multilevel = MultilevelLinkedList.from_nested([1, (2, [3, 4]), 5])
multilevel.append_child(2, 6)

print(multilevel.to_list())              # [1, 2, 3, 4, 6, 5]
print(multilevel.path_to(6))             # (1, 2)
print(multilevel.to_list("breadth_first"))  # [1, 2, 5, 3, 4, 6]

positional = PositionalLinkedList([1, 3])
middle = positional.add_after(positional.first_position(), 2)
positional.move_to_front(middle)

print(positional.to_list())  # [2, 1, 3]

self_organizing = SelfOrganizingLinkedList(
    ["cold", "warm", "hot"],
    strategy="move_to_front",
)
self_organizing.search("hot")

print(self_organizing.to_list())          # ['hot', 'cold', 'warm']
print(self_organizing.to_access_counts()) # [('hot', 1), ('cold', 0), ('warm', 0)]

sparse = SparseMatrixLinkedList.from_dense([[1, 0, 2], [0, 3, 0]])

print(sparse.to_entries())          # [(0, 0, 1), (0, 2, 2), (1, 1, 3)]
print(sparse.multiply_vector([2, 3, 4]))  # [10, 9]
print((sparse @ sparse.transpose()).to_dense())  # [[5, 0], [0, 9]]
```
