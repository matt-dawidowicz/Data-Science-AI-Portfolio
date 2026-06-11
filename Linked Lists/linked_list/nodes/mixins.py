"""Small node mixins for next, previous, and circular links."""

from typing import Optional


class NextMixin:
    """Provide a ``next`` pointer for a node."""

    def __init__(self, next_node: Optional[object] = None) -> None:
        """Initialize the forward link."""
        self.next = next_node


class PrevMixin:
    """Provide a ``prev`` pointer for a node."""

    def __init__(self, prev_node: Optional[object] = None) -> None:
        """Initialize the backward link."""
        self.prev = prev_node


class CircularMixin:
    """Turn absent node links into self-references."""

    def make_circular(self) -> None:
        """Point missing next and previous links back to this node."""
        if getattr(self, "next", None) is None:
            self.next = self
        if hasattr(self, "prev") and getattr(self, "prev", None) is None:
            self.prev = self
