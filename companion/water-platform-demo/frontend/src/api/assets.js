import { request } from './request.js';

export const loadLatest = assetId =>
  request(`/api/assets/${encodeURIComponent(assetId)}/readings/latest`);

// 唯一参数源：output/case-params.tex 的 cpFloodLimitLevel，见 8.1 节。
export const FLOOD_LIMIT_LEVEL = 165.5;
export function needsWaterLevelAttention(reading) {
  return reading?.assetId === 'DAM-A-WL-01' && reading.quality === 'valid'
    && reading.unit === 'm' && Number.isFinite(reading.value)
    && reading.value >= FLOOD_LIMIT_LEVEL;
}
