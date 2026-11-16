"""Tests for stage 5 console output and rendering workflow."""

import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from src.main import main


SETTINGS = {
    "package_name": "A",
    "repository": "tests/data/simple.txt",
    "test_mode": True,
    "output_file": "graph.svg",
    "ascii_tree": True,
    "exclude_substring": "",
}


class MainTests(unittest.TestCase):
    """Check output and SVG generation errors without network."""

    def test_diagram_and_tree_output(self):
        """Create .puml and call renderer when ASCII output is enabled."""
        with tempfile.TemporaryDirectory() as folder:
            settings = {
                **SETTINGS, "output_file": str(Path(folder) / "graph.svg")
            }
            output = StringIO()
            with patch("src.main.load_config", return_value=settings):
                with patch("src.main.render_svg") as renderer:
                    with redirect_stdout(output):
                        code = main()
            self.assertEqual(code, 0)
            self.assertEqual(renderer.call_count, 1)
            self.assertTrue(Path(folder, "graph.puml").exists())
            self.assertIn("ASCII dependency tree:", output.getvalue())
            self.assertIn("D (already shown)", output.getvalue())

    def test_tree_can_be_disabled(self):
        """Do not print the tree if the setting is false."""
        with tempfile.TemporaryDirectory() as folder:
            settings = {**SETTINGS, "ascii_tree": False,
                        "output_file": str(Path(folder) / "graph.svg")}
            output = StringIO()
            with patch("src.main.load_config", return_value=settings):
                with patch("src.main.render_svg"):
                    with redirect_stdout(output):
                        code = main()
            self.assertEqual(code, 0)
            self.assertNotIn("ASCII dependency tree:", output.getvalue())

    def test_render_failure_is_reported(self):
        """Report a network/rendering failure with nonzero exit code."""
        with tempfile.TemporaryDirectory() as folder:
            settings = {
                **SETTINGS, "output_file": str(Path(folder) / "graph.svg")
            }
            output = StringIO()
            with patch("src.main.load_config", return_value=settings):
                with patch(
                    "src.main.render_svg", side_effect=ValueError("offline")
                ):
                    with redirect_stdout(output):
                        code = main()
            self.assertEqual(code, 1)
            self.assertIn("Error: offline", output.getvalue())


if __name__ == "__main__":
    unittest.main()
