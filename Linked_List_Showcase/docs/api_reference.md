# API Reference

This package exposes educational linked structures from the `linked_list`
package. The APIs are intentionally small and inspectable so students can see
how each structure repairs links after mutation.

## Public Imports

```python
from linked_list import (
    LinkedDeque,
    LinkedList,
    MultilevelLinkedList,
    Position,
    PositionalLinkedList,
    SelfOrganizingLinkedList,
    SkipList,
    SortedLinkedList,
    SparseMatrixLinkedList,
    UnrolledLinkedList,
    to_mermaid,
)
```

## Containers

| Type | Purpose |
| --- | --- |
| `LinkedList[T]` | Classic singly, doubly, and circular linked-list variants. |
| `SortedLinkedList[T]` | Linked list that keeps values in ascending order. |
| `LinkedDeque[T]` | Double-ended queue with direct left and right operations. |
| `SkipList[T]` | Probabilistic ordered set with `floor` and `ceiling` helpers. |
| `UnrolledLinkedList[T]` | Linked sequence where each node stores a small block. |
| `MultilevelLinkedList[T]` | Nested linked list with sibling and child chains. |
| `PositionalLinkedList[T]` | Doubly linked list with stable `Position[T]` handles. |
| `SelfOrganizingLinkedList[T]` | Adaptive list with move-to-front, transpose, and frequency strategies. |
| `SparseMatrixLinkedList[T]` | Sparse matrix storing non-zero cells in row and column chains. |

## Construction

`LinkedList` accepts either an iterable of initial values or a list type plus
optional values:

```python
empty = LinkedList()
numbers = LinkedList([1, 2, 3])
doubly = LinkedList("doubly", [1, 2, 3])
ring = LinkedList("doubly_circular", ["intro", "main", "credits"])
```

The supported list types are `singly`, `doubly`, `singly_circular`, and
`doubly_circular`. The other sequence containers also accept iterable-first
construction where it fits their API.

## Typing

The containers are generic at the public API boundary:

```python
items: LinkedList[int] = LinkedList([1, 2, 3])
numbers: LinkedDeque[int] = LinkedDeque([1, 2, 3])
names: SkipList[str] = SkipList(["Ada", "Grace"])
ratings: SparseMatrixLinkedList[float] = SparseMatrixLinkedList.from_entries(
    3,
    3,
    [(0, 2, 4.5)],
)
```

Internal nodes still store `Any` because the code is designed for teaching and
debugging. The generic aliases are for user-facing annotations and editor/mypy
friendliness.

Index-based APIs, bounded search arguments, count-limited replacement methods,
selected constructor options such as `node_capacity` and `max_level`, and
sparse-matrix coordinates accept normal integers and integer-like objects that
implement Python's `__index__` protocol. Slice access remains available on
sequence-like containers.

## Visualization

`to_mermaid(values)` converts any iterable sequence into a Mermaid flowchart.
It is meant for docs, notebooks, and debugging small examples:

```python
queue = LinkedDeque(["ingest", "transform", "load"])
print(to_mermaid(queue, title="ETL queue"))
```

For large structures or live iterators, pass `max_items` so the diagram stays
readable and bounded. Pass `None` only when you intentionally want to render
every item from a finite iterable.

## Sparse Matrix Arithmetic

`SparseMatrixLinkedList` supports custom `zero` sentinels for storage and
dense round-tripping. Row sums, column sums, trace, matrix arithmetic, scalar
multiplication, and matrix-vector multiplication require `zero=0`, because
those operations skip missing cells and therefore rely on absent coordinates
behaving like numeric additive zero.
