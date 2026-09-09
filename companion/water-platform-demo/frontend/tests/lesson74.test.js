// S5 阶段包的验收：双向联动与拾取回指。
// chart 与 scene 都是注入的，所以这些用例既不需要 echarts 也不需要 WebGL。
import { describe, it, expect, beforeEach } from 'vitest';
import { createSceneBus } from '../src/lesson74/scene-bus.js';
import { createLinkController } from '../src/lesson74/link.js';
import { firstAsset } from '../src/lesson74/picker.js';

/** 假的 Three.js 网格：只保留联动真正用到的两样东西——材质颜色与业务标识。 */
const mesh = (assetId, parent = null) => ({
  userData: assetId ? { assetId } : {},
  material: { color: { value: 0x1565c0, set(v) { this.value = v; } } },
  parent,
});

/** 假的 bindAssets 返回值 */
function fakeBound(ids) {
  const byId = new Map(ids.map(id => [id, mesh(id)]));
  return { byId, find: id => byId.get(id) };
}

/** 假的 ECharts 实例：记录收到的 action 与已注册的处理器 */
function fakeChart() {
  const handlers = new Map();
  return {
    actions: [],
    handlers,
    on(evt, fn) { if (!handlers.has(evt)) handlers.set(evt, new Set()); handlers.get(evt).add(fn); },
    off(evt, fn) { handlers.get(evt)?.delete(fn); },
    dispatchAction(a) { this.actions.push(a); },
    fire(evt, params) { for (const fn of [...(handlers.get(evt) ?? [])]) fn(params); },
  };
}

const READINGS = [
  { assetId: 'DAM-A-PZ-07', occurredAt: '2026-07-01T00:00:00+08:00', value: 180.0, quality: 'valid' },
  { assetId: 'DAM-A-WL-01', occurredAt: '2026-07-01T00:05:00+08:00', value: 164.99, quality: 'valid' },
  { assetId: 'DAM-A-RF-01', occurredAt: '2026-07-01T00:10:00+08:00', value: 8.45, quality: 'valid' },
];

describe('场景封装', () => {
  let bound, bus;
  beforeEach(() => { bound = fakeBound(['DAM-A-PZ-07', 'DAM-A-WL-01']); bus = createSceneBus(bound); });

  it('focusAsset 高亮目标并把上一个复原', () => {
    expect(bus.focusAsset('DAM-A-PZ-07')).toBe(true);
    expect(bound.find('DAM-A-PZ-07').material.color.value).toBe(0xffa000);
    bus.focusAsset('DAM-A-WL-01');
    expect(bound.find('DAM-A-PZ-07').material.color.value).toBe(0x1565c0);
    expect(bound.find('DAM-A-WL-01').material.color.value).toBe(0xffa000);
    expect(bus.focused).toBe('DAM-A-WL-01');
  });

  it('场景里没有这个球时返回 false，不抛异常', () => {
    expect(bus.focusAsset('DAM-A-XX-99')).toBe(false);
    expect(bus.focused).toBeNull();
  });

  it('dispose 后复原颜色并清空订阅', () => {
    let hits = 0;
    bus.on('select', () => hits++);
    bus.focusAsset('DAM-A-PZ-07');
    bus.dispose();
    expect(bound.find('DAM-A-PZ-07').material.color.value).toBe(0x1565c0);
    bus.emit('select', mesh('DAM-A-PZ-07'));
    expect(hits).toBe(0);
  });
});

describe('双向联动', () => {
  let bound, bus, chart, unlink;
  beforeEach(() => {
    bound = fakeBound(['DAM-A-PZ-07', 'DAM-A-WL-01', 'DAM-A-RF-01']);
    bus = createSceneBus(bound);
    chart = fakeChart();
    unlink = createLinkController(chart, bus, READINGS);
  });

  it('点图表 → 高亮对应的三维对象（按 dataIndex）', () => {
    chart.fire('click', { dataIndex: 1, data: {} });
    expect(bus.focused).toBe('DAM-A-WL-01');
    expect(bus.focusedAt).toBe('2026-07-01T00:05:00+08:00');
  });

  it('params.data 自带 assetId 时优先用它，不靠下标', () => {
    chart.fire('click', { dataIndex: 0, data: { assetId: 'DAM-A-RF-01', occurredAt: 'x' } });
    expect(bus.focused).toBe('DAM-A-RF-01');
  });

  it('下标越界时安静返回，不高亮任何对象', () => {
    chart.fire('click', { dataIndex: 99, data: {} });
    expect(bus.focused).toBeNull();
  });

  it('点三维对象 → 图表 highlight 与 showTip 到同一下标', () => {
    bus.select(bound.find('DAM-A-RF-01'));
    expect(chart.actions).toEqual([
      { type: 'highlight', seriesId: 'level', dataIndex: 2 },
      { type: 'showTip', seriesId: 'level', dataIndex: 2 },
    ]);
  });

  it('曲线里没有该对象时不发 action', () => {
    bound.byId.set('DAM-A-D-01', mesh('DAM-A-D-01'));
    bus.select(bound.find('DAM-A-D-01'));
    expect(chart.actions).toHaveLength(0);
  });

  it('解绑后再点击不再叠加处理器', () => {
    unlink();
    chart.fire('click', { dataIndex: 0, data: {} });
    bus.select(bound.find('DAM-A-PZ-07'));
    expect(chart.actions).toHaveLength(0);
  });
});

describe('拾取回指', () => {
  it('跳过坝体，取第一个真正的测点', () => {
    const hits = [{ object: mesh('DAM-A') }, { object: mesh('DAM-A-PZ-07') }];
    expect(firstAsset(hits).userData.assetId).toBe('DAM-A-PZ-07');
  });

  it('标识写在祖先节点上也能找回', () => {
    const group = mesh('DAM-A-WL-01');
    expect(firstAsset([{ object: mesh(null, group) }]).userData.assetId).toBe('DAM-A-WL-01');
  });

  it('只点到坝体或空白时返回 null，由调用方提示未选中', () => {
    expect(firstAsset([{ object: mesh('DAM-A') }])).toBeNull();
    expect(firstAsset([])).toBeNull();
  });
});
