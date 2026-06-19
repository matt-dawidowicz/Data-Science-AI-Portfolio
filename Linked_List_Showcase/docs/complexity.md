# Linked Structure Complexity Guide

This guide explains the time and space complexity of the linked-list,
sorted-list, deque, skip-list, unrolled-list, multilevel-list,
positional-list, self-organizing-list, and sparse-matrix containers in this
repository.

The symbols used below are:

- `n`: number of values already stored in the container.
- `m`: number of incoming values from another iterable or list.
- `k`: number of positions rotated or number of replacements requested.
- `r`: number of values that actually match a removal or replacement target.
- `h`: height of a skip-list node or active skip-list level count.
- `b`: maximum number of values per unrolled-list block.
- `z`: number of stored non-zero sparse-matrix cells.
- `R` and `C`: sparse-matrix row and column counts.
- `p`: number of sparse multiplication products actually considered.

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
| Forward iteration | O(n) | O(1) | Bounded by the size captured at iterator creation. |
| Reverse iteration | O(n) | O(1) | Supported only by doubly linked variants. |

### LinkedList Mutation Operations

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `append(value)` | O(1) | O(1) | Uses `tail`; circular lists also repair `tail.next`. |
| `prepend(value)` | O(1) | O(1) | Uses `head`; doubly linked lists repair `prev`. |
| `insert(index, value)` | O(n) | O(1) | Head/tail inserts are O(1), middle inserts require traversal. |
| `remove(value)` | O(n) | O(1) | Removes the first match and repairs affected links. |
| `remove_all(value)` | O(n) | O(1) | Removes every match in one traversal and repairs links as it goes. |
| `remove_at(index)` | O(n) | O(1) | Edge removals delegate to `pop_front` or `pop`. |
| `replace(old, new)` | O(n) | O(1) | Updates node data only; links do not move. |
| `pop_front()` | O(1) | O(1) | Moves `head` forward and repairs circular/doubly links. |
| `pop()` on singly lists | O(n) | O(1) | Must find the node before `tail`. |
| `pop()` on doubly lists | O(n) | O(1) | Current implementation still walks for linear doubly lists. |
| `pop()` on doubly circular lists | O(1) | O(1) | Uses `tail.prev`. |
| `clear()` | O(n) | O(1) | Detaches every node before resetting state. |
| `extend(iterable)` | O(m) | O(1) or O(n) | Self-extension snapshots first; iterators are size-bounded. |
| `remove_duplicates()` | O(n) average, O(n^2) fallback | O(n) | Uses a `set` for hashable values and equality fallback for unhashable values. |

### LinkedList Algorithms

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `sort()` | O(n log n) | O(n) | Sorts a node snapshot first, then relinks after comparisons succeed. |
| `insert_sorted(value)` | O(n) | O(1) | Assumes the list is already sorted. |
| `merge(other)` | O(n + m) | O(n + m) | Uses value snapshots so `other` is not relinked or corrupted. |
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
| `remove_all(value)` | O(n) | O(1) | Inherits the base single-pass removal strategy. |
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

## SkipList Complexity

`SkipList` is an ordered set, so it stores each distinct value once. Its
probabilistic levels give logarithmic expected performance when the promotion
probability is balanced, while worst-case behavior is still linear if the
random levels are unlucky.

### SkipList Reads

| Operation | Expected Time | Worst Time | Extra Space | Notes |
| --- | --- | --- | --- | --- |
| `len(skip_list)` | O(1) | O(1) | O(1) | Reads the tracked `_size`. |
| `bool(skip_list)` | O(1) | O(1) | O(1) | Checks whether `_size` is nonzero. |
| `is_empty()` | O(1) | O(1) | O(1) | Explicit empty-state helper. |
| `value in skip_list` | O(log n) | O(n) | O(1) | Walks top-down through shortcut levels. |
| `find(value)` | O(log n) | O(n) | O(1) | Returns the stored value or `None`. |
| `floor(value)` | O(log n) | O(n) | O(1) | Finds the closest predecessor. |
| `ceiling(value)` | O(log n) | O(n) | O(1) | Finds the closest successor. |
| `first()` | O(1) | O(1) | O(1) | Reads the first bottom-level node. |
| `last()` | O(1) | O(1) | O(1) | Reads the tracked tail node. |
| Iteration | O(n) | O(n) | O(1) | Walks the fully populated bottom level. |
| Reverse iteration | O(n) | O(n) | O(n) | Builds a value snapshot, then yields it backward. |
| `to_list()` | O(n) | O(n) | O(n) | Copies bottom-level values into a list. |

### SkipList Mutations

| Operation | Expected Time | Worst Time | Extra Space | Notes |
| --- | --- | --- | --- | --- |
| Constructor from iterable | O(m log m) | O(m^2) | O(m) | Adds values one at a time and ignores duplicates. |
| `add(value)` | O(log n) | O(n) | O(h) | Finds predecessors, then links one new node through its levels. |
| `extend(iterable)` / `update(iterable)` | O(m log m + m log n) | O(m log m + mn) | O(m) | Sorts incoming values and searches the existing structure before mutation. |
| `remove(value)` / `discard(value)` | O(log n) | O(n) | O(h) | Finds predecessors, then bypasses the target on each level. |
| `pop_first()` | O(log n) | O(n) | O(h) | Reads the first value, then removes it. |
| `pop_last()` | O(log n) | O(n) | O(h) | Reads the tracked tail value, then removes it. |
| `clear()` | O(n) | O(n) | O(1) | Detaches all bottom-level nodes and resets header links. |
| `copy()` | O(n log n) | O(n^2) | O(n) | Rebuilds through normal insertion. |

### Why SkipList Is Useful Here

The linked lists in this project teach pointer repair and sequence behavior.
The skip list adds a different linked-structure idea: extra forward links can
trade memory for faster ordered lookups. It is still made of linked nodes, but
its shape is probabilistic rather than purely linear.

## UnrolledLinkedList Complexity

`UnrolledLinkedList` stores up to `b` values in each linked block. The block
chain has about `ceil(n / b)` nodes when values are well packed. Operations
that find a position walk block nodes first, then perform a small Python-list
operation inside one block.

### UnrolledLinkedList Reads

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `len(unrolled)` | O(1) | O(1) | Reads the tracked `_size`. |
| `bool(unrolled)` | O(1) | O(1) | Checks whether `_size` is nonzero. |
| `is_empty()` | O(1) | O(1) | Explicit empty-state helper. |
| `peek_front()` / `peek_back()` | O(1) | O(1) | Reads the first or last block. |
| `unrolled[index]` | O(n / b + b) | O(1) | Walks from the closer end, then indexes inside one block. |
| `unrolled[start:stop:step]` | O(n + s) | O(s) | Builds a value snapshot and returns a new unrolled list. |
| `get(index, default)` | O(n / b + b) | O(1) | Strict indexing wrapped with a fallback. |
| `value in unrolled` | O(n) | O(1) | Scans values until a match is found. |
| `count(value)` | O(n) | O(1) | Scans all values. |
| `index(value)` / `find(value)` | O(n) | O(n) | Uses a value snapshot for Python index semantics. |
| `to_list()` | O(n) | O(n) | Copies all values. |
| `to_blocks()` | O(n) | O(n) | Copies each block layout. |
| Forward/reverse iteration | O(n) | O(1) | Walks block nodes and in-block values. |

### UnrolledLinkedList Mutations

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `append(value)` | O(1) amortized | O(1) | Appends into the tail block or adds one new block. |
| `prepend(value)` | O(b) | O(1) | Inserts into the head block or adds one new block. |
| `insert(index, value)` | O(n / b + b) | O(1) | Locates a block, splits if full, then inserts inside a block. |
| `extend(iterable)` / `merge(iterable)` | O(m) | O(1) or O(n) | Self-extension snapshots first. |
| `pop()` | O(b) | O(1) | Removes from the tail block, then may rebalance. |
| `pop_front()` | O(b) | O(1) | Removes from the head block, then may rebalance. |
| `remove_at(index)` | O(n / b + b) | O(1) | Locates a block, removes one value, then rebalances. |
| `remove(value)` | O(n + b) | O(1) | Scans for the first match, then rebalances. |
| `remove_all(value)` | O(n) | O(n) | Builds kept values and rebuilds blocks if anything changed. |
| `replace(old, new)` | O(n) | O(n) | Computes updated values before rebuilding. |
| `remove_duplicates()` | O(n) average, O(n^2) fallback | O(n) | Uses hashing when possible and equality fallback for unhashable values. |
| `clear()` | O(n / b) | O(1) | Detaches each block node. |

### UnrolledLinkedList Algorithms

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `sort()` | O(n log n) | O(n) | Sorts values before rebuilding so comparison errors are atomic. |
| `reverse()` | O(n) | O(n) | Rebuilds from reversed values. |
| `rotate(k)` | O(n) | O(n) | Rebuilds from a rotated value snapshot. |
| `map(func)` | O(n) | O(n) | Builds a new unrolled list. |
| `filter(predicate)` | O(n) | O(n) | Builds a new unrolled list. |
| `reduce(func)` | O(n) | O(1) | Delegates to `functools.reduce`. |
| `copy()` | O(n) | O(n) | Copies block nodes but not stored values. |
| `deep_copy()` | O(n + d) | O(n + d) | Deep-copies stored values too. |

## MultilevelLinkedList Complexity

`MultilevelLinkedList` can be read as a hierarchy or as a depth-first
sequence. The implementation tracks the total number of reachable nodes, so
`len()` is constant-time even though traversal may cross child chains.

### MultilevelLinkedList Reads

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `len(multilevel)` | O(1) | O(1) | Reads the tracked total node count. |
| `bool(multilevel)` | O(1) | O(1) | Checks whether `_size` is nonzero. |
| `is_empty()` | O(1) | O(1) | Explicit empty-state helper. |
| `peek_front()` | O(1) | O(1) | Reads the top-level head. |
| `peek_back()` | O(n) | O(1) | Locates the final depth-first node. |
| `multilevel[index]` | O(n) | O(1) | Walks depth-first to the requested node. |
| `multilevel[start:stop:step]` | O(n + s) | O(s) | Builds a flat value snapshot and sliced flat list. |
| `to_list("depth_first")` | O(n) | O(n) | Copies depth-first values. |
| `to_list("breadth_first")` | O(n) | O(w) | Uses a queue; `w` is the widest pending frontier. |
| `to_top_level_list()` | O(t) | O(t) | Copies only `t` top-level values. |
| `to_nested_list()` | O(n) | O(n) | Recursively snapshots hierarchy. |
| `find(value)` / `find_node(value)` | O(n) | O(1) | Depth-first scan. |
| `path_to(value)` | O(n) | O(depth) | Recursively tracks sibling indexes. |
| `child_values(parent)` | O(n + c) | O(c) | Resolves parent, then copies `c` direct children. |
| `value in multilevel` | O(n) | O(1) | Depth-first scan. |

### MultilevelLinkedList Mutations

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `append(value)` | O(1) | O(1) | Uses the top-level tail. |
| `prepend(value)` | O(1) | O(1) | Updates the top-level head. |
| `extend(iterable)` / `merge(iterable)` | O(m) | O(1) or O(n) | Self-extension snapshots first. |
| `insert(index, value)` | O(n) | O(1) | Finds a depth-first reference and inserts as a sibling. |
| `append_child(parent, value)` | O(n + c) | O(1) | Resolves parent, then walks to child-chain tail. |
| `prepend_child(parent, value)` | O(n) | O(1) | Resolves parent and updates child head. |
| `extend_child(parent, iterable)` | O(n + c + m) | O(m) | Materializes incoming values, then appends children. |
| `detach_children(parent)` | O(n + c) | O(1) | Moves direct child chain into a new list. |
| `remove(value)` | O(n + s) | O(depth) | Finds a node and removes its subtree of size `s`. |
| `remove(..., promote_children=True)` | O(n + c) | O(depth) | Removes one node and splices in direct children. |
| `remove_all(value)` | O(n * r) | O(depth) | Repeatedly removes the first matching node. |
| `remove_at(index)` | O(n + s) | O(depth) | Finds by depth-first index, then removes a subtree. |
| `pop()` | O(n) | O(depth) | Removes the final depth-first node. |
| `pop_front()` | O(c) | O(1) | Removes the head and promotes its direct children. |
| `clear()` | O(n) | O(depth) | Recursively detaches every `next` and `child` link. |

### MultilevelLinkedList Algorithms

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `flatten("depth_first")` | O(n) | O(n) | Rewires existing nodes in depth-first order. |
| `flatten("breadth_first")` | O(n) | O(n) | Rewires existing nodes in breadth-first order. |
| `flattened(order)` | O(n) | O(n) | Builds a new flat list. |
| `reverse()` | O(n) | O(depth) | Reverses every sibling chain recursively. |
| `sort()` | O(n log n) | O(n) | Sorts values and rebuilds a flat list after comparisons succeed. |
| `rotate(k)` | O(n) | O(n) | Rebuilds a flat rotated list. |
| `remove_duplicates()` | O(n) average, O(n^2) fallback | O(n) | Keeps first depth-first occurrences and rebuilds flat. |
| `map(func)` | O(n) | O(n) | Builds a new hierarchy with transformed values. |
| `filter(predicate)` | O(n) | O(n) | Builds a new flat list of accepted values. |
| `reduce(func)` | O(n) | O(1) | Reduces depth-first values. |
| `copy()` | O(n) | O(n) | Copies nodes but not stored values. |
| `deep_copy()` | O(n + d) | O(n + d) | Deep-copies stored values too. |

## PositionalLinkedList Complexity

`PositionalLinkedList` is a doubly linked sequence with stable `Position`
handles. Numeric access still walks through the list, but operations that
already have a valid position can relink locally.

### PositionalLinkedList Reads

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `len(positional)` | O(1) | O(1) | Reads the tracked `_size`. |
| `bool(positional)` / `is_empty()` | O(1) | O(1) | Checks whether `_size` is nonzero. |
| `first_position()` / `last_position()` | O(1) | O(1) | Wraps `head` or `tail` in a `Position`. |
| `position_at(index)` | O(min(i, n - i)) | O(1) | Walks from the closer end. |
| `before(position)` / `after(position)` | O(1) | O(1) | Validates the handle, then reads one link. |
| `positional[index]` | O(min(i, n - i)) | O(1) | Uses the same closer-end lookup. |
| `positional[start:stop:step]` | O(n + s) | O(s) | Snapshots values, slices, and rebuilds. |
| `get(index, default)` | O(min(i, n - i)) | O(1) | Strict indexing wrapped with a fallback. |
| `find(value)` / `index(value)` | O(n) | O(1) | Scans values from the head. |
| `count(value)` | O(n) | O(1) | Counts matching values. |
| `positions()` / iteration | O(n) | O(1) | Yields values or position handles in order. |
| Reverse iteration | O(n) | O(1) | Walks backward through `prev` links. |
| `to_list()` | O(n) | O(n) | Copies visible values into a Python list. |

### PositionalLinkedList Mutations

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `add_first(value)` / `add_last(value)` | O(1) | O(1) | Updates `head`, `tail`, and neighbor links. |
| `add_before(position, value)` | O(1) | O(1) | Validates `position`, then relinks locally. |
| `add_after(position, value)` | O(1) | O(1) | Validates `position`, then relinks locally. |
| `insert(index, value)` | O(min(i, n - i)) | O(1) | Locates an index, then inserts locally. |
| `extend(iterable)` / `merge(iterable)` | O(m) | O(1) or O(n) | Self-extension snapshots first. |
| `delete(position)` | O(1) | O(1) | Validates and unlinks the exact node. |
| `replace(position, value)` | O(1) | O(1) | Changes one node's value. |
| `move_to_front(position)` / `move_to_back(position)` | O(1) | O(1) | Detaches one node and relinks it at an end. |
| `move_before(position, target)` | O(1) | O(1) | Relinks one known node before another. |
| `move_after(position, target)` | O(1) | O(1) | Relinks one known node after another. |
| `swap(first, second)` | O(1) | O(1) | Swaps stored values, not nodes. |
| `remove(value)` | O(n) | O(1) | Finds the first matching value, then unlinks it. |
| `remove_all(value)` | O(n) | O(1) | Removes matches in one traversal. |
| `remove_at(index)` | O(min(i, n - i)) | O(1) | Locates by index, then deletes. |
| `pop_first()` / `pop_last()` | O(1) | O(1) | Unlinks an end node. |
| `clear()` | O(n) | O(1) | Detaches every node and invalidates ownership. |
| `reverse()` | O(n) | O(1) | Swaps `prev` and `next` on each node. |
| `rotate(k)` | O(n) | O(n) | Builds a node snapshot and relinks in rotated order. |
| `sort()` | O(n log n) | O(n) | Sorts nodes before relinking so failures are atomic. |
| `remove_duplicates()` | O(n) average, O(n^2) fallback | O(n) | Uses hashing when possible and equality fallback otherwise. |
| `map(func)` / `filter(predicate)` | O(n) | O(n) | Builds a new positional list. |
| `reduce(func)` | O(n) | O(1) | Delegates to `functools.reduce`. |
| `copy()` / `deep_copy()` | O(n) or O(n + d) | O(n) or O(n + d) | Copies nodes, and optionally stored values. |

## SelfOrganizingLinkedList Complexity

`SelfOrganizingLinkedList` remains a linear linked list, so worst-case search
is still O(n). Its value is adaptive behavior: successful accesses can move
hot values closer to the front so skewed future searches inspect fewer nodes.

### SelfOrganizingLinkedList Reads

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `len(self_org)` | O(1) | O(1) | Reads the tracked `_size`. |
| `bool(self_org)` / `is_empty()` | O(1) | O(1) | Checks whether `_size` is nonzero. |
| `self_org[index]` | O(min(i, n - i)) | O(1) | Static lookup from the closer end. |
| `self_org[start:stop:step]` | O(n + s) | O(s) | Builds a sliced list with reset counts. |
| `get(index, default)` | O(min(i, n - i)) | O(1) | Static lookup wrapped with a fallback. |
| `value in self_org` / `contains_static(value)` | O(n) | O(1) | Scans without recording an access. |
| `find(value)` / `search(value)` | O(n) | O(1) | Finds the first match, records access, and reorganizes. |
| `access(index)` | O(min(i, n - i) + a) | O(1) | Finds by index and applies the selected strategy. |
| `access_count(value)` | O(n) | O(1) | Finds the first matching node without reorganizing. |
| `to_access_counts()` | O(n) | O(n) | Copies values and counts. |
| Forward/reverse iteration | O(n) | O(1) | Walks `next` or `prev` links. |

The `a` term for `access(index)` is O(1) for `move_to_front`, `transpose`, and
`none`, and O(n) worst case for `frequency_count` because the node may bubble
through many lower-frequency predecessors.

### SelfOrganizingLinkedList Mutations

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `append(value)` / `prepend(value)` | O(1) | O(1) | Updates an end of the doubly linked chain. |
| `insert(index, value)` | O(min(i, n - i)) | O(1) | Locates a position, then relinks locally. |
| `extend(iterable)` / `merge(iterable)` | O(m) | O(1) or O(n) | Self-extension snapshots first. |
| `remove(value)` | O(n) | O(1) | Finds and removes the first match. |
| `remove_all(value)` | O(n) | O(1) | Removes all matches in one traversal. |
| `remove_at(index)` | O(min(i, n - i)) | O(1) | Locates by index, then unlinks. |
| `pop_front()` / `pop()` | O(1) | O(1) | Removes an end node. |
| `replace(old, new)` | O(n) | O(1) | Updates matching node values without relinking. |
| `reset_counts()` | O(n) | O(1) | Sets every access count to zero. |
| `set_strategy(strategy)` | O(n log n) or O(1) | O(n) or O(1) | Frequency-count reorders by count; other strategies only set a field. |
| `reverse()` | O(n) | O(1) | Swaps `prev` and `next` on each node. |
| `rotate(k)` | O(n) | O(n) | Relinks a node snapshot in rotated order. |
| `sort()` | O(n log n) | O(n) | Sorts nodes while preserving access counts. |
| `remove_duplicates()` | O(n) average, O(n^2) fallback | O(n) | Supports hashable and unhashable values. |
| `map(func)` / `filter(predicate)` | O(n) | O(n) | Builds a new list with reset counts. |
| `copy()` / `deep_copy()` | O(n) or O(n + d) | O(n) or O(n + d) | Can preserve or reset access counts. |

## SparseMatrixLinkedList Complexity

`SparseMatrixLinkedList` stores only cells whose value differs from the
configured `zero`. Each stored cell is linked into one sorted row chain and
one sorted column chain.

### SparseMatrixLinkedList Reads

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `matrix.shape` | O(1) | O(1) | Reads row and column counts. |
| `len(matrix)` | O(1) | O(1) | Reads the stored non-zero count. |
| `bool(matrix)` / `is_empty()` | O(1) | O(1) | Checks whether any cell is stored. |
| `density()` | O(1) | O(1) | Divides stored cells by `R * C`. |
| `matrix[row, col]` / `get(row, col)` | O(r_i) | O(1) | Scans row `i` until the target column. |
| `(row, col) in matrix` | O(r_i) | O(1) | Validates bounds, then searches one row chain. |
| `row_items(row)` | O(r_i) | O(r_i) | Copies non-zero cells from one row. |
| `column_items(col)` | O(c_j) | O(c_j) | Copies non-zero cells from one column. |
| `items()` / `values()` | O(z) | O(1) | Iterates stored cells in row-major order. |
| `to_entries()` | O(z) | O(z) | Copies row-major triples. |
| `to_dense()` | O(R * C + z) | O(R * C) | Fills a dense matrix with zero values, then writes stored cells. |
| `row_sum(row)` | O(r_i) | O(1) | Requires `zero=0`; sums stored values in one row. |
| `column_sum(col)` | O(c_j) | O(1) | Requires `zero=0`; sums stored values in one column. |
| `trace()` | O(R + z) | O(1) | Requires `zero=0`; looks up each diagonal cell in its row chain. |

Here `r_i` is the number of stored cells in row `i`, and `c_j` is the number
of stored cells in column `j`.

In the mutation and algorithm tables below, `r + c` means the relevant row
and column chain lengths for the cells being inserted, updated, or removed.

### SparseMatrixLinkedList Mutations

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| Constructor from entries | O(m * (r + c)) | O(m) | Inserts each non-zero entry into row and column chains. |
| `from_dense(dense)` | O(R * C + z * (r + c)) | O(R * C) | Reads every dense cell, then stores non-zero values. |
| `set(row, col, value)` | O(r_i + c_j) | O(1) | Updates, inserts, or removes one cell. |
| `remove(row, col)` | O(r_i + c_j) | O(1) | Unlinks from both row and column chains. |
| `pop(row, col, default)` | O(r_i + c_j) | O(1) | Finds and removes one stored cell. |
| `clear()` | O(z) | O(1) | Detaches all stored links and resets heads. |
| `prune()` | O(z * (r + c)) | O(z) | Removes stored cells that now equal zero. |

### SparseMatrixLinkedList Algorithms

| Operation | Time | Extra Space | Notes |
| --- | --- | --- | --- |
| `copy()` | O(z * (r + c)) | O(z) | Rebuilds row and column chains. |
| `deep_copy()` | O(z * (r + c) + d) | O(z + d) | Deep-copies stored values and zero. |
| `transpose()` | O(z * (r + c)) | O(z) | Rebuilds with swapped row and column indexes. |
| `add_matrix(other)` | O(z + z_other * (r + c)) | O(z + z_other) | Requires `zero=0`; copies left, then adds right entries. |
| `subtract_matrix(other)` | O(z + z_other * (r + c)) | O(z + z_other) | Requires `zero=0`; copies left, then subtracts right entries. |
| `scalar_multiply(scalar)` | O(z * (r + c)) | O(z) | Requires `zero=0`; rebuilds and prunes products equal to zero. |
| `multiply_vector(vector)` | O(z + C) | O(R + C) | Requires `zero=0`; materializes the vector, then visits stored cells. |
| `matmul(other)` | O(p + z_result * (r + c)) | O(z_result) | Requires matching `zero=0`; multiplies only pairs where left column has right-row entries. |
| `map_values(func)` | O(z * (r + c)) | O(z) | Rebuilds from transformed stored values. |

## Space Complexity of Nodes

Each linked-list node stores one data reference plus link references:

- Singly linked node: `data` + `next`.
- Doubly linked node: `data` + `prev` + `next`.
- Circular nodes use the same fields as their linear counterparts, but their
  end links point back into the structure instead of to `None`.
- Skip-list nodes store `data` plus `h` forward links. Most nodes are short;
  only a few are promoted to high shortcut levels.
- Unrolled-list nodes store a Python value block plus `next` and `prev` block
  links. With capacity `b`, there are usually far fewer nodes than values.
- Multilevel-list nodes store `data`, `next`, and `child`, which makes nested
  structures possible without adding backward links.
- Positional-list nodes store `data`, `prev`, `next`, and an owner reference
  used to validate stale or foreign `Position` handles.
- Self-organizing-list nodes store `data`, an access count, `prev`, and
  `next`.
- Sparse-matrix nodes store `row`, `col`, `value`, a `right` row-chain link,
  and a `down` column-chain link.

The containers themselves store only `head`, `tail`, and `_size`, so container
state is O(1) for linked lists, deques, positional lists, self-organizing
lists, unrolled lists, and multilevel lists. Skip lists also store a fixed-size
header of `max_level` links. Sparse matrices store row-head and column-head
dictionaries with at most `R + C` entries total. The expected total node-link
storage for a skip list is O(n) for a fixed promotion probability, while
sparse-matrix node storage is O(z).

## Practical Tradeoffs

Linked structures are strongest when:

- Frequent insertions or removals happen near known nodes or at the ends.
- Stable node references matter.
- The educational goal is to understand pointer repair and invariants.
- Chunked linked storage, nested traversal, probabilistic ordered lookup,
  adaptive search, stable positions, or sparse row/column chains are the
  concept being demonstrated.

Python's built-in `list` is usually faster for index-heavy workloads because
it stores values contiguously and supports O(1) random access. This project is
therefore best read as a data-structure implementation and learning artifact,
not as a replacement for Python's optimized built-ins.
