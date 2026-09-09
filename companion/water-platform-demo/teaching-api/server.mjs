// 教学接口（第4章）：零依赖 Node 18+ 服务，按 8.1 节接口契约（tab:api-contract）
// 用 companion/datasets 的固定数据模拟后端；通过查询参数 teach= 注入故障（tab:api-teach-faults）。
// 用法：node teaching-api/server.mjs [端口，默认 8080]
// 前端 Vite 代理把 /api 指向 http://localhost:8080 即可与真实后端互换，前端代码不改。
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const DATA = path.resolve(HERE, '../../datasets');
const PORT = Number(process.argv[2] ?? 8080);

// ---------- 固定数据集 ----------
function csv(file) {
  const [head, ...rows] = fs.readFileSync(path.join(DATA, file), 'utf8').trim().split(/\r?\n/);
  const keys = head.split(',');
  return rows.map(r => Object.fromEntries(r.split(',').map((v, i) => [keys[i], v])));
}
const assets = csv('stations.csv').map(s => ({
  assetId: s.asset_id, displayName: s.display_name, assetType: s.asset_type, unit: s.unit,
}));
const readings = ['piezometer.csv', 'water_level.csv', 'rainfall.csv'].flatMap(csv).map(r => ({
  assetId: r.asset_id, occurredAt: r.occurred_at, value: r.value === '' ? null : Number(r.value),
  unit: r.unit, quality: r.quality, eventId: r.event_id, version: Number(r.version),
}));
const byAsset = new Map();
for (const r of readings) (byAsset.get(r.assetId) ?? byAsset.set(r.assetId, []).get(r.assetId)).push(r);
for (const list of byAsset.values()) list.sort((a, b) => a.occurredAt.localeCompare(b.occurredAt));
const warnings = JSON.parse(fs.readFileSync(path.join(DATA, 'warnings.json'), 'utf8')).map(w => ({
  warningId: w.warning_id, assetId: w.asset_id, level: w.level, evaluable: w.evaluable,
  score: w.score, reason: w.reason, status: w.status,
}));

// 教学账号与骨架后端一致（SecurityConfig）
const USERS = { duty01: ['duty123', 'DUTY'], analyst01: ['analyst123', 'ANALYST'], ops01: ['ops123', 'OPS'] };
const tokens = new Map(); // token -> {username, authorities, exp}
const workOrders = new Map(); // workOrderId -> 工单；内存态，重启即清空

// ---------- 工具 ----------
function send(res, status, body, headers = {}) {
  const payload = body === undefined ? '' : JSON.stringify(body);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*', ...headers });
  res.end(payload);
}
const fail = (res, status, code, message, field) => send(res, status, { code, message, ...(field ? { field } : {}) });
function readBody(req) {
  return new Promise(resolve => { let s = ''; req.on('data', c => s += c); req.on('end', () => resolve(s)); });
}
function auth(req, res) {
  const m = /^Bearer (.+)$/.exec(req.headers.authorization ?? '');
  const t = m && tokens.get(m[1]);
  if (!t || t.exp < Date.now()) { fail(res, 401, 'UNAUTHORIZED', '未登录或令牌已失效'); return null; }
  return t;
}
const sleep = ms => new Promise(r => setTimeout(r, ms));

// ---------- 路由 ----------
async function handle(req, res) {
  const url = new URL(req.url, 'http://localhost');
  const teach = url.searchParams.get('teach') ?? '';
  if (req.method === 'OPTIONS') return send(res, 204);
  console.log(new Date().toISOString(), req.method, url.pathname + url.search);

  // 故障注入：真实后端没有这段逻辑，所以前端不能依赖它
  if (teach.startsWith('delay:')) await sleep(Number(teach.slice(6)) || 3000);
  if (teach === 'unauthorized') return fail(res, 401, 'UNAUTHORIZED', '未登录或令牌已失效');
  if (teach === 'error') return fail(res, 503, 'SERVICE_UNAVAILABLE', '服务暂时不可用，请稍后重试');
  if (teach === 'invalid') return fail(res, 400, 'INVALID_RANGE', '时间范围非法', 'from');

  if (req.method === 'POST' && url.pathname === '/api/auth/login') {
    let body = {};
    try { body = JSON.parse(await readBody(req) || '{}'); } catch { return fail(res, 400, 'BAD_JSON', '请求体不是合法 JSON'); }
    const u = USERS[body.username];
    if (!u || u[0] !== body.password) return fail(res, 401, 'UNAUTHORIZED', '用户名或密码错误');
    const token = crypto.randomBytes(24).toString('base64url');
    tokens.set(token, { username: body.username, authorities: [u[1]], exp: Date.now() + 1800_000 });
    return send(res, 200, { accessToken: token, expiresInSeconds: 1800, authorities: [u[1]] });
  }

  if (!url.pathname.startsWith('/api/')) return fail(res, 404, 'NOT_FOUND', '路径不存在');
  if (!auth(req, res)) return;

  if (req.method === 'GET' && url.pathname === '/api/assets') {
    if (teach === 'empty') return send(res, 200, []);
    const type = url.searchParams.get('assetType');
    return send(res, 200, type ? assets.filter(a => a.assetType === type) : assets);
  }

  const m = /^\/api\/assets\/([^/]+)\/readings(\/latest)?$/.exec(url.pathname);
  if (req.method === 'GET' && m) {
    const id = decodeURIComponent(m[1]);
    if (!assets.some(a => a.assetId === id)) return fail(res, 404, 'ASSET_NOT_FOUND', `对象 ${id} 不存在`);
    const list = byAsset.get(id) ?? [];
    if (m[2]) {                                   // /readings/latest
      if (teach === 'empty' || list.length === 0) return send(res, 204);
      return send(res, 200, list[list.length - 1]);
    }
    const from = url.searchParams.get('from'), to = url.searchParams.get('to');
    const badFrom = !from || Number.isNaN(Date.parse(from));
    if (badFrom || !to || Number.isNaN(Date.parse(to)))
      return fail(res, 400, 'INVALID_RANGE', 'from/to 必须是带时区的 ISO-8601 时间', badFrom ? 'from' : 'to');
    if (Date.parse(from) >= Date.parse(to)) return fail(res, 400, 'INVALID_RANGE', 'from 必须早于 to', 'from');
    if (teach === 'empty') return send(res, 200, []);
    const f = Date.parse(from), t = Date.parse(to);   // 左闭右开
    return send(res, 200, list.filter(r => { const x = Date.parse(r.occurredAt); return x >= f && x < t; }));
  }

  if (req.method === 'GET' && url.pathname === '/api/warnings') {
    if (teach === 'empty') return send(res, 200, []);
    let out = warnings;
    for (const k of ['level', 'status', 'assetId']) {
      const v = url.searchParams.get(k); if (v) out = out.filter(w => w[k] === v);
    }
    return send(res, 200, out);
  }

  // —— 第8章闭环：确认预警 → 建工单 → 完成 ——
  // 状态机见 8.4 节图“预警与工单的受控状态流转”：
  // open → acknowledged → assigned → handled → closed，
  // 没有 open 直接到 closed 的边——关闭必须经过工单校验。
  const ack = /^\/api\/warnings\/([^/]+)\/ack$/.exec(url.pathname);
  if (req.method === 'POST' && ack) {
    const w = warnings.find(x => x.warningId === decodeURIComponent(ack[1]));
    if (!w) return fail(res, 404, 'WARNING_NOT_FOUND', `预警 ${ack[1]} 不存在`);
    if (!w.evaluable) return fail(res, 409, 'NOT_EVALUABLE', '未评估的事件不能确认，先处理数据质量');
    if (w.status !== 'open') return fail(res, 409, 'ILLEGAL_TRANSITION', `状态 ${w.status} 不允许确认`);
    w.status = 'acknowledged';
    w.acknowledgedAt = new Date().toISOString();
    return send(res, 200, w);
  }

  if (req.method === 'POST' && url.pathname === '/api/work-orders') {
    let body = {};
    try { body = JSON.parse(await readBody(req) || '{}'); } catch { return fail(res, 400, 'BAD_JSON', '请求体不是合法 JSON'); }
    for (const k of ['warningId', 'ownerRole', 'dueAt', 'action']) {
      if (!body[k]) return fail(res, 400, 'FIELD_REQUIRED', `缺少必填字段 ${k}`, k);
    }
    const w = warnings.find(x => x.warningId === body.warningId);
    if (!w) return fail(res, 404, 'WARNING_NOT_FOUND', `预警 ${body.warningId} 不存在`);
    if (w.status !== 'acknowledged') {
      return fail(res, 409, 'ILLEGAL_TRANSITION', '必须先确认预警才能派单', 'warningId');
    }
    const order = {
      workOrderId: 'wo-' + String(workOrders.size + 1).padStart(4, '0'),
      warningId: body.warningId, ownerRole: body.ownerRole,
      dueAt: body.dueAt, action: body.action, status: 'in_progress',
    };
    workOrders.set(order.workOrderId, order);
    w.status = 'assigned';
    return send(res, 201, order, { Location: `/api/work-orders/${order.workOrderId}` });
  }

  const done = /^\/api\/work-orders\/([^/]+)\/complete$/.exec(url.pathname);
  if (req.method === 'POST' && done) {
    let body = {};
    try { body = JSON.parse(await readBody(req) || '{}'); } catch { return fail(res, 400, 'BAD_JSON', '请求体不是合法 JSON'); }
    const order = workOrders.get(decodeURIComponent(done[1]));
    if (!order) return fail(res, 404, 'WORK_ORDER_NOT_FOUND', `工单 ${done[1]} 不存在`);
    if (order.status !== 'in_progress') {
      return fail(res, 409, 'ILLEGAL_TRANSITION', `状态 ${order.status} 不允许完成`);
    }
    if (!body.result) return fail(res, 400, 'FIELD_REQUIRED', '缺少处置结果 result', 'result');
    order.status = 'completed';
    order.result = body.result;
    order.completedAt = new Date().toISOString();
    const w = warnings.find(x => x.warningId === order.warningId);
    if (w) w.status = 'closed';          // 处置回写后预警才归档
    return send(res, 200, order);
  }

  return fail(res, 404, 'NOT_FOUND', '路径不存在');
}

http.createServer((req, res) => handle(req, res).catch(e => fail(res, 500, 'INTERNAL', e.message)))
  .listen(PORT, () => console.log(`教学接口已启动：http://localhost:${PORT}  数据集：${DATA}`));
