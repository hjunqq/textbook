// S6 阶段包：质量码门禁与四级预警定级。
//
// 这是第8章两个最容易踩的坑的正面写法：
//   坑一：把 suspect 数据送进评分，于是系统连续产生蓝色事件，值班员关掉推送，
//         真正的黄色趋势反而没人确认；
//   坑二：把“未评估”折叠成 NONE，于是缺测被显示成“正常”。
// 因此 evaluable 与 level 是两个维度：evaluable=false 表示质量不足以判定，
// evaluable=true 且 level=NONE 才是“当前规则下无预警”。
//
// 阈值是示例值，与 companion/datasets/warnings.json 一致（0.36 蓝 / 0.58 黄 /
// 0.74 橙 / 0.92 红）。生产阈值必须版本化，并记录适用工程、工况、审批人与生效时间。

/** 预警等级。NONE 表示规则算过且未触发，不表示“没算”。 */
export const WarningLevel = {
  NONE: 'NONE', BLUE: 'BLUE', YELLOW: 'YELLOW', ORANGE: 'ORANGE', RED: 'RED',
};

/** 示例阈值：下界闭、上界开。 */
export const THRESHOLDS = [
  [0.85, WarningLevel.RED],
  [0.70, WarningLevel.ORANGE],
  [0.50, WarningLevel.YELLOW],
  [0.30, WarningLevel.BLUE],
];

/** 质量码到“是否参与打分”的口径，见第8章质量码下游处理表。 */
export const SCORABLE = { valid: true, suspect: false, missing: false };

/**
 * 综合评分 S = Σ wi·fi，权重非负且和为 1。
 * 权重或指标不合法时抛错而不是悄悄归一化——错误的权重会让评分整体偏移，
 * 而偏移后的分数看起来仍然“像个分数”，最难被发现。
 */
export function score(indicators, weights) {
  if (indicators.length !== weights.length) {
    throw new Error('指标与权重个数不一致');
  }
  if (weights.some(w => w < 0)) throw new Error('权重不能为负');
  const sum = weights.reduce((a, b) => a + b, 0);
  if (Math.abs(sum - 1) > 1e-9) throw new Error(`权重之和必须为 1，当前为 ${sum}`);
  return indicators.reduce((acc, f, i) => acc + weights[i] * f, 0);
}

/**
 * 定级。质量码优先于分数：质量不合格时直接“未评估”，分数再高也不升级。
 * 返回 { evaluable, level, reason }，三者一起构成界面要显示的完整状态。
 */
export function classify(scoreValue, quality) {
  if (!(quality in SCORABLE)) {
    return { evaluable: false, level: WarningLevel.NONE, reason: `未评估：未知质量码 ${quality}` };
  }
  if (!SCORABLE[quality]) {
    const why = quality === 'missing' ? '记录缺测' : '数值存疑，仅供复核';
    return { evaluable: false, level: WarningLevel.NONE, reason: `未评估：${why}` };
  }
  if (typeof scoreValue !== 'number' || Number.isNaN(scoreValue)) {
    return { evaluable: false, level: WarningLevel.NONE, reason: '未评估：没有可用的综合评分' };
  }
  for (const [bound, level] of THRESHOLDS) {
    if (scoreValue >= bound) {
      return { evaluable: true, level, reason: `${LEVEL_TEXT[level]}：综合评分 ${scoreValue.toFixed(2)}` };
    }
  }
  return { evaluable: true, level: WarningLevel.NONE, reason: '无预警' };
}

export const LEVEL_TEXT = {
  NONE: '无预警', BLUE: '蓝色', YELLOW: '黄色', ORANGE: '橙色', RED: '红色',
};

/** 每一级的最小处置要求，与第8章预警等级表一致。 */
export const MIN_ACTION = {
  NONE: '保持监测，保留质量与规则版本',
  BLUE: '值班员确认，检查数据质量',
  YELLOW: '专业复核，创建工单',
  ORANGE: '启动会商，评估预案',
  RED: '按批准规程处置并持续跟踪',
};
