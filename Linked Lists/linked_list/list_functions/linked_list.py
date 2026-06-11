"""Concrete linked-list type assembled from behavior mixins."""

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
    """Linked list supporting singly, doubly, and circular variants."""

    pass
