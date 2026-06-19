# Design And Edge Cases

This document holds the implementation notes that are too detailed for the
README but useful for learners and reviewers.

## Core Design Principles

- Public containers expose familiar Python behavior: iteration, length,
  truthiness, membership, indexing where appropriate, and readable displays.
- Index-based sequence APIs accept Python integer-like objects through
  `__index__`, matching built-in container behavior for values such as NumPy
  integer scalars.
- Sparse-matrix dimensions and coordinates also accept integer-like objects
  but still reject `bool`, because `True` and `False` are ambiguous as matrix
  positions.
- Integer-like configuration options are normalized before storage so internal
  state uses plain Python `int` values.
- Count-limited replacement validates `count` before mutation so fractional
  counts fail clearly instead of acting like "replace all".
- Mutations repair both visible order and hidden node links before returning.
- Circular structures are always bounded by tracked size during iteration.
- Doubly linked structures keep `prev` links in sync with `next` links.
- Educational clarity is preferred over clever compact code.
- Runtime dependencies stay at zero; testing and tooling dependencies live in
  optional extras.

## Display Safety

Containers can store arbitrary Python objects, including themselves. Public
`repr` and `str` methods use recursion-safe display helpers so a direct
self-reference prints as `...` instead of raising `RecursionError`.

This matters for an educational package because learners often experiment
with unusual values. A display method should help them inspect state rather
than crash while they are debugging.

## LinkedList

The main `LinkedList` class is assembled from mixins:

- `base.py` handles shared metadata and node creation.
- `access.py` handles indexing, slicing, equality, membership, and display.
- `iteration.py` handles forward and reverse iteration.
- `mutation.py` handles append, prepend, insert, removal, popping, replacing,
  rotating, reversing, extending, merging, and duplicate removal.
- `sort_merge.py`, `functional.py`, and `utility.py` keep sorting,
  map/filter/reduce, conversion, copying, and cleanup behavior separated.

Edge cases covered:

- Empty lists and single-node lists.
- Negative indexing for reads, assignments, and remove-at.
- Circular head/tail reconnection after mutation.
- Doubly linked `prev` repair after insertion and deletion.
- Self-extension and self-merge snapshots.
- Unhashable values in duplicate removal.
- Comparison errors during sorting that leave existing links intact.
- Single-pass `remove_all()` so many matching values do not repeatedly scan
  from the head.

## LinkedDeque

The deque is separate from `LinkedList` because its purpose is narrower:
efficient operations at the two ends.

Edge cases covered:

- Appending and popping from both sides.
- Slicing and indexing from the closer end.
- Self-extension snapshots.
- `remove_all()` while walking through nodes that may be unlinked.
- Rotation in both directions.
- Direct self-referential display values.

## SortedLinkedList

`SortedLinkedList` inherits the base linked-list behavior but protects one
extra invariant: values stay in ascending order.

Edge cases covered:

- Constructor inputs are sorted before insertion.
- `append`, `prepend`, and `add` all mean ordered insertion.
- Direct index insertion is allowed only when it preserves sorted order.
- Replacement rebuilds after sorting succeeds.
- Reversal and non-trivial rotation are rejected because they would violate
  the class name.
- Duplicate removal works with comparable unhashable values.

## SkipList

`SkipList` is an ordered set. The bottom level stores every value, while upper
levels store random shortcuts.

Edge cases covered:

- Duplicate insertions are ignored.
- Promotion height is bounded by `max_level`.
- `seed` makes tests deterministic.
- Removing the final value resets tail and active level.
- Floor and ceiling return caller-provided defaults when no candidate exists.
- Public display handles a stored reference to the skip list itself.

## UnrolledLinkedList

An unrolled list stores several values in each linked node. That reduces node
count and makes block-level behavior visible.

Edge cases covered:

- `node_capacity` must be an integer of at least two.
- Full blocks split during insertion.
- Underfilled blocks merge or borrow after removal.
- Empty blocks are detached.
- `to_blocks()` exposes the internal block layout for learning and tests.
- Sorting, rotation, reverse, map, and filter rebuild blocks consistently.

## MultilevelLinkedList

Each node has a `next` sibling link and an optional `child` link. Public
iteration is depth-first by default.

Edge cases covered:

- Construction from nested `(value, children)` pairs.
- Depth-first and breadth-first traversal.
- Detaching child chains into a new list.
- Removing nodes with or without promoting children.
- Flattening while preserving node objects.
- Sorting and rotation intentionally rebuild a flat top-level list.
- Traversal is bounded by size to avoid infinite loops during corrupted-state
  experiments.

## PositionalLinkedList

The positional list exposes stable `Position` handles so callers can mutate
around a known node without searching by index again.

Edge cases covered:

- Positions validate their owning list before use.
- Deleted and cleared nodes invalidate old positions.
- Moving nodes preserves node identity and live positions.
- Sorting and rotation relink existing nodes instead of replacing them.
- Position iteration reflects the current list order.

## SelfOrganizingLinkedList

Self-organizing lists adapt after successful searches.

Strategies:

- `move_to_front`: move a found node directly to the head.
- `transpose`: swap a found node with its previous neighbor.
- `frequency_count`: bubble a found node left by access count.
- `none`: count accesses without reordering.

Edge cases covered:

- Static reads do not reorganize.
- Access counts can be reset, copied, or deep-copied.
- Strategy changes validate the target strategy.
- Frequency ordering is repaired locally after each access.
- Property tests compare adaptive access sequences with a Python reference
  model.

## SparseMatrixLinkedList

The sparse matrix stores only non-zero entries. Each stored cell participates
in a row chain through `right` links and a column chain through `down` links.

Edge cases covered:

- Empty dimensions are allowed.
- Dense input must be rectangular.
- Assigning the configured zero removes a stored entry.
- Row and column chains stay sorted after insertion and removal.
- Transpose, addition, subtraction, scalar multiplication, vector
  multiplication, and matrix multiplication are tested against dense models.
- Arithmetic methods require the configured `zero` to be numeric additive
  zero (`0`) because they skip missing cells for sparse efficiency.
- Custom zero sentinels are supported for storage and dense round-tripping,
  not for arithmetic shortcuts that assume missing cells add or multiply like
  numeric zero.

## Testing Strategy

The package uses three layers of tests:

- Unit tests for public behavior and expected errors.
- Coverage edge tests for hard-to-reach branches and defensive guards.
- Hypothesis property tests for randomized operation sequences and dense
  reference-model comparisons.

The property tests cover all major public containers, including multilevel,
positional, and self-organizing lists. They are intentionally bounded to small
inputs so they run quickly while still exploring many mutation combinations.
