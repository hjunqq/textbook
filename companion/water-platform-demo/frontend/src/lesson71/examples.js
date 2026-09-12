import {alignReadings} from './resample.js';
import {inspectReading} from './quality.js';
import {standardize} from './standardize.js';

const raw = {sensorId: 'PZ07', kind: 'pore', unit: 'Pa', value: 185091,
  time: '2026-07-01T08:00:00+08:00', quality: 'suspect', version: 1};
const normalized = standardize(raw, 'gateway-02', 'v3', '2026-07-01T00:00:01Z');
const checked = inspectReading(normalized, {unit: 'kPa'});
const buckets = alignReadings([checked], 60 * 60 * 1000, 'porePressure');
console.log(JSON.stringify({value: normalized.value, quality: checked.quality,
  participates: checked.participates, bucketQuality: buckets[0].quality}));
// 预期：185.091、suspect、false、suspect；上游可疑标记不会被升级。
try { standardize({...raw, sensorId: 'unknown'}, 'gateway-02', 'v3'); }
catch (error) { console.log(error.message); } // 设备编码尚未映射
try { alignReadings([checked, checked], 3600000, 'porePressure'); }
catch (error) { console.log(error.message); } // 重复观测时间
console.log(inspectReading({...normalized, value: Infinity}, {unit: 'kPa'}).issues);
// 预期包含 value，记录被拒收，不参与评分。
