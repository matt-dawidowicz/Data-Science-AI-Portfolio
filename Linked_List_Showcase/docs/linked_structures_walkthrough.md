# Linked Structures Walkthrough

This guide explains the linked-structure package as if you are reading the
code for the first time. It focuses on mental models, invariants, and how to
trace the algorithms by hand.

The package is educational. Python's built-in `list`, `collections.deque`, and
scientific libraries are usually faster for production workloads. The value
here is seeing how linked structures work internally and how small pointer
mistakes can affect the whole container.

## Reading Order

Start with the files in this order:

1. `linked_list/nodes/`
2. `linked_list/list_functions/base.py`
3. `linked_list/list_functions/iteration.py`
4. `linked_list/list_functions/mutation.py`
5. `linked_list/list_functions/linked_list.py`
6. The standalone containers such as `deque.py`, `skip_list.py`, and
   `sparse_matrix.py`

The node files introduce the fields. The mixin files show how the classic
`LinkedList` is assembled. The standalone containers then show variations on
the same linked-structure theme.

## Core Terms

`node`
: A small object that stores a value and one or more links.

`head`
: The first visible node in a chain.

`tail`
: The last visible node in a chain.

`next`
: A link from one node to the node after it.

`prev`
: A link from one node to the node before it.

`child`
: A link from a multilevel node down into a nested chain.

`right` and `down`
: Sparse-matrix links. `right` moves through a row, and `down` moves through a
  column.

`invariant`
: A promise that must remain true after every operation. For example,
  `len(container)` should match the number of nodes reachable from `head`.

## Classic LinkedList

The core `LinkedList` supports four shapes:

- `singly`
- `doubly`
- `singly_circular`
- `doubly_circular`

All four share the same public class. The selected `list_type` controls which
node class is created and which links must be repaired.

```python
values = LinkedList([1, 2, 3])
doubly = LinkedList("doubly", [1, 2, 3])
circular = LinkedList("singly_circular", ["A", "B", "C"])
```

### Singly Linked

A singly linked node has a value and a `next` pointer:

```text
head
 |
 v
[1] -> [2] -> [3] -> None
                  ^
                  |
                 tail
```

Forward traversal is easy. Removing the tail is harder because a singly linked
node does not know who points to it. The list often needs to walk from `head`
to find the previous node.

### Doubly Linked

A doubly linked node has `prev` and `next`:

```text
None <- [1] <-> [2] <-> [3] -> None
        ^                 ^
        |                 |
       head              tail
```

The extra `prev` link makes reverse traversal and tail-side repairs easier.
The cost is one more pointer per node and one more link to keep correct.

### Circular Linked

Circular lists do not end at `None`. Their tail points back to the head:

```text
head
 |
 v
[1] -> [2] -> [3]
 ^             |
 |_____________|
```

This is why iteration must be bounded by `_size`. A loop that waits for
`None` would never stop on a circular list.

## Mutation Checklist

When reading any method that changes a linked list, check these questions:

1. Does `head` still point to the first visible node?
2. Does `tail` still point to the last visible node?
3. Does `_size` match the number of visible values?
4. For doubly linked lists, do neighboring nodes agree about `prev` and
   `next`?
5. For circular lists, does `tail.next` point to `head`?
6. For doubly circular lists, does `head.prev` point to `tail`?
7. Are removed nodes detached so old references do not keep stale links?

The tests use these same ideas. They do not only check final values; they also
walk internal links after many operations.

## Choosing a Structure

Use this section when you know the problem shape but do not yet know which
container to inspect.

| Structure | Best educational use case | Main idea |
| --- | --- | --- |
| `LinkedList("singly")` | Forward-only traversal and basic pointer repair | Small nodes with only `next` links |
| `LinkedList("doubly")` | Reverse traversal and local deletion | Extra `prev` links make backward movement possible |
| `LinkedList("singly_circular")` | Round-robin examples and finite cyclic traversal | `tail.next` returns to `head` |
| `LinkedList("doubly_circular")` | Two-way cyclic navigation | Both ends wrap around |
| `LinkedDeque` | Queues, stacks, and double-ended workflows | Direct mutation at both ends |
| `SortedLinkedList` | Maintaining an ordering invariant | API behavior is constrained by sorted order |
| `SkipList` | Ordered-set lookup and nearest neighbors | Random shortcut levels speed average searches |
| `UnrolledLinkedList` | Block splitting and storage tradeoffs | Nodes store small arrays of values |
| `MultilevelLinkedList` | Outlines, menus, and nested lists | `child` links create hierarchy |
| `PositionalLinkedList` | Mutating around known locations | Stable `Position` handles identify nodes |
| `SelfOrganizingLinkedList` | Adaptive search demonstrations | Successful searches change future order |
| `SparseMatrixLinkedList` | Mostly-zero grids and sparse storage | One cell belongs to row and column chains |

These use cases are intentionally framed around learning and inspection. For
production code, Python's standard library and scientific ecosystem often
provide faster and more battle-tested choices.

## Real-World Occasions

The table below connects the educational structures to practical software
situations. The point is not that every production system literally uses this
exact Python class. The point is that these are the product and system shapes
where the same linked-structure tradeoffs appear.

| Structure | Real products and systems | Good occasion to reach for the idea |
| --- | --- | --- |
| `LinkedList("singly")` | Allocator free lists, packet chains, compiler token streams, simple processing pipelines | Data moves forward, old nodes can be discarded, and backward navigation is unnecessary |
| `LinkedList("doubly")` | Browser history, playlists, photo viewers, undo/redo stacks, LRU cache ordering | Users or algorithms need to move to the previous and next neighbor |
| `LinkedList("singly_circular")` | Round-robin CPU scheduling, rotating worker pools, multiplayer turn order, sensor polling | The same participants repeat in a fixed cycle |
| `LinkedList("doubly_circular")` | Carousel widgets, gallery navigation, circular media queues, ring menus | A user should be able to wrap around in either direction |
| `LinkedDeque` | Job queues, BFS in crawlers or route planners, sliding-window analytics, message buffers | Work arrives or leaves from both ends, or a queue/stack needs one shared structure |
| `SortedLinkedList` | Small timer queues, ordered event feeds, ranked waiting rooms, simple priority queues | New entries arrive over time and the list should stay sorted immediately |
| `SkipList` | Leaderboards, ordered indexes, autocomplete ranges, time-series windows, Redis-style sorted sets | Ordered search, range lookup, `floor`, or `ceiling` matters more than raw append speed |
| `UnrolledLinkedList` | Text buffers, log viewers, packet batching, cache-friendlier queues | Neighboring values are usually handled in groups, but chunks still need to split and merge |
| `MultilevelLinkedList` | File explorers, nested comments, menu systems, org charts, document outlines | Items can contain child lists and sometimes need to be flattened for display or export |
| `PositionalLinkedList` | Text editor cursors, playlist editors, timeline editors, kanban boards, drag-and-drop UIs | Code already has a handle to an item and wants to mutate around that exact item |
| `SelfOrganizingLinkedList` | Command palettes, contact lists, autocomplete candidates, small embedded lookup menus | Repeatedly accessed values should drift closer to the front over time |
| `SparseMatrixLinkedList` | Recommender ratings, graph adjacency matrices, search indexes, ML feature matrices, simulations | The data is mostly empty and storing explicit zeros would waste memory |

For real production Python, the final implementation choice often changes:
`collections.deque`, `dict`, `set`, NumPy, SciPy, pandas, graph libraries, or
a maintained sorted-collection package may be the right deployment tool. This
package is useful because it lets you inspect and explain the structure behind
those choices.

## LinkedDeque

`LinkedDeque` is a double-ended queue. It is built from doubly linked nodes and
keeps direct access to both ends.

Its core invariant is:

```text
head == leftmost node
tail == rightmost node
_size == number of nodes from head to tail
```

End operations are local:

- `append_left` touches the new node and old head.
- `append_right` touches the new node and old tail.
- `pop_left` unlinks the old head.
- `pop_right` unlinks the old tail.

Middle indexing is supported, but it is not the deque's main strength.

Use it when you want to understand how `collections.deque`-style end
operations can be implemented with a doubly linked chain. For production
queues, prefer `collections.deque`.

## SortedLinkedList

`SortedLinkedList` reuses the core linked-list machinery but protects a new
promise: values stay in ascending order.

That promise changes method behavior:

- `append` and `prepend` route to sorted insertion.
- `insert` is allowed only when the requested position keeps order valid.
- `reverse` and non-trivial `rotate` are rejected.
- `replace` rebuilds from a sorted snapshot because a changed value may need
  to move.

This class is a good example of an invariant shaping an API. The pointers are
ordinary linked-list pointers, but the container's promise is stricter.

Use it when you want to see how sorted-order rules affect mutation methods.
For production sorted sequences, prefer `bisect` with a list for simple cases
or a maintained sorted-collection package for larger workloads.

## SkipList

`SkipList` is a sorted set with multiple linked levels.

The bottom level stores every value:

```text
level 0: head -> 1 -> 3 -> 5 -> 8
```

Higher levels store shortcuts:

```text
level 2: head ----------> 5
level 1: head ----> 3 -> 5
level 0: head -> 1 -> 3 -> 5 -> 8
```

Search starts high, moves right while the next value is still before the
target, then drops down. The helper `_find_update(value)` returns the
predecessor at every level. Insertion and removal both use that same search
result.

The shape is probabilistic. Most nodes are short; a few are tall. With a
reasonable promotion probability, the average search path is much shorter than
walking the whole bottom level.

Use it to study ordered sets, `floor`, `ceiling`, and probabilistic balancing.
For production membership tests, prefer `set` or `dict` when hashing is enough.
For production ordered indexes, use a maintained sorted or tree-based library.

## UnrolledLinkedList

`UnrolledLinkedList` stores several values per node:

```text
[1, 2, 3] <-> [4, 5] <-> [6, 7, 8]
```

This reduces the number of node objects and pointer hops. The tradeoff is that
each block uses small Python-list operations inside the node.

Important operations:

- `insert` finds a block and offset.
- `_split_node` divides a full block.
- `_rebalance_after_remove` removes empty blocks, merges small neighbors, or
  borrows one value from a fuller neighbor.
- `to_blocks()` exposes the block layout for debugging and teaching.

Use it when you want to compare pure linked storage with chunked linked
storage. For production sequence work, Python's built-in `list` is usually
faster because it stores values contiguously.

## MultilevelLinkedList

`MultilevelLinkedList` adds a `child` pointer:

```text
1 -> 2 -> 5
     |
     v
     3 -> 4
```

Depth-first traversal yields:

```text
1, 2, 3, 4, 5
```

Breadth-first traversal yields:

```text
1, 2, 5, 3, 4
```

Some operations preserve hierarchy, such as `copy`, `deep_copy`, `map`, and
child insertion. Other operations flatten because their natural meaning is
sequence-wide, such as `sort`, `rotate`, `filter`, and `remove_duplicates`.

Use it to model nested outlines, menus, lightweight trees, and flattening
algorithms. For production graph or tree processing, use a domain-specific
library when you need mature traversal algorithms and interoperability.

## PositionalLinkedList

`PositionalLinkedList` introduces stable `Position` handles.

An index is just a number. If a value is inserted before that index, the number
now refers to a different node. A `Position` is different: it points to a
specific node as long as that node still belongs to the list.

That enables operations such as:

- `add_before(position, value)`
- `add_after(position, value)`
- `delete(position)`
- `replace(position, value)`
- `move_before(position, target)`
- `move_after(position, target)`

The important safety rule is validation. A position is valid only when:

- it is a `Position` object,
- it still has a node,
- the node still has an owner,
- and the owner is the exact list receiving the operation.

Deleting or clearing invalidates positions so stale handles fail clearly.

Use it when an algorithm already has a location and wants to mutate nearby.
Examples include teaching editor cursors, playlists, or textbook positional
list APIs. For production text editing, use specialized buffers or editor data
structures.

## SelfOrganizingLinkedList

`SelfOrganizingLinkedList` changes order after successful access. It still has
O(n) worst-case search, but it can improve repeated searches when the access
pattern is skewed.

Strategies:

- `move_to_front`: move the accessed node directly to `head`.
- `transpose`: swap the accessed node with its previous neighbor.
- `frequency_count`: keep higher access counts closer to the front.
- `none`: record counts without changing order.

Static reads are separate from adaptive reads:

- `value in list`, indexing, and `get` do not reorganize.
- `find`, `search`, and `access` increment counts and may move nodes.

That separation makes examples and tests predictable.

Use it when search frequency is uneven and you want to demonstrate adaptive
heuristics. For production caches, use dedicated cache structures or mappings
that match the eviction policy you need.

## SparseMatrixLinkedList

`SparseMatrixLinkedList` stores only non-zero cells. A stored cell belongs to a
row chain and a column chain at the same time:

```text
row 0: (0, 1) -> (0, 4)
row 2: (2, 0) -> (2, 3)

col 0: (2, 0)
col 1: (0, 1)
col 3: (2, 3)
col 4: (0, 4)
```

The same node object appears in both views. That means insertion and removal
must repair two chains:

- `_insert_into_row` and `_remove_from_row`
- `_insert_into_column` and `_remove_from_column`

Assigning the configured `zero` value removes a cell instead of storing it.
This is what keeps the matrix sparse after updates and numeric-zero
arithmetic.

Row sums, column sums, trace, matrix arithmetic, scalar multiplication, and
matrix-vector multiplication require `zero=0`. Custom zero sentinels are
useful for storage lessons and dense round-tripping, but the arithmetic
shortcuts intentionally require missing cells to behave like numeric additive
zero.

Use it to teach sparse storage and matrix operations without hiding the row and
column links. For production numerical work, prefer NumPy arrays or SciPy
sparse matrices.

## Why This Package Instead of Existing Python Tools

Use this package when you want the implementation to be visible. Existing
Python tools are excellent, but many of them hide the internals behind highly
optimized C code or mature library abstractions. That is exactly what you want
in production, and exactly what you do not want when the goal is to study
pointer repair.

This package is useful for:

- Learning how linked nodes are connected and disconnected.
- Teaching why `head`, `tail`, `_size`, and circular links are invariants.
- Comparing several linked-structure variants in one codebase.
- Writing portfolio explanations that connect code to data-structure theory.
- Running tests that inspect internal links after public operations.
- Experimenting without third-party runtime dependencies.

Use existing packages instead when:

- You need the fastest sequence operations: use built-in `list`.
- You need production double-ended queues: use `collections.deque`.
- You need hash lookup: use `dict` or `set`.
- You need numerical arrays or sparse linear algebra: use NumPy or SciPy.
- You need production data frames: use pandas.
- You need graph algorithms: use a graph library built for that domain.
- You need sorted collections in real applications: use a maintained
  sorted-collection package or another proven ordered-index structure.

The honest positioning is simple: this project optimizes for clarity,
coverage, and educational value. Existing libraries usually optimize for speed,
memory efficiency, and ecosystem support.

## How To Debug Pointer Bugs

When a linked structure misbehaves, use a small example and draw nodes on
paper. Then inspect the operation in phases:

1. What nodes exist before the operation?
2. Which node is being added, removed, or moved?
3. Which old links should change?
4. Which old links should stay the same?
5. Which container metadata should change?
6. Which removed nodes should be detached?

Good linked-structure tests check both visible values and hidden invariants.
That is why this project has randomized tests that compare public behavior
against Python `list` or dense matrix math, then walk internal links afterward.

## Small Example

```python
from linked_list import PositionalLinkedList, SparseMatrixLinkedList

positions = PositionalLinkedList([1, 3])
first = positions.first_position()
middle = positions.add_after(first, 2)
positions.move_to_front(middle)

print(positions.to_list())  # [2, 1, 3]

sparse = SparseMatrixLinkedList.from_dense([[1, 0, 2], [0, 3, 0]])
print(sparse.to_entries())  # [(0, 0, 1), (0, 2, 2), (1, 1, 3)]
print(sparse.multiply_vector([2, 3, 4]))  # [10, 9]
```

The positional example shows a stable handle being moved. The sparse matrix
example shows how only the non-zero cells are stored.
