"""CLI entry point for the APT dependency graph visualizer."""

from pathlib import Path

from src.apt_repository import load_repository_graph
from src.config import load_config
from src.graph import build_graph, load_test_graph


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.toml"


def main():
    """Build and print a dependency graph in BFS visit order."""
    try:
        settings = load_config(CONFIG_PATH)
        if settings["test_mode"]:
            repository = load_test_graph(settings["repository"])
        else:
            repository = load_repository_graph(settings["repository"])
        graph = build_graph(
            repository, settings["package_name"],
            settings["exclude_substring"]
        )
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    print(f"Dependency graph for {settings['package_name']} (BFS):")
    for package, dependencies in graph.items():
        names = ", ".join(dependencies) if dependencies else "(none)"
        print(f"{package} -> {names}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
