"""CLI entry point for the APT dependency graph visualizer."""

from pathlib import Path

from src.apt_repository import load_repository_graph
from src.config import load_config
from src.graph import build_graph, load_test_graph, reverse_repository


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.toml"


def main():
    """Show reverse dependencies in breadth-first search order."""
    try:
        settings = load_config(CONFIG_PATH)
        if settings["test_mode"]:
            repository = load_test_graph(settings["repository"])
        else:
            repository = load_repository_graph(settings["repository"])
        reversed_graph = reverse_repository(repository)
        graph = build_graph(
            reversed_graph, settings["package_name"],
            settings["exclude_substring"]
        )
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    package_name = settings["package_name"]
    print(f"Reverse dependency graph for {package_name} (BFS):")
    for package, dependents in graph.items():
        names = ", ".join(dependents) if dependents else "(none)"
        print(f"{package} <- {names}")
    all_dependents = list(graph)[1:]
    summary = ", ".join(all_dependents) if all_dependents else "(none)"
    print(f"All reverse dependencies: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
