import {describe, expect, it} from 'vitest';
import {alignReadings} from '../src/lesson71/resample.js';
import {inspectReading} from '../src/lesson71/quality.js';
import {standardize} from '../src/lesson71/standardize.js';

const sample = {assetId: 'DAM-A-PZ-07', unit: 'kPa', version: 1,
  value: 185.091, quality: 'valid', occurredAt: '2026-07-01T00:00:00Z'};
const raw = {sensorId: 'PZ07', kind: 'pore', unit: 'Pa', value: 185091,
  quality: 'valid', version: 1, time: '2026-07-01T08:00:00+08:00'};
const normalize = change => standardize({...raw, ...change}, 'gateway-02', 'v3',
  '2026-07-01T00:00:01Z');

describe('lesson71 event-time resampling', () => {
  it('selects the last usable instant across offsets without mutating input', () => {
    const rows = [{...sample, value: 186, occurredAt: '2026-07-01T00:55:00Z'},
      {...sample, value: 180, occurredAt: '2026-07-01T08:05:00+08:00'}];
    const before = structuredClone(rows);
    expect(alignReadings(rows, 3600000, 'porePressure')[0].value).toBe(186);
    expect(rows).toEqual(before);
  });
  it('excludes missing values, nonfinite values and rejected records', () => {
    const rows = [sample,
      {...sample, quality: 'missing', value: 999, occurredAt: '2026-07-01T00:05:00Z'},
      {...sample, value: Infinity, occurredAt: '2026-07-01T00:10:00Z'},
      {...sample, value: 999, rejected: true, occurredAt: '2026-07-01T00:15:00Z'}];
    expect(alignReadings(rows, 3600000, 'porePressure')[0])
      .toMatchObject({value: 185.091, sampleCount: 1, quality: 'suspect'});
    expect(alignReadings(rows.slice(1), 3600000, 'porePressure')[0])
      .toMatchObject({value: null, quality: 'missing'});
  });
  it('marks partially missing rainfall and absent samples as suspect', () => {
    const rain = {...sample, assetId: 'RAIN-RF-01', unit: 'mm', value: 1};
    const second = {...rain, value: 2, occurredAt: '2026-07-01T00:05:00Z'};
    expect(alignReadings([rain, second], 600000, 'rainfall', 300000)[0])
      .toMatchObject({value: 3, quality: 'valid', expectedSamples: 2});
    expect(alignReadings([rain, {...second, quality: 'missing', value: 999}],
      600000, 'rainfall', 300000)[0]).toMatchObject({value: 1, quality: 'suspect'});
    expect(alignReadings([rain], 600000, 'rainfall', 300000)[0].quality).toBe('suspect');
  });
  it('rejects duplicated instants, mixed assets and mixed observation versions', () => {
    expect(() => alignReadings([sample, {...sample,
      occurredAt: '2026-07-01T08:00:00+08:00'}], 3600000, 'porePressure')).toThrow('重复');
    for (const change of [{assetId: 'other'}, {version: 2}, {unit: 'm'}]) {
      expect(() => alignReadings([sample, {...sample, ...change}], 3600000,
        'porePressure')).toThrow('同一');
    }
  });
  it('only emits present buckets and rejects invalid time or grid configuration', () => {
    expect(alignReadings([], 3600000, 'porePressure')).toEqual([]);
    const later = {...sample, occurredAt: '2026-07-01T02:00:00Z'};
    expect(alignReadings([sample, later], 3600000, 'porePressure')).toHaveLength(2);
    expect(() => alignReadings([sample], 0, 'porePressure')).toThrow('格网');
    expect(() => alignReadings([sample], 3600000, 'rainfall')).toThrow('采样周期');
    expect(() => alignReadings([{...sample, occurredAt: '2026-02-30T00:00:00Z'}],
      3600000, 'porePressure')).toThrow('时间');
  });
});

describe('lesson71 quality preservation', () => {
  it('preserves upstream suspect and missing even when the numeric value is finite', () => {
    for (const quality of ['suspect', 'missing']) {
      expect(inspectReading({...sample, quality}, {unit: 'kPa'}))
        .toMatchObject({quality, participates: false});
    }
    expect(inspectReading({...sample, value: null}, {unit: 'kPa'}).quality).toBe('missing');
  });
  it.each([NaN, Infinity, -Infinity, '185.091', ''])('rejects invalid value %s', value => {
    expect(inspectReading({...sample, value}, {unit: 'kPa'}))
      .toMatchObject({quality: 'suspect', rejected: true, participates: false, issues: ['value']});
  });
  it('rejects unknown quality and applies optional limits without inventing defaults', () => {
    expect(inspectReading({...sample, quality: 'normal'}, {unit: 'kPa'}).issues).toContain('quality');
    expect(inspectReading(sample, {unit: 'kPa'}).participates).toBe(true);
    expect(inspectReading(sample, {unit: 'kPa', max: 180}).issues).toContain('range');
    expect(inspectReading(sample, {unit: 'm'}).issues).toContain('unit');
  });
  it('uses actual instants for ordering and rejects invalid timestamps', () => {
    const next = {...sample, occurredAt: '2026-07-01T01:00:00Z'};
    const previous = {...sample, occurredAt: '2026-07-01T08:00:00+08:00'};
    expect(inspectReading(next, {unit: 'kPa'}, previous).participates).toBe(true);
    expect(inspectReading(previous, {unit: 'kPa'}, next).issues).toContain('time-order');
    expect(inspectReading({...sample, occurredAt: '2026-07-01'}, {unit: 'kPa'}).issues)
      .toContain('time');
  });
});

describe('lesson71 source normalization', () => {
  it('converts Pa to kPa while retaining suspect quality and source provenance', () => {
    expect(normalize({quality: 'suspect'})).toMatchObject({assetId: 'DAM-A-PZ-07',
      value: 185.091, unit: 'kPa', quality: 'suspect', version: 1,
      occurredAt: '2026-07-01T00:00:00.000Z', sourceId: 'PZ07',
      conversion: {from: 'Pa', to: 'kPa', factor: 0.001}});
    expect(normalize({unit: 'kPa', value: 185.091}).value).toBe(185.091);
  });
  it.each([null, undefined, '', '  '])('keeps empty value %s missing rather than zero', value => {
    expect(normalize({value})).toMatchObject({quality: 'missing', value: null});
  });
  it('keeps upstream missing and rejects bad values, mappings, units and time', () => {
    expect(normalize({quality: 'missing', value: 185091}).value).toBeNull();
    for (const value of [NaN, Infinity, '185091', 'bad']) {
      expect(() => normalize({value})).toThrow('有限数字');
    }
    expect(() => normalize({sensorId: 'unknown'})).toThrow('尚未映射');
    expect(() => normalize({kind: 'level', unit: 'm'})).toThrow('台账不一致');
    expect(() => normalize({unit: 'bar'})).toThrow('单位转换');
    expect(() => normalize({quality: 'normal'})).toThrow('质量码');
    expect(() => normalize({time: '2026-07-01T00:00:00'})).toThrow('带时区');
  });
});
