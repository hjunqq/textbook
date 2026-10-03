"""R11 两条修订线整合后的跨文件回归检查（只用 Python 标准库）。

运行：python tools/test_reconcile_r11.py
这些检查不代替 Java/Vue 单元测试或 Docker 整栈验收。
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ReconciliationTest(unittest.TestCase):
    def test_online_and_print_labels_are_unique_and_resolvable(self):
        files = [*ROOT.glob('output/chapters/*.tex'),
                 *ROOT.glob('output/appendix/*.tex'), ROOT/'output/online/online.tex']
        labels: dict[str, Path] = {}
        references: set[str] = set()
        for path in files:
            text = re.sub(r'(?m)^\s*%.*$', '', path.read_text(encoding='utf-8'))
            for pair in re.findall(r'\\label\{([^}]+)\}|label=\{([^}]+)\}', text):
                label = next(value for value in pair if value)
                self.assertNotIn(label, labels, f'duplicate {label}: {path}')
                labels[label] = path
            references.update(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', text))
        self.assertFalse(references - labels.keys(), f'missing labels: {references-labels.keys()}')

    def test_online_topics_survive_learning_layer_regeneration(self):
        module = load_module('learning_layers', ROOT/'tools/learning_layers_table.py')
        original = (ROOT/'output/online/online.tex').read_text(encoding='utf-8')
        with tempfile.TemporaryDirectory(prefix='.reconcile-test-', dir=ROOT) as directory:
            target = Path(directory)/'online.tex'
            target.write_text(original, encoding='utf-8')
            with patch.object(module, 'ONLINE', target), patch('builtins.print'):
                module.main()
                first = target.read_text(encoding='utf-8')
                module.main()
            self.assertEqual(target.read_text(encoding='utf-8'), first)
            self.assertEqual(first.split(module.BEGIN)[0], original.split(module.BEGIN)[0])
            self.assertEqual(first.split(module.END)[1], original.split(module.END)[1])
        for label in ['app:ext-fe-focus-list', 'app:ext-fe-theme', 'app:ext-fe-release',
                      'app:ext-component-based-design', 'app:ext-ch06-gis-ops',
                      'app:ext-ch06-photogrammetry', 'app:ext-ch07-chart-runtime',
                      'app:ext-ch07-color-tokens', 'sec:appc-ch08-ops', 'online:teaching-guide']:
            self.assertIn('\\label{'+label+'}', original.split(module.BEGIN)[0])

    def test_java_packages_follow_file_locations_and_new_namespace(self):
        base = ROOT/'companion/water-platform-demo/backend/src'
        for kind in ('main', 'test'):
            source = base/kind/'java'
            for path in source.rglob('*.java'):
                text = path.read_text(encoding='utf-8')
                match = re.search(r'(?m)^package\s+([\w.]+);', text)
                self.assertIsNotNone(match, str(path))
                self.assertEqual(match.group(1).replace('.', '/'), path.parent.relative_to(source).as_posix())
                self.assertNotIn('edu.example.qingyuan', text)
        midpoint = (base/'main/java/edu/example/lesson54/Lesson54Application.java').read_text(encoding='utf-8')
        self.assertIn('edu.example.reservoir', midpoint)

    def test_stage54_ci_and_compose_use_same_database_names(self):
        ci = (ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
        compose = (ROOT/'companion/water-platform-demo/docker-compose.yml').read_text(encoding='utf-8')
        self.assertNotIn('qingyuan', ci + compose)
        for required in ['POSTGRES_DB: reservoir', 'POSTGRES_USER: reservoir_app',
                         'pg_isready -U reservoir_app -d reservoir',
                         'jdbc:postgresql://localhost:5432/reservoir']:
            self.assertIn(required, ci)
        self.assertIn('127.0.0.1:5432:5432', compose)
        self.assertIn('db-host', compose)

    def test_generated_station_data_and_frontend_copy_are_identical(self):
        module = load_module('teaching_datasets', ROOT/'companion/datasets/generate.py')
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            with patch.object(module, 'ROOT', temp):
                module.write_stations(module.stations())
            for name in ('stations.csv', 'stations.json'):
                self.assertEqual((temp/name).read_bytes(), (ROOT/'companion/datasets'/name).read_bytes())
        stations = (ROOT/'companion/datasets/stations.json').read_bytes()
        self.assertEqual(stations, (ROOT/'companion/water-platform-demo/frontend/public/datasets/stations.json').read_bytes())
        self.assertEqual(len(json.loads(stations)), 28)

    def test_student_text_uses_comment_layers_and_one_stage_system(self):
        for path in ROOT.glob('output/chapters/*.tex'):
            text = path.read_text(encoding='utf-8')
            self.assertNotIn('\\paragraph{本节层次}', text)
            self.assertNotIn('\\paragraph{进入本节所需知识}', text)
            self.assertNotRegex(text, r'(?m)^v[0-5]\s*&')
        preface = (ROOT/'output/chapters/preface.tex').read_text(encoding='utf-8')
        self.assertNotIn('\\section*{推荐教学组织方式}', preface)
        self.assertNotIn('两套编号', preface)

    def test_license_restricted_product_images_are_not_on_website(self):
        self.assertFalse(list((ROOT/'docs').rglob('51wim-*.jpg')))
        for path in (ROOT/'docs').rglob('*.md'):
            self.assertNotRegex(path.read_text(encoding='utf-8'), r'!\[[^\]]*\]\([^)]*51wim-[^)]*\.jpg')

    def test_glb_coordinate_transform_matches_exercise(self):
        module = load_module('dam_glb', ROOT/'companion/water-platform-demo/frontend/public/models/generate-dam-glb.py')
        for units in ('m', 'mm'):
            for z_up in (False, True):
                positions, normals, indices = module.build_mesh(units, z_up)
                scale = 0.001 if units == 'mm' else 1.0
                converted = [(x*scale, z*scale, -y*scale) if z_up else
                             (x*scale, y*scale, z*scale) for x, y, z in positions]
                extent = [max(p[k] for p in converted)-min(p[k] for p in converted) for k in range(3)]
                for value, expected in zip(extent, (160, 52, 40)):
                    self.assertAlmostEqual(value, expected, places=5)
                self.assertEqual(len(positions), 24)
                self.assertEqual(len(normals), 24)
                self.assertEqual(len(indices), 36)
        answer = (ROOT/'output/appendix/answers.tex').read_text(encoding='utf-8')
        self.assertIn('(160000,40000,52000)', answer)


if __name__ == '__main__':
    unittest.main(verbosity=2)
