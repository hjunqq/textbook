import {parseInstantMs} from '../../../shared/time.mjs';

const pore07 = {assetId: 'DAM-A-PZ-07', kind: 'pore', unit: 'kPa'};
const assetMap = new Map([['PZ07', pore07], ['pore-07', pore07]]);
const factors = {kPa: {kPa: 1}, Pa: {kPa: 0.001},
  m: {m: 1}, cm: {m: 0.01}, mm: {mm: 1}};

export function standardize(raw, source, schemaVersion,
    ingestTime = new Date().toISOString()) {
  const asset = assetMap.get(raw.sensorId);
  if (!asset) throw new Error('设备编码尚未映射');
  if (raw.kind !== asset.kind) throw new Error('测项与设备台账不一致');
  const {assetId, unit} = asset, factor = factors[raw.unit]?.[unit];
  if (!Number.isFinite(factor)) throw new Error('未知测项或不支持的单位转换');
  if (!['valid', 'suspect', 'missing'].includes(raw.quality)) throw new Error('未知质量码');
  if (!Number.isInteger(raw.version) || raw.version < 1) throw new Error('观测版本须为正整数');
  const ms = parseInstantMs(raw.time), received = parseInstantMs(ingestTime);
  if (!Number.isFinite(ms) || !Number.isFinite(received)) throw new Error('时间须有效且带时区');
  const empty = raw.value == null
    || (typeof raw.value === 'string' && raw.value.trim() === '');
  if (!empty && !Number.isFinite(raw.value)) throw new Error('数值须为有限数字');
  const quality = empty || raw.quality === 'missing' ? 'missing' : raw.quality;
  const value = quality === 'missing' ? null : raw.value * factor;
  if (value !== null && !Number.isFinite(value)) throw new Error('换算结果溢出');
  return {assetId, occurredAt: new Date(ms).toISOString(),
    ingestTime: new Date(received).toISOString(), value, unit, quality,
    version: raw.version, source, schemaVersion, sourceId: raw.sensorId,
    conversion: {from: raw.unit, to: unit, factor}};
}
