"""Tests for PlantUML, ASCII output and SVG rendering."""

import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from src.graph import build_graph, load_test_graph
from src.visualization import (
    ascii_tree, encode_plantuml, render_svg, to_plantuml,
)


DATA = Path(__file__).parent / "data"
SVG = b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'


class VisualizationTests(unittest.TestCase):
    """Check graph output without external network requests."""

    def test_plantuml_contains_all_edges(self):
        """Preserve both edges to a shared dependency."""
        graph = build_graph(load_test_graph(DATA / "simple.txt"), "A")
        diagram = to_plantuml(graph)
        self.assertTrue(diagram.startswith("@startuml"))
        self.assertTrue(diagram.endswith("@enduml\n"))
        self.assertIn('rectangle "A" as N0', diagram)
        self.assertIn("N1 --> N3", diagram)
        self.assertIn("N2 --> N3", diagram)

    def test_ascii_tree_shows_repeated_node(self):
        """Do not expand the same package twice."""
        graph = build_graph(load_test_graph(DATA / "simple.txt"), "A")
        tree = ascii_tree(graph, "A")
        self.assertIn("├── B", tree)
        self.assertIn("└── C", tree)
        self.assertIn("D (already shown)", tree)

    def test_ascii_cycle(self):
        """Stop expanding a cyclic dependency."""
        graph = build_graph(load_test_graph(DATA / "cycle.txt"), "A")
        self.assertIn("A (already shown)", ascii_tree(graph, "A"))

    def test_ascii_leaf(self):
        """Display a package with no dependencies."""
        self.assertEqual(ascii_tree({"A": []}, "A"), "A")

    def test_encoding_is_safe_for_url(self):
        """Use the PlantUML URL character set."""
        encoded = encode_plantuml("@startuml\nA -> B\n@enduml\n")
        self.assertTrue(encoded)
        self.assertRegex(encoded, r"^[A-Za-z0-9_-]+$")

    @patch.dict("os.environ", {"PLANTUML_JAR": ""})
    def test_svg_response_is_saved(self):
        """Write valid SVG returned by a mocked PlantUML service."""
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "graph.svg"
            with patch("src.visualization.urlopen", return_value=BytesIO(SVG)):
                render_svg("@startuml\nA -> B\n@enduml", destination)
            self.assertEqual(destination.read_bytes(), SVG)

    @patch.dict("os.environ", {"PLANTUML_JAR": ""})
    def test_invalid_svg_is_rejected(self):
        """Do not write an HTML error page with an SVG extension."""
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "graph.svg"
            with patch(
                "src.visualization.urlopen", return_value=BytesIO(b"bad")
            ):
                with self.assertRaisesRegex(ValueError, "invalid SVG"):
                    render_svg("@startuml\nA -> B\n@enduml", destination)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
