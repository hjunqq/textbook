import {parseInstantMs} from '../../../shared/time.mjs';

export function inspectReading(r, rules, previous) {
  if (!rules.unit || (rules.min !== undefined && !Number.isFinite(rules.min))
      || (rules.max !== undefined && !Number.isFinite(rules.max))
      || rules.min > rules.max) throw new Error('质量规则配置非法');
  const issues = [];
  let quality = r.quality, rejected = false;
  const reject = issue => {
    issues.push(issue); rejected = true;
    if (quality !== 'missing') quality = 'suspect';
  };
  if (!['valid', 'suspect', 'missing'].includes(quality)) reject('quality');
  if (r.value == null) quality = 'missing';
  else if (!Number.isFinite(r.value)) reject('value');
  if (r.unit !== rules.unit) reject('unit');
  if (quality !== 'missing' && Number.isFinite(r.value)
      && (r.value < rules.min || r.value > rules.max)) reject('range');
  const ms = parseInstantMs(r.occurredAt);
  if (!Number.isFinite(ms)) reject('time');
  if (previous) {
    const previousMs = parseInstantMs(previous.occurredAt);
    if (!Number.isFinite(previousMs)) reject('previous-time');
    else if (Number.isFinite(ms) && ms <= previousMs) reject('time-order');
  }
  return {...r, quality, issues, rejected,
    participates: quality === 'valid' && !rejected};
}
