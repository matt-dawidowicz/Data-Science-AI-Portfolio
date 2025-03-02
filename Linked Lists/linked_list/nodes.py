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

from typing import Any, Optional, Iterator


# Node classes for circular linked lists
class SinglyCircularLinkedNode:
    """
    Represents a node in a singly linked circular list.

    Attributes:
        data: The data stored in the node.
        next: Reference to the next node in the circular list.
    """

    def __init__(self, data: Any, next_node: Optional["SinglyCircularLinkedNode"] = None) -> None:
        self.data = data
        # In a circular list, if no next node is provided, the node references itself.
        self.next = next_node if next_node is not None else self

    def __repr__(self) -> str:
        return f"SinglyCircularLinkedNode({self.data!r})"


class DoublyCircularLinkedNode:
    """
    Represents a node in a doubly linked circular list.

    Attributes:
        data: The data stored in the node.
        prev: Reference to the previous node in the circular list.
        next: Reference to the next node in the circular list.
    """

    def __init__(
            self,
            data: Any,
            prev: Optional["DoublyCircularLinkedNode"] = None,
            next_node: Optional["DoublyCircularLinkedNode"] = None
    ) -> None:
        self.data = data
        # In a circular list, if no adjacent node is provided, the node references itself.
        self.prev = prev if prev is not None else self
        self.next = next_node if next_node is not None else self

    def __repr__(self) -> str:
        return f"DoublyCircularLinkedNode({self.data!r})"

# List classes that accommodate multiple nodes and offer versatility
class SinglyCircularLinkedList:
    """
    A class to manage a singly linked circular list.
    """

    def __init__(self) -> None:
        self.head: Optional[SinglyCircularLinkedNode] = None

    def append(self, data: Any) -> None:
        """
        Appends a new node with the provided data to the circular list.
        """
        if self.head is None:
            # Create a node that points to itself.
            self.head = SinglyCircularLinkedNode(data)
        else:
            current = self.head
            # Traverse the list until reaching the last node (which points back to head).
            while current.next != self.head:
                current = current.next
            new_node = SinglyCircularLinkedNode(data, self.head)
            current.next = new_node

    def __iter__(self) -> Iterator[Any]:
        """
        Iterator to traverse the circular list.
        """
        if self.head is None:
            return
        current = self.head
        yield current.data
        while current.next != self.head:
            current = current.next
            yield current.data

    def __repr__(self) -> str:
        # Represent the list by showing its node values.
        return " -> ".join(str(item) for item in self)


class DoublyCircularLinkedList:
    """
    A class to manage a doubly linked circular list.
    """

    def __init__(self) -> None:
        self.head: Optional[DoublyCircularLinkedNode] = None

    def append(self, data: Any) -> None:
        """
        Appends a new node with the provided data to the end of the circular list.
        """
        if self.head is None:
            # Create the first node that points to itself in both directions.
            self.head = DoublyCircularLinkedNode(data)
        else:
            tail = self.head.prev  # Since the list is circular, head.prev is the tail.
            new_node = DoublyCircularLinkedNode(data, prev=tail, next_node=self.head)
            tail.next = new_node
            self.head.prev = new_node

    def __iter__(self) -> Iterator[Any]:
        """
        Iterator to traverse the circular list forward.
        """
        if self.head is None:
            return
        current = self.head
        yield current.data
        while current.next != self.head:
            current = current.next
            yield current.data

    def __repr__(self) -> str:
        # Represent the list by showing its node values.
        return " <-> ".join(str(item) for item in self)
