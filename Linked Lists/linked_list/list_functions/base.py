"""Base linked-list state and node creation helpers."""

from typing import Any, Optional

from ..nodes import (
    DoublyCircularLinkedNode,
    DoublyLinkedNode,
    SinglyCircularLinkedNode,
    SinglyLinkedNode,
)


class BaseLinkedList:
    """Store common linked-list metadata and construct matching nodes."""

    def __init__(self, list_type: str = "singly") -> None:
        """Initialize an empty linked list of the requested type."""
        valid_types = (
            "singly",
            "doubly",
            "singly_circular",
            "doubly_circular",
        )
        normalized_type = list_type.strip().lower()
        if normalized_type not in valid_types:
            raise ValueError(f"Invalid list_type: {list_type}")
        self._list_type = normalized_type
        self._is_circular = "circular" in normalized_type
        self.head: Optional[Any] = None
        self.tail: Optional[Any] = None
        self._size: int = 0

    def __len__(self) -> int:
        """Return the number of values stored in the list."""
        return self._size

    def _create_node(self, data: Any) -> Any:
        """Create a node that matches the configured list type."""
        if self._is_circular:
            if self._list_type == "singly_circular":
                return SinglyCircularLinkedNode(data)
            if self._list_type == "doubly_circular":
                return DoublyCircularLinkedNode(data)

        if self._list_type == "singly":
            return SinglyLinkedNode(data)
        if self._list_type == "doubly":
            return DoublyLinkedNode(data)

        raise ValueError("Invalid list type for node creation")
