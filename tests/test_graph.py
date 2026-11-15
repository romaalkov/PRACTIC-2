"""Tests for BFS traversal and the file-based test repository."""

import tempfile
import unittest
from pathlib import Path

from src.graph import build_graph, load_test_graph


DATA = Path(__file__).parent / "data"


class GraphTests(unittest.TestCase):
    """Check branching, cycles, filtering and input errors."""

    def test_transitive_dependencies(self):
        """Visit all reachable nodes in breadth-first order."""
        repository = load_test_graph(DATA / "simple.txt")
        graph = build_graph(repository, "A")
        self.assertEqual(list(graph), ["A", "B", "C", "D"])
        self.assertEqual(graph["B"], ["D"])
        self.assertEqual(graph["C"], ["D"])

    def test_cycle(self):
        """Stop traversing already visited packages but keep cycle edges."""
        repository = load_test_graph(DATA / "cycle.txt")
        graph = build_graph(repository, "A")
        self.assertEqual(list(graph), ["A", "B", "C"])
        self.assertEqual(graph["C"], ["A"])

    def test_exclusion_filter(self):
        """Exclude matches and do not traverse through them."""
        repository = load_test_graph(DATA / "filter.txt")
        graph = build_graph(repository, "A", "X")
        self.assertEqual(list(graph), ["A", "B", "C", "D"])
        self.assertEqual(graph["A"], ["B", "C"])
        self.assertEqual(graph["B"], [])

    def test_unknown_package(self):
        """Reject a starting package not found in the repository."""
        repository = load_test_graph(DATA / "simple.txt")
        with self.assertRaisesRegex(ValueError, "not found"):
            build_graph(repository, "Z")

    def test_filtered_start(self):
        """Reject filtering out the selected starting package."""
        repository = load_test_graph(DATA / "simple.txt")
        with self.assertRaisesRegex(ValueError, "exclusion"):
            build_graph(repository, "A", "A")

    def test_invalid_test_file(self):
        """Reject names that are not uppercase Latin letters."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.txt"
            path.write_text("A: b\nb:\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Invalid package"):
                load_test_graph(path)

    def test_undefined_test_package(self):
        """Reject a dependency without its own declaration."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "invalid.txt"
            path.write_text("A: B\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Undefined"):
                load_test_graph(path)


if __name__ == "__main__":
    unittest.main()
