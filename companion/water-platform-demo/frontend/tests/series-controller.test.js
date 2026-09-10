import { describe, it, expect } from 'vitest';
import { createSeriesController } from '../src/lesson74/series-controller.js';
import { createSceneBus } from '../src/lesson74/scene-bus.js';

const PZ = 'DAM-A-PZ-07';
const WL = 'DAM-A-WL-01';
const EMPTY = 'DAM-A-D-01';
const reading = assetId => [{ assetId, occurredAt: '2026-07-01T00:00:00+08:00',
  value: 12, unit: 'm', quality: 'valid' }];

function setup() {
  const waiting = [];
  const handlers = new Map();
  const chart = {
    option: null, actions: [],
    clear() { this.option = null; },
    setOption(value) { this.option = value; },
    on(event, fn) { handlers.set(event, fn); },
    off(event, fn) { if (handlers.get(event) === fn) handlers.delete(event); },
    dispatchAction(action) { this.actions.push(action); },
  };
  const status = { textContent: '' };
  const scene = createSceneBus({ find: () => null });
  const controller = createSeriesController({ chart, scene, status,
    // 故意忽略取消信号，证明仅靠 abort 不足以阻止已完成的旧请求。
    loadSeries: (id, signal) => new Promise((resolve, reject) => {
      waiting.push({ id, signal, resolve, reject });
    }),
  });
  scene.on('select', mesh => controller.showAsset(mesh.userData.assetId));
  return { controller, waiting, chart, status, scene, handlers };
}

describe('S5 曲线切换的异常路径', () => {
  it('新对象先返回后，旧响应不能覆盖曲线或状态', async () => {
    const s = setup();
    const old = s.controller.showAsset(PZ);
    const latest = s.controller.showAsset(WL);
    expect(s.waiting[0].signal.aborted).toBe(true);
    s.waiting[1].resolve(reading(WL)); await latest;
    const option = s.chart.option;
    s.waiting[0].resolve(reading(PZ)); await old;
    expect(s.chart.option).toBe(option);
    expect(s.status.textContent).toContain(WL);
  });

  it('加载空对象时立即解绑；空结果不留下旧曲线点击事件', async () => {
    const s = setup();
    const first = s.controller.showAsset(PZ);
    s.waiting[0].resolve(reading(PZ)); await first;
    const next = s.controller.showAsset(EMPTY);
    expect(s.handlers.size).toBe(0);
    expect(s.chart.option).toBeNull();
    s.waiting[1].resolve([]); await next;
    expect(s.status.textContent).toBe(`${EMPTY}：暂无观测`);
    expect(s.handlers.size).toBe(0);
  });

  it('当前网络错误显示原因，重新选择后能够恢复', async () => {
    const s = setup();
    const first = s.controller.showAsset(PZ);
    s.waiting[0].reject(new Error('HTTP 503')); await first;
    expect(s.status.textContent).toContain('HTTP 503');
    expect(s.chart.option).toBeNull();
    const next = s.controller.showAsset(PZ);
    s.waiting[1].resolve(reading(PZ)); await next;
    expect(s.status.textContent).toBe(`${PZ}：1 条观测`);
  });

  it('旧请求失败不能覆盖新对象的成功状态', async () => {
    const s = setup();
    const old = s.controller.showAsset(PZ);
    const next = s.controller.showAsset(WL);
    s.waiting[1].resolve(reading(WL)); await next;
    s.waiting[0].reject(new Error('旧请求超时')); await old;
    expect(s.status.textContent).toBe(`${WL}：1 条观测`);
  });

  it('卸载后到达的结果不能再次创建曲线或监听器', async () => {
    const s = setup();
    const first = s.controller.showAsset(PZ);
    s.controller.dispose();
    const status = s.status.textContent;
    expect(s.waiting[0].signal.aborted).toBe(true);
    s.waiting[0].resolve(reading(PZ)); await first;
    expect(s.chart.option).toBeNull();
    expect(s.status.textContent).toBe(status);
    expect(s.handlers.size).toBe(0);
    await s.controller.showAsset(WL);
    expect(s.waiting).toHaveLength(1);
  });

  it('同一次场景点击中已解绑的旧联动不再向清空的图表发 action', async () => {
    const s = setup();
    const first = s.controller.showAsset(PZ);
    s.waiting[0].resolve(reading(PZ)); await first;
    s.scene.emit('select', { userData: { assetId: PZ } });
    expect(s.chart.actions).toHaveLength(0);
    s.controller.dispose();
    s.waiting[1].resolve([]);
  });
});
