
"""Tests for stage 2 command-line output."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from src.main import main


class MainTests(unittest.TestCase):
    """Check that the CLI displays dependencies and handles errors."""

    def test_direct_dependencies_output(self):
        """Display dependency names returned by the repository parser."""
        output = StringIO()
        fake_dependencies = ["libc6", "libssl3 | libressl3"]
        with patch(
            "src.main.get_direct_dependencies", return_value=fake_dependencies
        ), redirect_stdout(output):
            result = main()
        self.assertEqual(result, 0)
        self.assertIn("Direct dependencies of bash:", output.getvalue())
        self.assertIn("- libc6", output.getvalue())
        self.assertIn("- libssl3 | libressl3", output.getvalue())

    def test_download_error(self):
        """Display a clear message when repository access fails."""
        output = StringIO()
        with patch(
            "src.main.get_direct_dependencies",
            side_effect=ValueError("Cannot read repository"),
        ), redirect_stdout(output):
            result = main()
        self.assertEqual(result, 1)
        self.assertIn("Error: Cannot read repository", output.getvalue())


if __name__ == "__main__":
    unittest.main()
