
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


def validate_config(settings):
    """Validate all configuration parameters."""
    for name, expected_type in REQUIRED_TYPES.items():
        if name not in settings:
            raise ValueError(f"Missing parameter: {name}")
        if type(settings[name]) is not expected_type:
            raise ValueError(f"Invalid type for: {name}")

    package = settings["package_name"]
    pattern = r"[A-Z]+" if settings["test_mode"] else r"[a-z0-9][a-z0-9+.-]*"
    if re.fullmatch(pattern, package) is None:
        raise ValueError("Invalid package_name")

    source = settings["repository"]
    if settings["test_mode"]:
        if not Path(source).is_file():
            raise ValueError("Invalid repository: file not found")
    else:
        url = urlsplit(source)
        if url.scheme not in ("http", "https") or not url.netloc:
            raise ValueError("Invalid repository URL")

    if Path(settings["output_file"]).suffix.lower() != ".svg":
        raise ValueError("Invalid output_file: expected .svg")


def load_config(path):
    """Read settings from a TOML file and validate them."""
    try:
        with path.open("rb") as file:
            settings = tomllib.load(file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ValueError(f"Cannot read TOML config: {error}") from error

    validate_config(settings)
    return settings
