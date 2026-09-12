"""Resolve original raster assets embedded in otherwise vector TikZ figures."""
import base64
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from svg_provenance import file_hash


_GRAPHICS = re.compile(r"\\includegraphics\*?(?:\[[^\]]*\])?\{([^}]+)\}")


def graphics_paths(snippet):
    paths = _GRAPHICS.findall(snippet)
    if len(paths) != len(re.findall(r"\\includegraphics\*?(?![A-Za-z])", snippet)):
        raise ValueError("混合图的 includegraphics 必须直接指定 PNG 文件路径")
    return paths


def generated_source(tex_path, output):
    """Only generated PNGs are eligible; licensed screenshots cannot enter SVGs."""
    path = tex_path.replace(r"\_", "_")
    if not re.fullmatch(r"images/generated/[A-Za-z0-9_.-]+\.png", path):
        raise ValueError("TikZ 混合图仅允许 images/generated 下的原创 PNG: " + tex_path)
    root = (Path(output) / "images/generated").resolve()
    source = (Path(output) / path).resolve()
    if not source.is_relative_to(root):
        raise ValueError("混合图路径越界: " + tex_path)
    if not source.is_file():
        raise FileNotFoundError(source)
    return path, source


def graphics_dependencies(snippet, output):
    dependencies = {}
    for tex_path in graphics_paths(snippet):
        path, source = generated_source(tex_path, output)
        dependencies[path] = file_hash(source)
    return dict(sorted(dependencies.items()))


def stage_graphics(dependencies, output, build):
    """Use relative TeX paths and verify the staged bytes against current inputs."""
    for path, digest in dependencies.items():
        relative, source = generated_source(path, output)
        if file_hash(source) != digest:
            raise ValueError("混合图图片在准备编译时发生变化: " + path)
        target = Path(build) / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        if not target.is_file() or target.read_bytes() != data:
            target.write_bytes(data)
        if file_hash(target) != digest:
            raise ValueError("混合图图片在复制时发生变化: " + path)


def verify_embedded_images(svg, required=False):
    """Cairo must embed pixels, never leave browser-dependent filesystem links."""
    images = [element for element in ET.parse(svg).iter()
              if element.tag.rsplit("}", 1)[-1] == "image"]
    if required and not images:
        raise ValueError("混合图 SVG 缺少嵌入图片: " + str(svg))
    for element in images:
        href = element.get("href") or element.get("{http://www.w3.org/1999/xlink}href", "")
        if not href.startswith("data:image/png;base64,"):
            raise ValueError("SVG 图片必须内嵌为 PNG 数据: " + str(svg))
        try:
            pixels = base64.b64decode(href.split(",", 1)[1], validate=True)
        except ValueError as error:
            raise ValueError("SVG 内嵌图片编码无效: " + str(svg)) from error
        if not pixels.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("SVG 内嵌图片不是 PNG: " + str(svg))
