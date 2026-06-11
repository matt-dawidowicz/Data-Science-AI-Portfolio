"""Singly linked node variants."""

from typing import Any, Optional

from .base_node import BaseNode
from .mixins import CircularMixin, NextMixin


class SinglyLinkedNode(BaseNode, NextMixin):
    """Node with a payload and a forward link."""

    def __init__(
        self,
        data: Any,
        next_node: Optional["SinglyLinkedNode"] = None,
    ) -> None:
        """Initialize a singly linked node."""
        BaseNode.__init__(self, data)
        NextMixin.__init__(self, next_node)
        if (
            next_node is not None
            and not isinstance(next_node, SinglyLinkedNode)
        ):
            raise TypeError("next_node must be a SinglyLinkedNode or None")


class SinglyCircularLinkedNode(BaseNode, NextMixin, CircularMixin):
    """Singly linked node whose forward link defaults to itself."""

    def __init__(
        self,
        data: Any,
        next_node: Optional["SinglyCircularLinkedNode"] = None,
    ) -> None:
        """Initialize a singly circular linked node."""
        BaseNode.__init__(self, data)
        NextMixin.__init__(self, next_node)
        CircularMixin.make_circular(self)
