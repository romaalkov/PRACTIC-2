
"""Tests for parsing Ubuntu package metadata without network access."""

import gzip
from io import BytesIO, StringIO
import unittest
from unittest.mock import patch

from src.apt_repository import (
    get_direct_dependencies,
    iter_packages,
    parse_dependencies,
)


SAMPLE_INDEX = """Package: demo-app
Version: 1.0
Depends: libc6 (>= 2.38), libssl3 | libressl3,
 zlib1g
Pre-Depends: base-files

Package: second-package
Version: 2.0
Depends: python3
"""


class RepositoryTests(unittest.TestCase):
    """Check parsing and dependency retrieval."""

    def test_multiline_package_metadata(self):
        """Read continued fields in a package entry."""
        packages = list(iter_packages(StringIO(SAMPLE_INDEX)))
        self.assertEqual(len(packages), 2)
        self.assertIn("zlib1g", packages[0]["Depends"])

    def test_dependency_alternatives(self):
        """Retain alternative dependencies in the output."""
        dependencies = parse_dependencies("a (>= 1), b:any | c")
        self.assertEqual(dependencies, ["a", "b | c"])

    def test_fetch_dependencies(self):
        """Read a compressed package index from a mocked response."""
        response = BytesIO(gzip.compress(SAMPLE_INDEX.encode("utf-8")))
        with patch("src.apt_repository.urlopen", return_value=response):
            dependencies = get_direct_dependencies(
                "https://example.org", "demo-app"
            )
        self.assertEqual(
            dependencies,
            ["base-files", "libc6", "libssl3 | libressl3", "zlib1g"],
        )

    def test_missing_package(self):
        """Report when a requested package is absent."""
        response = BytesIO(gzip.compress(SAMPLE_INDEX.encode("utf-8")))
        with patch("src.apt_repository.urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "not found"):
                get_direct_dependencies("https://example.org", "unknown")


if __name__ == "__main__":
    unittest.main()
