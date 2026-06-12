# Linked Structure Complexity Guide

This guide explains the time and space complexity of the linked-list,
sorted-list, and deque containers in this repository.

The symbols used below are:

- `n`: number of values already stored in the container.
- `m`: number of incoming values from another iterable or list.
- `k`: number of positions rotated or number of replacements requested.
- `r`: number of values that actually match a removal or replacement target.

The code is intentionally educational, so several methods favor clear pointer
repair over micro-optimizing every case. The tables below describe the actual
behavior of the implementation.

## LinkedList Overview

`LinkedList` supports four shapes:

- `singly`
- `doubly`
- `singly_circular`
- `doubly_circular`

All four shapes store `head`, `tail`, and `_size`, so operations that touch the
ends often avoid a full traversal. Middle access still walks through nodes
because linked lists do not have array-style random access.

### LinkedList Read Operations

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `len(linked_list)` | O(1) | O(1) | Reads the tracked `_size`. |
| `bool(linked_list)` | O(1) | O(1) | Checks whether `_size` is nonzero. |
| `is_empty()` | O(1) | O(1) | Explicit empty-state helper. |
| `linked_list[index]` | O(n) | O(1) | Walks from `head`; negative indexes are normalized first. |
| `linked_list[start:stop:step]` | O(n + s) | O(s) | Builds a Python snapshot, slices it, then rebuilds a list with `s` items. |
| `get(index, default)` | O(n) | O(1) | Same lookup cost as indexing, but catches `IndexError`. |
| `peek_front()` | O(1) | O(1) | Reads `head.data`. |
| `peek_back()` | O(1) | O(1) | Reads `tail.data`. |
| `value in linked_list` | O(n) | O(1) | Stops early if a match is found. |
| `index(value)` | O(n) | O(n) | Converts to a Python list, then uses `list.index`. |
| `find(value)` | O(n) | O(n) | Wraps `index` and returns `None` instead of raising. |
| `count(value)` | O(n) | O(1) | Traverses every value once. |
| `nth_from_end(n)` | O(n) | O(1) | Converts `n` into a zero-based index, then walks from `head`. |
| `to_list()` | O(n) | O(n) | Copies every value into a Python list. |
| Forward iteration | O(n) | O(1) | Circular lists stop after returning to `head`. |
| Reverse iteration | O(n) | O(1) | Supported only by doubly linked variants. |

### LinkedList Mutation Operations

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `append(value)` | O(1) | O(1) | Uses `tail`; circular lists also repair `tail.next`. |
| `prepend(value)` | O(1) | O(1) | Uses `head`; doubly linked lists repair `prev`. |
| `insert(index, value)` | O(n) | O(1) | Head/tail inserts are O(1), middle inserts require traversal. |
| `remove(value)` | O(n) | O(1) | Removes the first match and repairs affected links. |
| `remove_all(value)` | O(n * r) | O(1) | Repeatedly calls `remove`, so many duplicates can make this quadratic. |
| `remove_at(index)` | O(n) | O(1) | Edge removals delegate to `pop_front` or `pop`. |
| `replace(old, new)` | O(n) | O(1) | Updates node data only; links do not move. |
| `pop_front()` | O(1) | O(1) | Moves `head` forward and repairs circular/doubly links. |
| `pop()` on singly lists | O(n) | O(1) | Must find the node before `tail`. |
| `pop()` on doubly lists | O(n) | O(1) | Current implementation still walks for linear doubly lists. |
| `pop()` on doubly circular lists | O(1) | O(1) | Uses `tail.prev`. |
| `clear()` | O(n) | O(1) | Detaches every node before resetting state. |
| `extend(iterable)` | O(m) | O(1) or O(n) | Self-extension snapshots first, otherwise appends as it reads. |
| `remove_duplicates()` | O(n) average | O(n) | Uses a `set`, so stored values must be hashable. |

### LinkedList Algorithms

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `sort()` | O(n log n) | O(log n) | Merge sort recursion; nodes are relinked rather than indexed. |
| `insert_sorted(value)` | O(n) | O(1) | Assumes the list is already sorted. |
| `merge(other)` linear lists | O(n + m) | O(1) | Relinks nodes from both lists. |
| `merge(other)` circular lists | O(n + m) | O(n + m) | Uses value snapshots to avoid circular traversal hazards. |
| `reverse()` | O(n) | O(1) | Rewrites each node's direction links. |
| `rotate(k)` circular lists | O(n) | O(1) | Advances `head` and `tail` up to `n` steps. |
| `rotate(k)` linear lists | O(n) | O(1) | Finds a new break point and reconnects the old tail. |
| `map(func)` | O(n) | O(n) | Builds a new linked list. |
| `filter(predicate)` | O(n) | O(n) | Builds a new linked list with accepted values. |
| `reduce(func)` | O(n) | O(1) | Delegates to `functools.reduce`. |
| `copy()` | O(n) | O(n) | Copies nodes but not stored values. |
| `deep_copy()` | O(n + d) | O(n + d) | Also deep-copies stored values; `d` depends on value structure. |

## SortedLinkedList Complexity

`SortedLinkedList` uses the same node shapes as `LinkedList`, but it protects a
stronger invariant: values are always stored in ascending order. Some methods
therefore rebuild from sorted snapshots instead of performing a local pointer
edit that might leave the structure unsorted.

### SortedLinkedList Reads

Read operations have the same complexity as `LinkedList`:

- `len`, `bool`, `is_empty`, `peek_front`, and `peek_back`: O(1).
- Indexing, `get`, membership, `count`, and iteration: O(n).
- Slicing, `copy`, and `deep_copy`: O(n) time and O(n) space.

The important difference is semantic: any returned `SortedLinkedList` remains
sorted even if the source slice or mapped values were produced in a different
order.

### SortedLinkedList Mutations

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| Constructor from iterable | O(m log m) | O(m) | Sorts incoming values before rebuilding nodes. |
| `add(value)` | O(n) | O(1) | Walks to the insertion point. |
| `append(value)` | O(n) | O(1) | Routes to `add`; it does not force tail insertion. |
| `prepend(value)` | O(n) | O(1) | Routes to `add`; it does not force head insertion. |
| `insert(index, value)` | O(n) | O(1) | Checks neighboring values before relinking. |
| `sorted_list[index] = value` | O(n) | O(1) | Checks neighbors before changing data. |
| `extend(iterable)` | O((n + m) log(n + m)) | O(n + m) | Sorts a combined snapshot, then rebuilds. |
| `replace(old, new)` | O(n log n) | O(n) | Rebuilds if any replacement changes ordering. |
| `merge(other)` | O((n + m) log(n + m)) | O(n + m) | Copies values from `other`; `other` is unchanged. |
| `sort()` | O(n log n) | O(n) | Rebuilds from a sorted value snapshot. |
| `remove(value)` | O(n) | O(1) | Same first-match removal as `LinkedList`. |
| `remove_all(value)` | O(n * r) | O(1) | Inherited repeated-removal strategy. |
| `remove_at(index)` | O(n) | O(1) | Removing cannot break sorted order. |
| `pop_front()` | O(1) | O(1) | Removes the smallest value. |
| `pop()` | O(n) or O(1) | O(1) | Same list-shape behavior as `LinkedList.pop`. |
| `remove_duplicates()` | O(n) | O(1) | Compares adjacent values; supports unhashable values. |
| `reverse()` | O(1) | O(1) | No-op for size 0 or 1; otherwise raises `ValueError`. |
| `rotate(k)` | O(1) | O(1) | No-op rotations return; non-trivial rotations raise `ValueError`. |

### Why SortedLinkedList Rebuilds Some Operations

For a normal linked list, changing a node's data is local. For a sorted list,
changing a value can require moving that node to a completely different
position. Rebuilding from a sorted snapshot is easier to reason about and has a
clear safety benefit: if Python cannot compare the new values, the original
list remains unchanged.

## LinkedDeque Complexity

`LinkedDeque` is backed by doubly linked nodes and keeps direct `head`, `tail`,
and `_size` references. That makes both ends efficient while still allowing
educational sequence-style helpers.

### LinkedDeque Reads

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `len(deque)` | O(1) | O(1) | Reads `_size`. |
| `bool(deque)` | O(1) | O(1) | Checks whether `_size` is nonzero. |
| `is_empty()` | O(1) | O(1) | Explicit empty-state helper. |
| `peek_left()` | O(1) | O(1) | Reads `head.data`. |
| `peek_right()` / `peek()` | O(1) | O(1) | Reads `tail.data`. |
| `deque[index]` | O(min(i, n - i)) | O(1) | Walks from the closer end. |
| `deque[start:stop:step]` | O(n + s) | O(n + s) | Builds a Python snapshot, slices it, then builds a deque. |
| `get(index, default)` | O(min(i, n - i)) | O(1) | Strict indexing wrapped with a fallback. |
| `value in deque` | O(n) | O(1) | Stops early on a match. |
| `count(value)` | O(n) | O(1) | Traverses every value once. |
| `index(value)` | O(n) | O(1) | Respects optional search bounds. |
| `find(value)` | O(n) | O(1) | Wraps `index` and returns `None` on misses. |
| `to_list()` | O(n) | O(n) | Copies values into a Python list. |
| Forward iteration | O(n) | O(1) | Bounded by the size captured at iterator creation. |
| Reverse iteration | O(n) | O(1) | Walks backward through `prev` links. |

### LinkedDeque Mutations

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `append_left(value)` / `appendleft(value)` | O(1) | O(1) | Relinks the old head. |
| `append_right(value)` / `append(value)` | O(1) | O(1) | Relinks the old tail. |
| `pop_left()` / `popleft()` | O(1) | O(1) | Unlinks `head`. |
| `pop_right()` / `pop()` | O(1) | O(1) | Unlinks `tail`. |
| `insert(index, value)` | O(min(i, n - i)) | O(1) | Ends are O(1); middle walks from the closer end. |
| `extend(iterable)` | O(m) | O(1) or O(n) | Self-extension snapshots first. |
| `extend_left(iterable)` / `extendleft` | O(m) | O(1) or O(n) | Prepends each incoming item; final order is reversed. |
| `remove(value)` | O(n) | O(1) | Removes the first matching value. |
| `remove_all(value)` | O(n) | O(1) | One traversal; stores `next` before unlinking. |
| `replace(old, new)` | O(n) | O(1) | Updates node data only. |
| `reverse()` | O(n) | O(1) | Swaps every node's `prev` and `next`. |
| `rotate(k)` | O(k mod n) | O(1) | Repeatedly moves one end node to the other end. |
| `clear()` | O(n) | O(1) | Detaches every node before resetting state. |
| `copy()` | O(n) | O(n) | Builds a new deque with the same values. |

## Space Complexity of Nodes

Each linked-list node stores one data reference plus link references:

- Singly linked node: `data` + `next`.
- Doubly linked node: `data` + `prev` + `next`.
- Circular nodes use the same fields as their linear counterparts, but their
  end links point back into the structure instead of to `None`.

The containers themselves store only `head`, `tail`, and `_size`, so container
state is O(1). The total memory cost for stored nodes is O(n).

## Practical Tradeoffs

Linked structures are strongest when:

- Frequent insertions or removals happen near known nodes or at the ends.
- Stable node references matter.
- The educational goal is to understand pointer repair and invariants.

Python's built-in `list` is usually faster for index-heavy workloads because
it stores values contiguously and supports O(1) random access. This project is
therefore best read as a data-structure implementation and learning artifact,
not as a replacement for Python's optimized built-ins.
