"""Leaderboard rankings with a skip list."""

from dataclasses import dataclass

import _bootstrap  # noqa: F401
from linked_list import SkipList


@dataclass(order=True, frozen=True)
class ScoreEntry:
    """Comparable leaderboard entry sorted by score, then name."""

    score: int
    player: str


def top_players() -> list[ScoreEntry]:
    """Return the highest-scoring players from a sorted set."""
    board: SkipList[ScoreEntry] = SkipList(seed=7)
    board.extend(
        [
            ScoreEntry(1200, "Ada"),
            ScoreEntry(980, "Grace"),
            ScoreEntry(1510, "Katherine"),
            ScoreEntry(1510, "Dorothy"),
        ],
    )
    return list(reversed(board))[:3]


def main() -> None:
    """Print the top leaderboard entries."""
    for entry in top_players():
        print(f"{entry.player}: {entry.score}")


if __name__ == "__main__":
    main()
