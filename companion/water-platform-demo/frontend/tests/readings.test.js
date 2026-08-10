import {describe, expect, it} from 'vitest';
import {qualityText, readingQuery, toChartPoints} from '../src/utils/readings';

describe('toChartPoints', () => {
  it('keeps missing readings as null to break the line', () => {
    const points = toChartPoints([
      {occurredAt: '2026-08-08T08:00:00+08:00', value: 118.6, quality: 'valid'},
      {occurredAt: '2026-08-08T08:05:00+08:00', value: null, quality: 'missing'},
      {occurredAt: '2026-08-08T08:10:00+08:00', value: 119.1, quality: 'suspect'},
    ]);
    expect(points[0].value[1]).toBe(118.6);
    expect(points[1].value[1]).toBeNull();   // 缺测保位断线，而不是丢点
    expect(points[2].quality).toBe('suspect');
  });
});

describe('readingQuery', () => {
  it('builds a left-closed right-open window', () => {
    const query = readingQuery({from: '2026-08-07T08:00:00Z', to: '2026-08-08T08:00:00Z'});
    expect(query).toEqual({from: '2026-08-07T08:00:00Z', to: '2026-08-08T08:00:00Z'});
  });
  it('rejects an inverted window', () => {
    expect(() => readingQuery({from: '2026-08-08T08:00:00Z', to: '2026-08-07T08:00:00Z'}))
        .toThrow('时间窗起点必须早于终点');
  });
});

describe('qualityText', () => {
  it('covers exactly the three-value contract', () => {
    expect(Object.keys(qualityText).sort()).toEqual(['missing', 'suspect', 'valid']);
  });
});
