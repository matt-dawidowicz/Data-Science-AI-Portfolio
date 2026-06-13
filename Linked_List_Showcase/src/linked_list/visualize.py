"""Mermaid visualization helpers for small linked-structure examples.

The package is educational, so a lightweight diagram helper is useful in
notebooks, README snippets, and debugging sessions. The helper accepts any
iterable and renders the visible order as a Mermaid flowchart. It intentionally
uses only public iteration instead of reaching into node internals.
"""

from collections.abc import Iterable
from typing import Any

_VALID_DIRECTIONS = {"BT", "LR", "RL", "TB", "TD"}


def to_mermaid(
    values: Iterable[Any],
    *,
    title: str | None = None,
    direction: str = "LR",
    max_items: int | None = 50,
) -> str:
    """Return a Mermaid flowchart for the visible order of ``values``.

    ``values`` may be any package container or ordinary iterable. The helper
    snapshots values first so it can count truncation cleanly. ``max_items``
    keeps accidental large diagrams readable; pass ``None`` to render every
    item.
    """
    if direction not in _VALID_DIRECTIONS:
        valid = ", ".join(sorted(_VALID_DIRECTIONS))
        raise ValueError(f"direction must be one of: {valid}")
    if max_items is not None and max_items < 0:
        raise ValueError("max_items must be non-negative or None")

    snapshot = list(values)
    visible = snapshot if max_items is None else snapshot[:max_items]
    hidden_count = len(snapshot) - len(visible)

    lines = [f"flowchart {direction}"]
    if title is not None:
        lines.append(f'    title["{_escape_label(title)}"]')

    if not visible:
        lines.append('    empty["(empty)"]')
        return "\n".join(lines)

    for index, value in enumerate(visible):
        label = _escape_label(f"{index}: {value!r}")
        lines.append(f'    n{index}["{label}"]')

    for index in range(len(visible) - 1):
        lines.append(f"    n{index} --> n{index + 1}")

    if hidden_count > 0:
        lines.append(f'    more["... {hidden_count} more"]')
        lines.append(f"    n{len(visible) - 1} --> more")

    return "\n".join(lines)


def _escape_label(value: str) -> str:
    """Escape text for a Mermaid quoted node label."""
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("[", "(")
        .replace("]", ")")
    )
