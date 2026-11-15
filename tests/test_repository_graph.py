"""Tests for loading graph data from a compressed Ubuntu index."""

import gzip
from io import BytesIO
import unittest
from unittest.mock import patch

from src.apt_repository import load_repository_graph


SAMPLE_INDEX = """Package: demo
Depends: alpha (>= 1), beta | gamma

Package: alpha
Depends: demo

Package: beta

Package: gamma
"""


class RepositoryGraphTests(unittest.TestCase):
    """Check conversion from package metadata to adjacency lists."""

    def test_packages_index(self):
        """Parse alternatives and a cycle without internet access."""
        response = BytesIO(gzip.compress(SAMPLE_INDEX.encode("utf-8")))
        with patch("src.apt_repository.urlopen", return_value=response):
            repository = load_repository_graph("https://example.org/data.gz")
        self.assertEqual(repository["demo"], ["alpha", "beta", "gamma"])
        self.assertEqual(repository["alpha"], ["demo"])
        self.assertEqual(repository["beta"], [])


if __name__ == "__main__":
    unittest.main()
