from typing import Any, Optional

class SinglyLinkedNode:
    """

    Represents a node in a singly linked list.

    This class defines the structure of an individual node used in a singly linked list,
    which includes storing the data and a reference to the next node in the sequence. It
    is used as a building block for creating a linked list.

    Attributes:
        data (Any): The value or data stored in the node.
        next (Optional[SinglyLinkedNode]): A reference to the next node in the singly
            linked list, or None if this is the last node.
    """

    def __init__(self, data: Any, next_node: Optional["SinglyLinkedNode"] = None) -> None:
        """
        Initializes a singly linked list node with data and an optional pointer to the next node.
        This forms the basic structure used in implementing linked list data structures.

        Args:
            data: The data to be stored in the node. Can be of any type.
            next_node: An optional instance of SinglyLinkedNode representing the
                next node in the list. If None is passed, the node will not point
                to any other node.

        Raises:
            TypeError: If next_node is provided and is not an instance of
                SinglyLinkedNode or None.
        """
        self.data = data
        if next_node is not None and not isinstance(next_node, SinglyLinkedNode):
            raise TypeError("next_node must be a SinglyLinkedNode or None")
        self.next = next_node

    def __repr__(self) -> str:
        """
        Represents the string representation of a SinglyLinkedNode instance for debugging purposes.

        This method provides a customized, unambiguous string representation of the
        SinglyLinkedNode object, typically used for debugging or logging.

        Returns:
            str: A string representing the instance in the format 'SinglyLinkedNode(data)'.

        """
        return f"SinglyLinkedNode({self.data!r})"

class DoublyLinkedNode:
    """
    Represents a node in a doubly linked list.

    Attributes:
        data: The data stored in the node.
        next: Reference to the next node in the linked list, or None if there is no next node.
        prev: Reference to the previous node in the linked list, or None if there is no previous node.
    """

    def __init__(self, data: Any,
                 prev_node: Optional["DoublyLinkedNode"] = None,
                 next_node: Optional["DoublyLinkedNode"] = None) -> None:
        """
        Represents a node in a doubly linked list.

        Each node contains data and links to the previous and next nodes in the list.

        Attributes:
            data: The data stored in the node.
            prev_node: A reference to the previous node in the doubly linked list or None
                if this is the first node.
            next_node: A reference to the next node in the doubly linked list or None if
                this is the last node.

        Args:
            data: The data to be stored in the node.
            prev_node: A reference to the previous node in the doubly linked list or
                None if there is no previous node.
            next_node: A reference to the next node in the doubly linked list or None
                if there is no next node.

        Raises:
            TypeError: If `prev_node` or `next_node` is not a `DoublyLinkedNode` or
                None.
        """
        self.data = data

        if prev_node is not None and not isinstance(prev_node, DoublyLinkedNode):
            raise TypeError("prev_node must be a DoublyLinkedNode or None")
        self.prev = prev_node

        if next_node is not None and not isinstance(next_node, DoublyLinkedNode):
            raise TypeError("next_node must be a DoublyLinkedNode or None")
        self.next = next_node

    def __repr__(self) -> str:
        """
        Represents the string representation of the DoublyLinkedNode instance.

        This method is used to provide a developer-friendly string representation of
        the instance, often useful for debugging purposes. The representation
        includes the value of the data attribute enclosed in parentheses.

        Returns:
            str: A string in the format "DoublyLinkedNode(data)" where `data` is the
            value of the node's data attribute.
        """
        return f"DoublyLinkedNode({self.data!r})"


# Node classes for circular linked lists
class SinglyCircularLinkedNode:
    """
    Represents a node in a singly circular linked list.

    This class is used as a building block for implementing singly circular linked lists
    where the last node of the list points back to the first node. Each instance stores
    data and a reference to the next node in the circular list.

    Attributes:
        data (Any): The data stored in the node.
        next (Optional[SinglyCircularLinkedNode]): Reference to the next node in the
            circular linked list. Defaults to reference itself if no next node is
            explicitly provided.
    """

    def __init__(self, data: Any, next_node: Optional["SinglyCircularLinkedNode"] = None) -> None:
        """
        Represents a node in a singly circular linked list.

        Each node contains data and a reference pointing to the next node in the list.
        If no next node is specified during initialization, the node will reference itself,
        forming a circular structure by default.

        Attributes:
            data: Holds the data for the node.
            next: Points to the next node in the circular linked list. Defaults to referencing
                the node itself if no next node is provided.

        Args:
            data: The value or object to store in the node.
            next_node: Optional; The next node in the circular linked list. If not provided,
                the node will reference itself.
        """
        self.data = data
        # In a circular list, if no next node is provided, the node references itself.
        self.next = next_node if next_node is not None else self

    def __repr__(self) -> str:
        """
        Returns a string representation of the instance for debugging and logging purposes. The representation includes the
        data attribute of the class to provide relevant information about the instance.

        Returns:
            str: A string that represents the class instance, displaying the `data` attribute.
        """
        return f"SinglyCircularLinkedNode({self.data!r})"


class DoublyCircularLinkedNode:
    """
    Represents a node in a doubly circular linked list.

    A doubly circular linked list node contains data, a reference to the previous node,
    and a reference to the next node. If no previous or next nodes are provided during
    initialization, the node will reference itself, ensuring the circular structure
    of the list is maintained.

    Attributes:
        data (Any): The data stored in the node.
        prev (Optional[DoublyCircularLinkedNode]): Reference to the previous node. Defaults
            to itself if not provided.
        next (Optional[DoublyCircularLinkedNode]): Reference to the next node. Defaults
            to itself if not provided.
    """

    def __init__(
            self,
            data: Any,
            prev: Optional["DoublyCircularLinkedNode"] = None,
            next_node: Optional["DoublyCircularLinkedNode"] = None
    ) -> None:
        """
        Represents a node in a doubly circular linked list. Each node contains a piece
        of data, a reference to the previous node, and a reference to the next node. If
        no adjacent nodes are provided, the node points to itself for both previous and
        next references, maintaining the circular structure of the list.
        """
        self.data = data
        # In a circular list, if no adjacent node is provided, the node references itself.
        self.prev = prev if prev is not None else self
        self.next = next_node if next_node is not None else self

    def __repr__(self) -> str:
        """
        Returns a string representation of a DoublyCircularLinkedNode instance for debugging.

        It now includes additional details about the previous and next nodes.
        If the node's 'prev' or 'next' pointers reference the node itself,
        it indicates this by showing 'self', otherwise it shows the data of the linked node.

        Returns:
            str: A detailed string representation of the node.
        """
        prev_info = "self" if self.prev is self else repr(self.prev.data)
        next_info = "self" if self.next is self else repr(self.next.data)
        return f"DoublyCircularLinkedNode(data={self.data!r}, prev={prev_info}, next={next_info})"