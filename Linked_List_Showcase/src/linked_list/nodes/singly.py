"""Singly linked node variants.

Singly linked nodes can move forward through ``next`` but cannot move
backward. That one missing pointer is the central tradeoff: each node is
smaller, but operations such as removing the tail may need to traverse from
the head to find the previous node.
"""

from typing import Any

from .base_node import BaseNode
from .mixins import CircularMixin, NextMixin


class SinglyLinkedNode(BaseNode, NextMixin):
    """Node with a payload and one forward link."""

    def __init__(
        self,
        data: Any,
        next_node: "SinglyLinkedNode | None" = None,
    ) -> None:
        """Initialize a singly linked node.

        The optional ``next_node`` is validated so accidental cross-linking to
        an unrelated node type is caught early in examples and tests.
        """
        BaseNode.__init__(self, data)
        NextMixin.__init__(self, next_node)
        if next_node is not None and not isinstance(
            next_node, SinglyLinkedNode
        ):
            raise TypeError("next_node must be a SinglyLinkedNode or None")


class SinglyCircularLinkedNode(BaseNode, NextMixin, CircularMixin):
    """Singly linked node whose forward link defaults to itself.

    A one-node circular list is already a valid loop: following ``next`` from
    the node returns to the same node. Larger circular lists later replace the
    tail's ``next`` link with the current head.
    """

    def __init__(
        self,
        data: Any,
        next_node: "SinglyCircularLinkedNode | None" = None,
    ) -> None:
        """Initialize a singly circular linked node."""
        BaseNode.__init__(self, data)
        NextMixin.__init__(self, next_node)
        CircularMixin.make_circular(self)
