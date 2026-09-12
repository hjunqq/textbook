import {describe, expect, it} from 'vitest';
import {qualityText, readingQuery, toChartPoints} from '../src/utils/readings';
import {parseInstantMs} from '../../shared/time.mjs';

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
  it('compares instants across UTC offsets instead of comparing text', () => {
    const range = {from: '2026-07-01T08:00:00+08:00', to: '2026-07-01T01:00:00Z'};
    expect(readingQuery(range)).toEqual(range);
    expect(() => readingQuery({from: range.to, to: range.from})).toThrow('起点必须早于终点');
    expect(() => readingQuery({from: range.from, to: '2026-07-01T00:00:00Z'}))
      .toThrow('起点必须早于终点');
  });
  it.each(['2026-07-01', '2026-07-01T00:00:00', '2026-02-30T00:00:00Z',
    '2026-07-01T24:00:00Z', '2026-07-01T00:00:00+19:00', 'bad', 123])(
    'rejects invalid or unzoned input %s', from => {
      expect(() => readingQuery({from, to: '2026-07-02T00:00:00Z'})).toThrow('带时区');
    });
  it('rejects an invalid upper bound and accepts leap day and milliseconds', () => {
    expect(() => readingQuery({from: '2026-07-01T00:00:00Z', to: 'not-a-date'})).toThrow('带时区');
    expect(parseInstantMs('2024-02-29T08:00:00.123+08:00'))
      .toBe(Date.UTC(2024, 1, 29, 0, 0, 0, 123));
  });
});

describe('qualityText', () => {
  it('covers exactly the three-value contract', () => {
    expect(Object.keys(qualityText).sort()).toEqual(['missing', 'suspect', 'valid']);
  });
});
