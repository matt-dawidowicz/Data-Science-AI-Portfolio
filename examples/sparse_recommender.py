"""Sparse ratings matrix for a small recommender-style workflow."""

from __future__ import annotations

import _bootstrap  # noqa: F401
from linked_list import SparseMatrixLinkedList


def unrated_movies_for_user(user_id: int) -> list[int]:
    """Return movie IDs the user has not rated yet."""
    ratings: SparseMatrixLinkedList[float] = (
        SparseMatrixLinkedList.from_entries(
            3,
            5,
            [
                (0, 0, 5.0),
                (0, 2, 4.0),
                (1, 1, 3.5),
                (2, 0, 4.5),
                (2, 3, 5.0),
            ],
        )
    )
    rated = {movie_id for movie_id, _ in ratings.row_items(user_id)}
    return [
        movie_id for movie_id in range(ratings.cols) if movie_id not in rated
    ]


def main() -> None:
    """Print unrated movie IDs for one user."""
    print(unrated_movies_for_user(0))


if __name__ == "__main__":
    main()
