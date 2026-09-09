// S1 阶段包：列表页的装配。
// 三件事：把固定数据渲染成列表、按关键字筛选与按值排序、把点击转成跳转。
// 事件委托的写法与 4.4 节清单“测站列表的事件委托与 preventDefault”一致：
// 监听器挂在稳定的父容器上，用 closest 找回具体按钮，再确认它确实属于本容器。

import { assets } from './assets.js';
import { filterByKeyword, sortByValue, parseAssetId, findAsset } from './query.js';
import { renderAssetList, renderSummary } from './render.js';

const listElement = document.querySelector('#asset-list');
const summaryElement = document.querySelector('#asset-summary');
const keywordInput = document.querySelector('#keyword');
const sortSelect = document.querySelector('#sort-direction');
const jumpInput = document.querySelector('#asset-id');
const jumpButton = document.querySelector('#jump-detail');
const jumpResult = document.querySelector('#jump-result');

// 当前视图 = 数据 → 筛选 → 排序 → 渲染。
// 每次交互都从原始 assets 重算，不在已渲染的 DOM 上做增量修改：
// 数据量只有 28 条，可预测比省几毫秒重要。
function refresh() {
  const filtered = filterByKeyword(assets, keywordInput.value);
  const ordered = sortByValue(filtered, sortSelect.value);
  const shown = renderAssetList(listElement, ordered);
  renderSummary(summaryElement, shown, assets.length);
}

keywordInput.addEventListener('input', refresh);
sortSelect.addEventListener('change', refresh);

// 事件委托：列表项是重新渲染出来的，逐个绑定监听器会随渲染次数累积
listElement.addEventListener('click', event => {
  const button = event.target.closest('button[data-asset-id]');
  if (!button || !listElement.contains(button)) return;
  location.href = `lesson44-detail.html?assetId=${button.dataset.assetId}`;
});

// 直接按编码跳转：这是 S1 验收要求的故障入口，
// 输入 DAM-A-XX-99 这类不存在的编码时，详情页必须给出明确提示而不是空白页。
jumpButton.addEventListener('click', () => {
  const parsed = parseAssetId(jumpInput.value);
  if (!parsed.ok) {
    jumpResult.dataset.state = 'invalid';
    jumpResult.textContent = parsed.message;
    return;
  }
  // 格式合法不等于对象存在：格式在前端判断，存在与否要查数据
  if (!findAsset(assets, parsed.assetId)) {
    jumpResult.dataset.state = 'not-found';
    jumpResult.textContent =
      `编码 ${parsed.assetId} 格式正确，但台账里没有这个测点。`;
    return;
  }
  jumpResult.dataset.state = 'ok';
  jumpResult.textContent = '';
  location.href = `lesson44-detail.html?assetId=${parsed.assetId}`;
});

refresh();
