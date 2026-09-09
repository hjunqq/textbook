// 开发时由 Vite 代理把 /api 转发到教学接口或真实后端（见 4.5.6）
let token = null;

export async function login(username, password) {
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ username, password })
  });
  if (!res.ok) throw new Error(`LOGIN_${res.status}`);
  token = (await res.json()).accessToken;
}

async function getJson(path, signal) {
  const res = await fetch(path, {
    headers: { Accept: 'application/json', Authorization: `Bearer ${token}` },
    signal
  });
  if (res.status === 204) return null;                // 契约：尚无观测
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));  // 契约：{code, message, field?}
    throw Object.assign(new Error(body.code ?? `HTTP_${res.status}`),
                        { status: res.status, body });
  }
  return res.json();
}

export const loadAssets = () => getJson('/api/assets');
export const loadLatest = (assetId, signal) =>
  getJson(`/api/assets/${encodeURIComponent(assetId)}/readings/latest`, signal);

export function renderLatest(el, asset, reading) {
  if (!reading) { el.textContent = `${asset.displayName}：暂无观测`; return; }
  el.textContent = `${asset.displayName}：${reading.value} ${reading.unit}`
    + `（${reading.occurredAt}，质量 ${reading.quality}）`;
}

// 页面入口（index.html 中 <p id="latest"></p> 与 <script type="module" src="/src/detail.js">）
const output = document.querySelector('#latest');
await login('duty01', 'duty123');
const assets = await loadAssets();
const pz07 = assets.find(a => a.assetId === 'DAM-A-PZ-07');
renderLatest(output, pz07, await loadLatest(pz07.assetId));
