"""Tests for generic public aliases and Mermaid visualization."""

import unittest
from itertools import count

from linked_list import (
    LinkedDeque,
    LinkedList,
    MultilevelLinkedList,
    PositionalLinkedList,
    SelfOrganizingLinkedList,
    SkipList,
    SortedLinkedList,
    SparseMatrixLinkedList,
    UnrolledLinkedList,
    to_mermaid,
)


class TestTypingAndVisualization(unittest.TestCase):
    """Cover package-level typing aliases and diagram export."""

    def test_public_containers_accept_generic_aliases(self) -> None:
        """Generic aliases should remain callable at runtime."""
        linked = LinkedList[int]("singly")
        linked.extend([1, 2])

        self.assertEqual(linked.to_list(), [1, 2])
        self.assertEqual(LinkedDeque[str](["a"]).to_list(), ["a"])
        self.assertEqual(SortedLinkedList[int]([2, 1]).to_list(), [1, 2])
        self.assertEqual(SkipList[int]([2, 1]).to_list(), [1, 2])
        self.assertEqual(UnrolledLinkedList[int]([1, 2]).to_list(), [1, 2])
        self.assertEqual(MultilevelLinkedList[str](["x"]).to_list(), ["x"])
        self.assertEqual(PositionalLinkedList[str](["x"]).to_list(), ["x"])
        self.assertEqual(
            SelfOrganizingLinkedList[str](["x"]).to_list(),
            ["x"],
        )
        matrix = SparseMatrixLinkedList[int].from_entries(
            2,
            2,
            [(0, 1, 5)],
        )
        self.assertEqual(matrix[0, 1], 5)

    def test_to_mermaid_renders_visible_sequence(self) -> None:
        """A small sequence should become a readable Mermaid graph."""
        diagram = to_mermaid(LinkedDeque(["ingest", "load"]), title="queue")

        self.assertIn("flowchart LR", diagram)
        self.assertIn('title["queue"]', diagram)
        self.assertIn("n0[\"0: 'ingest'\"]", diagram)
        self.assertIn("n0 --> n1", diagram)

    def test_to_mermaid_handles_empty_and_truncated_sequences(self) -> None:
        """Empty and large sequences should stay readable."""
        self.assertIn("(empty)", to_mermaid([]))

        diagram = to_mermaid(range(5), max_items=2)
        self.assertIn("... 3 more", diagram)
        self.assertIn("n1 --> more", diagram)

        zero_visible = to_mermaid(range(5), max_items=0)
        self.assertIn('more["... 5 more"]', zero_visible)
        self.assertNotIn("n0", zero_visible)

    def test_to_mermaid_bounds_unsized_iterators_when_limited(self) -> None:
        """Limited diagrams should not exhaust an unsized iterator."""
        diagram = to_mermaid(count(), max_items=2)

        self.assertIn('n0["0: 0"]', diagram)
        self.assertIn('n1["1: 1"]', diagram)
        self.assertIn('more["... more"]', diagram)
        self.assertNotIn("2: 2", diagram)

    def test_to_mermaid_can_render_all_items_from_finite_generator(
        self,
    ) -> None:
        """Passing max_items=None should keep the explicit render-all mode."""
        diagram = to_mermaid((value for value in [1, 2]), max_items=None)

        self.assertIn('n0["0: 1"]', diagram)
        self.assertIn('n1["1: 2"]', diagram)
        self.assertNotIn("more", diagram)

    def test_to_mermaid_accepts_integer_like_max_items(self) -> None:
        """Integer-like limits should follow normal Python index rules."""

        class TwoItems:
            def __index__(self) -> int:
                return 2

        diagram = to_mermaid(range(4), max_items=TwoItems())  # type: ignore[arg-type]

        self.assertIn('n1["1: 1"]', diagram)
        self.assertIn("... 2 more", diagram)

    def test_to_mermaid_validates_options(self) -> None:
        """Invalid rendering options should fail clearly."""
        with self.assertRaises(ValueError):
            to_mermaid([1], direction="SIDEWAYS")
        with self.assertRaises(ValueError):
            to_mermaid([1], max_items=-1)
        with self.assertRaises(TypeError):
            to_mermaid([1], max_items="bad")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
