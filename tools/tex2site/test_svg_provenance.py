"""Regression checks for stale diagrams after renumbering and source edits."""
import json
from pathlib import Path
import tempfile
import unittest
from svg_provenance import source_hash, file_hash, verified_svg


class StaleFigureTest(unittest.TestCase):
    def test_renumbering_and_shared_macro_change_require_rebuild(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            svg = root/'chapter04_fig_4_12.svg'
            svg.write_text('<svg>old lifecycle drawing</svg>', encoding='utf-8')
            digest = source_hash('lifecycle', 'fonts', 'macros-v1')
            (root/'svg-manifest.json').write_text(json.dumps({'figures': {svg.name: {
                'source_sha256': digest, 'svg_sha256': file_hash(svg)}}}), encoding='utf-8')
            self.assertEqual(verified_svg(root,svg.name,digest),svg)
            # A newly inserted figure shifts JWT into the same old filename.
            self.assertIsNone(verified_svg(root,svg.name,source_hash('JWT','fonts','macros-v1')))
            self.assertIsNone(verified_svg(root,svg.name,source_hash('lifecycle','fonts','macros-v2')))
            # A replaced output must not be accepted using a valid old source manifest.
            svg.write_text('<svg>unrelated picture</svg>', encoding='utf-8')
            self.assertIsNone(verified_svg(root,svg.name,digest))

    def test_unrecorded_legacy_svg_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder)/'chapter01_fig_1_5.svg').write_text('<svg/>',encoding='utf-8')
            self.assertIsNone(verified_svg(folder,'chapter01_fig_1_5.svg','any'))

    def test_builder_rebuilds_when_intermediate_pdf_is_missing_or_changed(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);svg=root/'chapter01_fig_1_5.svg';pdf=svg.with_suffix('.pdf')
            svg.write_text('<svg/>',encoding='utf-8')
            record={'source_sha256':'current','svg_sha256':file_hash(svg),'pdf_sha256':'missing'}
            (root/'svg-manifest.json').write_text(json.dumps({'figures':{svg.name:record}}),encoding='utf-8')
            self.assertEqual(verified_svg(root,svg.name,'current'),svg)
            self.assertIsNone(verified_svg(root,svg.name,'current',require_pdf=True))
            pdf.write_bytes(b'%PDF stale intermediate')
            self.assertIsNone(verified_svg(root,svg.name,'current',require_pdf=True))


if __name__ == '__main__':
    unittest.main()
