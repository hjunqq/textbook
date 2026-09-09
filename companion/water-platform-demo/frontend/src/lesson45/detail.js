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

// 教材 4.5.2 的清单在这里还有一段页面入口（查 #latest、登录、渲染 PZ-07），
// 因为那时 detail.js 就是页面唯一的脚本。4.5.5 起 main.js 成为入口后必须删掉它：
// 模块顶层的语句在被 import 时就会执行，留着会导致每次导入都重新登录、
// 并在 main.js 渲染列表之前先渲染一次 PZ-07；测试里导入 controller.js 也会被它带跑。
