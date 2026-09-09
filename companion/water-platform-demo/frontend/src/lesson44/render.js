// S1 阶段包：把对象数组写进 DOM。
// 手法与 4.4 节清单“安全创建和更新测站 DOM”一致：先攒 DocumentFragment，
// 再用 replaceChildren 一次写入；所有外部数据一律走 textContent。
// 对象名称是数据，不是模板——用 innerHTML 拼接的话，
// 数据里一旦出现 <script> 就会被当成脚本执行。

import { formatReading } from './query.js';

/**
 * 渲染测点列表。
 * 结果为空时不是留白，而是显式写出“暂无测点”——
 * 空白页无法区分“没有匹配”和“代码坏了”。
 */
export function renderAssetList(listElement, assets) {
  if (assets.length === 0) {
    const empty = document.createElement('li');
    empty.className = 'asset-empty';
    empty.textContent = '暂无测点';
    listElement.replaceChildren(empty);
    return 0;
  }

  const fragment = document.createDocumentFragment();
  for (const asset of assets) {
    const item = document.createElement('li');
    item.className = 'asset-card';
    item.dataset.assetId = asset.assetId;

    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.assetId = asset.assetId;
    // 屏幕阅读器听到的是这句，不是拆散的三段文本
    button.setAttribute('aria-label',
      `${asset.displayName}，最新观测 ${formatReading(asset)}`);

    const name = document.createElement('span');
    name.className = 'asset-name';
    name.textContent = asset.displayName;

    const code = document.createElement('span');
    code.className = 'asset-code';
    code.textContent = asset.assetId;

    const reading = document.createElement('span');
    reading.className = 'asset-reading';
    reading.dataset.quality = asset.quality ?? 'none';
    reading.textContent = formatReading(asset);

    button.append(name, code, reading);
    item.append(button);
    fragment.append(item);
  }
  listElement.replaceChildren(fragment);
  return assets.length;
}

/** 更新列表上方的计数说明，aria-live 区域会把变化读给屏幕阅读器。 */
export function renderSummary(summaryElement, shown, total) {
  summaryElement.textContent = `显示 ${shown} 个测点，共 ${total} 个`;
}

/**
 * 渲染详情。找不到对象时写明输入了什么编码——
 * 只说“未找到”，学生无法判断是打错字还是数据缺失。
 */
export function renderAssetDetail(rootElement, asset, requestedId) {
  if (!asset) {
    rootElement.dataset.state = 'not-found';
    rootElement.textContent =
      `未找到编码 ${requestedId} 对应的测点。请回到列表页重新选择。`;
    return false;
  }

  rootElement.dataset.state = 'ready';
  const rows = [
    ['对象编码', asset.assetId],
    ['名称', asset.displayName],
    ['类型', asset.assetType],
    ['最新观测', formatReading(asset)],
    ['质量码', asset.quality ?? '无'],
    ['观测时间', asset.occurredAt ?? '无'],
  ];
  const list = document.createElement('dl');
  list.className = 'asset-detail';
  for (const [label, value] of rows) {
    const dt = document.createElement('dt');
    dt.textContent = label;
    const dd = document.createElement('dd');
    dd.textContent = value;
    list.append(dt, dd);
  }
  rootElement.replaceChildren(list);
  return true;
}
