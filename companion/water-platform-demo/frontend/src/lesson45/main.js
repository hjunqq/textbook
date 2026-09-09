// 4.5 节阶段页入口：把对象列表渲染成按钮，点击后调用 controller.js 的 showAsset
import { loadAssets } from './detail.js';
import { bindList } from './controller.js';

const listEl = document.querySelector('#assets');
const outputEl = document.querySelector('#latest');
const assets = await loadAssets();
listEl.innerHTML = assets
  .map(a => `<li><button type="button" data-asset-id="${a.assetId}">${a.displayName}（${a.assetType}）</button></li>`)
  .join('');
bindList(listEl, outputEl, assets);
