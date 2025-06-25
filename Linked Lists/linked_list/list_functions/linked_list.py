from .base import BaseLinkedList
from .access import Access
from .iteration import Iteration
from .mutation import Mutation
from .sort_merge import SortMerge
from .functional import Functional
from .utility import Utility

class LinkedList(BaseLinkedList,
                 Access,
                 Iteration,
                 Mutation,
                 SortMerge,
                 Functional,
                 Utility):
    pass
