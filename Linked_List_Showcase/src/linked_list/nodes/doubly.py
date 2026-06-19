"""Doubly linked node variants.

Doubly linked nodes store both directions of travel. The extra ``prev`` link
costs one more reference per node, but it makes reverse iteration, tail-side
removal, and deque right-end operations direct and easy to reason about.
"""

from reprlib import recursive_repr
from typing import Any

from .._display import safe_repr_item
from .base_node import BaseNode
from .mixins import CircularMixin, NextMixin, PrevMixin


def _repr_neighbor_data(owner: object, neighbor: Any | None) -> str:
    """Return a compact representation for a circular node neighbor."""
    if neighbor is owner:
        return "self"
    if neighbor is None:
        return "None"
    return safe_repr_item(owner, neighbor.data)


class DoublyLinkedNode(BaseNode, PrevMixin, NextMixin):
    """Node with payload, previous link, and next link."""

    def __init__(
        self,
        data: Any,
        prev_node: "DoublyLinkedNode | None" = None,
        next_node: "DoublyLinkedNode | None" = None,
    ) -> None:
        """Initialize a doubly linked node.

        ``prev_node`` and ``next_node`` may be supplied when a caller already
        knows the neighboring nodes. The constructor validates those neighbors
        so a doubly linked chain does not accidentally mix node families.
        """
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
    """Doubly linked node whose links default to itself.

    In a single-node doubly circular list, both directions lead back to the
    same node. In a larger list, the container rewires ``head.prev`` and
    ``tail.next`` so traversal can wrap around in either direction.
    """

    def __init__(
        self,
        data: Any,
        prev: "DoublyCircularLinkedNode | None" = None,
        next_node: "DoublyCircularLinkedNode | None" = None,
    ) -> None:
        """Initialize a doubly circular linked node."""
        if prev is not None and not isinstance(prev, DoublyCircularLinkedNode):
            raise TypeError("prev must be a DoublyCircularLinkedNode or None")
        if next_node is not None and not isinstance(
            next_node, DoublyCircularLinkedNode
        ):
            raise TypeError(
                "next_node must be a DoublyCircularLinkedNode or None"
            )
        BaseNode.__init__(self, data)
        PrevMixin.__init__(self, prev)
        NextMixin.__init__(self, next_node)
        CircularMixin.make_circular(self)

    @recursive_repr()
    def __repr__(self) -> str:
        """Return a representation that avoids infinite self-reference."""
        prev_info = _repr_neighbor_data(self, self.prev)
        next_info = _repr_neighbor_data(self, self.next)
        return (
            "DoublyCircularLinkedNode("
            f"data={safe_repr_item(self, self.data)}, "
            f"prev={prev_info}, "
            f"next={next_info}"
            ")"
        )
