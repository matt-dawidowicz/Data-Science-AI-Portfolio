from typing import Any, Optional
from ..nodes import (
    SinglyLinkedNode,
    DoublyLinkedNode,
    SinglyCircularLinkedNode,
    DoublyCircularLinkedNode,
)

class BaseLinkedList:
    def __init__(self, list_type: str = "singly"):
        valid_types = ("singly", "doubly", "singly_circular", "doubly_circular")
        normalized_type = list_type.strip().lower()
        if normalized_type not in valid_types:
            raise ValueError(f"Invalid list_type: {list_type}")
        self._list_type = normalized_type
        self._is_circular = "circular" in normalized_type
        self.head: Optional[Any] = None
        self.tail: Optional[Any] = None
        self._size: int = 0

    def __len__(self):
        return self._size

    def _create_node(self, data: Any) -> Any:
        if self._is_circular:
            if self._list_type == "singly_circular":
                return SinglyCircularLinkedNode(data)
            elif self._list_type == "doubly_circular":
                return DoublyCircularLinkedNode(data)
        else:
            if self._list_type == "singly":
                return SinglyLinkedNode(data)
            elif self._list_type == "doubly":
                return DoublyLinkedNode(data)
        raise ValueError("Invalid list type for node creation")
