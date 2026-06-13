"""Chunked text-buffer edits with an unrolled linked list."""

from __future__ import annotations

import _bootstrap  # noqa: F401
from linked_list import UnrolledLinkedList


def edit_text() -> tuple[str, list[list[str]]]:
    """Insert text while preserving an inspectable block layout."""
    buffer: UnrolledLinkedList[str] = UnrolledLinkedList(
        "linkedlist",
        node_capacity=4,
    )
    buffer.insert(6, "-")
    return "".join(buffer), buffer.to_blocks()


def main() -> None:
    """Print edited text and internal blocks."""
    text, blocks = edit_text()
    print(text)
    print(blocks)


if __name__ == "__main__":
    main()
