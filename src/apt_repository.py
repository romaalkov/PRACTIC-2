
"""Read direct APT dependencies from an Ubuntu Packages.gz index."""

import gzip
from io import TextIOWrapper
import re
from urllib.request import urlopen


PACKAGE_NAME = re.compile(r"^[a-z0-9][a-z0-9+.-]*")


def iter_packages(lines):
    """Yield package metadata records from deb822-style text."""
    record = {}
    last_key = None
    for raw_line in lines:
        line = raw_line.rstrip("\r\n")
        if not line:
            if record:
                yield record
            record = {}
            last_key = None
        elif line[0].isspace():
            if last_key:
                record[last_key] += " " + line.strip()
        elif ":" in line:
            last_key, value = line.split(":", 1)
            record[last_key] = value.strip()
    if record:
        yield record


def parse_dependencies(value):
    """Extract package names and preserve alternative dependency groups."""
    result = []
    for group in value.split(","):
        alternatives = []
        for part in group.split("|"):
            match = PACKAGE_NAME.match(part.strip())
            if match:
                alternatives.append(match.group())
        if alternatives:
            result.append(" | ".join(alternatives))
    return result


def get_direct_dependencies(url, package):
    """Fetch an index and return the target package's direct dependencies."""
    try:
        with urlopen(url, timeout=30) as response:
            with gzip.GzipFile(fileobj=response, mode="rb") as archive:
                with TextIOWrapper(archive, encoding="utf-8") as stream:
                    for entry in iter_packages(stream):
                        if entry.get("Package") == package:
                            fields = ("Pre-Depends", "Depends")
                            raw = ", ".join(
                                entry[key] for key in fields if key in entry
                            )
                            return parse_dependencies(raw)
    except (OSError, EOFError) as error:
        raise ValueError(f"Cannot read repository: {error}") from error
    raise ValueError(f"Package not found in repository: {package}")
