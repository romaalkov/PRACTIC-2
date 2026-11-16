"""Tests for stage 4 command-line output."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from src.main import main


SETTINGS = {
    "package_name": "D",
    "repository": "tests/data/simple.txt",
    "test_mode": True,
    "output_file": "graph.svg",
    "ascii_tree": False,
    "exclude_substring": "",
}


class MainTests(unittest.TestCase):
    """Check reverse dependency output and error reporting."""

    def test_reverse_bfs_output(self):
        """Print reverse links and list of all dependent packages."""
        output = StringIO()
        with patch("src.main.load_config", return_value=SETTINGS):
            with redirect_stdout(output):
                code = main()
        self.assertEqual(code, 0)
        self.assertIn("D <- B, C", output.getvalue())
        self.assertIn("B <- A", output.getvalue())
        self.assertIn("All reverse dependencies: B, C, A", output.getvalue())

    def test_unknown_package(self):
        """Report an error when the starting package is unavailable."""
        output = StringIO()
        settings = {**SETTINGS, "package_name": "Z"}
        with patch("src.main.load_config", return_value=settings):
            with redirect_stdout(output):
                code = main()
        self.assertEqual(code, 1)
        self.assertIn("Package not found", output.getvalue())

    def test_no_dependents(self):
        """Show an explicit empty result for an unused package."""
        output = StringIO()
        settings = {**SETTINGS, "package_name": "A"}
        with patch("src.main.load_config", return_value=settings):
            with redirect_stdout(output):
                code = main()
        self.assertEqual(code, 0)
        self.assertIn("All reverse dependencies: (none)", output.getvalue())


if __name__ == "__main__":
    unittest.main()
