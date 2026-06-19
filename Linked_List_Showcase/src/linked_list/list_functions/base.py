"""Base linked-list state and node creation helpers.

The ``LinkedList`` class is split across mixins, but all of those mixins share
the same small set of state:

- ``head`` is the first node a forward traversal should visit.
- ``tail`` is the last node in the visible order.
- ``_size`` is the number of stored values.
- ``_list_type`` names the concrete representation.
- ``_is_circular`` records whether the tail should link back to the head.

The selected ``list_type`` controls which node class is created and which
pointer invariants every mutation must preserve.
"""

from typing import Any

from ..nodes import (
    DoublyCircularLinkedNode,
    DoublyLinkedNode,
    SinglyCircularLinkedNode,
    SinglyLinkedNode,
)


class BaseLinkedList:
    """Store common linked-list metadata and construct matching nodes.

    ``head`` and ``tail`` give constant-time access to the ends of the list.
    ``_size`` lets operations validate indexes and bound circular traversal.
    ``_is_circular`` avoids repeating string checks in every traversal method.

    This base class does not implement high-level behavior by itself. It gives
    the other mixins a consistent foundation to read from and write to.
    """

    def __init__(
        self,
        list_type: str = "singly",
    ) -> None:
        """Initialize linked-list metadata for the requested type.

        ``list_type`` is normalized once here so later methods can compare a
        predictable internal value. Invalid names fail before any node state is
        created.
        """
        valid_types = (
            "singly",
            "doubly",
            "singly_circular",
            "doubly_circular",
        )
        if not isinstance(list_type, str):
            raise TypeError("list_type must be a string")

        normalized_type = list_type.strip().lower()
        if normalized_type not in valid_types:
            raise ValueError(f"Invalid list_type: {list_type}")
        self._list_type: str = normalized_type
        self._is_circular: bool = "circular" in normalized_type
        self.head: Any | None = None
        self.tail: Any | None = None
        self._size: int = 0

    def __len__(self) -> int:
        """Return the number of values stored in the list."""
        return self._size

    def __bool__(self) -> bool:
        """Return whether the list contains at least one value."""
        return self._size > 0

    def is_empty(self) -> bool:
        """Return whether the list currently stores no values."""
        return self._size == 0

    def _create_node(self, data: Any) -> Any:
        """Create a node that matches the configured list type.

        This factory keeps node-selection logic in one place. Mutating methods
        can ask for a node without needing to know which concrete node class is
        required for the current list variant.
        """
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
