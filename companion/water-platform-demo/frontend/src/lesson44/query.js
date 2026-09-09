// S1 阶段包：列表的筛选、排序与编码校验。
// 这里全部是纯函数——输入数组和参数，返回新数组或结果对象，不碰 DOM、不改入参。
// 这样做有两个好处：4.4 节的自测题可以直接调用它们，4.6 节改用 Vue 时这一层原样保留。

/** 对象编码的形状：DAM-A-<类型码>-<序号>，见 8.1 节参数表的编码规则。 */
const ASSET_ID_PATTERN = /^DAM-A-[A-Z]{1,2}-\d{2}$/;

/**
 * 校验用户输入的对象编码。
 * 返回 { ok: true, assetId } 或 { ok: false, message }——不抛异常，
 * 因为“用户打错字”是正常业务分支，不是程序错误。
 */
export function parseAssetId(raw) {
  const text = String(raw ?? '').trim().toUpperCase();
  if (text === '') {
    return { ok: false, message: '请输入对象编码，例如 DAM-A-PZ-07' };
  }
  if (!ASSET_ID_PATTERN.test(text)) {
    return { ok: false, message: `“${text}”不是合法的对象编码，格式应为 DAM-A-PZ-07` };
  }
  return { ok: true, assetId: text };
}

/**
 * 按显示名称或编码筛选。关键字为空时返回全部。
 * 大小写不敏感；关键字只做包含匹配，不做模糊搜索。
 */
export function filterByKeyword(assets, keyword) {
  const text = String(keyword ?? '').trim().toLowerCase();
  if (text === '') return [...assets];
  return assets.filter(asset =>
    asset.displayName.toLowerCase().includes(text) ||
    asset.assetId.toLowerCase().includes(text));
}

/**
 * 按最新观测值排序。
 * 没有观测的对象（value 为 null）永远排在最后，不参与升降序比较——
 * 否则 null 会被当成 0，8 个位移测点就会挤到升序的最前面，看起来像“水位最低”。
 */
export function sortByValue(assets, direction = 'asc') {
  const sign = direction === 'desc' ? -1 : 1;
  return [...assets].sort((a, b) => {
    if (a.value === null && b.value === null) return 0;
    if (a.value === null) return 1;
    if (b.value === null) return -1;
    return sign * (a.value - b.value);
  });
}

/** 按编码查找单个对象；找不到返回 undefined，由调用方决定怎么提示。 */
export function findAsset(assets, assetId) {
  return assets.find(asset => asset.assetId === assetId);
}

/** 观测值的显示文本。没有观测时给出明确说明，不显示空白也不显示 0。 */
export function formatReading(asset) {
  if (asset.value === null) return '暂无观测';
  return `${asset.value} ${asset.unit}`;
}
