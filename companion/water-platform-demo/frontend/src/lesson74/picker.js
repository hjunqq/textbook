// S5 阶段包：射线拾取器。
// 与 7.4 节清单“PointPicker：射线拾取器”逐字一致，只把书中默认的全局 THREE
// 改成 ES 模块导入（配套工程用 Vite，没有全局 THREE）。
import * as THREE from 'three';

export class PointPicker {
  constructor(camera, scene, canvas) {
    this.camera = camera;
    this.scene = scene;
    this.canvas = canvas;
    this.raycaster = new THREE.Raycaster();
  }
  pick(clientX, clientY) {
    const rect = this.canvas.getBoundingClientRect();
    const ndc = new THREE.Vector2(
      2 * (clientX - rect.left) / rect.width - 1,
      1 - 2 * (clientY - rect.top) / rect.height);
    this.raycaster.setFromCamera(ndc, this.camera);
    return this.raycaster.intersectObjects(
      this.scene.children, true);
  }
}

/**
 * 从一组交点里找回业务对象。
 * 交点按距相机由近到远排序，但最近的那个未必是测点——
 * 可能是坝体本身（它的 userData.assetId 是 'DAM-A'，不是测点编码）。
 * 所以要沿列表往后找第一个真正绑定了测点的网格；一个都没有就返回 null，
 * 由调用方显示“未选中测点”，而不是默默高亮一个错误的球。
 */
export function firstAsset(intersections, isAsset = id => id && id !== 'DAM-A') {
  for (const hit of intersections) {
    let node = hit.object;
    // 测点可能是 Group 的子节点，标识写在自身或祖先上
    while (node) {
      if (isAsset(node.userData?.assetId)) return node;
      node = node.parent;
    }
  }
  return null;
}
