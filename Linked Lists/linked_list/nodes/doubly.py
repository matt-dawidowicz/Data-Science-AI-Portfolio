"""Doubly linked node variants.

Doubly linked nodes store both directions of travel. That extra ``prev`` link
is what makes reverse iteration and right-end deque operations direct.
"""

from __future__ import annotations

from typing import Any

from .base_node import BaseNode
from .mixins import CircularMixin, NextMixin, PrevMixin


class DoublyLinkedNode(BaseNode, PrevMixin, NextMixin):
    """Node with payload, previous link, and next link."""

    def __init__(
        self,
        data: Any,
        prev_node: DoublyLinkedNode | None = None,
        next_node: DoublyLinkedNode | None = None,
    ) -> None:
        """Initialize a doubly linked node."""
        BaseNode.__init__(self, data)
        PrevMixin.__init__(self, prev_node)
        NextMixin.__init__(self, next_node)

        if prev_node is not None and not isinstance(
            prev_node, DoublyLinkedNode
        ):
            raise TypeError("prev_node must be a DoublyLinkedNode or None")
        if next_node is not None and not isinstance(
            next_node, DoublyLinkedNode
        ):
            raise TypeError("next_node must be a DoublyLinkedNode or None")


class DoublyCircularLinkedNode(BaseNode, PrevMixin, NextMixin, CircularMixin):
    """Doubly linked node whose links default to itself."""

    def __init__(
        self,
        data: Any,
        prev: DoublyCircularLinkedNode | None = None,
        next_node: DoublyCircularLinkedNode | None = None,
    ) -> None:
        """Initialize a doubly circular linked node."""
        BaseNode.__init__(self, data)
        PrevMixin.__init__(self, prev)
        NextMixin.__init__(self, next_node)
        CircularMixin.make_circular(self)

    def __repr__(self) -> str:
        """Return a representation that avoids infinite self-reference."""
        prev_info = "self" if self.prev is self else repr(self.prev.data)
        next_info = "self" if self.next is self else repr(self.next.data)
        return (
            "DoublyCircularLinkedNode("
            f"data={self.data!r}, "
            f"prev={prev_info}, "
            f"next={next_info}"
            ")"
        )
