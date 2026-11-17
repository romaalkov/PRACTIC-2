"""Load and validate application settings from TOML."""

from pathlib import Path
import re
import tomllib
from urllib.parse import urlsplit


REQUIRED_TYPES = {
    "package_name": str,
    "repository": str,
    "test_mode": bool,
    "output_file": str,
    "ascii_tree": bool,
    "exclude_substring": str,
}

TEST_PACKAGE_PATTERN = re.compile(r"[A-Z]+")
APT_PACKAGE_PATTERN = re.compile(r"[a-z0-9][a-z0-9+.-]*")


def _validate_types(settings):
    """Reject missing options and options with an unexpected data type."""
    for name, expected_type in REQUIRED_TYPES.items():
        if name not in settings:
            raise ValueError(f"Missing parameter: {name}")
        if type(settings[name]) is not expected_type:
            raise ValueError(f"Invalid type for: {name}")


def _validate_package_name(settings):
    """Validate a test package name or an Ubuntu package name."""
    pattern = (
        TEST_PACKAGE_PATTERN if settings["test_mode"]
        else APT_PACKAGE_PATTERN
    )
    if pattern.fullmatch(settings["package_name"]) is None:
        raise ValueError("Invalid package_name")


def _validate_repository(settings):
    """Check the test file path or basic syntax of the repository URL."""
    source = settings["repository"]
    if settings["test_mode"]:
        if not Path(source).is_file():
            raise ValueError("Invalid repository: file not found")
        return
    url = urlsplit(source)
    if url.scheme not in ("http", "https") or not url.netloc:
        raise ValueError("Invalid repository URL")


def _validate_output_file(settings):
    """Require an SVG filename for the generated dependency graph."""
    if Path(settings["output_file"]).suffix.lower() != ".svg":
        raise ValueError("Invalid output_file: expected .svg")


def validate_config(settings):
    """Validate the six required configuration parameters."""
    _validate_types(settings)
    _validate_package_name(settings)
    _validate_repository(settings)
    _validate_output_file(settings)


def load_config(path):
    """Read settings from a TOML file and validate them."""
    try:
        with path.open("rb") as file:
            settings = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ValueError(f"Cannot read TOML config: {error}") from error
    validate_config(settings)
    return settings
