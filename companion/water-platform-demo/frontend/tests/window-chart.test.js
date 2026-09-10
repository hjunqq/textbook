// @vitest-environment node
import { afterEach, describe, expect, it } from 'vitest';
import * as echarts from 'echarts';
import { createWindowChart } from '../src/lesson74/window-chart.js';

let chart;
function setup() {
  chart = echarts.init(null, null, { renderer: 'svg', ssr: true, width: 640, height: 360 });
  return createWindowChart(chart);
}
afterEach(() => chart?.dispose());

describe('书中折线清单在 ECharts 5.5.1 上的行为', () => {
  it('超过300条后保留末尾窗口，missing仍为空值并断线', () => {
    const live = setup();
    for (let i = 0; i < 301; i++) live.appendTail({
      occurredAt: new Date(Date.UTC(2026, 6, 1, 0, i)).toISOString(),
      value: i, quality: i === 300 ? 'missing' : 'valid',
    });
    const series = chart.getOption().series.find(s => s.id === 'level');
    expect(series.data).toHaveLength(300);
    expect(series.data[0][1]).toBe(1);
    expect(series.data.at(-1)[1]).toBeNull();
    expect(series.connectNulls).toBe(false);
    expect(chart.renderToSVGString()).toContain('<svg');
  });

  it('切换水位与雨量后使用不同的单位轴，后续追加保留新窗口', () => {
    const live = setup();
    const time = '2026-07-01T00:00:00+08:00';
    live.replaceWithTwoSeries([[time, 165]], [[time, 8]]);
    live.appendTail({ occurredAt: '2026-07-01T00:05:00+08:00', value: 166, quality: 'valid' });
    const option = chart.getOption();
    expect(option.series.map(s => s.yAxisIndex)).toEqual([0, 1]);
    expect(option.yAxis.map(a => a.name)).toEqual(['水位/m', '雨量/mm']);
    expect(option.series[0].data).toHaveLength(2);
    expect(option.series[1].data).toEqual([[time, 8]]);
  });
});
