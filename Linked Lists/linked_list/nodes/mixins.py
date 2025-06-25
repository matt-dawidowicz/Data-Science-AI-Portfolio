from typing import Optional

class NextMixin:
    def __init__(self, next_node: Optional[object] = None) -> None:
        self.next = next_node

class PrevMixin:
    def __init__(self, prev_node: Optional[object] = None) -> None:
        self.prev = prev_node

class CircularMixin:
    def make_circular(self):
        if getattr(self, "next", None) is None:
            self.next = self
        if hasattr(self, "prev") and getattr(self, "prev", None) is None:
            self.prev = self
