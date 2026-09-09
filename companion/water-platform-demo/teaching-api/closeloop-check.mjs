// S6 闭环核对：把第8章“观测 → 质量检查 → 预警 → 值班员确认 → 工单 → 处置回写并归档”
// 这条链变成可执行的断言，并逐条验证受控状态流转的约束。
//
// 用法：node teaching-api/closeloop-check.mjs [baseUrl]
//   node teaching-api/server.mjs &
//   node teaching-api/closeloop-check.mjs http://localhost:8080
//
// 教学接口的工单是内存态，重启即清空——所以本脚本每次都从干净状态开始。
// 对接了数据库的完整后端，第8章的清单实现完成后同样应当全绿。

const base = (process.argv[2] ?? 'http://localhost:8080').replace(/\/$/, '');

let pass = 0, fail = 0;
const log = [];
const check = (name, cond, detail = '') => {
  if (cond) { pass++; log.push(['OK  ', name, '']); }
  else { fail++; log.push(['FAIL', name, detail]); }
};

async function call(path, options = {}) {
  const res = await fetch(base + path, options);
  const text = await res.text();
  let json = null;
  try { json = text === '' ? null : JSON.parse(text); } catch { /* 非 JSON */ }
  return { status: res.status, json, text };
}

const isContractError = (j, code) =>
  j && typeof j.code === 'string' && typeof j.message === 'string' && (!code || j.code === code);

const run = async () => {
  // 0. 登录
  const auth = await call('/api/auth/login', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'duty01', password: 'duty123' }),
  });
  check('值班员登录成功', auth.status === 200 && auth.json?.accessToken, `status=${auth.status}`);
  const h = { Authorization: `Bearer ${auth.json?.accessToken}`, 'Content-Type': 'application/json' };

  // 1. 观测进入平台：PZ-07 有可查的观测
  const latest = await call('/api/assets/DAM-A-PZ-07/readings/latest', { headers: h });
  check('PZ-07 有最新观测', latest.status === 200 && typeof latest.json?.value === 'number',
    `status=${latest.status}`);

  // 2. 质量检查：质量码必须是三选一，界面据此决定是否参与打分
  check('观测带质量码且取值合法',
    ['valid', 'suspect', 'missing'].includes(latest.json?.quality), `quality=${latest.json?.quality}`);

  // 3. 预警：四级 + NONE，且“未评估”与“无预警”分开表达
  const warnings = await call('/api/warnings', { headers: h });
  check('预警列表可读', warnings.status === 200 && Array.isArray(warnings.json), `status=${warnings.status}`);
  const levels = new Set((warnings.json ?? []).map(w => w.level));
  check('等级取 NONE/BLUE/YELLOW/ORANGE/RED',
    [...levels].every(l => ['NONE', 'BLUE', 'YELLOW', 'ORANGE', 'RED'].includes(l)), [...levels].join(','));
  const notEvaluable = (warnings.json ?? []).find(w => w.evaluable === false);
  check('存在 evaluable=false 的“未评估”事件，且其 level 为 NONE',
    notEvaluable && notEvaluable.level === 'NONE', JSON.stringify(notEvaluable));

  // 4. 受控状态流转：未评估的事件不能确认
  if (notEvaluable) {
    const bad = await call(`/api/warnings/${notEvaluable.warningId}/ack`, { method: 'POST', headers: h });
    check('未评估事件不允许确认（409）', bad.status === 409, `status=${bad.status}`);
    check('该 409 是契约错误体', isContractError(bad.json, 'NOT_EVALUABLE'), bad.text.slice(0, 140));
  }

  // 5. 取一个 open 的可评估预警走完整条链
  const open = (warnings.json ?? []).find(w => w.status === 'open' && w.evaluable);
  check('存在待处理的 open 预警', Boolean(open), JSON.stringify(warnings.json?.map(w => w.status)));
  if (!open) return;

  // 5a. 没确认就派单 → 409（图中没有从“已发出”直接到工单的边）
  const early = await call('/api/work-orders', {
    method: 'POST', headers: h,
    body: JSON.stringify({ warningId: open.warningId, ownerRole: '运维员', dueAt: '2026-07-06T12:00:00+08:00', action: '现场核查' }),
  });
  check('未确认就派单被拒（409）', early.status === 409, `status=${early.status}`);
  check('该 409 是契约错误体', isContractError(early.json, 'ILLEGAL_TRANSITION'), early.text.slice(0, 140));

  // 5b. 值班员确认
  const acked = await call(`/api/warnings/${open.warningId}/ack`, { method: 'POST', headers: h });
  check('值班员确认成功，状态转为 acknowledged',
    acked.status === 200 && acked.json?.status === 'acknowledged', acked.text.slice(0, 140));

  // 5c. 重复确认 → 409（状态机不允许回退，重复操作不能悄悄成功）
  const again = await call(`/api/warnings/${open.warningId}/ack`, { method: 'POST', headers: h });
  check('重复确认被拒（409）', again.status === 409, `status=${again.status}`);

  // 5d. 派单，缺字段先试一次
  const missingField = await call('/api/work-orders', {
    method: 'POST', headers: h, body: JSON.stringify({ warningId: open.warningId, ownerRole: '运维员' }),
  });
  check('派单缺字段返回 400 且指出字段',
    missingField.status === 400 && isContractError(missingField.json, 'FIELD_REQUIRED')
      && typeof missingField.json.field === 'string', missingField.text.slice(0, 140));

  const created = await call('/api/work-orders', {
    method: 'POST', headers: h,
    body: JSON.stringify({ warningId: open.warningId, ownerRole: '运维员', dueAt: '2026-07-06T12:00:00+08:00', action: '现场核查渗压计' }),
  });
  check('派单成功返回 201 与工单号',
    created.status === 201 && typeof created.json?.workOrderId === 'string', created.text.slice(0, 140));
  check('工单初始状态为 in_progress', created.json?.status === 'in_progress', created.json?.status);

  // 5e. 处置回写：没有 result 不能完成
  const noResult = await call(`/api/work-orders/${created.json?.workOrderId}/complete`, {
    method: 'POST', headers: h, body: JSON.stringify({}),
  });
  check('完成工单缺 result 返回 400', noResult.status === 400 && isContractError(noResult.json),
    noResult.text.slice(0, 140));

  const completed = await call(`/api/work-orders/${created.json?.workOrderId}/complete`, {
    method: 'POST', headers: h, body: JSON.stringify({ result: '现场检查未见渗漏，传感器重新标定' }),
  });
  check('工单完成返回 200 且状态为 completed',
    completed.status === 200 && completed.json?.status === 'completed', completed.text.slice(0, 140));

  // 5f. 归档：处置回写后预警才关闭
  const after = await call(`/api/warnings?assetId=${open.assetId}`, { headers: h });
  const archived = (after.json ?? []).find(w => w.warningId === open.warningId);
  check('处置回写后预警归档为 closed', archived?.status === 'closed', JSON.stringify(archived));

  // 5g. 已关闭的工单不能再次完成
  const twice = await call(`/api/work-orders/${created.json?.workOrderId}/complete`, {
    method: 'POST', headers: h, body: JSON.stringify({ result: '重复提交' }),
  });
  check('已完成的工单不能重复完成（409）', twice.status === 409, `status=${twice.status}`);
};

run().then(() => {
  for (const [tag, name, detail] of log) console.log(`  ${tag} ${name}${detail ? '  << ' + detail : ''}`);
  console.log(`\n第8章闭环 @ ${base}：通过 ${pass}，失败 ${fail}`);
  finish(fail ? 1 : 0);
}).catch(err => {
  console.error(`无法连接 ${base}：${err.message}`);
  finish(2);
});

// 退出：设置退出码后主动关掉 fetch 的连接池再退出。
// 直接调 process.exit() 会与 undici 尚未关闭的 keep-alive 套接字竞争，
// 在 Windows 上偶发 libuv 断言（退出码 127），CI 里会被误读成脚本失败。
async function finish(code) {
  process.exitCode = code;
  try { await globalThis[Symbol.for('undici.globalDispatcher.1')]?.close(); } catch { /* 忽略 */ }
}
