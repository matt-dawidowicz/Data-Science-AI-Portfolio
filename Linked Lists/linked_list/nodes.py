from typing import Any, Optional

class SinglyLinkedNode:
    """
    Represents a node in a singly linked list.

    Attributes:
        data: The data stored in the node.
        next: Reference to the next node in the linked list, or None if there is no next node.
    """

    def __init__(self, data: Any, next_node: Optional["SinglyLinkedNode"] = None) -> None:
        self.data = data
        self.next = next_node

    def __repr__(self) -> str:
        return f"SinglyLinkedNode({self.data!r})"

class DoublyLinkedNode:
    """
    A class that represents a node in a doubly linked list. Each node contains data, a reference to the previous node, and a reference to the next node.

    Attributes:
        data: The value or data stored in the node.
        prev: A reference to the previous node in the doubly linked list. Defaults to None.
        next: A reference to the next node in the doubly linked list. Defaults to None.
    """

    def __init__(
            self,
            data: Any,
            prev: Optional["DoublyLinkedNode"] = None,
            next_node: Optional["DoublyLinkedNode"] = None
    ) -> None:
        self.data = data
        self.prev = prev
        self.next = next_node

    def __repr__(self) -> str:
        return f"DoublyLinkedNode({self.data!r})"