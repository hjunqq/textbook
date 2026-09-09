// S6 阶段包：质量码门禁与四级定级。
// 前三个用例与第8章清单 lst:ch08-classification-test 的三个 JUnit 断言一一对应，
// 把同一份契约在前后端各钉一次。
import { describe, it, expect } from 'vitest';
import { classify, score, WarningLevel, MIN_ACTION } from '../src/lesson84/classify.js';

describe('与书中 JUnit 用例对齐', () => {
  it('低分且有效 → 无预警（evaluable=true, NONE）', () => {
    const r = classify(0.01, 'valid');
    expect(r.evaluable).toBe(true);
    expect(r.level).toBe(WarningLevel.NONE);
    expect(r.reason).toBe('无预警');
  });

  it('0.30 且有效 → 蓝色', () => {
    const r = classify(0.30, 'valid');
    expect(r.evaluable).toBe(true);
    expect(r.level).toBe(WarningLevel.BLUE);
    expect(r.reason).toContain('蓝色');
  });

  it('高分但可疑 → 未评估，且 level 仍为 NONE', () => {
    const r = classify(0.90, 'suspect');
    expect(r.evaluable).toBe(false);
    expect(r.level).toBe(WarningLevel.NONE);
    expect(r.reason.startsWith('未评估')).toBe(true);
  });
});

describe('阈值与数据集一致', () => {
  it.each([
    [0.36, WarningLevel.BLUE],
    [0.58, WarningLevel.YELLOW],
    [0.74, WarningLevel.ORANGE],
    [0.92, WarningLevel.RED],
  ])('评分 %f 定级为 %s（与 warnings.json 一致）', (s, level) => {
    expect(classify(s, 'valid').level).toBe(level);
  });

  it('边界取下界闭、上界开', () => {
    expect(classify(0.2999, 'valid').level).toBe(WarningLevel.NONE);
    expect(classify(0.50, 'valid').level).toBe(WarningLevel.YELLOW);
    expect(classify(0.85, 'valid').level).toBe(WarningLevel.RED);
  });
});

describe('质量码门禁', () => {
  it('missing 不参与打分，理由说明是缺测', () => {
    const r = classify(0.95, 'missing');
    expect(r.evaluable).toBe(false);
    expect(r.reason).toContain('缺测');
  });

  it('未知质量码同样按未评估处理，不当成 valid', () => {
    expect(classify(0.95, 'unknown').evaluable).toBe(false);
  });

  it('有效但没有分数时也是未评估，不能当成无预警', () => {
    const r = classify(null, 'valid');
    expect(r.evaluable).toBe(false);
    expect(r.level).toBe(WarningLevel.NONE);
  });
});

describe('综合评分', () => {
  it('S = Σ wi·fi', () => {
    expect(score([0.2, 0.8], [0.5, 0.5])).toBeCloseTo(0.5, 10);
  });

  it('权重之和不为 1 时抛错，不悄悄归一化', () => {
    expect(() => score([0.2, 0.8], [0.5, 0.6])).toThrow(/权重之和/);
    expect(() => score([0.2], [-1])).toThrow(/不能为负/);
    expect(() => score([0.2, 0.8], [1])).toThrow(/个数不一致/);
  });
});

describe('最小处置要求', () => {
  it('五个状态各有一条处置要求', () => {
    expect(Object.keys(MIN_ACTION).sort())
      .toEqual(['BLUE', 'NONE', 'ORANGE', 'RED', 'YELLOW']);
    expect(MIN_ACTION.YELLOW).toContain('工单');
  });
});
