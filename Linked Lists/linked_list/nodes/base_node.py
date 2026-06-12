"""Base node shared by linked-list node variants.

Every linked structure is built from small node objects. The simplest useful
node has only one responsibility: hold a payload value. Directional links such
as ``next`` and ``prev`` are added by mixins and subclasses so the code can
show exactly which pointer fields each linked-list variant needs.

This separation is educational rather than performance-driven. A reader can
first understand ``BaseNode.data``, then layer on forward links, backward
links, and circular self-links one idea at a time.
"""

from __future__ import annotations

from typing import Any


class BaseNode:
    """Store the payload shared by all concrete node types.

    The node deliberately does not know which container owns it. Ownership and
    traversal rules are handled by the list classes. That keeps the node small
    and makes pointer repair visible in the container methods.
    """

    def __init__(self, data: Any) -> None:
        """Initialize the node with its payload."""
        self.data = data

    def __repr__(self) -> str:
        """Return a debugging representation for the node."""
        return f"{self.__class__.__name__}({self.data!r})"
