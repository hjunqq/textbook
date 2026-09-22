// 截图专用视图：保留阶段模块、台账坐标和观测，只调整相机并添加识读标记。
// 所有标记均由浏览器在原 Three.js 场景坐标上绘制，不对 PNG 做后期绘制。
module.exports = async function prepareSceneDisplay(page, { linked = false } = {}) {
  return page.evaluate(async ({ linked }) => {
    const url = performance.getEntriesByType('resource').find(e => /\/three\.js(?:\?|$)/.test(e.name))?.name;
    if (!url) throw new Error('Loaded Three.js module not found');
    const THREE = await import(url);
    const { scene, camera, renderer, controls } = window;
    const group = scene.getObjectByName('assets');
    const mesh = group.children.find(m => m.userData.assetId === 'DAM-A-PZ-07');
    if (!mesh) throw new Error('Bound PZ-07 mesh not found');
    const positions = group.children.map(m => [m.userData.assetId, ...m.position.toArray()]);
    const selected = mesh.position.clone();
    // 渗压计埋在坝体内部（台账高程在坝基与坝顶之间），截图时把坝体材质调为半透明，
    // 只改显示属性，不改几何体、位置和台账坐标。
    Object.assign(window.dam.material, { transparent: true, opacity: 0.35 });
    window.dam.material.needsUpdate = true;
    const width = linked ? 464 : 600, height = 440;
    const groundY = window.dam.position.y - window.dam.geometry.parameters.height / 2;
    const grid = new THREE.GridHelper(100, 10, 0x94aabd, 0xc4d0da);
    grid.position.set(selected.x, groundY, selected.z);
    grid.userData.captureGuide = true;
    scene.add(grid);
    const guideGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(selected.x, groundY, selected.z), selected,
    ]);
    const guide = new THREE.Line(guideGeometry, new THREE.LineDashedMaterial({ color: 0x678296, dashSize: 2, gapSize: 1 }));
    guide.computeLineDistances(); scene.add(guide);
    const target = selected.clone().add(new THREE.Vector3(0, 6, 0));
    camera.position.copy(target).add(new THREE.Vector3(62, 48, 104));
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    controls.target.copy(target); controls.update();
    renderer.setSize(width, height);
    Object.assign(renderer.domElement.style, { position: 'fixed', left: '0', top: '0' });
    mesh.material.color.set(0xffa000);
    renderer.render(scene, camera);
    const projected = selected.clone().project(camera);
    const click = { x: (projected.x + 1) * width / 2, y: (1 - projected.y) * height / 2 };
    const ground = new THREE.Vector3(selected.x, groundY, selected.z).project(camera);
    const html = document.createElement('div');
    html.id = 'capture-scene-guide';
    Object.assign(html.style, { pointerEvents: 'none', position: 'fixed', inset: '0', fontFamily: 'Microsoft YaHei, sans-serif', color: '#173b54' });
    const title = linked ? '① 点击三维测点' : '测点绑定的局部视图';
    const coordinate = selected.toArray().map(v => v.toFixed(2));
    html.innerHTML = `<div style="position:absolute;left:24px;top:20px;font-size:24px;font-weight:600">${title}</div>
      <div style="position:absolute;left:${Math.min(click.x + 16, width - 205)}px;top:${click.y - 37}px;font-size:21px;background:#ffffffed;border-left:4px solid #ed9700;padding:6px 10px">DAM-A-PZ-07</div>
      <div style="position:absolute;left:24px;bottom:20px;font-size:18px;line-height:1.55">Y 轴向上 · 球体代表测点 · 坝体显示为半透明<br>网格间距 10 m · 水平参考面 y = ${groundY.toFixed(0)} m</div>
      <div style="position:absolute;left:${click.x + 16}px;top:${(1 - ground.y) * height / 2 - 5}px;font-size:18px">垂直投影</div>`;
    if (!linked) html.innerHTML += `<div style="position:absolute;left:620px;right:22px;top:22px;bottom:22px;background:#fff;border:1px solid #bdcbd6;border-radius:5px;padding:22px;font-size:23px;line-height:1.65;box-sizing:border-box">
      <div style="font-size:24px;font-weight:600;margin-bottom:13px">通过编码定位测点</div>
      <div style="font-size:22px;color:#925a00;background:#fff4dc;padding:8px 12px">bound.find('DAM-A-PZ-07')</div>
      <div style="margin-top:12px">局部坐标（m）</div>
      <div>x = ${coordinate[0]}<br>y = ${coordinate[1]}（高程）<br>z = ${coordinate[2]}</div>
      <div style="font-size:19px;color:#526777;border-top:1px solid #d4dee5;margin-top:14px;padding-top:12px">场景共绑定 ${group.children.length} 个测点<br>当前相机聚焦 PZ-07</div></div>`;
    document.body.append(html);
    document.querySelector('#tip').style.display = 'none';
    if (JSON.stringify(positions) !== JSON.stringify(group.children.map(m => [m.userData.assetId, ...m.position.toArray()]))) throw new Error('Asset positions changed');
    return { selectedAssetId: mesh.userData.assetId, actualAssets: group.children.length, coordinate: selected.toArray(), groundY, gridSpacing: 10, geometryAndCoordinatesUnchanged: true, click, viewport: { width, height }, annotation: '采集时添加局部参考网格、投影线与编码标签；调整相机；坝体材质调为半透明以显示埋在坝内的渗压计；不代表阶段页默认外观' };
  }, { linked });
};
