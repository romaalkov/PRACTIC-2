
"""Tests for the application entry point."""

import unittest
from contextlib import redirect_stdout
from io import StringIO

from src.main import main


class MainTests(unittest.TestCase):
    """Check the CLI output."""

    def test_configuration_output(self):
        """Check that the application prints configuration values."""
        output = StringIO()
        with redirect_stdout(output):
            result = main()

        self.assertEqual(result, 0)
        self.assertIn("package_name = bash", output.getvalue())
        self.assertIn("output_file = graph.svg", output.getvalue())


if __name__ == "__main__":
    unittest.main()
