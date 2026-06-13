"""Educational linked-structure containers exposed by the package.

The package groups several related data structures behind one import surface.
They all use linked nodes in some form, but each one teaches a different
tradeoff:

- ``LinkedList`` shows the classic singly, doubly, and circular variants.
- ``LinkedDeque`` focuses on constant-time work at both ends.
- ``SortedLinkedList`` protects an ordering invariant after every mutation.
- ``SkipList`` adds probabilistic shortcut links for faster ordered lookup.
- ``UnrolledLinkedList`` stores small arrays inside linked blocks.
- ``MultilevelLinkedList`` models nested sibling and child chains.
- ``PositionalLinkedList`` exposes validated handles to known nodes.
- ``SelfOrganizingLinkedList`` adapts order after successful access.
- ``SparseMatrixLinkedList`` stores sparse row and column chains.

The individual modules contain the implementation details. This file keeps the
public API easy to discover for examples, tests, and portfolio review.
"""

from __future__ import annotations

from .deque import LinkedDeque
from .list_functions.linked_list import LinkedList
from .multilevel_list import MultilevelLinkedList
from .positional_list import Position, PositionalLinkedList
from .self_organizing_list import SelfOrganizingLinkedList
from .skip_list import SkipList
from .sorted_list import SortedLinkedList
from .sparse_matrix import SparseMatrixLinkedList
from .unrolled_list import UnrolledLinkedList
from .visualize import to_mermaid

__all__ = [
    "LinkedDeque",
    "LinkedList",
    "MultilevelLinkedList",
    "Position",
    "PositionalLinkedList",
    "SelfOrganizingLinkedList",
    "SkipList",
    "SparseMatrixLinkedList",
    "SortedLinkedList",
    "UnrolledLinkedList",
    "to_mermaid",
]
