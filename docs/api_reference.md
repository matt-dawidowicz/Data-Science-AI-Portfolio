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

## Typing

The containers are generic at the public API boundary:

```python
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

## Visualization

`to_mermaid(values)` converts any iterable sequence into a Mermaid flowchart.
It is meant for docs, notebooks, and debugging small examples:

```python
queue = LinkedDeque(["ingest", "transform", "load"])
print(to_mermaid(queue, title="ETL queue"))
```

For large structures, pass `max_items` so the diagram stays readable.
