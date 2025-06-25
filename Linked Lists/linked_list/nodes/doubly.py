from typing import Optional, Any
from .base_node import BaseNode
from .mixins import NextMixin, PrevMixin, CircularMixin

class DoublyLinkedNode(BaseNode, PrevMixin, NextMixin):
    def __init__(
        self,
        data: Any,
        prev_node: Optional["DoublyLinkedNode"] = None,
        next_node: Optional["DoublyLinkedNode"] = None,
    ) -> None:
        BaseNode.__init__(self, data)
        PrevMixin.__init__(self, prev_node)
        NextMixin.__init__(self, next_node)

        if prev_node is not None and not isinstance(prev_node, DoublyLinkedNode):
            raise TypeError("prev_node must be a DoublyLinkedNode or None")
        if next_node is not None and not isinstance(next_node, DoublyLinkedNode):
            raise TypeError("next_node must be a DoublyLinkedNode or None")

class DoublyCircularLinkedNode(BaseNode, PrevMixin, NextMixin, CircularMixin):
    def __init__(
        self,
        data: Any,
        prev: Optional["DoublyCircularLinkedNode"] = None,
        next_node: Optional["DoublyCircularLinkedNode"] = None,
    ) -> None:
        BaseNode.__init__(self, data)
        PrevMixin.__init__(self, prev)
        NextMixin.__init__(self, next_node)
        CircularMixin.make_circular(self)

    def __repr__(self) -> str:
        prev_info = "self" if self.prev is self else repr(self.prev.data)
        next_info = "self" if self.next is self else repr(self.next.data)
        return f"DoublyCircularLinkedNode(data={self.data!r}, prev={prev_info}, next={next_info})"
