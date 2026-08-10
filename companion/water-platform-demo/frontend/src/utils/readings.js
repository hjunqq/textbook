// 与图表和列表共享的纯函数，便于单元测试（vitest）

export const qualityText = {valid: '有效', suspect: '可疑', missing: '缺测'};

/** 缺测点以 null 保留时间位置，曲线在此断开（connectNulls 必须为 false）。 */
export function toChartPoints(readings) {
  return readings.map(item => ({
    value: [item.occurredAt, item.quality === 'missing' ? null : item.value],
    quality: item.quality,
  }));
}

/** 观测查询参数：左闭右开时间窗，时间必须是 ISO 8601 字符串。 */
export function readingQuery(range) {
  if (!range?.from || !range?.to) throw new Error('时间窗 from/to 不能为空');
  if (range.from >= range.to) throw new Error('时间窗起点必须早于终点');
  return {from: range.from, to: range.to};
}
