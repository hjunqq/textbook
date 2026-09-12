import {parseInstantMs} from '../../../shared/time.mjs';

export function alignReadings(readings, gridMs, kind, sampleMs) {
  if (!Number.isSafeInteger(gridMs) || gridMs <= 0) throw new Error('格网须为正整数毫秒');
  if (!['level', 'porePressure', 'rainfall'].includes(kind)) throw new Error('未知测项');
  const isRain = kind === 'rainfall';
  if (isRain && (!Number.isSafeInteger(sampleMs) || sampleMs <= 0
      || gridMs % sampleMs !== 0)) throw new Error('雨量采样周期须整除格网');
  const buckets = new Map(), times = new Set();
  const first = readings[0];
  for (const r of readings) {
    if (!r.assetId || !r.unit || !Number.isInteger(r.version) || r.version < 1
        || r.assetId !== first.assetId || r.unit !== first.unit
        || r.version !== first.version) throw new Error('须为同一对象、单位和版本');
    if (!['valid', 'suspect', 'missing'].includes(r.quality)) throw new Error('未知质量码');
    const ms = parseInstantMs(r.occurredAt);
    if (!Number.isFinite(ms)) throw new Error('观测时间须为带时区的有效时间');
    if (times.has(ms)) throw new Error('重复观测时间，请先解决重复记录');
    times.add(ms);
    if (isRain && ms % sampleMs !== 0) throw new Error('雨量时间须位于采样格网上');
    const start = Math.floor(ms / gridMs) * gridMs;
    const rows = buckets.get(start) ?? [];
    rows.push({...r, ms});
    buckets.set(start, rows);
  }
  return [...buckets].sort(([a], [b]) => a - b).map(([start, rows]) => {
    rows.sort((a, b) => a.ms - b.ms);
    const usable = rows.filter(r => r.quality !== 'missing'
      && Number.isFinite(r.value) && !r.rejected);
    const expectedSamples = isRain ? gridMs / sampleMs : null;
    const complete = !isRain || usable.length === expectedSamples;
    const clean = rows.every(r => r.quality === 'valid'
      && Number.isFinite(r.value) && !r.rejected);
    const value = usable.length === 0 ? null : isRain
      ? usable.reduce((sum, r) => sum + r.value, 0) : usable.at(-1).value;
    if (value !== null && !Number.isFinite(value)) throw new Error('聚合结果溢出');
    return {assetId: first.assetId, unit: first.unit, version: first.version,
      time: new Date(start).toISOString(), value, gridMs, expectedSamples,
      sampleCount: usable.length, aggregated: true,
      quality: !usable.length ? 'missing' : complete && clean ? 'valid' : 'suspect'};
  });
}
