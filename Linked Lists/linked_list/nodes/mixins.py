"""Small node mixins for next, previous, and circular links.

The mixins keep pointer setup reusable and explicit. A singly linked node
needs only ``NextMixin`` because it can travel forward. A doubly linked node
combines ``PrevMixin`` and ``NextMixin`` because it can travel in both
directions. Circular nodes add ``CircularMixin`` after their normal links
exist, turning missing end links into self-references for the single-node
case.

Using mixins here makes the code easier to teach: each field is introduced by
the mixin that owns it instead of being hidden inside one large node class.
"""

from __future__ import annotations

from typing import Any


class NextMixin:
    """Provide a ``next`` pointer for forward traversal.

    ``next`` either points to the following node or to ``None`` for the end of
    a linear chain. Circular nodes may later rewrite ``None`` to point back to
    the node itself or to the list head.
    """

    next: Any | None

    def __init__(self, next_node: Any | None = None) -> None:
        """Initialize the forward link."""
        self.next: Any | None = next_node


class PrevMixin:
    """Provide a ``prev`` pointer for backward traversal.

    ``prev`` is the extra storage cost that gives doubly linked structures
    efficient reverse traversal and easier right-end removal.
    """

    prev: Any | None

    def __init__(self, prev_node: Any | None = None) -> None:
        """Initialize the backward link."""
        self.prev: Any | None = prev_node


class CircularMixin:
    """Turn absent node links into self-references.

    A single circular node points back to itself, which lets circular-list code
    treat one-node lists as valid loops.
    """

    def make_circular(self) -> None:
        """Point missing next and previous links back to this node.

        This helper is used during node construction only. Container mutation
        methods are still responsible for connecting the tail back to the
        current head after insertions and removals.
        """
        if getattr(self, "next", None) is None:
            self.next = self
        if hasattr(self, "prev") and getattr(self, "prev", None) is None:
            self.prev = self
