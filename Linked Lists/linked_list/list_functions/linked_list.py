"""Concrete linked-list type assembled from behavior mixins.

The project uses composition through mixins to keep each behavior group small:
access methods live in one file, mutation methods in another, and so on. The
final ``LinkedList`` type combines those pieces into the class users import.
"""

from .base import BaseLinkedList
from .access import Access
from .functional import Functional
from .iteration import Iteration
from .mutation import Mutation
from .sort_merge import SortMerge
from .utility import Utility


class LinkedList(
    BaseLinkedList,
    Access,
    Iteration,
    Mutation,
    SortMerge,
    Functional,
    Utility,
):
    """Linked list supporting singly, doubly, and circular variants.

    The selected ``list_type`` decides which node links exist and which
    invariants operations must preserve.
    """

    pass
