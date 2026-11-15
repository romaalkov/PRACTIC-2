
"""Tests for the initial application."""

import unittest
from contextlib import redirect_stdout
from io import StringIO

from src.main import main


class MainTests(unittest.TestCase):
    """Check the initial CLI behavior."""

    def test_start_message(self):
        """Check that the application displays its name."""
        output = StringIO()

        with redirect_stdout(output):
            main()

        self.assertIn(
            "APT Dependency Graph Visualizer",
            output.getvalue(),
        )


if __name__ == "__main__":
    unittest.main()
    