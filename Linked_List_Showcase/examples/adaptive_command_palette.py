"""Adaptive command palette with a self-organizing linked list."""

from __future__ import annotations

import _bootstrap  # noqa: F401
from linked_list import SelfOrganizingLinkedList


def command_order_after_usage() -> list[str]:
    """Move frequently selected commands toward the front."""
    commands: SelfOrganizingLinkedList[str] = SelfOrganizingLinkedList(
        ["Open File", "Run Tests", "Format Document", "Git Push"],
        strategy="frequency_count",
    )
    commands.search("Run Tests")
    commands.search("Run Tests")
    commands.search("Git Push")
    return commands.to_list()


def main() -> None:
    """Print the adapted command order."""
    print(command_order_after_usage())


if __name__ == "__main__":
    main()
