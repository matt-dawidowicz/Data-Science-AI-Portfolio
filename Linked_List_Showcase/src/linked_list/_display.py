"""Recursion-safe display helpers for linked containers.

Several structures in this package can store arbitrary Python objects,
including the container itself. These helpers keep ``repr`` and ``str``
readable for those direct self-reference cases while leaving normal values to
Python's built-in display functions.
"""

from typing import Any


def safe_repr_item(owner: object, item: Any) -> str:
    """Return ``repr(item)`` with a compact direct self-reference marker."""
    if item is owner:
        return "..."
    return repr(item)


def safe_str_item(owner: object, item: Any) -> str:
    """Return ``str(item)`` with a compact direct self-reference marker."""
    if item is owner:
        return "..."
    return str(item)
