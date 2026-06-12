"""Concrete linked-list type assembled from behavior mixins.

The project uses composition through mixins to keep each behavior group small:
access methods live in one file, mutation methods in another, and so on. The
final ``LinkedList`` type combines those pieces into the class users import.

For someone reading the code for the first time, this file is the table of
contents. The real behavior lives in the inherited mixins listed below.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from .access import Access
from .base import BaseLinkedList
from .functional import Functional
from .iteration import Iteration
from .mutation import Mutation
from .sort_merge import SortMerge
from .utility import Utility

T = TypeVar("T")


class LinkedList(
    BaseLinkedList,
    Access,
    Iteration,
    Mutation,
    SortMerge,
    Functional,
    Utility,
    Generic[T],
):
    """Linked list supporting singly, doubly, and circular variants.

    The selected ``list_type`` decides which node links exist and which
    invariants operations must preserve.

    Supported ``list_type`` values are:

    - ``"singly"``: each node has ``next`` only.
    - ``"doubly"``: each node has ``prev`` and ``next``.
    - ``"singly_circular"``: ``tail.next`` points back to ``head``.
    - ``"doubly_circular"``: both end links wrap around.
    """

    pass
