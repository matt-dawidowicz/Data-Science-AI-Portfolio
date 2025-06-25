from typing import Optional, Any
from .base_node import BaseNode
from .mixins import NextMixin, CircularMixin

class SinglyLinkedNode(BaseNode, NextMixin):
    def __init__(self, data: Any, next_node: Optional["SinglyLinkedNode"] = None) -> None:
        BaseNode.__init__(self, data)
        NextMixin.__init__(self, next_node)
        if next_node is not None and not isinstance(next_node, SinglyLinkedNode):
            raise TypeError("next_node must be a SinglyLinkedNode or None")

class SinglyCircularLinkedNode(BaseNode, NextMixin, CircularMixin):
    def __init__(self, data: Any, next_node: Optional["SinglyCircularLinkedNode"] = None) -> None:
        BaseNode.__init__(self, data)
        NextMixin.__init__(self, next_node)
        CircularMixin.make_circular(self)
