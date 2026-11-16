"""CLI entry point for APT dependency visualization (stage 5)."""

from pathlib import Path

from src.apt_repository import load_repository_graph
from src.config import load_config
from src.graph import build_graph, load_test_graph
from src.visualization import ascii_tree, render_svg, to_plantuml


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.toml"


def main():
    """Build the forward graph and save its PlantUML and SVG files."""
    try:
        settings = load_config(CONFIG_PATH)
        if settings["test_mode"]:
            repository = load_test_graph(settings["repository"])
        else:
            repository = load_repository_graph(settings["repository"])
        start = settings["package_name"]
        graph = build_graph(
            repository, start, settings["exclude_substring"]
        )
        source = to_plantuml(graph)
        svg_path = Path(settings["output_file"])
        puml_path = svg_path.with_suffix(".puml")
        puml_path.parent.mkdir(parents=True, exist_ok=True)
        puml_path.write_text(source, encoding="utf-8")
        render_svg(source, svg_path)
    except (OSError, ValueError) as error:
        print(f"Error: {error}")
        return 1

    print(f"Dependency graph for {start} (BFS):")
    print(f"PlantUML saved to: {puml_path}")
    print(f"SVG saved to: {svg_path}")
    if settings["ascii_tree"]:
        print("ASCII dependency tree:")
        print(ascii_tree(graph, start))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
