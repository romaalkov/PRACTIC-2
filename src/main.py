
"""CLI entry point for the APT dependency graph visualizer."""

from pathlib import Path

from src.apt_repository import get_direct_dependencies
from src.config import load_config


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.toml"


def main():
    """Print direct dependencies for a selected Ubuntu package."""
    try:
        settings = load_config(CONFIG_PATH)
        if settings["test_mode"]:
            raise ValueError("Test repository mode will be added in stage 3")
        dependencies = get_direct_dependencies(
            settings["repository"], settings["package_name"]
        )
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    print(f"Direct dependencies of {settings['package_name']}:")
    if not dependencies:
        print("(none)")
    for dependency in dependencies:
        print(f"- {dependency}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
