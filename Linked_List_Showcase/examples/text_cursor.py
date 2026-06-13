"""Text editing around a stable cursor position."""

import _bootstrap  # noqa: F401
from linked_list import Position, PositionalLinkedList


def insert_at_cursor() -> str:
    """Insert text around a cursor without searching by index each time."""
    buffer: PositionalLinkedList[str] = PositionalLinkedList("helo")
    cursor: Position[str] = buffer.position_at(2)

    buffer.add_after(cursor, "l")
    buffer.add_last("!")
    return "".join(buffer)


def main() -> None:
    """Print the edited text."""
    print(insert_at_cursor())


if __name__ == "__main__":
    main()
