from typing import Any

class BaseNode:
    def __init__(self, data: Any) -> None:
        self.data = data

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.data!r})"
