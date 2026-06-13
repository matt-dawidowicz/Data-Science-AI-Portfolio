"""Round-robin worker scheduling with a circular linked list."""

from __future__ import annotations

import _bootstrap  # noqa: F401
from linked_list import LinkedList


class RoundRobinScheduler:
    """Rotate through workers without resetting to the first worker."""

    def __init__(self, workers: list[str]) -> None:
        """Initialize a circular worker list."""
        self._workers: LinkedList[str] = LinkedList("singly_circular")
        for worker in workers:
            self._workers.append(worker)

    def assign_next(self) -> str:
        """Return the next worker and rotate to the following worker."""
        worker = self._workers.peek_front()
        self._workers.rotate(-1)
        return worker


def main() -> None:
    """Show repeated round-robin assignment."""
    scheduler = RoundRobinScheduler(["api-1", "api-2", "api-3"])
    assignments = [scheduler.assign_next() for _ in range(8)]
    print(assignments)


if __name__ == "__main__":
    main()
