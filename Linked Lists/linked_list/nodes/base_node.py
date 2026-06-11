"""Base node shared by linked-list node variants."""

from typing import Any


class BaseNode:
    """Store the data payload shared by all node types."""

    def __init__(self, data: Any) -> None:
        """Initialize the node with its payload."""
        self.data = data

    def __repr__(self) -> str:
        """Return a debugging representation for the node."""
        return f"{self.__class__.__name__}({self.data!r})"
