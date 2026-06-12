# Data Science AI Portfolio

This repository currently contains a Python linked-list project with singly,
doubly, singly circular, and doubly circular linked-list variants, plus sorted
linked-list, linked-deque, and skip-list implementations.

## Project Layout

```text
docs/
  complexity.md
.pre-commit-config.yaml
Linked Lists/
  linked_list/
    __init__.py
    deque.py
    py.typed
    skip_list.py
    sorted_list.py
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
  test_linked_deque.py
  test_linked_list.py
  test_skip_list.py
  test_sorted_linked_list.py
pyproject.toml
requirements-dev.txt
```

## Features

- Singly and doubly linked lists
- Singly circular and doubly circular linked lists
- Sorted linked lists that preserve ascending order after mutation
- Linked deque backed by a doubly linked list
- Skip list ordered set with probabilistic multi-level links
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
- PEP 561 typed-package marker and mypy configuration for static type checks
- Ruff linting and format-check configuration
- Pytest and coverage configuration for alternate test workflows
- Local pre-commit hooks for linting, type checking, and tests
- Dedicated complexity guide in `docs/complexity.md`

## Project Explanation

This project is meant to show that I understand linked data structures from the
inside out, not just how to call a built-in list or deque. I implemented the
core linked-list behavior myself, then separated the code into focused modules
so each part of the data structure is easier to explain, test, and maintain.

At the highest level, the project has four public containers:

- `LinkedList`, which supports singly linked, doubly linked, singly circular,
  and doubly circular list variants.
- `SortedLinkedList`, which uses the same list variants but keeps values in
  ascending order at all times.
- `LinkedDeque`, which is a double-ended queue built on top of doubly linked
  nodes.
- `SkipList`, which is a probabilistic ordered set with average logarithmic
  search, insertion, and removal.

The two structures are related, but they are not the same thing. A doubly
linked list is a general-purpose sequence where operations like indexing,
insertion, removal, sorting, merging, and traversal matter. A deque is focused
on efficient access at both ends. With `LinkedDeque`, the main design goal is
to make left-side and right-side operations direct and predictable:
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
- `remove(value)` and `discard(value)` remove a value and return whether it
  existed.
- `find(value)` returns the stored matching value or `None`.
- `floor(value)` returns the greatest stored value less than or equal to the
  requested value.
- `ceiling(value)` returns the smallest stored value greater than or equal to
  the requested value.
- `first()` and `last()` read the smallest and largest values.

The class accepts `max_level`, `probability`, and `seed` parameters. That keeps
the public container simple while making tests deterministic and making the
probabilistic design visible for learning purposes.

## Feature Reference

The package now exposes enough behavior to use these structures as practical
teaching containers, not only as minimal linked-list examples.

For detailed Big-O notes, see `docs/complexity.md`. That guide breaks down
time and space costs for `LinkedList`, `SortedLinkedList`, `LinkedDeque`,
`SkipList`, node storage, circular-list behavior, and the tradeoffs behind
snapshot-based operations.

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
- `value in skip_list` checks membership.
- `add(value)` inserts a value and returns `True` only when it was not already
  present.
- `extend(iterable)` adds many values and returns the number of new insertions.
- `remove(value)` and `discard(value)` remove a value and return whether it
  existed.
- `find(value)` returns a matching stored value or `None`.
- `floor(value, default=None)` and `ceiling(value, default=None)` support
  ordered nearest-neighbor lookups.
- `first()` and `last()` read the smallest and largest values.
- `to_list()`, `copy()`, and `clear()` provide conversion and lifecycle
  helpers.

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
- Removing the head, middle, tail, missing values, and the final value keeps
  all active levels consistent.
- `clear()` detaches old nodes and resets the active level count.
- `extend(self)` snapshots first so self-extension is bounded.
- Seeded construction gives deterministic node heights for tests.
- Invalid tuning parameters fail clearly before any nodes are created.
- Comparison errors leave existing values unchanged.
- Tests walk every active level to verify that shortcut levels stay sorted and
  contain only values present on the bottom level.

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

The detailed complexity analysis lives in `docs/complexity.md`. The short
version is:

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
- Self-extension, copying, clearing, and subclass-preserving construction.
- Equality and reproducible seeded node heights.
- Comparison errors that leave the original list unchanged.
- Randomized add/remove/extend/clear/floor/ceiling behavior against Python
  `set` semantics.
- Internal level invariants for every active skip-list level.

The tests do more than check final lists of values. For the linked deque, they
also walk the nodes forward and backward to verify that `next` and `prev`
connections are correct. That is important because a linked structure can look
correct from one direction while still having broken backward links. For the
sorted list, the tests also verify that public values remain sorted and that
circular head-tail links stay intact. For the skip list, the tests verify that
each shortcut level remains sorted and only references values that exist on
the bottom level.

## Requirements

- Python 3.10 or newer
- No third-party runtime dependencies
- Optional development dependencies for local checks: `mypy`, `ruff`,
  `pytest`, `coverage`, and `pre-commit`

## Running Tests

From the repository root:

```bash
cd "Linked Lists"
python -m unittest discover -v
```

The GitHub Actions workflow runs the same unittest suite on pushes and pull
requests targeting `master`.

## Developer Checks

The repository includes configuration for mypy, Ruff, pytest, coverage, and
pre-commit in `pyproject.toml` and `.pre-commit-config.yaml`.

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
python -m coverage run -m unittest discover -s "Linked Lists" -v
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
from linked_list import LinkedDeque, LinkedList, SkipList, SortedLinkedList

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
```
