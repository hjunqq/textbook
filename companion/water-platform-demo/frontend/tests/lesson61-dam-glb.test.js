// 6.1.4 节教学模型：public/models/dam.glb 由 generate-dam-glb.py 生成。
// 这里用 Three.js 自己的 GLTFLoader 解析它，并重放 load-dam.js 的三项检查，
// 确认“单位、轴向、基面”的答案与书中所说一致：不缩放、不旋转，只把底面抬到坝基高程。
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const MODELS = resolve(process.cwd(), 'public/models');   // vitest 以 frontend/ 为工作目录
const DAM_HEIGHT = 52, BASE_ELEV = 120;   // 与 load-dam.js 相同的已知尺寸（8.1 节）

function parse(file) {
  const bytes = readFileSync(file);
  // jsdom 环境下 Node Buffer 背后的 ArrayBuffer 不是当前全局的 ArrayBuffer，
  // GLTFLoader 的 instanceof 判断会失败，所以复制一份到当前环境的 ArrayBuffer 里
  const buffer = new ArrayBuffer(bytes.byteLength);
  new Uint8Array(buffer).set(bytes);
  return new Promise((resolve, reject) => new GLTFLoader().parse(buffer, '', resolve, reject));
}

/** 与书中清单 lst:ch06-gltf-load 相同的三步改正，返回改正后的包围盒。 */
function correct(model) {
  const size = () => new THREE.Box3().setFromObject(model).getSize(new THREE.Vector3());
  const applied = { scaled: false, rotated: false };
  if (Math.max(size().y, size().z) > DAM_HEIGHT * 100) { model.scale.setScalar(0.001); applied.scaled = true; }
  if (Math.abs(size().z - DAM_HEIGHT) < Math.abs(size().y - DAM_HEIGHT)) { model.rotation.x = -Math.PI / 2; applied.rotated = true; }
  const box = new THREE.Box3().setFromObject(model);
  model.position.y += BASE_ELEV - box.min.y;
  return { applied, box: new THREE.Box3().setFromObject(model) };
}

const near = (v, expected) => expect(v).toBeCloseTo(expected, 3);

describe('教学坝体模型 dam.glb', () => {
  it('GLTFLoader 能解析，且尺寸等于教学几何表：160 × 52 × 40 m，底面 y=0', async () => {
    const gltf = await parse(join(MODELS, 'dam.glb'));
    const meshes = [];
    gltf.scene.traverse(o => { if (o.isMesh) meshes.push(o); });
    expect(meshes).toHaveLength(1);
    expect(meshes[0].geometry.attributes.position.count).toBe(24);
    expect(meshes[0].geometry.index.count).toBe(36);
    expect(meshes[0].geometry.attributes.normal).toBeDefined();
    const box = new THREE.Box3().setFromObject(gltf.scene);
    near(box.min.x, -80); near(box.max.x, 80);
    near(box.min.y, 0); near(box.max.y, 52);
    near(box.min.z, -20); near(box.max.z, 20);
  });

  it('三项检查：默认文件只需抬到坝基高程，结果与 6.1.2 节坝体的包围盒相同', async () => {
    const gltf = await parse(join(MODELS, 'dam.glb'));
    const { applied, box } = correct(gltf.scene);
    expect(applied).toEqual({ scaled: false, rotated: false });
    near(box.min.y, 120); near(box.max.y, 172);
    near(box.min.x, -80); near(box.max.x, 80);
    near(box.min.z, -20); near(box.max.z, 20);
  });

  it('--units mm --z-up 生成的文件触发前两项检查，改正后与默认文件重合', async () => {
    const out = join(tmpdir(), `dam-mm-zup-${process.pid}.glb`);
    execFileSync('python3', [join(MODELS, 'generate-dam-glb.py'), '-o', out, '--units', 'mm', '--z-up']);
    const gltf = await parse(out);
    const raw = new THREE.Box3().setFromObject(gltf.scene).getSize(new THREE.Vector3());
    near(raw.x, 160000); near(raw.y, 40000); near(raw.z, 52000);
    const { applied, box } = correct(gltf.scene);
    expect(applied).toEqual({ scaled: true, rotated: true });
    near(box.min.y, 120); near(box.max.y, 172);
    near(box.min.z, -20); near(box.max.z, 20);
  });
});
