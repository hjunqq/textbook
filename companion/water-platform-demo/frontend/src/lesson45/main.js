// 4.5 节阶段页入口：把对象列表渲染成按钮，点击后调用 controller.js 的 showAsset
import { login, loadAssets } from './detail.js';
import { bindList } from './controller.js';

const listEl = document.querySelector('#assets');
const outputEl = document.querySelector('#latest');
// 入口自己登录：detail.js 不再有顶层入口块，令牌必须由这里取得，
// 否则后面的请求带着 Bearer null，教学接口按契约返回 401。
await login('duty01', 'duty123');
const assets = await loadAssets();
listEl.innerHTML = assets
  .map(a => `<li><button type="button" data-asset-id="${a.assetId}">${a.displayName}（${a.assetType}）</button></li>`)
  .join('');
bindList(listEl, outputEl, assets);
