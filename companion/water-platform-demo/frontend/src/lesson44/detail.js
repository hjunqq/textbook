// S1 阶段包：详情页。
// 这里出现的 URLSearchParams 是 S1 与 S2 之间的桥：
// 本阶段用 ?assetId=... 从地址栏取参数，4.7 节换成 Vue Router 的 /assets/:assetId 后，
// 取参数的那一行变了，页面其余部分不用改——这就是“深链接”最朴素的形态。

import { assets } from './assets.js';
import { findAsset, parseAssetId } from './query.js';
import { renderAssetDetail } from './render.js';

const rootElement = document.querySelector('#asset-detail');
const titleElement = document.querySelector('#detail-title');

const requestedRaw = new URLSearchParams(location.search).get('assetId') ?? '';
const parsed = parseAssetId(requestedRaw);

if (!parsed.ok) {
  // 地址栏可以被任意编辑，所以这里必须重新校验一次，不能信任列表页已经校验过
  rootElement.dataset.state = 'invalid';
  rootElement.textContent = parsed.message;
  titleElement.textContent = '测点详情';
} else {
  const asset = findAsset(assets, parsed.assetId);
  renderAssetDetail(rootElement, asset, parsed.assetId);
  titleElement.textContent = asset ? asset.displayName : '未找到测点';
  document.title = `${titleElement.textContent} - 测点详情`;
}
