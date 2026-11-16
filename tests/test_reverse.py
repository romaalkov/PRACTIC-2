"""Tests for reverse dependencies found with BFS."""

import unittest
from pathlib import Path

from src.graph import build_graph, load_test_graph, reverse_repository


DATA = Path(__file__).parent / "data"


class ReverseDependencyTests(unittest.TestCase):
    """Check direct, transitive, cyclic and filtered reverse links."""

    def test_direct_and_transitive_reverse_dependencies(self):
        """Show both direct dependents and more distant packages."""
        repository = load_test_graph(DATA / "simple.txt")
        reversed_graph = reverse_repository(repository)
        result = build_graph(reversed_graph, "D")
        self.assertEqual(list(result), ["D", "B", "C", "A"])
        self.assertEqual(result["D"], ["B", "C"])
        self.assertEqual(result["B"], ["A"])
        self.assertEqual(result["C"], ["A"])

    def test_cycle_in_reverse_graph(self):
        """Stop at visited packages even when dependencies form a cycle."""
        repository = load_test_graph(DATA / "cycle.txt")
        result = build_graph(reverse_repository(repository), "A")
        self.assertEqual(list(result), ["A", "C", "B"])
        self.assertEqual(result["B"], ["A"])

    def test_reverse_with_exclusion_filter(self):
        """Ignore matching packages during the reversed BFS."""
        repository = load_test_graph(DATA / "filter.txt")
        result = build_graph(reverse_repository(repository), "D", "X")
        self.assertEqual(list(result), ["D", "C", "A"])
        self.assertEqual(result["D"], ["C"])
        self.assertEqual(result["C"], ["A"])

    def test_package_without_reverse_dependencies(self):
        """Return a single vertex for an unused package."""
        repository = load_test_graph(DATA / "simple.txt")
        result = build_graph(reverse_repository(repository), "A")
        self.assertEqual(result, {"A": []})

    def test_reverse_unknown_dependency_name(self):
        """Retain package references missing from a partial index."""
        repository = {"A": ["B"], "C": []}
        self.assertEqual(reverse_repository(repository)["B"], ["A"])


if __name__ == "__main__":
    unittest.main()
