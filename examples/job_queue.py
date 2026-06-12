"""Producer-consumer job queue with a linked deque."""

from __future__ import annotations

import _bootstrap  # noqa: F401
from linked_list import LinkedDeque


def process_jobs() -> list[str]:
    """Process urgent jobs from the left and normal jobs from the right."""
    queue: LinkedDeque[str] = LinkedDeque()
    queue.append_right("send-welcome-email")
    queue.append_right("build-daily-report")
    queue.append_left("retry-failed-payment")

    processed = []
    while queue:
        processed.append(queue.pop_left())
    return processed


def main() -> None:
    """Print the processing order."""
    print(process_jobs())


if __name__ == "__main__":
    main()
