"""Nested document outline with a multilevel linked list."""

import _bootstrap  # noqa: F401
from linked_list import MultilevelLinkedList


def build_outline() -> MultilevelLinkedList[str]:
    """Build a course outline with nested lessons."""
    return MultilevelLinkedList.from_nested(
        [
            ("Module 1", ["Intro", "Install Python"]),
            ("Module 2", ["Linked nodes", "Pointer repair"]),
            "Final project",
        ],
    )


def main() -> None:
    """Print flat and nested views of the outline."""
    outline = build_outline()
    print(outline.to_list())
    print(outline.to_nested_list())


if __name__ == "__main__":
    main()
