"""A portrait remains part of its diagram and cannot bypass image provenance."""
import base64
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import convert
from hybrid_graphics import (graphics_dependencies, stage_graphics,
                            verify_embedded_images)
from svg_provenance import source_hash, file_hash, verified_svg


PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=")
SNIPPET = (r"\begin{tikzpicture}\node (actor) {"
           r"\includegraphics[width=2cm]{images/generated/personnel-operator.png}};"
           r"\draw (actor.east)--++(1,0);\end{tikzpicture}")


class HybridFigureTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.output = self.root / "output"
        self.source = self.output / "images/generated/personnel-operator.png"
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(PNG)

    def test_portraits_and_connectors_produce_one_vector_job(self):
        figure = (r"\begin{figure}" + SNIPPET +
                  r"\caption{用例图}\label{fig:hybrid-test}\end{figure}")
        with patch.object(convert, "SRC", self.output / "chapters"):
            converter = convert.Conv("chapter03", 3)
            converter.extract_fig(figure)
        self.assertEqual(converter.tikz_jobs, [("chapter03_fig_3_1.svg", SNIPPET)])
        self.assertEqual(converter.raster_jobs, [])
        self.assertEqual(sum(text.count("![图") for text in converter.tokens.values()), 1)
        self.assertIn(r"\draw (actor.east)", converter.tikz_jobs[0][1])

    def test_changed_portrait_invalidates_cached_svg_without_tex_changes(self):
        dependencies = graphics_dependencies(SNIPPET, self.output)
        digest = source_hash(SNIPPET, "preamble", "definitions", dependencies)
        svg = self.root / "figure.svg"
        svg.write_text("<svg/>", encoding="utf-8")
        (self.root / "svg-manifest.json").write_text(json.dumps({"figures": {
            svg.name: {"source_sha256": digest, "svg_sha256": file_hash(svg)}}}), encoding="utf-8")
        self.assertEqual(verified_svg(self.root, svg.name, digest), svg)
        self.source.write_bytes(PNG + b"updated asset")
        changed = graphics_dependencies(SNIPPET, self.output)
        self.assertIsNone(verified_svg(self.root, svg.name,
                          source_hash(SNIPPET, "preamble", "definitions", changed)))
        with self.assertRaisesRegex(ValueError, "发生变化"):
            stage_graphics(dependencies, self.output, self.root / "build")

    def test_optional_short_caption_keeps_full_caption_and_ai_disclosure(self):
        full_caption = "水利工程安全监测平台用例图（人物为AI生成教学渲染）"
        for caption_command in (r"\caption", r"\caption[用例图]", "\\caption [用例图]\n"):
            with self.subTest(command=caption_command), patch.object(convert, "SRC", self.output / "chapters"):
                converter = convert.Conv("chapter03", 3)
                converter.extract_fig(r"\begin{figure}" + SNIPPET + caption_command + "{" +
                                      full_caption + r"}\label{fig:hybrid-test}\end{figure}")
            rendered = "".join(converter.tokens.values())
            self.assertIn("<figcaption>图 3.1  " + full_caption + "</figcaption>", rendered)

    def test_licensed_runtime_and_traversal_assets_cannot_enter_hybrid_svg(self):
        for path in ("images/chapter08/51wim-test.jpg", "images/generated/51wim-test.jpg",
                     "images/runtime/operator.png", "images/generated/../../private.png",
                     "C:/outside/personnel-operator.png"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "原创 PNG"):
                graphics_dependencies(SNIPPET.replace("images/generated/personnel-operator.png", path),
                                      self.output)
        licensed = SNIPPET.replace("images/generated/personnel-operator.png",
                                   "images/chapter08/51wim-security.jpg")
        webfigs = self.root / "webfigs"
        webfigs.mkdir()
        (webfigs / "51wim-security.tex").write_text(r"\begin{tikzpicture}\end{tikzpicture}", encoding="utf-8")
        with patch.object(convert, "WEBFIGS", webfigs), self.assertRaisesRegex(ValueError, "原创 PNG"):
            convert.Conv("chapter03", 3).extract_fig(r"\begin{figure}" + licensed + r"\end{figure}")
        outside = r"\includegraphics{images/generated/personnel-operator.png}"
        with patch.object(convert, "SRC", self.output / "chapters"), self.assertRaisesRegex(ValueError, "同一个 TikZ"):
            convert.Conv("chapter03", 3).extract_fig(
                r"\begin{figure}" + SNIPPET + outside + r"\end{figure}")

    def test_staged_assets_and_embedded_svg_need_no_external_image_file(self):
        dependencies = graphics_dependencies(SNIPPET, self.output)
        build = self.root / "build"
        stage_graphics(dependencies, self.output, build)
        self.assertEqual((build / "images/generated/personnel-operator.png").read_bytes(), PNG)
        svg = self.root / "figure.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><image href="data:image/png;base64,'
                       + base64.b64encode(PNG).decode() + '"/></svg>', encoding="utf-8")
        verify_embedded_images(svg, required=True)
        svg.write_text('<svg><image href="images/generated/personnel-operator.png"/></svg>', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "内嵌"):
            verify_embedded_images(svg, required=True)
        svg.write_text("<svg/>", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "缺少"):
            verify_embedded_images(svg, required=True)

    def test_pure_vector_hash_stays_compatible(self):
        expected = hashlib.sha256(json.dumps(["drawing", "fonts", "macros"],
                                            ensure_ascii=False).encode()).hexdigest()
        self.assertEqual(source_hash("drawing", "fonts", "macros", {}), expected)


if __name__ == "__main__":
    unittest.main()
