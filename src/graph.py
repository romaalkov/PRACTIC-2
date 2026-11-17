"""Load test dependency data and build graphs with iterative BFS."""

from collections import deque
from pathlib import Path
import re


TEST_NAME = re.compile(r"[A-Z]+")


def _read_test_lines(path):
    """Read the test repository file, reporting file access problems."""
    try:
        return Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValueError(f"Cannot read test repository: {error}") from error


def _parse_test_record(line, number):
    """Parse and validate one test record such as 'A: B, C'."""
    if ":" not in line:
        raise ValueError(f"Invalid test data on line {number}")
    package, raw_dependencies = line.split(":", 1)
    package = package.strip()
    dependencies = [
        name.strip() for name in raw_dependencies.split(",")
        if name.strip()
    ]
    names = [package, *dependencies]
    if not all(TEST_NAME.fullmatch(name) for name in names):
        raise ValueError(f"Invalid package name on line {number}")
    return package, list(dict.fromkeys(dependencies))


def _check_test_repository(repository):
    """Reject an empty repository or undefined dependency names."""
    if not repository:
        raise ValueError("Test repository is empty")
    referenced = {
        dependency for dependencies in repository.values()
        for dependency in dependencies
    }
    missing = referenced - repository.keys()
    if missing:
        raise ValueError(f"Undefined packages: {', '.join(sorted(missing))}")


def load_test_graph(path):
    """Load test packages with uppercase Latin-letter names."""
    repository = {}
    for number, raw_line in enumerate(_read_test_lines(path), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        package, dependencies = _parse_test_record(line, number)
        if package in repository:
            raise ValueError(f"Duplicate package: {package}")
        repository[package] = dependencies
    _check_test_repository(repository)
    return repository


def build_graph(repository, start, exclude_substring=""):
    """Traverse dependencies breadth-first without recursion."""
    if start not in repository:
        raise ValueError(f"Package not found: {start}")
    if exclude_substring and exclude_substring in start:
        raise ValueError("The selected package matches the exclusion filter")
    queue = deque([start])
    visited = {start}
    graph = {}
    while queue:
        package = queue.popleft()
        neighbors = list(dict.fromkeys(
            dependency for dependency in repository.get(package, [])
            if not exclude_substring or exclude_substring not in dependency
        ))
        graph[package] = neighbors
        for dependency in neighbors:
            if dependency not in visited:
                visited.add(dependency)
                queue.append(dependency)
    return graph


def reverse_repository(repository):
    """Return lists of packages that depend on each package."""
    reversed_graph = {package: [] for package in repository}
    for package, dependencies in repository.items():
        for dependency in dependencies:
            reversed_graph.setdefault(dependency, []).append(package)
    return {
        package: list(dict.fromkeys(dependents))
        for package, dependents in reversed_graph.items()
    }
