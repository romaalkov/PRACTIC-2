"""Create PlantUML diagrams, SVG files and text dependency trees."""

import os
from pathlib import Path
import subprocess
from urllib.request import urlopen
from xml.etree import ElementTree
import zlib


ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
SERVER_URL = "https://www.plantuml.com/plantuml/svg/"
MAX_PLANTUML_URL_LENGTH = 6000


def to_plantuml(graph):
    """Build a PlantUML description of a directed dependency graph."""
    nodes = list(dict.fromkeys(
        [*graph, *(child for values in graph.values() for child in values)]
    ))
    aliases = {name: f"N{number}" for number, name in enumerate(nodes)}
    lines = ["@startuml", "left to right direction",
             "skinparam backgroundColor white"]
    for name in nodes:
        lines.append(f'rectangle "{name}" as {aliases[name]}')
    for package, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(f"{aliases[package]} --> {aliases[dependency]}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def ascii_tree(graph, start):
    """Show graph edges as a text tree, marking repeated nodes."""
    lines = [start]
    visited = {start}
    stack = [(start, "", list(graph.get(start, [])), 0)]
    while stack:
        package, prefix, neighbors, index = stack[-1]
        if index >= len(neighbors):
            stack.pop()
            continue
        stack[-1] = (package, prefix, neighbors, index + 1)
        child = neighbors[index]
        last = index == len(neighbors) - 1
        branch = "└── " if last else "├── "
        repeated = child in visited
        suffix = " (already shown)" if repeated else ""
        lines.append(f"{prefix}{branch}{child}{suffix}")
        if not repeated:
            visited.add(child)
            child_prefix = prefix + ("    " if last else "│   ")
            stack.append((child, child_prefix, list(graph.get(child, [])), 0))
    return "\n".join(lines)


def encode_plantuml(text):
    """Encode text as deflate and PlantUML's custom base64 alphabet."""
    compressor = zlib.compressobj(wbits=-15)
    packed = compressor.compress(text.encode("utf-8")) + compressor.flush()
    result = []
    for offset in range(0, len(packed), 3):
        chunk = packed[offset:offset + 3].ljust(3, b"\0")
        first, second, third = chunk
        numbers = (
            first >> 2,
            ((first & 3) << 4) | (second >> 4),
            ((second & 15) << 2) | (third >> 6),
            third & 63,
        )
        result.extend(ALPHABET[number] for number in numbers)
    return "".join(result)


def _render_local(svg_path, jar_path):
    """Render the matching .puml file using a local PlantUML JAR."""
    puml_path = svg_path.with_suffix(".puml")
    try:
        result = subprocess.run(
            ["java", "-jar", str(jar_path), "-tsvg", str(puml_path)],
            capture_output=True, text=True, check=False, timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError(f"Local PlantUML error: {error}") from error
    if result.returncode != 0 or not svg_path.is_file():
        raise ValueError(f"PlantUML could not render: {result.stderr}")


def _render_server(source, svg_path):
    """Ask the public PlantUML server to produce SVG."""
    url = SERVER_URL + encode_plantuml(source)
    if len(url) > MAX_PLANTUML_URL_LENGTH:
        raise ValueError(
            "Diagram is too large for URL rendering. "
            "Set PLANTUML_JAR for local rendering."
        )
    try:
        with urlopen(url, timeout=45) as response:
            image = response.read()
    except OSError as error:
        raise ValueError(f"PlantUML server error: {error}") from error
    try:
        root = ElementTree.fromstring(image)
    except ElementTree.ParseError as error:
        raise ValueError("PlantUML returned invalid SVG") from error
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("PlantUML did not return an SVG image")
    svg_path.write_bytes(image)


def render_svg(source, path):
    """Render to SVG locally if configured, or via PlantUML server."""
    svg_path = Path(path)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    jar_path = os.environ.get("PLANTUML_JAR")
    if jar_path:
        _render_local(svg_path, jar_path)
    else:
        _render_server(source, svg_path)
