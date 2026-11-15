"""Tests for stage 3 command-line output."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from src.main import main


SETTINGS = {
    "package_name": "A",
    "repository": "tests/data/simple.txt",
    "test_mode": True,
    "output_file": "graph.svg",
    "ascii_tree": False,
    "exclude_substring": "",
}


class MainTests(unittest.TestCase):
    """Check test-mode CLI output and error reporting."""

    def test_bfs_output(self):
        """Print a dependency graph using the test repository."""
        output = StringIO()
        with patch("src.main.load_config", return_value=SETTINGS):
            with redirect_stdout(output):
                code = main()
        self.assertEqual(code, 0)
        self.assertIn("A -> B, C", output.getvalue())
        self.assertIn("D -> (none)", output.getvalue())

    def test_missing_package(self):
        """Display an error if the selected package is absent."""
        output = StringIO()
        settings = {**SETTINGS, "package_name": "Z"}
        with patch("src.main.load_config", return_value=settings):
            with redirect_stdout(output):
                code = main()
        self.assertEqual(code, 1)
        self.assertIn("Package not found", output.getvalue())


if __name__ == "__main__":
    unittest.main()
