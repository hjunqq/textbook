import { loadLatest } from './detail.js';
import { State, render } from './state.js';

let sequence = 0;       // 每次切换递增；只有最新序号的响应才允许写入页面
let controller = null;  // 上一次请求的取消句柄

export async function showAsset(el, asset) {
  const mine = ++sequence;
  controller?.abort();                        // 第一道防线：通知旧请求结果不再需要
  controller = new AbortController();
  render(el, { state: State.LOADING, asset });
  try {
    const reading = await loadLatest(asset.assetId, controller.signal);
    if (mine !== sequence) return;            // 第二道防线：迟到的旧响应静默丢弃
    render(el, reading ? { state: State.READY, asset, reading }
                       : { state: State.EMPTY, asset });
  } catch (error) {
    if (error.name === 'AbortError') return;  // 被自己取消的不是故障
    if (mine !== sequence) return;
    render(el, { state: State.ERROR, asset, error });
  }
}

// 列表点击：<button data-asset-id="DAM-A-PZ-07">…</button>
export function bindList(listEl, outputEl, assets) {
  listEl.addEventListener('click', event => {
    const id = event.target.closest('button')?.dataset.assetId;
    const asset = assets.find(a => a.assetId === id);
    if (asset) showAsset(outputEl, asset);
  });
}
