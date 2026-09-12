import {describe, expect, it} from 'vitest';
import {acceptEvent, createEventWindow} from '../src/lesson71/event-window';

const reading = occurredAt => ({occurredAt, ingestTime: '2026-09-12T00:00:00Z'});
describe('event-time window', () => {
  it('replays historical data using event time and routes late events to revisions', () => {
    const state = createEventWindow(60 * 60_000, 10 * 60_000);
    acceptEvent(state, reading('2026-07-01T00:20:00Z'));
    acceptEvent(state, reading('2026-07-01T00:15:00Z'));
    const result = acceptEvent(state, reading('2026-07-01T00:05:00Z'));
    expect(result.events.map(e => e.occurredAt)).toEqual(['2026-07-01T00:15:00Z', '2026-07-01T00:20:00Z']);
    expect(result.revisions).toHaveLength(1);
    expect(result.watermark).toBe(Date.parse('2026-07-01T00:10:00Z'));
  });
  it('accepts the watermark boundary, preserves monotonicity and trims by event horizon', () => {
    const state = createEventWindow(60 * 60_000, 10 * 60_000);
    acceptEvent(state, reading('2026-07-01T00:20:00Z'));
    acceptEvent(state, reading('2026-07-01T08:10:00+08:00'));
    expect(state.events).toHaveLength(2);
    expect(state.watermark).toBe(Date.parse('2026-07-01T00:10:00Z'));
    acceptEvent(state, reading('2026-07-01T01:21:00Z'));
    expect(state.events).toHaveLength(1);
  });
  it('rejects invalid configuration and times without mutating the window', () => {
    expect(() => createEventWindow(0, 10)).toThrow();
    expect(() => createEventWindow(1000, -1)).toThrow();
    const state = createEventWindow(1000, 0);
    expect(() => acceptEvent(state, reading('2026-07-01T00:00:00'))).toThrow('带时区');
    expect(state.maxEventMs).toBe(-Infinity);
  });
});
