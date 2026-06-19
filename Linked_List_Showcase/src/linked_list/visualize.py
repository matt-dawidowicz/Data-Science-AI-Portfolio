"""Mermaid visualization helpers for small linked-structure examples.

The package is educational, so a lightweight diagram helper is useful in
notebooks, README snippets, and debugging sessions. The helper accepts any
iterable and renders the visible order as a Mermaid flowchart. It intentionally
uses only public iteration instead of reaching into node internals.
"""

from collections.abc import Iterable, Sized
from itertools import islice
from operator import index as to_index
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
    ``max_items`` keeps accidental large diagrams readable; pass ``None`` to
    render every item. When a limit is supplied, unsized iterators are consumed
    only far enough to render the visible items and detect whether more data
    exists.
    """
    if direction not in _VALID_DIRECTIONS:
        valid = ", ".join(sorted(_VALID_DIRECTIONS))
        raise ValueError(f"direction must be one of: {valid}")
    if max_items is not None:
        max_items = to_index(max_items)
        if max_items < 0:
            raise ValueError("max_items must be non-negative or None")

    hidden_count: int | None = 0
    has_hidden = False
    if max_items is None:
        visible = list(values)
    elif isinstance(values, Sized):
        visible = list(islice(values, max_items))
        hidden_count = max(0, len(values) - len(visible))
        has_hidden = hidden_count > 0
    else:
        limited = list(islice(values, max_items + 1))
        visible = limited[:max_items]
        has_hidden = len(limited) > len(visible)
        hidden_count = None

    lines = [f"flowchart {direction}"]
    if title is not None:
        lines.append(f'    title["{_escape_label(title)}"]')

    if not visible and not has_hidden:
        lines.append('    empty["(empty)"]')
        return "\n".join(lines)

    for index, value in enumerate(visible):
        label = _escape_label(f"{index}: {value!r}")
        lines.append(f'    n{index}["{label}"]')

    for index in range(len(visible) - 1):
        lines.append(f"    n{index} --> n{index + 1}")

    if has_hidden:
        more_label = (
            f"... {hidden_count} more"
            if hidden_count is not None
            else "... more"
        )
        lines.append(f'    more["{more_label}"]')
        if visible:
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
