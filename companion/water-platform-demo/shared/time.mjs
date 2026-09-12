// 本教材在界面与教学数据处理中以 UTC 毫秒比较带时区时间。
// 先检查格式与日历日期，避免 Date.parse 的宽松解析接受本地时间或日期溢出。
export function parseInstantMs(value) {
  if (typeof value !== 'string') return NaN;
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,9}))?)?(Z|[+-]\d{2}:\d{2})$/.exec(value);
  if (!match) return NaN;
  const [, year, month, day, hour, minute, second = '0', , zone] = match;
  const y = Number(year), m = Number(month), d = Number(day);
  const leap = y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
  const days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  if (m < 1 || m > 12 || d < 1 || d > days[m - 1]
      || Number(hour) > 23 || Number(minute) > 59 || Number(second) > 59) return NaN;
  if (zone !== 'Z') {
    const zh = Number(zone.slice(1, 3)), zm = Number(zone.slice(4));
    if (zh > 18 || zm > 59 || (zh === 18 && zm !== 0)) return NaN;
  }
  return Date.parse(value);
}
