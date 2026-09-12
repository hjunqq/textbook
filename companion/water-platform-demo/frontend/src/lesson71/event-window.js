import {parseInstantMs} from '../../../shared/time.mjs';

export function createEventWindow(windowMs, allowedLatenessMs) {
  if (!Number.isFinite(windowMs) || windowMs <= 0
      || !Number.isFinite(allowedLatenessMs) || allowedLatenessMs < 0)
    throw new Error('窗口长度须为正数，乱序容忍度须为非负数');
  return {windowMs, allowedLatenessMs, maxEventMs: -Infinity,
    watermark: -Infinity, events: [], revisions: []};
}

export function acceptEvent(state, reading) {
  const eventMs = parseInstantMs(reading.occurredAt);
  const ingestMs = parseInstantMs(reading.ingestTime);
  if (!Number.isFinite(eventMs) || !Number.isFinite(ingestMs))
    throw new Error('观测与接收时间必须有效且带时区');
  // 用此前的水印判断迟到；处理时间只用于测量延迟。
  const item = {...reading, eventMs, ingestMs, late: eventMs < state.watermark};
  if (item.late) state.revisions.push(item);
  else state.events.push(item);
  state.maxEventMs = Math.max(state.maxEventMs, eventMs);
  state.watermark = state.maxEventMs - state.allowedLatenessMs;
  const start = state.maxEventMs - state.windowMs;
  state.events = state.events.filter(e => e.eventMs >= start)
    .sort((a, b) => a.eventMs - b.eventMs);
  return {events: state.events, revisions: state.revisions,
    watermark: state.watermark};
}

export function windowExample() {
  const state = createEventWindow(25 * 60 * 60 * 1000, 10 * 60 * 1000);
  const reading = {assetId: 'DAM-A-PZ-07', occurredAt: '2026-07-01T00:20:00Z',
    ingestTime: '2026-09-12T00:00:00Z', value: 185.091, quality: 'valid'};
  acceptEvent(state, reading);
  return acceptEvent(state, {...reading, occurredAt: '2026-07-01T00:05:00Z'});
}
console.log(windowExample().revisions.length); // 输出 1：历史回放中一次过迟事件
