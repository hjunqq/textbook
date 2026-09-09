// S5 阶段包：图表与三维对象的双向联动。
// 与 7.3 节清单“ECharts与Three.js对象的双向联动控制器”逐字一致。
//
// 它不 import echarts 也不 import three：chart 与 scene 都是构造时传进来的。
// 因此这个模块可以用两个假对象在 Node 里直接测试——见 tests/lesson74.test.js。
// scene 是 scene-bus.js 造出来的应用层封装，不是 THREE.Scene（后者没有 on/off）。

export function createLinkController(chart, scene, readings) {
  const byAsset = new Map(readings.map((r, i) => [r.assetId, {i, r}]));
  const onChartClick = params => {
    const point = params.data?.assetId
      ? params.data : readings[params.dataIndex];
    if (!point) return;
    scene.focusAsset(point.assetId, point.occurredAt);
  };
  const onSceneSelect = object => {
    const assetId = object.userData.assetId;
    const hit = byAsset.get(assetId);
    if (!hit) return;
    chart.dispatchAction({type: 'highlight', seriesId: 'level', dataIndex: hit.i});
    chart.dispatchAction({type: 'showTip', seriesId: 'level', dataIndex: hit.i});
  };
  chart.on('click', onChartClick);
  // scene 是应用层的场景封装对象（带事件总线），
  // 不是 THREE.Scene 本身——后者没有 on/off 接口
  scene.on('select', onSceneSelect);
  return () => {
    chart.off('click', onChartClick);
    scene.off('select', onSceneSelect);
  };
}
