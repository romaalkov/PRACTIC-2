
"""Tests for TOML configuration validation."""

import tempfile
import unittest
from pathlib import Path

from src.config import load_config


VALID_CONFIG = '''
package_name = "bash"
repository = "https://example.org/Packages.gz"
test_mode = false
output_file = "graph.svg"
ascii_tree = true
exclude_substring = ""
'''


class ConfigTests(unittest.TestCase):
    """Check valid and invalid configuration values."""

    def setUp(self):
        """Create a temporary configuration file."""
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "config.toml"
        self.path.write_text(VALID_CONFIG, encoding="utf-8")

    def tearDown(self):
        """Remove temporary test files."""
        self.directory.cleanup()

    def test_valid_configuration(self):
        """Accept a valid configuration."""
        settings = load_config(self.path)
        self.assertEqual(settings["package_name"], "bash")

    def test_invalid_parameter_values(self):
        """Reject invalid values for each of the six parameters."""
        replacements = {
            "package_name": ('"bash"', '""'),
            "repository": ('"https://example.org/Packages.gz"', '"bad"'),
            "test_mode": ("false", '"yes"'),
            "output_file": ('"graph.svg"', '"graph.png"'),
            "ascii_tree": ("true", '"yes"'),
            "exclude_substring": ('""', '5'),
        }
        for name, (correct, incorrect) in replacements.items():
            with self.subTest(parameter=name):
                old_line = f"{name} = {correct}"
                new_line = f"{name} = {incorrect}"
                changed = VALID_CONFIG.replace(old_line, new_line)
                self.path.write_text(changed, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, name):
                    load_config(self.path)

    def test_missing_parameter(self):
        """Reject a configuration missing a required field."""
        changed = VALID_CONFIG.replace('package_name = "bash"\n', "")
        self.path.write_text(changed, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "package_name"):
            load_config(self.path)

    def test_invalid_toml(self):
        """Reject malformed TOML."""
        self.path.write_text('package_name = "oops', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "TOML"):
            load_config(self.path)

    def test_missing_file(self):
        """Reject a missing configuration file."""
        self.path.unlink()
        with self.assertRaisesRegex(ValueError, "TOML"):
            load_config(self.path)


if __name__ == "__main__":
    unittest.main()
