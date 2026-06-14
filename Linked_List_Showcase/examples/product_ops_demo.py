"""Mini product-operations workflow using several linked structures.

The scenario is a small incident-response snapshot for a software product.
It intentionally combines multiple containers so a reviewer can see the
package used as a coherent toolkit instead of as isolated toy examples.
"""

from dataclasses import dataclass
from typing import TypedDict

import _bootstrap  # noqa: F401
from linked_list import (
    LinkedDeque,
    MultilevelLinkedList,
    SelfOrganizingLinkedList,
    SkipList,
    SparseMatrixLinkedList,
    UnrolledLinkedList,
)


@dataclass(order=True, frozen=True)
class Escalation:
    """Incident escalation ordered by deadline, then ticket ID."""

    due_in_minutes: int
    ticket_id: str
    owner: str


class OpsSnapshot(TypedDict):
    """Structured output produced by the product-ops demo."""

    first_tasks: list[str]
    remaining_queue: list[str]
    next_escalation: Escalation
    next_after_twenty: Escalation
    command_counts: list[tuple[str, int]]
    playbook_steps: list[str]
    drain_queue_path: tuple[int, ...] | None
    service_scores: list[tuple[str, int]]
    event_blocks: list[list[str]]


def build_work_queue() -> tuple[list[str], list[str]]:
    """Process the first urgent tasks and keep the remaining queue."""
    queue: LinkedDeque[str] = LinkedDeque()
    queue.append_right("sync billing report")
    queue.append_right("refresh search index")
    queue.append_left("rollback failed deploy")

    first_tasks = [queue.pop_left(), queue.pop_left()]
    return first_tasks, queue.to_list()


def build_escalation_index() -> tuple[Escalation, Escalation]:
    """Return the next escalation and the first one after 20 minutes."""
    escalations: SkipList[Escalation] = SkipList(seed=11)
    escalations.extend(
        [
            Escalation(30, "INC-104", "data-platform"),
            Escalation(10, "INC-101", "payments"),
            Escalation(45, "INC-111", "search"),
            Escalation(20, "INC-108", "checkout"),
        ],
    )

    next_escalation = escalations.first()
    next_after_twenty = escalations.ceiling(Escalation(21, "", ""))
    return next_escalation, next_after_twenty


def build_command_palette() -> list[tuple[str, int]]:
    """Record repeated command use and expose the adapted command order."""
    commands: SelfOrganizingLinkedList[str] = SelfOrganizingLinkedList(
        [
            "open runbook",
            "restart worker",
            "silence alert",
            "page owner",
        ],
        strategy="move_to_front",
    )

    for command in [
        "restart worker",
        "open runbook",
        "restart worker",
        "restart worker",
    ]:
        commands.search(command)

    return commands.to_access_counts()


def build_playbook() -> tuple[list[str], tuple[int, ...] | None]:
    """Represent a nested incident playbook and locate one nested step."""
    playbook: MultilevelLinkedList[str] = MultilevelLinkedList.from_nested(
        [
            "detect",
            ("diagnose", ["check logs", "compare metrics"]),
            ("mitigate", ["rollback release", "drain queue"]),
            "review",
        ],
    )
    return playbook.to_list(), playbook.path_to("drain queue")


def build_service_impact() -> list[tuple[str, int]]:
    """Rank service impact from sparse service-by-region incident counts."""
    services = ["checkout", "search", "email"]
    regional_weight = [1, 2, 3]
    impact: SparseMatrixLinkedList[int] = SparseMatrixLinkedList.from_entries(
        3,
        3,
        [
            (0, 0, 18),
            (0, 2, 5),
            (1, 1, 8),
            (2, 0, 2),
        ],
    )
    scores = impact.multiply_vector(regional_weight)
    return list(zip(services, scores, strict=True))


def build_event_blocks() -> list[list[str]]:
    """Store a short audit trail in linked blocks."""
    events: UnrolledLinkedList[str] = UnrolledLinkedList(
        [
            "deploy started",
            "alert fired",
            "rollback queued",
            "owner paged",
            "queue drained",
        ],
        node_capacity=3,
    )
    return events.to_blocks()


def run_ops_snapshot() -> OpsSnapshot:
    """Return all demo outputs for tests, docs, and console printing."""
    first_tasks, remaining_queue = build_work_queue()
    next_escalation, next_after_twenty = build_escalation_index()
    command_counts = build_command_palette()
    playbook_steps, drain_queue_path = build_playbook()
    service_scores = build_service_impact()
    event_blocks = build_event_blocks()

    return {
        "first_tasks": first_tasks,
        "remaining_queue": remaining_queue,
        "next_escalation": next_escalation,
        "next_after_twenty": next_after_twenty,
        "command_counts": command_counts,
        "playbook_steps": playbook_steps,
        "drain_queue_path": drain_queue_path,
        "service_scores": service_scores,
        "event_blocks": event_blocks,
    }


def main() -> None:
    """Print a compact product-operations snapshot."""
    snapshot = run_ops_snapshot()
    next_escalation = snapshot["next_escalation"]
    next_after_twenty = snapshot["next_after_twenty"]

    print("Product ops snapshot")
    print(f"first tasks: {', '.join(snapshot['first_tasks'])}")
    print(f"remaining queue: {snapshot['remaining_queue']}")
    print(
        "next escalation: "
        f"{next_escalation.ticket_id} in "
        f"{next_escalation.due_in_minutes} minutes",
    )
    print(
        "next after 20 minutes: "
        f"{next_after_twenty.ticket_id} owned by "
        f"{next_after_twenty.owner}",
    )
    print(f"adapted command order: {snapshot['command_counts']}")
    print(f"playbook steps: {snapshot['playbook_steps']}")
    print(f"drain queue path: {snapshot['drain_queue_path']}")
    print(f"service impact scores: {snapshot['service_scores']}")
    print(f"event blocks: {snapshot['event_blocks']}")


if __name__ == "__main__":
    main()
