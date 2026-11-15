
"""CLI entry point for the APT dependency graph visualizer."""

from pathlib import Path

from src.config import load_config


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.toml"


def main():
    """Print checked configuration settings."""
    try:
        settings = load_config(CONFIG_PATH)
    except ValueError as error:
        print(f"Configuration error: {error}")
        return 1

    for name, value in settings.items():
        print(f"{name} = {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
